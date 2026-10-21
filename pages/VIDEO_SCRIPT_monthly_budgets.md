# Video Script — Abhishek's page: `pages/monthly_budgets.py`

| | |
| --- | --- |
| **Presenter** | Abhishek |
| **Page presented** | `pages/monthly_budgets.py` — shown in the sidebar as **Abhishek – Budgets** |
| **Dataset** | `data/dummy_abhishek_budgets.csv` (monthly budgets vs actual spending) |
| **App** | Financial Expense Tracker with Spending Analytics (22AIE205, Group B9) |
| **Target length** | 3–4 minutes (~570 spoken words at 140–160 words per minute) |
| **Format** | Screen recording of the live app, with the code shown for the key lines |

---

## 0. Before you hit record

- [ ] Terminal open in the project root, `streamlit run app.py` already running.
- [ ] Editor open at `pages/monthly_budgets.py`; put the **browser (left) + editor (right)** side by side.
- [ ] Browser on the **Abhishek – Budgets** page, browser zoom at 90–100 %.
- [ ] The yellow **“PLACEHOLDER DATA”** banner at the top of the page is expected — the real team CSV replaces these dummy files later. Mention it once, do not apologise for it.
- [ ] **Rehearse the demo row once before recording** (Appendix E) so the mouse moves are smooth.
- [ ] The demo adds, updates and deletes **the same record (ID 19)**, so `data/dummy_abhishek_budgets.csv` is exactly the same before and after the recording.

---

## 1. The script

### Scene 1 — Hook (0:00 – 0:15)

**SCREEN** — Home page `app.py`; point at the sidebar, then click **Abhishek – Budgets**.

**SAY**
> Hi everyone, I am Abhishek, and this is my part of the Financial Expense Tracker. My dataset is monthly budgets versus actual spending, and my page is `pages/monthly_budgets.py`.

**SHOW CODE** — `pages/monthly_budgets.py:11` (page title) and `pages/monthly_budgets.py:15` (`st.title`).

---

### Scene 2 — How the code is organised (0:15 – 0:40)

**SCREEN** — Switch to the editor. Show the import block, then the folder tree.

**SAY**
> The code has three layers. The top layer is the Streamlit page, which only builds the user interface. The middle layer is my `BudgetManager` class, which holds my rules and the four CRUD operations. The bottom layer is `CSVManager`, shared by the whole team, which reads and writes one CSV safely. My class inherits from it, so I reuse the file handling and only add my own rules.

**SHOW CODE**
- `pages/monthly_budgets.py:6-9` — the page imports the manager and the helpers.
- `modules/abhishek_manager.py:15` — `class BudgetManager(CSVManager)`.
- `modules/abhishek_manager.py:16-18` — `columns`, `required_columns`, `duplicate_key`.
- `modules/csv_manager.py:26` — the shared base class `CSVManager`.

---

### Scene 3 — CRUD, one tab each (0:40 – 1:40)

**SCREEN** — Back to the browser. The six tabs are on screen: View Data, Add Record, Update Record, Delete Record, Analytics, Report.

**SAY**
> Now CRUD, one tab each.
>
> **Create.** In the Add Record tab I pick a month and a category, type the budget and the actual spending, and submit. Before anything is written, my `_prepare` method validates everything — the month format, the category, the amount ranges — and it checks the duplicate key, month and category, so there can never be two budgets for the same category in the same month. If something is wrong it raises a `DataError` and I show a red message listing every problem. If it is fine, the row is appended, the CSV is saved, and I show the new ID.
>
> **Read.** The View Data tab shows the table, with month, category and status filters in the sidebar. The file is read again on every rerun, so the table always shows the current CSV. On top of the five stored columns the code calculates three more: variance, budget minus actual spent; utilisation, actual spent as a percentage of the budget; and status, within or over budget. I can sort by any column.
>
> **Update.** I type the record ID, the manager fetches it, and the form appears already filled with the current values. The same validation runs when I save, but the duplicate check ignores the row I am editing.
>
> **Delete.** I type the ID, the record is shown so I can check it, and the delete button stays disabled until I tick a confirmation box — because deleting is permanent.

