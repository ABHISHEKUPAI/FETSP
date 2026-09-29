"""Home / landing page — shared by the whole team (it is NOT one of the four student pages)."""
import streamlit as st

from modules.abhishek_manager import BudgetManager
from modules.anhal_manager import GoalManager
from modules.csv_manager import DataError
from modules.gautam_manager import IncomeManager
from modules.helpers import PLACEHOLDER_DATA
from modules.shawn_manager import TransactionManager

st.set_page_config(page_title="Financial Expense Tracker", page_icon="💰", layout="wide")

st.title("💰 Financial Expense Tracker with Spending Analytics")
st.caption("22AIE205 – Introduction to Python  •  Group B9  •  Shawn, Gautam, Abhishek, Anhal")

if PLACEHOLDER_DATA:
    st.warning(
        "⚠️ **PLACEHOLDER DATA** — the four datasets below are temporary dummy files used only to "
        "build and test the application. They will be replaced by the team's real CSV files."
    )

# ------------------------------------------------------------------ overview
st.header("Project overview")
st.write(
    "This is a Python web application for **managing, analysing, visualising and reporting "
    "financial data stored in CSV files**. Every team member owns one dataset and one page. "
    "On their own page they can add, view, update and delete records (CRUD), see summary "
    "statistics and charts, and export a report."
)
st.write(
    "**Why it is useful:** money data is only helpful if it is kept accurate and easy to read. "
    "Turning raw rows into totals, trends and charts makes it easier to see where money comes "
    "from, where it goes, and whether the plan is being followed."
)

st.subheader("How the four datasets fit together")
st.caption("Placeholder datasets — this table will change when the real datasets are provided.")
st.table({
    "Student": ["Shawn", "Gautam", "Abhishek", "Anhal"],
    "Placeholder dataset": ["Expense transactions", "Income records",
                            "Monthly budgets vs actual", "Savings goals"],
    "Role in the theme": ["Where money goes", "Where money comes from",
                          "The spending plan", "What the money is saved for"],
})

st.subheader("How to use the app")
st.markdown(
    "1. Pick a student page from the sidebar (or the buttons below).\n"
    "2. Use the tabs: **View Data**, **Add / Update / Delete Record**, **Analytics** and **Report**.\n"
    "3. Use the sidebar filters — the table, statistics, charts and report all follow the filters.\n"
    "4. Every change is saved straight to that student's CSV file in the `data` folder."
)

# ----------------------------------------------------------------- navigation
st.header("Go to a student page")
pages = [
    ("pages/1_Shawn.py", "🧾 Shawn's page", TransactionManager()),
    ("pages/2_Gautam.py", "💵 Gautam's page", IncomeManager()),
    ("pages/3_Abhishek.py", "📒 Abhishek's page", BudgetManager()),
    ("pages/4_Anhal.py", "🎯 Anhal's page", GoalManager()),
]
columns = st.columns(4)
for column, (page_path, label, manager) in zip(columns, pages):
    with column:
        st.page_link(page_path, label=label)
        try:
            # Read-only: the Home page never changes any student's CSV.
            column.metric("Records in CSV", len(manager.load()))
        except DataError:
            column.metric("Records in CSV", "n/a")
            column.caption("CSV could not be read — open the page for details.")

# ------------------------------------------------------------------------ SDGs
st.header("SDG connection")
sdg8, sdg12 = st.columns(2)
with sdg8:
    st.subheader("SDG 8 — Decent Work and Economic Growth")
    st.write(
        "SDG 8 aims to promote sustained, inclusive economic growth and decent work for all. "
        "People take part in the economy more confidently when they can track their income and "
        "plan their savings. This project supports that at a personal scale: it records income, "
        "budgets and savings goals so that earnings can be managed deliberately."
    )
with sdg12:
    st.subheader("SDG 12 — Responsible Consumption and Production")
    st.write(
        "SDG 12 aims to ensure sustainable consumption and production patterns. Responsible "
        "consumption starts with awareness of what we buy and how much we spend. The spending "
        "analytics in this project show spending by category and over time, and compare it with "
        "budgets, helping users notice and reduce unnecessary consumption."
    )
