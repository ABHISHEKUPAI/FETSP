from datetime import date, datetime

import plotly.express as px
import streamlit as st

from modules.csv_manager import DataError
from modules.gautam_manager import INCOME_TYPES, IncomeManager
from modules.helpers import (build_report, date_filter, index_of, load_or_stop,
                             multiselect_filter, placeholder_banner, search_filter,
                             show_metrics, show_problem_warning, to_date, to_float)

st.set_page_config(page_title="Gautam – Income", page_icon="💵", layout="wide")

manager = IncomeManager()

st.title("Income Records")
placeholder_banner("income records", manager)
load_or_stop(manager)  # health check: stops here with a friendly message if the CSV is unusable

tab_view, tab_add, tab_update, tab_delete, tab_stats, tab_report = st.tabs(
    ["📋 View Data", "➕ Add Record", "✏️ Update Record", "🗑️ Delete Record", "📊 Analytics", "📄 Report"]
)

# ------------------------------------------------------------------ CREATE
with tab_add:
    st.subheader("Add a new income entry")
    with st.form("ga_add_form"):
        col1, col2 = st.columns(2)
        add_date = col1.date_input("Date", value=date.today(), key="ga_add_date")
        add_type = col1.selectbox("Income type", INCOME_TYPES, key="ga_add_type")
        add_source = col2.text_input("Source (who paid you?)", key="ga_add_source")
        add_amount = col2.number_input("Amount (₹)", min_value=0.0, step=100.0, format="%.2f",
                                       key="ga_add_amount")
        add_submitted = st.form_submit_button("Add income entry")
    if add_submitted:
        try:
            new_id = manager.create_record({
                "date": add_date, "source": add_source,
                "income_type": add_type, "amount": add_amount,
            })
        except DataError as err:
            st.error(f"Could not add the income entry:\n\n{err}")
        else:
            st.success(f"Income entry added with ID {new_id}.")

# ------------------------------------------------------------------ UPDATE
with tab_update:
    st.subheader("Update an existing income entry")
    update_id = st.number_input("Record ID to update", min_value=1, step=1, key="ga_upd_id")
    try:
        current = manager.get_record(update_id)
    except DataError as err:
        st.warning(str(err))
    else:
        with st.form(f"ga_upd_form_{update_id}"):
            col1, col2 = st.columns(2)
            upd_date = col1.date_input("Date", value=to_date(current["date"]),
                                       key=f"ga_upd_date_{update_id}")
            upd_type = col1.selectbox("Income type", INCOME_TYPES,
                                      index=index_of(INCOME_TYPES, current["income_type"]),
                                      key=f"ga_upd_type_{update_id}")
            upd_source = col2.text_input("Source", value=current["source"],
                                         key=f"ga_upd_source_{update_id}")
            upd_amount = col2.number_input("Amount (₹)", min_value=0.0, step=100.0, format="%.2f",
                                           value=to_float(current["amount"]),
                                           key=f"ga_upd_amount_{update_id}")
            upd_submitted = st.form_submit_button("Save changes")
        if upd_submitted:
            try:
                manager.update_record(update_id, {
                    "date": upd_date, "source": upd_source,
                    "income_type": upd_type, "amount": upd_amount,
                })
            except DataError as err:
                st.error(f"Could not update record {update_id}:\n\n{err}")
            else:
                st.success(f"Record {update_id} updated.")

# ------------------------------------------------------------------ DELETE
with tab_delete:
    st.subheader("Delete an income entry")
    delete_id = st.number_input("Record ID to delete", min_value=1, step=1, key="ga_del_id")
    try:
        to_delete = manager.get_record(delete_id)
    except DataError as err:
        st.warning(str(err))
    else:
        st.write("This is the record that will be deleted:")
        st.table([to_delete])
        confirmed = st.checkbox("Yes, I want to permanently delete this record",
                                key=f"ga_del_confirm_{delete_id}")
        if st.button("Delete record", type="primary", disabled=not confirmed, key="ga_del_button"):
            try:
                manager.delete_record(delete_id)
            except DataError as err:
                st.error(f"Could not delete record {delete_id}:\n\n{err}")
            else:
                st.success(f"Record {delete_id} deleted.")

# ---------------------------------------------- READ (reload after any change)
data = load_or_stop(manager)

st.sidebar.header("🔎 Filters")
active_filters = []
filtered = date_filter(data, "date", "Date range", active_filters)
filtered = multiselect_filter(filtered, "income_type", "Income type",
                              sorted(set(INCOME_TYPES) | set(data["income_type"].dropna())), active_filters)
filtered = multiselect_filter(filtered, "source", "Source",
                              sorted(data["source"].dropna().unique()), active_filters)
filtered = search_filter(filtered, "source", "Search source", active_filters)

problems = manager.problem_rows(filtered)
stats = manager.summary_stats(filtered)

with tab_view:
    st.subheader("All income entries")
    st.caption(f"Showing {len(filtered)} of {len(data)} records. Use the sidebar to filter.")
    show_problem_warning(problems)
    col1, col2 = st.columns(2)
    sort_by = col1.selectbox("Sort by", list(filtered.columns), key="ga_sort_by")
    order = col2.radio("Order", ["Ascending", "Descending"], horizontal=True, key="ga_order")
    shown = filtered.sort_values(sort_by, ascending=(order == "Ascending"), na_position="last")
    if shown.empty:
        st.info("No records match the current filters.")
    else:
        st.dataframe(shown, hide_index=True, column_config={
            "id": st.column_config.NumberColumn("ID", format="%d"),
            "date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
            "amount": st.column_config.NumberColumn("Amount (₹)", format="₹%.2f"),
        })

with tab_stats:
    if not stats:
        st.info("There are no valid amounts for the current filters, so there is nothing to analyse.")
    else:
        st.subheader("Summary statistics")
        show_metrics(stats)
        st.subheader("Charts")
        left, right = st.columns(2)
        with left:
            fig = px.pie(manager.type_totals(filtered), names="income_type", values="amount",
                         hole=0.45, title="Income by type")
            st.plotly_chart(fig, key="ga_chart_type")
        with right:
            fig = px.line(manager.monthly_totals(filtered), x="month", y="amount", markers=True,
                          title="Monthly income",
                          labels={"month": "Month", "amount": "Total (₹)"})
            st.plotly_chart(fig, key="ga_chart_monthly")
        fig = px.histogram(filtered.dropna(subset=["amount"]), x="amount", nbins=10,
                           title="Distribution of entry amounts",
                           labels={"amount": "Amount (₹)"})
        fig.update_layout(yaxis_title="Number of entries")
        st.plotly_chart(fig, key="ga_chart_hist")

with tab_report:
    st.subheader("Summary report")
    report_text = build_report("Gautam — Income Records Report", "Gautam", manager,
                               len(data), len(filtered), len(problems), active_filters, stats)
    st.code(report_text, language="text")
    st.download_button("⬇️ Download report (.txt)", data=report_text,
                       file_name=f"gautam_report_{datetime.now():%Y%m%d_%H%M%S}.txt",
                       mime="text/plain", key="ga_report_download")
