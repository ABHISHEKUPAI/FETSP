from datetime import date, datetime

import plotly.express as px
import streamlit as st

from modules.abhishek_manager import CATEGORIES, BudgetManager
from modules.csv_manager import DataError
from modules.helpers import (build_report, index_of, load_or_stop, multiselect_filter,
                             placeholder_banner, show_metrics, show_problem_warning, to_float)

st.set_page_config(page_title="Abhishek – Budgets", page_icon="📒", layout="wide")

manager = BudgetManager()

st.title("📒 Monthly Budgets")
placeholder_banner("monthly budgets vs actual spending", manager)
load_or_stop(manager)  # health check: stops here with a friendly message if the CSV is unusable

tab_view, tab_add, tab_update, tab_delete, tab_stats, tab_report = st.tabs(
    ["📋 View Data", "➕ Add Record", "✏️ Update Record", "🗑️ Delete Record", "📊 Analytics", "📄 Report"]
)

# ------------------------------------------------------------------ CREATE
with tab_add:
    st.subheader("Add a new budget line")
    with st.form("ab_add_form"):
        col1, col2 = st.columns(2)
        add_month = col1.text_input("Month (YYYY-MM)", value=date.today().strftime("%Y-%m"),
                                    key="ab_add_month")
        add_category = col1.selectbox("Category", CATEGORIES, key="ab_add_category")
        add_budget = col2.number_input("Budget amount (₹)", min_value=0.0, step=100.0, format="%.2f",
                                       key="ab_add_budget")
        add_spent = col2.number_input("Actual spent (₹)", min_value=0.0, step=100.0, format="%.2f",
                                      key="ab_add_spent")
        add_submitted = st.form_submit_button("Add budget line")
    if add_submitted:
        try:
            new_id = manager.create_record({
                "month": add_month, "category": add_category,
                "budget_amount": add_budget, "actual_spent": add_spent,
            })
        except DataError as err:
            st.error(f"Could not add the budget line:\n\n{err}")
        else:
            st.success(f"Budget line added with ID {new_id}.")

# ------------------------------------------------------------------ UPDATE
with tab_update:
    st.subheader("Update an existing budget line")
    update_id = st.number_input("Record ID to update", min_value=1, step=1, key="ab_upd_id")
    try:
        current = manager.get_record(update_id)
    except DataError as err:
        st.warning(str(err))
    else:
        with st.form(f"ab_upd_form_{update_id}"):
            col1, col2 = st.columns(2)
            upd_month = col1.text_input("Month (YYYY-MM)", value=current["month"],
                                        key=f"ab_upd_month_{update_id}")
            upd_category = col1.selectbox("Category", CATEGORIES,
                                          index=index_of(CATEGORIES, current["category"]),
                                          key=f"ab_upd_category_{update_id}")
            upd_budget = col2.number_input("Budget amount (₹)", min_value=0.0, step=100.0,
                                           format="%.2f", value=to_float(current["budget_amount"]),
                                           key=f"ab_upd_budget_{update_id}")
            upd_spent = col2.number_input("Actual spent (₹)", min_value=0.0, step=100.0,
                                          format="%.2f", value=to_float(current["actual_spent"]),
                                          key=f"ab_upd_spent_{update_id}")
            upd_submitted = st.form_submit_button("Save changes")
        if upd_submitted:
            try:
                manager.update_record(update_id, {
                    "month": upd_month, "category": upd_category,
                    "budget_amount": upd_budget, "actual_spent": upd_spent,
                })
            except DataError as err:
                st.error(f"Could not update record {update_id}:\n\n{err}")
            else:
                st.success(f"Record {update_id} updated.")

