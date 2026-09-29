"""Anhal's data manager.

PLACEHOLDER SCHEMA — savings goals (dummy data).
Replace the columns, validation and statistics when the real CSV is provided.
"""
import numpy as np
import pandas as pd

from modules.csv_manager import CSVManager, DataError, rupees

PRIORITIES = ["High", "Medium", "Low"]
MAX_AMOUNT = 10_000_000


class GoalManager(CSVManager):
    columns = ["id", "goal_name", "target_amount", "saved_amount", "deadline", "priority"]
    required_columns = ["goal_name", "target_amount", "saved_amount", "deadline", "priority"]
    duplicate_key = ["goal_name"]

    def __init__(self):
        super().__init__("dummy_anhal_goals.csv")

    # ------------------------------------------------------------ validation
    def _prepare(self, record):
        errors = []

        goal_name = str(record.get("goal_name", "")).strip()
        if not goal_name:
            errors.append("Goal name is required.")
        elif len(goal_name) > 60:
            errors.append("Goal name must be 60 characters or fewer.")

        priority = str(record.get("priority", "")).strip()
        if priority not in PRIORITIES:
            errors.append("Please choose a valid priority.")

        deadline = pd.to_datetime(record.get("deadline"), errors="coerce")
        if pd.isna(deadline):
            errors.append("Deadline is not a valid date.")
        elif deadline.year < 2000:
            errors.append("Deadline must be in the year 2000 or later.")

        target = saved = None
        try:
            target = float(record.get("target_amount"))
        except (TypeError, ValueError):
            errors.append("Target amount must be a number.")
        else:
            if not 0 < target <= MAX_AMOUNT:
                errors.append(f"Target must be greater than 0 and at most ₹{MAX_AMOUNT:,}.")
        try:
            saved = float(record.get("saved_amount"))
        except (TypeError, ValueError):
            errors.append("Saved amount must be a number.")
        else:
            if saved < 0:
                errors.append("Saved amount cannot be negative.")
        if target is not None and saved is not None and saved > target:
            errors.append("Saved amount cannot be more than the target amount.")

        if errors:
            raise DataError("\n".join(f"- {e}" for e in errors))
        return {
            "goal_name": goal_name,
            "target_amount": f"{target:.2f}",
            "saved_amount": f"{saved:.2f}",
            "deadline": deadline.strftime("%Y-%m-%d"),
            "priority": priority,
        }

    # ------------------------------------------------------------------ CRUD
    def create_record(self, record):
        """Add a savings goal. Returns the new record ID."""
        clean = self._prepare(record)
        df = self.load()
        if self._is_duplicate(df, clean, self.duplicate_key):
            raise DataError(f"A goal named '{clean['goal_name']}' already exists.")
        new_id = self._next_id(df)
        df.loc[len(df)] = [str(new_id)] + [clean[c] for c in self.columns[1:]]
        self._save(df)
        return new_id

    def read_records(self):
        """All records with proper types plus derived columns (progress, remaining, days left)."""
        df = self.load()
        df["id"] = pd.to_numeric(df["id"], errors="coerce")
        df["target_amount"] = pd.to_numeric(df["target_amount"], errors="coerce")
        df["saved_amount"] = pd.to_numeric(df["saved_amount"], errors="coerce")
        df["deadline"] = pd.to_datetime(df["deadline"], format="%Y-%m-%d", errors="coerce")
        # Derived columns (NaN when a needed value is missing)
        df["progress_pct"] = df["saved_amount"] / df["target_amount"].replace(0, np.nan) * 100
        df["remaining"] = df["target_amount"] - df["saved_amount"]
        df["days_left"] = (df["deadline"] - pd.Timestamp.today().normalize()).dt.days
        df["status"] = np.where(df["remaining"] <= 0, "Completed", "In progress")
        df.loc[df["remaining"].isna(), "status"] = np.nan
        return df

    def update_record(self, record_id, record):
        df = self.load()
        index = self._find_index(df, record_id)
        clean = self._prepare(record)
        if self._is_duplicate(df, clean, self.duplicate_key, exclude_index=index):
            raise DataError(f"Another goal is already named '{clean['goal_name']}'.")
        for column, value in clean.items():
            df.loc[index, column] = value
        self._save(df)

    def delete_record(self, record_id):
        df = self.load()
        index = self._find_index(df, record_id)
        self._save(df.drop(index=index))

    # -------------------------------------------------------------- analysis
    def _complete_rows(self, df):
        return df.dropna(subset=["target_amount", "saved_amount"])

    def summary_stats(self, df):
        valid = self._complete_rows(df)
        if valid.empty:
            return {}
        total_target = valid["target_amount"].sum()
        total_saved = valid["saved_amount"].sum()
        overall = total_saved / total_target * 100 if total_target else np.nan
        completed = int((valid["remaining"] <= 0).sum())

        upcoming = valid[(valid["remaining"] > 0) & (valid["days_left"] >= 0)]
        if upcoming.empty:
            next_deadline = "None upcoming"
        else:
            row = upcoming.sort_values("deadline").iloc[0]
            next_deadline = f"{row['goal_name']} ({row['deadline']:%d %b %Y})"
        return {
            "Total target": rupees(total_target),
            "Total saved": rupees(total_saved),
            "Overall progress": "—" if pd.isna(overall) else f"{overall:.1f}%",
            "Average goal progress": f"{valid['progress_pct'].mean():.1f}%",
            "Goals completed": f"{completed} of {len(valid)}",
            "Still to save": rupees(valid["remaining"].clip(lower=0).sum()),
            "Next deadline": next_deadline,
        }

    def progress_data(self, df):
        """Goals with a progress % for the bar chart, lowest progress first."""
        return self._complete_rows(df).sort_values("progress_pct")

    def priority_targets(self, df):
        return self.group_total(df, "priority", "target_amount")
