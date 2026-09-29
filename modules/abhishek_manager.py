"""Abhishek's data manager.

PLACEHOLDER SCHEMA — monthly budgets vs actual spending (dummy data).
Replace the columns, validation and statistics when the real CSV is provided.
"""
import numpy as np
import pandas as pd

from modules.csv_manager import CSVManager, DataError, rupees

CATEGORIES = ["Food", "Transport", "Utilities", "Entertainment", "Shopping", "Health", "Education"]
MAX_AMOUNT = 1_000_000


class BudgetManager(CSVManager):
    columns = ["id", "month", "category", "budget_amount", "actual_spent"]
    required_columns = ["month", "category", "budget_amount", "actual_spent"]
    duplicate_key = ["month", "category"]  # one budget line per category per month

    def __init__(self):
        super().__init__("dummy_abhishek_budgets.csv")

    # ------------------------------------------------------------ validation
    def _prepare(self, record):
        errors = []

        month_text = str(record.get("month", "")).strip()
        month = pd.to_datetime(month_text + "-01", format="%Y-%m-%d", errors="coerce")
        if pd.isna(month):
            errors.append("Month must look like YYYY-MM (for example 2026-09).")
        elif not 2000 <= month.year <= 2100:
            errors.append("Month must be between the years 2000 and 2100.")

        category = str(record.get("category", "")).strip()
        if category not in CATEGORIES:
            errors.append("Please choose a valid category.")

        budget = spent = None
        try:
            budget = float(record.get("budget_amount"))
        except (TypeError, ValueError):
            errors.append("Budget amount must be a number.")
        else:
            if not 0 < budget <= MAX_AMOUNT:
                errors.append(f"Budget must be greater than 0 and at most ₹{MAX_AMOUNT:,}.")
        try:
            spent = float(record.get("actual_spent"))
        except (TypeError, ValueError):
            errors.append("Actual spent must be a number.")
        else:
            if not 0 <= spent <= MAX_AMOUNT:
                errors.append(f"Actual spent must be between 0 and ₹{MAX_AMOUNT:,}.")

        if errors:
            raise DataError("\n".join(f"- {e}" for e in errors))
        return {
            "month": month.strftime("%Y-%m"),
            "category": category,
            "budget_amount": f"{budget:.2f}",
            "actual_spent": f"{spent:.2f}",
        }

    # ------------------------------------------------------------------ CRUD
    def create_record(self, record):
        """Add a budget line. Returns the new record ID."""
        clean = self._prepare(record)
        df = self.load()
        if self._is_duplicate(df, clean, self.duplicate_key):
            raise DataError(f"A budget for {clean['category']} in {clean['month']} already exists. "
                            "Use Update Record to change it.")
        new_id = self._next_id(df)
        df.loc[len(df)] = [str(new_id)] + [clean[c] for c in self.columns[1:]]
        self._save(df)
        return new_id

    def read_records(self):
        """All records with proper types plus derived columns (variance, utilisation, status)."""
        df = self.load()
        df["id"] = pd.to_numeric(df["id"], errors="coerce")
        month = pd.to_datetime(df["month"] + "-01", format="%Y-%m-%d", errors="coerce")
        df["month"] = month.dt.strftime("%Y-%m")
        df["budget_amount"] = pd.to_numeric(df["budget_amount"], errors="coerce")
        df["actual_spent"] = pd.to_numeric(df["actual_spent"], errors="coerce")
        # Derived columns (NaN when a needed value is missing)
        df["variance"] = df["budget_amount"] - df["actual_spent"]
        df["utilisation_pct"] = df["actual_spent"] / df["budget_amount"].replace(0, np.nan) * 100
        df["status"] = np.where(df["variance"] < 0, "Over budget", "Within budget")
        df.loc[df["variance"].isna(), "status"] = np.nan
        return df

    def update_record(self, record_id, record):
        df = self.load()
        index = self._find_index(df, record_id)
        clean = self._prepare(record)
        if self._is_duplicate(df, clean, self.duplicate_key, exclude_index=index):
            raise DataError(f"A budget for {clean['category']} in {clean['month']} already exists.")
        for column, value in clean.items():
            df.loc[index, column] = value
        self._save(df)

    def delete_record(self, record_id):
        df = self.load()
        index = self._find_index(df, record_id)
        self._save(df.drop(index=index))

    # -------------------------------------------------------------- analysis
    def _complete_rows(self, df):
        return df.dropna(subset=["budget_amount", "actual_spent"])

    def summary_stats(self, df):
        valid = self._complete_rows(df)
        if valid.empty:
            return {}
        total_budget = valid["budget_amount"].sum()
        total_spent = valid["actual_spent"].sum()
        overall = total_spent / total_budget * 100 if total_budget else np.nan
        over = valid[valid["variance"] < 0]
        worst = "None"
        if not over.empty:
            row = over.loc[over["variance"].idxmin()]
            worst = f"{row['category']} {row['month']} ({rupees(-row['variance'])} over)"
        return {
            "Total budgeted": rupees(total_budget),
            "Total spent": rupees(total_spent),
            "Overall utilisation": "—" if pd.isna(overall) else f"{overall:.1f}%",
            "Average utilisation": f"{valid['utilisation_pct'].mean():.1f}%",
            "Over-budget lines": f"{len(over)} of {len(valid)}",
            "Biggest overspend": worst,
            "Remaining budget": rupees(valid["variance"].sum()),
        }

    def budget_vs_actual(self, df):
        """Budget and actual totals per category, in long format for a grouped bar chart."""
        valid = self._complete_rows(df)
        totals = valid.groupby("category")[["budget_amount", "actual_spent"]].sum().reset_index()
        long = totals.melt(id_vars="category", var_name="Type", value_name="Amount")
        return long.replace({"budget_amount": "Budget", "actual_spent": "Actual spent"})

    def scatter_data(self, df):
        return self._complete_rows(df)