**SHOW CODE**
- Create: `pages/monthly_budgets.py:26` (`st.form`), `:38` (`manager.create_record`), `modules/abhishek_manager.py:24-61` (`_prepare` validation) and `:64-74` (`create_record`).
- Read: `pages/monthly_budgets.py:103` (`data = load_or_stop(manager)` — re-read), `:107-112` (sidebar filters), `modules/abhishek_manager.py:85-88` (derived columns).
- Update: `pages/monthly_budgets.py:52` (`get_record`), `:56` (pre-filled form), `:72` (`update_record`), `modules/abhishek_manager.py:91-99`.
- Delete: `pages/monthly_budgets.py:92` (confirmation checkbox), `:94` (`disabled=not confirmed`), `modules/abhishek_manager.py:101-104`.

---

### Scene 4 — The two graphs (1:40 – 2:25)

**SCREEN** — Analytics tab. First the summary metrics, then the grouped bar chart on the left, then the scatter plot on the right.

**SAY**
> For analytics I have two charts. The first is a grouped bar chart: the manager sums the budget and the actual spending per category and reshapes the table into long format, and Plotly draws two bars side by side for every category. Shopping is the clearest example — I budgeted four thousand rupees but spent about four thousand five hundred, so the actual bar is taller.
>
> The second chart is a scatter plot. The x-axis is the budget, the y-axis is the actual spending, and each dot is one budget line. I drew a dashed diagonal line where actual equals budget, so dots below the line are within budget and dots above it are over budget.

**SHOW CODE**
- `modules/abhishek_manager.py:132-137` — `budget_vs_actual()`: `groupby` + `melt` into long format.
- `pages/monthly_budgets.py:147-150` — `px.bar(..., barmode="group")` + `st.plotly_chart`.
- `modules/abhishek_manager.py:139-140` — `scatter_data()` returns the rows with valid amounts.
- `pages/monthly_budgets.py:153-159` — `px.scatter`, `fig.add_shape(...)` for the dashed line and `fig.add_annotation(...)` for the "on budget" label.
- `pages/monthly_budgets.py:161` — the caption explaining how to read the dots.

---

### Scene 5 — Report (2:25 – 2:40)

**SCREEN** — Report tab. Scroll the plain-text report, then hover the download button.

**SAY**
> The Report tab builds a plain-text summary from exactly what is on screen — the timestamp, the row counts, the active filters and the statistics — and I can download it as a text file.

**SHOW CODE** — `pages/monthly_budgets.py:165` (`build_report`), `:167` (`st.code`), `:168-170` (`st.download_button`).

---

### Scene 6 — Error handling and safe saving (2:40 – 3:05)

**SCREEN** — In the Update Record tab type the ID `999` and press Enter → the friendly warning appears. Then briefly show the code for the atomic write in the editor.

**SAY**
> Finally, the app never shows a traceback. If the CSV is missing, empty or malformed, the user gets a friendly message instead. And every save is written to a temporary file first and only replaces the real CSV after it succeeded, so the data can never be left half-written.

**SHOW CODE**
- `modules/csv_manager.py:72-85` — `_save()`: write `.tmp` → `os.replace()` → clean up in `finally`.
- `modules/csv_manager.py:39-61` — `load()` catches a missing, empty, malformed file or a missing column.
- `modules/helpers.py:41-60` — `load_or_stop()` turns a `DataError` into a friendly message and stops the page.

---

### Scene 7 — Numbers and close (3:05 – 3:25)

**SCREEN** — View Data tab, show the whole table. (Optionally the Analytics metrics row.)

**SAY**
> For the current data: sixteen budget lines, twenty-five thousand eight hundred rupees budgeted, twenty-three thousand fifty-six spent — eighty-nine point four percent utilisation — and five lines over budget, the biggest being Shopping in July 2026. That is my part. Thank you.

**SHOW CODE** — `modules/abhishek_manager.py:110-130` (`summary_stats`) and `pages/monthly_budgets.py:143` (`show_metrics`).

---

## Appendix A — Continuous read-aloud script (~3.5–4 minutes)

> Read this block top to bottom while recording. No stage directions, no line numbers — just the words.

Hi everyone, I am Abhishek, and this is my part of the Financial Expense Tracker. My dataset is monthly budgets versus actual spending, and my page is `pages/monthly_budgets.py`.

