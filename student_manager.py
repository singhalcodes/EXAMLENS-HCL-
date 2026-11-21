"""CSV-backed student record operations for ExamLens."""

from pathlib import Path
import pandas as pd

COLUMNS = ["Student_ID", "Name", "Department", "Subject", "Marks", "Attendance",
           "Study_Hours", "Assignment_Score", "Exam_Type"]
NUMERIC_COLUMNS = ["Marks", "Attendance", "Study_Hours", "Assignment_Score"]
DEPARTMENTS = ("CSE", "IT", "AIML", "DS", "ECE")
SUBJECTS = ("Python", "Mathematics", "Physics", "Statistics", "Data Structures")
EXAM_TYPES = ("Midterm", "Endterm", "Quiz")


def load_data(file_path="dataset.csv"):
    """Load the CSV, creating a header-only file if it does not exist."""
    path = Path(file_path)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(columns=COLUMNS).to_csv(path, index=False)
    try:
        frame = pd.read_csv(path)
        missing_columns = [column for column in COLUMNS if column not in frame.columns]
        if missing_columns:
            raise ValueError("CSV is missing required columns: " + ", ".join(missing_columns))
        frame = frame[COLUMNS].copy()
        for column in NUMERIC_COLUMNS:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
        return frame
    except (pd.errors.ParserError, UnicodeDecodeError) as error:
        raise ValueError(f"Could not read {path.name}: {error}") from error


def save_data(frame, file_path="dataset.csv"):
    """Persist a DataFrame in the project's canonical column order."""
    frame[COLUMNS].to_csv(file_path, index=False)


def validate_student_data(record, existing_ids=None):
    """Return a list of human-readable validation errors."""
    existing_ids = set(existing_ids) if existing_ids is not None else set()
    errors = []
    student_id = str(record.get("Student_ID", "")).strip()
    if not student_id:
        errors.append("Student_ID cannot be blank.")
    elif student_id in existing_ids:
        errors.append("Student_ID already exists.")
    if not str(record.get("Name", "")).strip():
        errors.append("Name cannot be blank.")
    if record.get("Department") not in DEPARTMENTS:
        errors.append("Department must be one of: " + ", ".join(DEPARTMENTS))
    if record.get("Subject") not in SUBJECTS:
        errors.append("Subject must be one of: " + ", ".join(SUBJECTS))
    if record.get("Exam_Type") not in EXAM_TYPES:
        errors.append("Exam_Type must be one of: " + ", ".join(EXAM_TYPES))
    for column in NUMERIC_COLUMNS:
        try:
            value = float(record.get(column))
            if not pd.notna(value):
                raise ValueError
            minimum, maximum = (0, 100) if column != "Study_Hours" else (0, 24)
            if not minimum <= value <= maximum:
                errors.append(f"{column} must be between {minimum} and {maximum}.")
        except (TypeError, ValueError):
            errors.append(f"{column} must be a valid number.")
    return errors


def add_student(frame, record, file_path="dataset.csv"):
    errors = validate_student_data(record, frame["Student_ID"].dropna().astype(str))
    if errors:
        return frame, errors
    new_row = {column: record[column] for column in COLUMNS}
    updated = pd.concat([frame, pd.DataFrame([new_row])], ignore_index=True)
    save_data(updated, file_path)
    return updated, []


def display_students(frame, page=1, page_size=20):
    """Return a manageable page, using list slicing for pagination."""
    rows = frame.to_dict("records")
    rows.sort(key=lambda row: str(row.get("Student_ID", "")))
    start = max(0, page - 1) * page_size
    return rows[start:start + page_size]


def search_student(frame, query):
    """Search exact IDs or case-insensitive partial names."""
    query = str(query).strip()
    if not query:
        return frame.iloc[0:0]
    mask = frame["Student_ID"].astype(str).str.casefold().eq(query.casefold())
    mask |= frame["Name"].fillna("").astype(str).str.contains(query, case=False, regex=False)
    return frame[mask].copy()


def update_student(frame, student_id, updates, file_path="dataset.csv"):
    matches = frame["Student_ID"].astype(str).eq(str(student_id))
    if not matches.any():
        return frame, False, ["Student ID was not found."]
    candidate = frame.loc[matches].iloc[0].to_dict()
    candidate.update({key: value for key, value in updates.items() if value is not None})
    errors = validate_student_data(candidate, set())
    if errors:
        return frame, False, errors
    for key, value in candidate.items():
        frame.loc[matches, key] = value
    save_data(frame, file_path)
    return frame, True, []


def delete_student(frame, student_id, file_path="dataset.csv"):
    mask = frame["Student_ID"].astype(str).eq(str(student_id))
    if not mask.any():
        return frame, False
    updated = frame.loc[~mask].copy().reset_index(drop=True)
    save_data(updated, file_path)
    return updated, True


def unique_values(frame, column):
    """Use a set to find unique categorical values, then sort for display."""
    values = set(frame[column].dropna().astype(str).tolist())
    return sorted(values)