# ------------------------------------------------------------------ DELETE
with tab_delete:
    st.subheader("Delete a budget line")
    delete_id = st.number_input("Record ID to delete", min_value=1, step=1, key="ab_del_id")
    try:
        to_delete = manager.get_record(delete_id)
    except DataError as err:
        st.warning(str(err))
    else:
        st.write("This is the record that will be deleted:")
        st.table([to_delete])
        confirmed = st.checkbox("Yes, I want to permanently delete this record",
                                key=f"ab_del_confirm_{delete_id}")
        if st.button("Delete record", type="primary", disabled=not confirmed, key="ab_del_button"):
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
filtered = multiselect_filter(data, "month", "Month",
                              sorted(data["month"].dropna().unique()), active_filters)
filtered = multiselect_filter(filtered, "category", "Category",
                              sorted(set(CATEGORIES) | set(data["category"].dropna())), active_filters)
filtered = multiselect_filter(filtered, "status", "Status",
                              ["Within budget", "Over budget"], active_filters)

problems = manager.problem_rows(filtered)
stats = manager.summary_stats(filtered)

with tab_view:
    st.subheader("All budget lines")
    st.caption(f"Showing {len(filtered)} of {len(data)} records. Use the sidebar to filter. "
               "Variance, utilisation and status are calculated from the two amount columns.")
    show_problem_warning(problems)
    col1, col2 = st.columns(2)
    sort_by = col1.selectbox("Sort by", list(filtered.columns), key="ab_sort_by")
    order = col2.radio("Order", ["Ascending", "Descending"], horizontal=True, key="ab_order")
    shown = filtered.sort_values(sort_by, ascending=(order == "Ascending"), na_position="last")
    if shown.empty:
        st.info("No records match the current filters.")
    else:
        st.dataframe(shown, hide_index=True, column_config={
            "id": st.column_config.NumberColumn("ID", format="%d"),
            "budget_amount": st.column_config.NumberColumn("Budget (₹)", format="₹%.2f"),
            "actual_spent": st.column_config.NumberColumn("Actual spent (₹)", format="₹%.2f"),
            "variance": st.column_config.NumberColumn("Variance (₹)", format="₹%.2f"),
            "utilisation_pct": st.column_config.NumberColumn("Utilisation (%)", format="%.1f"),
        })

with tab_stats:
    if not stats:
        st.info("There are no complete budget lines for the current filters, "
                "so there is nothing to analyse.")
    else:
        st.subheader("Summary statistics")
        show_metrics(stats)
        st.subheader("Charts")
        left, right = st.columns(2)
        with left:
            fig = px.bar(manager.budget_vs_actual(filtered), x="category", y="Amount",
                         color="Type", barmode="group", title="Budget vs actual spending by category",
                         labels={"category": "Category", "Amount": "Total (₹)"})
            st.plotly_chart(fig, key="ab_chart_grouped")
        with right:
            points = manager.scatter_data(filtered)
            fig = px.scatter(points, x="budget_amount", y="actual_spent", color="category",
                             hover_data=["month"], title="Budget vs actual (each dot = one line)",
                             labels={"budget_amount": "Budget (₹)", "actual_spent": "Actual spent (₹)"})
            limit = float(max(points["budget_amount"].max(), points["actual_spent"].max()))
            fig.add_shape(type="line", x0=0, y0=0, x1=limit, y1=limit,
                          line=dict(dash="dot", color="gray"))
            fig.add_annotation(x=limit, y=limit, text="on budget", showarrow=False, yshift=12)
            st.plotly_chart(fig, key="ab_chart_scatter")
        st.caption("Dots above the dotted line are over budget; dots below it are within budget.")

with tab_report:
    st.subheader("Summary report")
    report_text = build_report("Abhishek — Monthly Budgets Report", "Abhishek", manager,
                               len(data), len(filtered), len(problems), active_filters, stats)
    st.code(report_text, language="text")
    st.download_button("⬇️ Download report (.txt)", data=report_text,
                       file_name=f"abhishek_report_{datetime.now():%Y%m%d_%H%M%S}.txt",
                       mime="text/plain", key="ab_report_download")
