"""Gautam's data manager.

PLACEHOLDER SCHEMA — income records (dummy data).
Replace the columns, validation and statistics when the real CSV is provided.
"""
import pandas as pd

from modules.csv_manager import CSVManager, DataError, rupees

INCOME_TYPES = ["Earned", "Scholarship", "Allowance", "Interest"]
MAX_AMOUNT = 5_000_000


class IncomeManager(CSVManager):
    columns = ["id", "date", "source", "income_type", "amount"]
    required_columns = ["date", "source", "income_type", "amount"]
    duplicate_key = ["date", "source", "amount"]

    def __init__(self):
        super().__init__("dummy_gautam_income.csv")

    # ------------------------------------------------------------ validation
    def _prepare(self, record):
        errors = []

        date = pd.to_datetime(record.get("date"), errors="coerce")
        if pd.isna(date):
            errors.append("Date is not a valid date.")
        elif date > pd.Timestamp.today():
            errors.append("Date cannot be in the future.")

        source = str(record.get("source", "")).strip()
        if not source:
            errors.append("Source is required.")
        elif len(source) > 60:
            errors.append("Source must be 60 characters or fewer.")

        income_type = str(record.get("income_type", "")).strip()
        if income_type not in INCOME_TYPES:
            errors.append("Please choose a valid income type.")

        amount = None
        try:
            amount = float(record.get("amount"))
        except (TypeError, ValueError):
            errors.append("Amount must be a number.")
        else:
            if not 0 < amount <= MAX_AMOUNT:
                errors.append(f"Amount must be greater than 0 and at most ₹{MAX_AMOUNT:,}.")

        if errors:
            raise DataError("\n".join(f"- {e}" for e in errors))
        return {
            "date": date.strftime("%Y-%m-%d"),
            "source": source,
            "income_type": income_type,
            "amount": f"{amount:.2f}",
        }

    # ------------------------------------------------------------------ CRUD
    def create_record(self, record):
        """Add an income entry. Returns the new record ID."""
        clean = self._prepare(record)
        df = self.load()
        if self._is_duplicate(df, clean, self.duplicate_key):
            raise DataError("This income entry already exists (same date, source and amount).")
        new_id = self._next_id(df)
        df.loc[len(df)] = [str(new_id)] + [clean[c] for c in self.columns[1:]]
        self._save(df)
        return new_id

    def read_records(self):
        df = self.load()
        df["id"] = pd.to_numeric(df["id"], errors="coerce")
        df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d", errors="coerce")
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
        return df

    def update_record(self, record_id, record):
        df = self.load()
        index = self._find_index(df, record_id)
        clean = self._prepare(record)
        if self._is_duplicate(df, clean, self.duplicate_key, exclude_index=index):
            raise DataError("Another income entry already has the same date, source and amount.")
        for column, value in clean.items():
            df.loc[index, column] = value
        self._save(df)

    def delete_record(self, record_id):
        df = self.load()
        index = self._find_index(df, record_id)
        self._save(df.drop(index=index))

    # -------------------------------------------------------------- analysis
    def summary_stats(self, df):
        amounts = df["amount"].dropna()
        if amounts.empty:
            return {}
        by_source = self.source_totals(df)
        monthly = self.monthly_totals(df)
        top_source = "—"
        if not by_source.empty:
            top = by_source.iloc[0]
            top_source = f"{top['source']} ({rupees(top['amount'])})"
        return {
            "Total income": rupees(amounts.sum()),
            "Average per entry": rupees(amounts.mean()),
            "Median entry": rupees(amounts.median()),
            "Largest entry": rupees(amounts.max()),
            "Top source": top_source,
            "Average monthly income": rupees(monthly["amount"].mean()) if not monthly.empty else "—",
            "Entries counted": str(len(amounts)),
        }

    def source_totals(self, df):
        return self.group_total(df, "source", "amount")

    def type_totals(self, df):
        return self.group_total(df, "income_type", "amount")

    def monthly_totals(self, df):
        return self.monthly_total(df, "date", "amount")
