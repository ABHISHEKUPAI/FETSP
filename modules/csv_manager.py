"""Shared base class for the four student managers.

It knows how to read and write ONE csv file safely.  Each student's manager
inherits from it and adds its own schema, validation, CRUD methods and analysis.
"""
import os
from pathlib import Path

import pandas as pd

# Paths are relative to the project root (never hard-coded like C:\Users\...)
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class DataError(Exception):
    """A problem the user can understand (bad input, missing file, ...)."""


def rupees(value):
    """Format a number as Indian rupees, e.g. ₹1,250.00."""
    if pd.isna(value):
        return "—"
    return f"₹{value:,.2f}"


class CSVManager:
    columns = []           # every column in the CSV, in order (first one is the id)
    required_columns = []  # columns that must not be blank / invalid
    id_column = "id"

    def __init__(self, filename):
        self._path = DATA_DIR / filename  # private: only this class touches the file

    @property
    def path(self):
        return self._path

    # ------------------------------------------------------------------ reading
    def load(self):
        """Read the CSV exactly as stored (all values as text).

        Keeping everything as text means saving never silently changes a value
        the user typed, e.g. a bad number stays visible so it can be fixed.
        """
        try:
            df = pd.read_csv(self._path, dtype=str)
        except FileNotFoundError:
            raise DataError(f"The file data/{self._path.name} was not found.") from None
        except pd.errors.EmptyDataError:
            raise DataError(f"The file data/{self._path.name} is empty (no header row).") from None
        except (pd.errors.ParserError, UnicodeDecodeError):
            raise DataError(f"The file data/{self._path.name} is not a valid CSV file.") from None
        except PermissionError:
            raise DataError(f"No permission to read data/{self._path.name}.") from None
        else:
            missing = [c for c in self.columns if c not in df.columns]
            if missing:
                raise DataError(
                    f"data/{self._path.name} is missing required column(s): {', '.join(missing)}."
                )
            return df[self.columns].copy()

    def can_reset(self):
        """True only if it is safe to create a fresh file (missing or 0 bytes)."""
        return (not self._path.exists()) or self._path.stat().st_size == 0

    def create_empty_file(self):
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._save(pd.DataFrame(columns=self.columns))

    # ------------------------------------------------------------------ writing
    def _save(self, df):
        """Safe write: write a temp file first, replace the real CSV only on success."""
        temp_path = self._path.with_suffix(".tmp")
        try:
            df.to_csv(temp_path, index=False)
            os.replace(temp_path, self._path)
        except OSError:
            raise DataError(
                "Could not save the CSV file. If it is open in another program "
                "(e.g. Excel), close it and try again."
            ) from None
        finally:
            if temp_path.exists():  # only true if something went wrong above
                temp_path.unlink()

    # ------------------------------------------------------------------ helpers
    def _find_index(self, df, record_id):
        """Row index for a record ID, or a friendly DataError."""
        try:
            wanted = str(int(record_id))
        except (TypeError, ValueError):
            raise DataError("Please enter a valid record ID (a whole number).") from None
        matches = df.index[df[self.id_column].str.strip() == wanted]
        if len(matches) == 0:
            raise DataError(f"Record ID {wanted} not found. Please enter a valid record ID.")
        return matches[0]

    def get_record(self, record_id):
        """One record as a dict of text values (blank cells become '')."""
        df = self.load()
        index = self._find_index(df, record_id)
        return df.loc[index].fillna("").to_dict()

    def _next_id(self, df):
        ids = pd.to_numeric(df[self.id_column], errors="coerce").dropna()
        return 1 if ids.empty else int(ids.max()) + 1

    @staticmethod
    def _normalise(value):
        text = str(value).strip().lower()
        try:
            return f"{float(text):.2f}"  # so "450" and "450.00" count as equal
        except ValueError:
            return text

    def _is_duplicate(self, df, clean, key_columns, exclude_index=None):
        """Does another row have the same values in the key columns?"""
        target = [self._normalise(clean[c]) for c in key_columns]
        for index, row in df.iterrows():
            if index == exclude_index:
                continue
            if [self._normalise(row[c]) for c in key_columns] == target:
                return True
        return False

    # ------------------------------------------------- small analysis helpers
    def problem_rows(self, typed_df):
        """Rows where a required value is blank or could not be converted."""
        return typed_df[typed_df[self.required_columns].isna().any(axis=1)]

    def group_total(self, df, by, value):
        """Sum of `value` for each group in `by`, largest first (missing values skipped)."""
        valid = df.dropna(subset=[by, value])
        totals = valid.groupby(by)[value].sum().reset_index()
        return totals.sort_values(value, ascending=False).reset_index(drop=True)

    def monthly_total(self, df, date_col, value):
        """Sum of `value` per calendar month (rows without a valid date are skipped)."""
        valid = df.dropna(subset=[date_col, value])
        months = valid[date_col].dt.strftime("%Y-%m").rename("month")
        return valid.groupby(months)[value].sum().reset_index()
