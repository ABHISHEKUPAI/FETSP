"""Shawn's data manager.

PLACEHOLDER SCHEMA — expense transactions (dummy data).
Replace the columns, validation and statistics when the real CSV is provided.
"""
import numpy as np
import pandas as pd

from modules.csv_manager import CSVManager, DataError, rupees

CATEGORIES = ["Food", "Transport", "Rent", "Utilities", "Entertainment",
              "Health", "Shopping", "Education", "Other"]
PAYMENT_MODES = ["UPI", "Cash", "Card", "Net Banking"]
MAX_AMOUNT = 1_000_000


class TransactionManager(CSVManager):
    columns = ["id", "date", "category", "description", "amount", "payment_mode"]
    required_columns = ["date", "category", "description", "amount", "payment_mode"]
    duplicate_key = ["date", "category", "description", "amount"]

    def __init__(self):
        super().__init__("dummy_shawn_transactions.csv")

    # ------------------------------------------------------------ validation
    def _prepare(self, record):
        """Check the form input; return clean text values or raise DataError."""
        errors = []

        date = pd.to_datetime(record.get("date"), errors="coerce")
        if pd.isna(date):
            errors.append("Date is not a valid date.")
        elif date > pd.Timestamp.today():
            errors.append("Date cannot be in the future.")

        category = str(record.get("category", "")).strip()
        if category not in CATEGORIES:
            errors.append("Please choose a valid category.")

        payment_mode = str(record.get("payment_mode", "")).strip()
        if payment_mode not in PAYMENT_MODES:
            errors.append("Please choose a valid payment mode.")

        description = str(record.get("description", "")).strip()
        if not description:
            errors.append("Description is required.")
        elif len(description) > 100:
            errors.append("Description must be 100 characters or fewer.")

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
            "category": category,
            "description": description,
            "amount": f"{amount:.2f}",
            "payment_mode": payment_mode,
        }

    # ------------------------------------------------------------------ CRUD
    def create_record(self, record):
        """Add a transaction. Returns the new record ID."""
        clean = self._prepare(record)
        df = self.load()
        if self._is_duplicate(df, clean, self.duplicate_key):
            raise DataError("This transaction already exists "
                            "(same date, category, description and amount).")
        new_id = self._next_id(df)
        df.loc[len(df)] = [str(new_id)] + [clean[c] for c in self.columns[1:]]
        self._save(df)
        return new_id

    def read_records(self):
        """All records with proper data types (bad values become NaN/NaT)."""
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
            raise DataError("Another transaction already has the same date, "
                            "category, description and amount.")
        for column, value in clean.items():
            df.loc[index, column] = value
        self._save(df)

    def delete_record(self, record_id):
        df = self.load()
        index = self._find_index(df, record_id)
        self._save(df.drop(index=index))

    # -------------------------------------------------------------- analysis
    def summary_stats(self, df):
        """Ordered {label: text} of summary statistics for the given rows."""
        amounts = df["amount"].dropna()
        if amounts.empty:
            return {}
        by_category = self.category_totals(df)
        top = by_category.iloc[0]
        return {
            "Total spent": rupees(amounts.sum()),
            "Average transaction": rupees(amounts.mean()),
            "Median transaction": rupees(amounts.median()),
            "Largest transaction": rupees(amounts.max()),
            "90th percentile": rupees(np.percentile(amounts, 90)),
            "Top category": f"{top['category']} ({rupees(top['amount'])})",
            "Transactions counted": str(len(amounts)),
        }

    def category_totals(self, df):
        return self.group_total(df, "category", "amount")

    def payment_totals(self, df):
        return self.group_total(df, "payment_mode", "amount")

    def monthly_totals(self, df):
        return self.monthly_total(df, "date", "amount")
