"""Small helpers shared by the pages: messages, sidebar filters, report text."""
from datetime import datetime

import pandas as pd
import streamlit as st

from modules.csv_manager import DataError

# Switch to False once the real CSV files have replaced the dummy ones.
PLACEHOLDER_DATA = True


# ------------------------------------------------------------- value conversion
def to_float(value, default=0.0):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return default if pd.isna(number) else number


def to_date(value):
    parsed = pd.to_datetime(value, errors="coerce")
    return datetime.today().date() if pd.isna(parsed) else parsed.date()


def index_of(options, value):
    return options.index(value) if value in options else 0


# ------------------------------------------------------------------- messages


def load_or_stop(manager):
    """Return the typed data, or show a friendly message and stop the page."""
    try:
        return manager.read_records()
    except DataError as err:
        st.error(f"Could not load the data. {err}")
        if manager.can_reset():
            st.info("The file is missing or completely empty. You can create a fresh, empty CSV "
                    "with the correct columns.")
            if st.button("Create empty CSV", key=f"reset_{manager.path.stem}"):
                try:
                    manager.create_empty_file()
                except DataError as save_error:
                    st.error(str(save_error))
                else:
                    st.rerun()
        else:
            st.info("Please fix the CSV file manually (check the header row and file format), "
                    "then reload this page.")
        st.stop()


def show_problem_warning(problems):
    if problems.empty:
        return
    st.warning(
        f"⚠️ {len(problems)} row(s) have missing or invalid values (blank cells, or text where a "
        "number/date is expected). They stay in the CSV and are shown in the table, but are left "
        "out of any statistic or chart that needs the missing value. Fix them with **Update Record**."
    )
    with st.expander("Show the affected rows"):
        st.dataframe(problems, hide_index=True)


def show_metrics(stats):
    """Show a dict of {label: text} as rows of 4 KPI metrics."""
    items = list(stats.items())
    for start in range(0, len(items), 4):
        columns = st.columns(4)
        for column, (label, value) in zip(columns, items[start:start + 4]):
            column.metric(label, value)


# -------------------------------------------------------------- sidebar filters
# Each filter records itself in `active_filters` only when it actually narrows the data.
def date_filter(df, column, label, active_filters):
    valid = df[column].dropna()
    if valid.empty:
        return df
    first, last = valid.min().date(), valid.max().date()
    picked = st.sidebar.date_input(label, value=(first, last), min_value=first, max_value=last)
    if len(picked) == 2 and (picked[0] > first or picked[1] < last):
        active_filters.append(f"{label}: {picked[0]} to {picked[1]}")
        return df[df[column].between(pd.Timestamp(picked[0]), pd.Timestamp(picked[1]))]
    return df


def multiselect_filter(df, column, label, options, active_filters):
    picked = st.sidebar.multiselect(label, options, default=options)
    if set(picked) != set(options):
        chosen = ", ".join(picked) if picked else "(nothing selected)"
        active_filters.append(f"{label}: {chosen}")
        return df[df[column].isin(picked)]
    return df


def search_filter(df, column, label, active_filters):
    text = st.sidebar.text_input(label).strip()
    if text:
        active_filters.append(f"{label}: '{text}'")
        return df[df[column].str.contains(text, case=False, na=False, regex=False)]
    return df


# ---------------------------------------------------------------------- report
def build_report(title, owner, manager, total_rows, shown_rows, problem_count,
                 active_filters, stats):
    """Plain-text summary report of the owner's current data and filters."""
    line = "=" * 62
    lines = [
        line,
        title.upper(),
        line,
        f"Generated at              : {datetime.now():%Y-%m-%d %H:%M:%S}",
        f"Owner                     : {owner}",
        f"Dataset file              : data/{manager.path.name}",
    ]
    if PLACEHOLDER_DATA:
        lines.append("NOTE                      : PLACEHOLDER dummy data (not the final dataset)")
    lines += [
        "",
        f"Rows in CSV (total)       : {total_rows}",
        f"Rows after filters        : {shown_rows}",
        f"Rows missing/invalid data : {problem_count}",
        "",
        "Active filters:",
    ]
    lines += [f"  - {item}" for item in active_filters] or ["  - None (all records)"]
    lines += ["", "Summary statistics:"]
    if stats:
        lines += [f"  - {label}: {value}" for label, value in stats.items()]
    else:
        lines.append("  - No valid data for the current filters.")
    lines += [
        "",
        "Note: rows with missing/invalid values stay in the CSV but are excluded",
        "from any statistic that needs the missing value.",
        line,
    ]
    return "\n".join(lines)