The code has three layers. The top layer is the Streamlit page, which only builds the user interface. The middle layer is my `BudgetManager` class, which holds my rules and the four CRUD operations. The bottom layer is `CSVManager`, shared by the whole team, which reads and writes one CSV safely. My class inherits from it, so I reuse the file handling and only add my own rules.

Now CRUD, one tab each.

Create. In the Add Record tab I pick a month and a category, type the budget and the actual spending, and submit. Before anything is written, my `_prepare` method validates everything — the month format, the category, the amount ranges — and it checks the duplicate key, month and category, so there can never be two budgets for the same category in the same month. If something is wrong it raises a `DataError` and I show a red message listing every problem. If it is fine, the row is appended, the CSV is saved, and I show the new ID.

Read. The View Data tab shows the table, with month, category and status filters in the sidebar. The file is read again on every rerun, so the table always shows the current CSV. On top of the five stored columns the code calculates three more: variance, budget minus actual spent; utilisation, actual spent as a percentage of the budget; and status, within or over budget. I can sort by any column.

Update. I type the record ID, the manager fetches it, and the form appears already filled with the current values. The same validation runs when I save, but the duplicate check ignores the row I am editing.

Delete. I type the ID, the record is shown so I can check it, and the delete button stays disabled until I tick a confirmation box — because deleting is permanent.

For analytics I have two charts. The first is a grouped bar chart: the manager sums the budget and the actual spending per category and reshapes the table into long format, and Plotly draws two bars side by side for every category. Shopping is the clearest example — I budgeted four thousand rupees but spent about four thousand five hundred, so the actual bar is taller.

The second chart is a scatter plot. The x-axis is the budget, the y-axis is the actual spending, and each dot is one budget line. I drew a dashed diagonal line where actual equals budget, so dots below the line are within budget and dots above it are over budget.

The Report tab builds a plain-text summary from exactly what is on screen — the timestamp, the row counts, the active filters and the statistics — and I can download it as a text file.

Finally, the app never shows a traceback. If the CSV is missing, empty or malformed, the user gets a friendly message instead. And every save is written to a temporary file first and only replaces the real CSV after it succeeded, so the data can never be left half-written.

For the current data: sixteen budget lines, twenty-five thousand eight hundred rupees budgeted, twenty-three thousand fifty-six spent — eighty-nine point four percent utilisation — and five lines over budget, the biggest being Shopping in July 2026. That is my part. Thank you.

---

## Appendix B — CRUD map

| Operation | Tab | Streamlit widgets used | Manager method | What happens in the CSV | Code |
| --- | --- | --- | --- | --- | --- |
| **Create** | Add Record | `st.form`, `st.columns`, `st.text_input`, `st.selectbox`, `st.number_input`, `st.form_submit_button` | `BudgetManager.create_record()` → `_prepare()` | New row appended, ID = max + 1, file rewritten | `pages/monthly_budgets.py:24-45`, `modules/abhishek_manager.py:64-74` |
| **Read** | View Data | `st.dataframe` + `st.column_config.NumberColumn`, `st.selectbox` (sort), `st.radio` (order), `st.sidebar.multiselect` (filters) | `read_records()`, `problem_rows()`, `summary_stats()` | Read-only — the file is never modified | `pages/monthly_budgets.py:103-135`, `modules/abhishek_manager.py:76-89` |
| **Update** | Update Record | `st.number_input` (ID), `st.form` with a **dynamic key** `f"ab_upd_form_{update_id}"`, `st.form_submit_button` | `get_record()` → `update_record()` → `_prepare()` | That one row's columns are overwritten and the file is rewritten | `pages/monthly_budgets.py:48-79`, `modules/abhishek_manager.py:91-99` |
| **Delete** | Delete Record | `st.number_input` (ID), `st.table`, `st.checkbox` (confirm), `st.button(type="primary", disabled=not confirmed)` | `get_record()` → `delete_record()` | The row is dropped with `df.drop(index=index)` and the file is rewritten | `pages/monthly_budgets.py:82-100`, `modules/abhishek_manager.py:101-104` |

**Validation rules** (`modules/abhishek_manager.py:24-61`)

