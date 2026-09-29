# Financial Expense Tracker with Spending Analytics

**Course:** 22AIE205 – Introduction to Python  |  **Group:** B9

> ⚠️ **PLACEHOLDER DATA.** The four datasets currently in `data/` are **temporary dummy files**
> (`dummy_*.csv`) used only to build and test the application. Their columns, values and the
> student-to-dataset assignments are placeholders and will be replaced by the team's real
> datasets. See [Replacing the placeholder datasets](#replacing-the-placeholder-datasets).

## Project overview

A Python-based interactive web application (Streamlit) for managing, analysing, visualising and
reporting financial data stored in CSV files. Each student owns **one CSV dataset and one page**
and is responsible for the complete slice on that page: CRUD, analysis, visualisation, error
handling and reporting. A shared Home page introduces the project and links to the four pages.

```text
Input Data → Update CSV → Read / Analyse / View → Visualise → Report
```

## SDG connection

- **SDG 8 – Decent Work and Economic Growth:** tracking income, budgets and savings supports
  people in managing their earnings and taking part confidently in the economy.
- **SDG 12 – Responsible Consumption and Production:** spending analytics make consumption
  visible (by category, over time, against budget), helping users notice and reduce unnecessary spending.

## Team and dataset ownership (PLACEHOLDER)

| Student  | Dataset (placeholder)       | CSV                                   | Page                     |
| -------- | --------------------------- | ------------------------------------- | ------------------------ |
| Shawn    | Expense transactions        | `data/dummy_shawn_transactions.csv`   | `pages/1_Shawn.py`       |
| Gautam   | Income records              | `data/dummy_gautam_income.csv`        | `pages/2_Gautam.py`      |
| Abhishek | Monthly budgets vs actual   | `data/dummy_abhishek_budgets.csv`     | `pages/3_Abhishek.py`    |
| Anhal    | Savings goals               | `data/dummy_anhal_goals.csv`          | `pages/4_Anhal.py`       |

The Home page (`app.py`) is an **additional shared page**; it is not one of the four student pages.
A student's page only reads and writes **their own** CSV. (The Home page only *counts* rows, read-only.)

## Project structure

```text
financial-expense-tracker/
├── app.py                     # Home / landing page (shared)
├── pages/
│   ├── 1_Shawn.py             # one page per student (UI only)
│   ├── 2_Gautam.py
│   ├── 3_Abhishek.py
│   └── 4_Anhal.py
├── modules/
│   ├── csv_manager.py         # base class CSVManager: safe CSV read/write + shared helpers
│   ├── shawn_manager.py       # TransactionManager(CSVManager)  – Shawn's CRUD + analysis
│   ├── gautam_manager.py      # IncomeManager(CSVManager)       – Gautam's CRUD + analysis
│   ├── abhishek_manager.py    # BudgetManager(CSVManager)       – Abhishek's CRUD + analysis
│   ├── anhal_manager.py       # GoalManager(CSVManager)         – Anhal's CRUD + analysis
│   └── helpers.py             # small UI helpers: filters, messages, report text
├── data/                      # the four CSV files (the only persistent storage)
├── requirements.txt
└── README.md
```

## Technologies used

Python 3.10+, Streamlit (multipage app), Pandas, NumPy, Plotly, CSV files (only storage), Git/GitHub,
a Python virtual environment. No database, no external APIs, no authentication.

## Installation

```bash
# 1. create and activate a virtual environment
python -m venv venv
venv\Scripts\activate            # Windows
# source venv/bin/activate       # macOS / Linux

# 2. install the dependencies
pip install -r requirements.txt
```

On Windows you can pick a specific Python with the launcher: `py -3.11 -m venv venv`.

## How to run

```bash
streamlit run app.py
```

Then open the address Streamlit prints (usually http://localhost:8501).

## Pages

| Page | What it is |
| ---- | ---------- |
| **Home** (`app.py`) | Project overview, how the datasets fit together, SDG connection, navigation to the four pages, record counts. |
| **Student pages** | Same tabs on each page: **View Data**, **Add Record**, **Update Record**, **Delete Record**, **Analytics**, **Report**. Filters live in the sidebar and drive the table, statistics, charts and report. |

## Datasets (PLACEHOLDER — dummy data)

Each dummy file is small and deliberately contains a few blank/invalid cells so the missing-data
handling can be seen working.

| Dataset | Columns | Rows |
| ------- | ------- | ---- |
| Expense transactions (Shawn) | id, date, category, description, amount, payment_mode | 40 |
| Income records (Gautam) | id, date, source, income_type, amount | 26 |
| Monthly budgets (Abhishek) | id, month, category, budget_amount, actual_spent | 18 |
| Savings goals (Anhal) | id, goal_name, target_amount, saved_amount, deadline, priority | 9 |

## CRUD functionality

Each student's manager class has `create_record`, `read_records`, `update_record`, `delete_record`.

- **Create** – form with validation of required fields, data types, reasonable ranges and duplicates; clear success/error message.
- **Read** – table of the *current* CSV with sidebar filters, search, sorting and a row count.
- **Update** – enter a record ID, the form is pre-filled, changes are validated and saved. Unknown IDs show a friendly message.
- **Delete** – enter a record ID, review the record, tick the confirmation box; the delete button stays disabled until confirmed.

## Analytics and visualisations

Every statistic and chart is calculated from the current CSV (after filters); nothing is hard-coded.

| Page | Statistics (≥3 each) | Charts (≥2 types each) |
| ---- | -------------------- | ---------------------- |
| Shawn | total, mean, median, max, 90th percentile, top category, count | bar, line, donut |
| Gautam | total, mean, median, max, top source, average monthly income, count | donut, line, histogram |
| Abhishek | total budget/spent, utilisation %, over-budget lines, biggest overspend, remaining | grouped bar, scatter |
| Anhal | total target/saved, overall & average progress, goals completed, still to save, next deadline | horizontal bar, donut |

## Missing data, validation and error handling

- **Missing / invalid cells** are never silently ignored: the page shows a warning with the count and the affected rows. They stay in the CSV, and are excluded only from calculations that need the missing value. They can be fixed with *Update Record*.
- **Lossless saving:** the CSV is read as text, so saving never changes a value the user did not edit.
- **Handled without crashing:** missing file, empty file, malformed file, missing columns, wrong data types, invalid record ID, duplicate records, invalid form input. Users see friendly messages, not tracebacks.
- **Safe writes:** every write goes to a temporary file first and replaces the real CSV only if that succeeded (`try / except / finally`), so the CSV is never left half-written.
- Specific exception types are used (`FileNotFoundError`, `pd.errors.EmptyDataError`, `pd.errors.ParserError`, `ValueError`, `TypeError`, `OSError`).

## Reporting

The **Report** tab shows a plain-text summary and a **Download report (.txt)** button. It contains the
timestamp, total rows, rows after filters, rows with missing/invalid data, the **active filters** and the
summary statistics, all based on the student's own current data.

## OOP design

`CSVManager` (in `modules/csv_manager.py`) holds what all four students need identically: reading a CSV, the safe write,
ID lookup and duplicate checking. Each student's manager **inherits** from it and adds its own columns,
validation, CRUD methods and analysis. The file path is stored privately (`_path`), which is **encapsulation**.

## Replacing the placeholder datasets

When the real CSVs are ready, for each student:

1. Put the CSV in `data/` and inspect its columns, types and problems.
2. Update that student's `modules/<name>_manager.py`: `columns`, `required_columns`, `duplicate_key`, the file name, `_prepare` (validation) and `read_records` (types), then the statistics/chart-data methods.
3. Update the forms, filters and charts in that student's `pages/N_<Name>.py`.
4. Set `PLACEHOLDER_DATA = False` in `modules/helpers.py` to remove the placeholder banners and report note.
5. Update the tables in this README and on the Home page.
