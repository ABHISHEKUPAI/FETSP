from datetime import date, datetime

import plotly.express as px
import streamlit as st

from modules.csv_manager import DataError
from modules.helpers import (build_report, date_filter, index_of, load_or_stop,
                             multiselect_filter, search_filter,
                             show_metrics, show_problem_warning, to_date, to_float)
from modules.shawn_manager import CATEGORIES, PAYMENT_MODES, TransactionManager

st.set_page_config(page_title="Shawn – Transactions", page_icon="🧾", layout="wide")

manager = TransactionManager()

st.title("Expense Transactions")
load_or_stop(manager)  # health check: stops here with a friendly message if the CSV is unusable

tab_view, tab_add, tab_update, tab_delete, tab_stats, tab_report = st.tabs(
    ["View Data", "Add Record", "Update Record", "Delete Record", "Analytics", "Report"]
)

# ------------------------------------------------------------------ CREATE
with tab_add:
    st.subheader("Add a new transaction")
    with st.form("sh_add_form"):
        col1, col2 = st.columns(2)
        add_date = col1.date_input("Date", value=date.today(), key="sh_add_date")
        add_category = col1.selectbox("Category", CATEGORIES, key="sh_add_category")
        add_payment = col1.selectbox("Payment mode", PAYMENT_MODES, key="sh_add_payment")
        add_description = col2.text_input("Description", key="sh_add_description")
        add_amount = col2.number_input("Amount (₹)", min_value=0.0, step=10.0, format="%.2f",
                                       key="sh_add_amount")
        add_submitted = st.form_submit_button("Add transaction")
    if add_submitted:
        try:
            new_id = manager.create_record({
                "date": add_date, "category": add_category, "description": add_description,
                "amount": add_amount, "payment_mode": add_payment,
            })
        except DataError as err:
            st.error(f"Could not add the transaction:\n\n{err}")
        else:
            st.success(f"Transaction added with ID {new_id}.")

# ------------------------------------------------------------------ UPDATE
with tab_update:
    st.subheader("Update an existing transaction")
    update_id = st.number_input("Record ID to update", min_value=1, step=1, key="sh_upd_id")
    try:
        current = manager.get_record(update_id)
    except DataError as err:
        st.warning(str(err))
    else:
        with st.form(f"sh_upd_form_{update_id}"):
            col1, col2 = st.columns(2)
            upd_date = col1.date_input("Date", value=to_date(current["date"]),
                                       key=f"sh_upd_date_{update_id}")
            upd_category = col1.selectbox("Category", CATEGORIES,
                                          index=index_of(CATEGORIES, current["category"]),
                                          key=f"sh_upd_category_{update_id}")
            upd_payment = col1.selectbox("Payment mode", PAYMENT_MODES,
                                         index=index_of(PAYMENT_MODES, current["payment_mode"]),
                                         key=f"sh_upd_payment_{update_id}")
            upd_description = col2.text_input("Description", value=current["description"],
                                              key=f"sh_upd_description_{update_id}")
            upd_amount = col2.number_input("Amount (₹)", min_value=0.0, step=10.0, format="%.2f",
                                           value=to_float(current["amount"]),
                                           key=f"sh_upd_amount_{update_id}")
            upd_submitted = st.form_submit_button("Save changes")
        if upd_submitted:
            try:
                manager.update_record(update_id, {
                    "date": upd_date, "category": upd_category, "description": upd_description,
                    "amount": upd_amount, "payment_mode": upd_payment,
                })
            except DataError as err:
                st.error(f"Could not update record {update_id}:\n\n{err}")
            else:
                st.success(f"Record {update_id} updated.")

# ------------------------------------------------------------------ DELETE
with tab_delete:
    st.subheader("Delete a transaction")
    delete_id = st.number_input("Record ID to delete", min_value=1, step=1, key="sh_del_id")
    try:
        to_delete = manager.get_record(delete_id)
    except DataError as err:
        st.warning(str(err))
    else:
        st.write("This is the record that will be deleted:")
        st.table([to_delete])
        confirmed = st.checkbox("Yes, I want to permanently delete this record",
                                key=f"sh_del_confirm_{delete_id}")
        if st.button("Delete record", type="primary", disabled=not confirmed, key="sh_del_button"):
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
filtered = multiselect_filter(filtered, "category", "Category",
                              sorted(set(CATEGORIES) | set(data["category"].dropna())), active_filters)
filtered = multiselect_filter(filtered, "payment_mode", "Payment mode",
                              sorted(set(PAYMENT_MODES) | set(data["payment_mode"].dropna())), active_filters)
filtered = search_filter(filtered, "description", "Search description", active_filters)

problems = manager.problem_rows(filtered)
stats = manager.summary_stats(filtered)

with tab_view:
    st.subheader("All transactions")
    st.caption(f"Showing {len(filtered)} of {len(data)} records. Use the sidebar to filter.")
    show_problem_warning(problems)
    col1, col2 = st.columns(2)
    sort_by = col1.selectbox("Sort by", list(filtered.columns), key="sh_sort_by")
    order = col2.radio("Order", ["Ascending", "Descending"], horizontal=True, key="sh_order")
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
            fig = px.bar(manager.category_totals(filtered), x="category", y="amount",
                         title="Spending by category",
                         labels={"category": "Category", "amount": "Total (₹)"})
            st.plotly_chart(fig, key="sh_chart_category")
        with right:
            fig = px.line(manager.monthly_totals(filtered), x="month", y="amount", markers=True,
                          title="Monthly spending trend",
                          labels={"month": "Month", "amount": "Total (₹)"})
            st.plotly_chart(fig, key="sh_chart_monthly")
        fig = px.pie(manager.payment_totals(filtered), names="payment_mode", values="amount",
                     hole=0.45, title="Share of spending by payment mode")
        st.plotly_chart(fig, key="sh_chart_payment")

with tab_report:
    st.subheader("Summary report")
    report_text = build_report("Shawn — Expense Transactions Report", "Shawn", manager,
                               len(data), len(filtered), len(problems), active_filters, stats)
    st.code(report_text, language="text")
    st.download_button("⬇️ Download report (.txt)", data=report_text,
                       file_name=f"shawn_report_{datetime.now():%Y%m%d_%H%M%S}.txt",
                       mime="text/plain", key="sh_report_download")