| Field | Rule | Error message shown |
| --- | --- | --- |
| month | must parse as `YYYY-MM`, year between 2000 and 2100 | "Month must look like YYYY-MM…" |
| category | must be one of `CATEGORIES` (7 values, line 11) | "Please choose a valid category." |
| budget_amount | number, `0 < amount <= 1,000,000` | "Budget must be greater than 0 and at most ₹1,000,000." |
| actual_spent | number, `0 <= amount <= 1,000,000` | "Actual spent must be between 0 and ₹1,000,000." |
| month + category | must be unique (the `duplicate_key`, line 18) | "A budget for {category} in {month} already exists." |

All rule failures are collected into one list and raised together as a single `DataError`, so the user sees **every** problem at once instead of fixing them one by one.

---

## Appendix C — Streamlit properties used on this page

| Streamlit API | Where | Why it is used here |
| --- | --- | --- |
| `st.set_page_config` | `:11` | Sets the tab title, the page icon and the wide layout. Must be the first Streamlit call on a page. |
| `st.title` | `:15` | The page heading. |
| `st.tabs` | `:19-21` | The six CRUD/analysis sections in one screen. Everything in a tab body runs on every rerun, so `with tab:` blocks are used instead of functions. |
| `st.form` | `:26`, `:56` | Groups inputs so the page only reruns when the user submits — not on every keystroke. The update form uses a dynamic key so each record ID gets its own form. |
| `st.form_submit_button` | `:35`, `:69` | The button that triggers the form's rerun and returns `True` on click. |
| `st.columns` | `:27`, `:57`, `:122`, `:145` | Side-by-side layout for forms, KPI rows and charts. |
| `st.text_input` | `col1.text_input` `:28`, `:58` | Free-text entry (the month). |
| `st.selectbox` | `col1.selectbox` `:30`, `:60`, `:123` | One choice from a list (category, and the sort column). `index=` pre-selects the current category in the update form. |
| `st.number_input` | `col2.number_input` `:31`, `:33`, `:63`, `:67`; `st.number_input` `:50`, `:84` | Numeric entry with `min_value`, `step` and `format` — the `min_value=0.0` stops negative amounts at the widget level, before Python validation. |
| `st.radio` | `col2.radio` `:124` | Ascending / Descending sort order, laid out horizontally. |
| `st.checkbox` | `:92` | The delete confirmation. The button stays disabled until it is ticked. |
| `st.button` | `:94` | The delete action, styled `type="primary"` and `disabled=not confirmed`. |
| `st.dataframe` | `:129` | The interactive table. `hide_index=True` removes the pandas index; `column_config` formats the columns. |
| `st.column_config.NumberColumn` | `:130-134` | Per-column formatting: `₹%.2f` for the money columns, `%.1f` for the percentage, `%d` for the ID. |
| `st.table` | `:91` | A small static table showing the record that is about to be deleted. |
| `st.metric` | `column.metric` `modules/helpers.py:81` | The KPI row (4 metrics per row). |
| `st.plotly_chart` | `:150`, `:160` | Renders the two Plotly figures. `key=` keeps the two charts' state separate. |
| `st.sidebar.multiselect` | `modules/helpers.py:99` | The three filters (month, category, status) in the sidebar. |
| `st.sidebar.header` | `:105` | The "Filters" heading in the sidebar. |
| `st.success` / `st.error` / `st.warning` / `st.info` | `:45`, `:43`, `:54`, `:127`, `:100` | Feedback after an action. Green = done, red = the action failed, yellow = a warning, blue = neutral information. |
| `st.caption` | `:119`, `:161` | Small helper text under a table or a chart. |
| `st.subheader` | `:25`, `:49`, `:83`, `:118`, `:142`, `:144`, `:164` | Section headings inside the tabs. |
| `st.code` | `:167` | Shows the plain-text report in a monospace block. |
| `st.download_button` | `:168-170` | Downloads the report as a `.txt` file with a timestamped name. |
| `st.expander` | `modules/helpers.py:71` | Collapsible box listing the rows with missing/invalid data. |
| `st.rerun` | `modules/helpers.py:56` | Restarts the script after a fresh empty CSV is created. |
| `st.stop` | `modules/helpers.py:60` | Ends the page early when the CSV cannot be read. |
| `key=` | everywhere | A unique key for every widget. Streamlit uses it as the widget's identity, so two widgets with the same label do not clash, and the update/delete forms get a **different key per record ID**. |

