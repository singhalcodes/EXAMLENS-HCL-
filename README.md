# ExamLens

**Student Performance & Academic Intelligence System**

ExamLens is a beginner-friendly Python terminal application created for an HCL Tech training demonstration. It combines student record CRUD, persistent CSV file handling, Pandas exploration, NumPy calculations, and transparent academic analytics. It runs locally and uses no API, database, web server, or external service.

## Run it

Python 3.10 or newer is recommended.

```bash
python -m pip install -r requirements.txt
python main.py
```

Choose a numbered menu item and press Enter. The dataset is read from `dataset.csv` in the project folder. CRUD changes are saved to that same file immediately. The initial CSV contains 80 Indian student names, varied scores, and four intentional missing numeric values. A generated report can optionally be saved as `summary_report.txt`.

## Menu

1. Paginated student records
2. Add a student with validation and unique ID checks
3. Search by exact ID or case-insensitive partial name
4. Update fields; blank inputs keep existing values
5. Delete with explicit `YES` confirmation
6. Overall performance dashboard
7. Subject averages, highs, lows, and counts
8. Department marks, attendance, and record counts
9. Attendance risks (below 75%)
10. Study hours and marks correlation
11. Top and bottom five performers
12. Academic risk records and reasons
13. NumPy array, indexing, slicing, statistics, and correlation demo
14. Pandas rows, columns, filters, sorts, groupings, missing counts, and statistics
15. Dynamic summary report (optional TXT save)
16. Exit

## Analytics methodology

- Pass mark is **40**. Missing marks are excluded from pass rate and mark statistics; they are never silently treated as zero.
- Performance bands are **Excellent** (85+), **Good** (70–84.9), **Average** (50–69.9), and **Needs Improvement** (below 50).
- Academic risk flags are independent and transparent: marks below 40, attendance below 75%, or assignment score below 50. A record can carry more than one reason.
- Each metric uses available non-missing values. Pandas views show per-column missing counts. The explorer also demonstrates mean imputation in memory only; it does not overwrite source data.
- NumPy arrays for statistical calculations exclude missing marks. Two-variable calculations use only complete pairs. Correlation describes association in these records and does not establish causation or predict an individual outcome.
- Study-hours correlation is described as positive at 0.30 or above, negative at -0.30 or below, and weak in between. It is not presented as causal evidence.

## Project structure

- `main.py` — terminal menu, prompts, formatting, and feature orchestration
- `student_manager.py` — schema, CSV loading/saving, validation, CRUD, search, and unique-value extraction
- `analytics.py` — NumPy and Pandas analytics, performance bands, risk rules, and insights
- `report_generator.py` — dynamic terminal and TXT summary report
- `dataset.csv` — persistent seed dataset (80 records)
- `requirements.txt` — minimal third-party dependencies

## Python concepts demonstrated

The app uses lists for menu and record collections, list sorting and slicing for display, a tuple for fixed grading boundaries, sets to find unique department/subject values, dictionaries for records and generated statistics, and modular functions across four files. CRUD operations use Pandas-backed CSV file handling. Pandas covers DataFrames, CSV reads, filtering, sorting, grouping, missing-value counts, imputation demonstration, and descriptive statistics. NumPy covers 1D and 2D arrays, indexing, slicing, aggregate calculations, and correlation.

## Notes for a viva

- `load_data()` reads the actual CSV every time the program starts; this is not a hardcoded DataFrame.
- `save_data()` writes updates to CSV, so changes survive a restart.
- `validate_student_data()` checks ID uniqueness, allowed categories, and numeric ranges (0–100, or 0–24 hours per day).
- Missing numeric values are parsed as missing and excluded from applicable calculations. They are not replaced in the source file.
- The analytics are descriptive and rule-based. They do not use machine learning or predict academic outcomes.
