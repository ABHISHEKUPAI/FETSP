from datetime import date, datetime, timedelta

import plotly.express as px
import streamlit as st

from modules.anhal_manager import PRIORITIES, GoalManager
from modules.csv_manager import DataError
from modules.helpers import (build_report, index_of, load_or_stop, multiselect_filter,
                             search_filter, show_metrics,
                             show_problem_warning, to_date, to_float)

st.set_page_config(page_title="Anhal – Savings Goals", page_icon="🎯", layout="wide")

manager = GoalManager()

st.title("Savings Goals")
load_or_stop(manager)  # health check: stops here with a friendly message if the CSV is unusable

tab_view, tab_add, tab_update, tab_delete, tab_stats, tab_report = st.tabs(
    ["View Data", "Add Record", "Update Record", "Delete Record", "Analytics", "Report"]
)

# ------------------------------------------------------------------ CREATE
with tab_add:
    st.subheader("Add a new savings goal")
    with st.form("an_add_form"):
        col1, col2 = st.columns(2)
        add_name = col1.text_input("Goal name", key="an_add_name")
        add_priority = col1.selectbox("Priority", PRIORITIES, index=1, key="an_add_priority")
        add_deadline = col1.date_input("Deadline", value=date.today() + timedelta(days=180),
                                       key="an_add_deadline")
        add_target = col2.number_input("Target amount (₹)", min_value=0.0, step=500.0, format="%.2f",
                                       key="an_add_target")
        add_saved = col2.number_input("Saved so far (₹)", min_value=0.0, step=500.0, format="%.2f",
                                      key="an_add_saved")
        add_submitted = st.form_submit_button("Add goal")
    if add_submitted:
        try:
            new_id = manager.create_record({
                "goal_name": add_name, "target_amount": add_target, "saved_amount": add_saved,
                "deadline": add_deadline, "priority": add_priority,
            })
        except DataError as err:
            st.error(f"Could not add the goal:\n\n{err}")
        else:
            st.success(f"Goal added with ID {new_id}.")

# ------------------------------------------------------------------ UPDATE
with tab_update:
    st.subheader("Update an existing goal")
    update_id = st.number_input("Record ID to update", min_value=1, step=1, key="an_upd_id")
    try:
        current = manager.get_record(update_id)
    except DataError as err:
        st.warning(str(err))
    else:
        with st.form(f"an_upd_form_{update_id}"):
            col1, col2 = st.columns(2)
            upd_name = col1.text_input("Goal name", value=current["goal_name"],
                                       key=f"an_upd_name_{update_id}")
            upd_priority = col1.selectbox("Priority", PRIORITIES,
                                          index=index_of(PRIORITIES, current["priority"]),
                                          key=f"an_upd_priority_{update_id}")
            upd_deadline = col1.date_input("Deadline", value=to_date(current["deadline"]),
                                           key=f"an_upd_deadline_{update_id}")
            upd_target = col2.number_input("Target amount (₹)", min_value=0.0, step=500.0,
                                           format="%.2f", value=to_float(current["target_amount"]),
                                           key=f"an_upd_target_{update_id}")
            upd_saved = col2.number_input("Saved so far (₹)", min_value=0.0, step=500.0,
                                          format="%.2f", value=to_float(current["saved_amount"]),
                                          key=f"an_upd_saved_{update_id}")
            upd_submitted = st.form_submit_button("Save changes")
        if upd_submitted:
            try:
                manager.update_record(update_id, {
                    "goal_name": upd_name, "target_amount": upd_target,
                    "saved_amount": upd_saved, "deadline": upd_deadline, "priority": upd_priority,
                })
            except DataError as err:
                st.error(f"Could not update record {update_id}:\n\n{err}")
            else:
                st.success(f"Record {update_id} updated.")

# ------------------------------------------------------------------ DELETE
with tab_delete:
    st.subheader("Delete a goal")
    delete_id = st.number_input("Record ID to delete", min_value=1, step=1, key="an_del_id")
    try:
        to_delete = manager.get_record(delete_id)
    except DataError as err:
        st.warning(str(err))
    else:
        st.write("This is the record that will be deleted:")
        st.table([to_delete])
        confirmed = st.checkbox("Yes, I want to permanently delete this record",
                                key=f"an_del_confirm_{delete_id}")
        if st.button("Delete record", type="primary", disabled=not confirmed, key="an_del_button"):
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
filtered = multiselect_filter(data, "priority", "Priority",
                              sorted(set(PRIORITIES) | set(data["priority"].dropna())), active_filters)
filtered = multiselect_filter(filtered, "status", "Status",
                              ["In progress", "Completed"], active_filters)
filtered = search_filter(filtered, "goal_name", "Search goal name", active_filters)

problems = manager.problem_rows(filtered)
stats = manager.summary_stats(filtered)

with tab_view:
    st.subheader("All savings goals")
    st.caption(f"Showing {len(filtered)} of {len(data)} records. Use the sidebar to filter. "
               "Progress, remaining, days left and status are calculated from the other columns.")
    show_problem_warning(problems)
    col1, col2 = st.columns(2)
    sort_by = col1.selectbox("Sort by", list(filtered.columns), key="an_sort_by")
    order = col2.radio("Order", ["Ascending", "Descending"], horizontal=True, key="an_order")
    shown = filtered.sort_values(sort_by, ascending=(order == "Ascending"), na_position="last")
    if shown.empty:
        st.info("No records match the current filters.")
    else:
        st.dataframe(shown, hide_index=True, column_config={
            "id": st.column_config.NumberColumn("ID", format="%d"),
            "target_amount": st.column_config.NumberColumn("Target (₹)", format="₹%.2f"),
            "saved_amount": st.column_config.NumberColumn("Saved (₹)", format="₹%.2f"),
            "deadline": st.column_config.DateColumn("Deadline", format="YYYY-MM-DD"),
            "progress_pct": st.column_config.NumberColumn("Progress (%)", format="%.1f"),
            "remaining": st.column_config.NumberColumn("Remaining (₹)", format="₹%.2f"),
            "days_left": st.column_config.NumberColumn("Days left", format="%d"),
        })

with tab_stats:
    if not stats:
        st.info("There are no goals with valid amounts for the current filters, "
                "so there is nothing to analyse.")
    else:
        st.subheader("Summary statistics")
        show_metrics(stats)
        st.subheader("Charts")
        left, right = st.columns(2)
        with left:
            fig = px.bar(manager.progress_data(filtered), x="progress_pct", y="goal_name",
                         orientation="h", title="Progress towards each goal (%)",
                         labels={"progress_pct": "Progress (%)", "goal_name": "Goal"})
            st.plotly_chart(fig, key="an_chart_progress")
        with right:
            fig = px.pie(manager.priority_targets(filtered), names="priority",
                         values="target_amount", hole=0.45,
                         title="Share of total target by priority")
            st.plotly_chart(fig, key="an_chart_priority")

with tab_report:
    st.subheader("Summary report")
    report_text = build_report("Anhal — Savings Goals Report", "Anhal", manager,
                               len(data), len(filtered), len(problems), active_filters, stats)
    st.code(report_text, language="text")
    st.download_button("⬇️ Download report (.txt)", data=report_text,
                       file_name=f"anhal_report_{datetime.now():%Y%m%d_%H%M%S}.txt",
                       mime="text/plain", key="an_report_download")