**Widget placement — `st.x(...)` vs `col.x(...)`.** Inside a column the widget is called on the column object, for example `col1.text_input("Month (YYYY-MM)", ...)` at `pages/monthly_budgets.py:28` and `col2.number_input("Budget amount (₹)", ...)` at `:31`. It is the **same widget** as `st.text_input` / `st.number_input`, just scoped to that column, so it appears in the left or right half of the form. Widgets that are not inside a column are called directly on `st` — for example `st.number_input("Record ID to update", ...)` at `:50`, `st.checkbox(...)` at `:92` and `st.dataframe(...)` at `:129`.

**The Streamlit rerun model** — worth saying once in the video: Streamlit re-executes the whole script from top to bottom on every interaction. That is why the data is re-read at `pages/monthly_budgets.py:103` (after the create/update/delete tabs) and why filters, metrics, charts and the report all stay in sync with the current CSV.

---

## Appendix D — The two graphs explained

### Chart 1 — Grouped bar: budget vs actual by category

```text
read_records()            → rows with budget_amount, actual_spent, variance, status
   ↓
budget_vs_actual()        → groupby("category")[["budget_amount","actual_spent"]].sum()
   ↓  melt(id_vars="category", var_name="Type", value_name="Amount")
   ↓  replace → "Budget" / "Actual spent"
long format (2 rows per category)
   ↓
px.bar(x="category", y="Amount", color="Type", barmode="group")
```

- The long ("melted") format is what lets **one** `px.bar` call draw two bars per category — the category is on the x-axis, the amount on the y-axis, and the `color="Type"` column decides which bar each row becomes.
- `barmode="group"` puts the two bars **side by side** (instead of stacked, which would be `barmode="stack"`).
- Shopping is the category to point at: budget ₹4,000.00 vs actual ₹4,503.76 — the actual bar is visibly taller, and it is the biggest overspend in the dataset.
- Click a bar in the live app to show the hover tooltip.

### Chart 2 — Scatter: one dot per budget line

```text
scatter_data()            → the rows where both amounts are valid
   ↓
px.scatter(x="budget_amount", y="actual_spent", color="category", hover_data=["month"])
   ↓
fig.add_shape(type="line", x0=0, y0=0, x1=limit, y1=limit, line=dict(dash="dot"))
fig.add_annotation(x=limit, y=limit, text="on budget", showarrow=False, yshift=12)
```

- `x = budget_amount`, `y = actual_spent`. A dot **on** the dashed diagonal means the spending exactly matched the plan.
- **Below the line** → actual < budget → *within budget*. **Above the line** → actual > budget → *over budget*.
- `limit` is the largest budget or actual value in the filtered data, so the diagonal always spans the whole plot.
- `add_shape` adds the reference line, `add_annotation` adds the "on budget" label just above its end point. Both are Plotly figure methods, not Streamlit calls — they change the figure before it is passed to `st.plotly_chart`.
- `hover_data=["month"]` shows which month a dot belongs to when you hover.

### The derived columns that feed both charts

| Column | Formula | Example (ID 5: Shopping 2026-07) | Meaning |
| --- | --- | --- | --- |
| `variance` | `budget_amount - actual_spent` | 2000 − 2463.48 = **−463.48** | Negative = over budget. |
| `utilisation_pct` | `actual_spent / budget_amount * 100` | 2463.48 / 2000 × 100 = **123.2 %** | Over 100 % means over budget. |
| `status` | `"Over budget"` if `variance < 0` else `"Within budget"` | **Over budget** | The text used by the sidebar filter. |

The divide-by-zero guard on `utilisation_pct` is `budget_amount.replace(0, np.nan)` — a zero budget gives `NaN`, not `inf`, and that row is then left out of the statistics by `_complete_rows()`.

---

## Appendix E — Demo cheat sheet

### The demo row (add → update → delete the same record)

| Step | Tab | What to enter | Expected on screen |
| --- | --- | --- | --- |
| 1 | Add Record | month `2026-10`, category `Health`, budget `900`, spent `720` → **Add budget line** | 🟢 "Budget line added with ID **19**." |
| 2 | View Data | filter Month → `2026-10` | "Showing 1 of 17 records" — the new row is visible |
| 3 | Update Record | ID `19` → change actual spent `720` → `950` → **Save changes** | 🟢 "Record 19 updated." (now over budget: variance −50, utilisation 105.6 %) |
| 4 | Analytics | — | the new dot sits just **above** the dashed line |
| 5 | Delete Record | ID `19` → tick the confirmation box → **Delete record** | 🟢 "Record 19 deleted." → back to 16 records |

The CSV ends exactly as it started — do **not** forget step 5, and do not keep a failed run as the final take.

### Error demos (only if you have time)

| Try this | Expected message |
| --- | --- |
| Add `2026-09` + `Food` (already exists) | "A budget for Food in 2026-09 already exists. Use Update Record to change it." |
| Add a budget of `0` | "Budget must be greater than 0 and at most ₹1,000,000." |
| Update / delete ID `999` | "Record ID 999 not found. Please enter a valid record ID." |

### Numbers you can quote (verified against the current CSV)

| Metric | Value |
| --- | --- |
| Rows in the CSV | 16 |
| Total budgeted | ₹25,800.00 |
| Total spent | ₹23,056.41 |
| Overall utilisation | 89.4 % |
| Average utilisation (per line) | 87.5 % |
| Over-budget lines | 5 of 16 |
| Biggest overspend | Shopping, 2026-07 — ₹463.48 over |
| Remaining budget | ₹2,743.59 |
| Category totals (budget → spent) | Food 9,000 → 8,504.58 · Shopping 4,000 → 4,503.76 · Transport 4,500 → 3,322.33 · Utilities 3,600 → 2,852.26 · Entertainment 3,100 → 2,631.96 · Health 1,600 → 1,241.52 |

---

## Appendix F — Likely viva questions

**Q1. Why is there a manager class and not all the code in the page?**
The page handles only the UI; the manager holds the rules and the data access. That keeps the validation and the CSV handling testable and out of the UI layer.

**Q2. What does `super().__init__("dummy_abhishek_budgets.csv")` do?**
It calls the parent constructor so the base class stores the file path in `self._path`. My class never writes the path itself.

**Q3. Why is the CSV read with `dtype=str`?**
So saving never silently changes a value the user typed. A bad number stays visible as text and can be fixed with Update Record instead of disappearing.

**Q4. What stops the CSV from being corrupted?**
`_save()` writes to a `.tmp` file first and calls `os.replace()` only after the write succeeded, inside `try / except / finally`.

**Q5. What is the duplicate key, and why?**
`["month", "category"]` — one budget line per category per month. It is checked on create and on update (ignoring the row being edited).

**Q6. What happens with a blank or invalid cell in the CSV?**
It stays in the file and is shown in the table, but the page warns how many rows are affected and excludes them from any statistic that needs the missing value.

**Q7. Why does the Update tab use `f"ab_upd_form_{update_id}"` as the form key?**
Streamlit identifies widgets by key. Making the key depend on the record ID gives each record its own form state, so pre-filling a different record does not mix up the values.

**Q8. How do you know the charts are not hard-coded?**
Every number comes from `read_records()` on the current CSV, then the sidebar filters narrow the frame, and the statistics and both charts are computed from that filtered frame.

**Q9. What is `st.rerun()` for?**
After a fresh empty CSV is created the page has to re-read the data, so the script restarts from the top.

**Q10. Why `melt()` instead of two separate charts?**
Melt turns the two amount columns into one long table with a `Type` column, so a single `px.bar` call with `color="Type"` draws both bars per category — less code and the bars share one axis.

**Q11. What does `utilisation_pct` show and why is there a `replace(0, np.nan)`?**
Actual spending as a percentage of the budget. A zero budget would cause a division by zero, so it becomes `NaN` and the row is left out of the statistics instead of breaking them.

**Q12. What is the SDG link for your page?**
SDG 12 — Responsible Consumption and Production: comparing actual spending with the plan makes over-consumption visible and helps reduce it. SDG 8 as well, because a budget is part of managing earnings deliberately.

---

### Small note on the code

`pages/monthly_budgets.py:20` has a leading space in the tab label `" Delete Record"` — a harmless typo that makes the tab label look slightly indented. It is mentioned here only so the gap does not surprise you while reading the code on camera; it does not affect anything.
