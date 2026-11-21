"""Pandas and NumPy academic analytics for ExamLens."""

import numpy as np
import pandas as pd

PASS_MARK = 40
ATTENDANCE_LIMIT = 75
LOW_ASSIGNMENT_LIMIT = 50
# A tuple suits fixed grading boundaries: the configuration is immutable.
GRADE_THRESHOLDS = ((85, "Excellent"), (70, "Good"), (50, "Average"), (0, "Needs Improvement"))


def _numeric(frame, column):
    return pd.to_numeric(frame[column], errors="coerce")


def calculate_statistics(frame):
    marks = _numeric(frame, "Marks").dropna()
    attendance = _numeric(frame, "Attendance").dropna()
    study = _numeric(frame, "Study_Hours").dropna()
    passed = marks >= PASS_MARK
    stats = {"total_records": len(frame), "valid_marks": int(marks.count()),
             "average_marks": marks.mean(), "highest_marks": marks.max(),
             "lowest_marks": marks.min(), "median_marks": marks.median(),
             "marks_std": marks.std(), "passed": int(passed.sum()),
             "failed": int((~passed).sum()),
             "pass_percentage": (float(passed.mean() * 100) if len(marks) else np.nan),
             "average_attendance": attendance.mean(), "average_study_hours": study.mean()}
    return stats


def analyse_subjects(frame):
    valid = frame.dropna(subset=["Marks"])
    return valid.groupby("Subject")["Marks"].agg(
        Average="mean", Highest="max", Lowest="min", Count="count").sort_values("Average", ascending=False)


def analyse_departments(frame):
    return frame.groupby("Department").agg(
        Average_Marks=("Marks", "mean"), Average_Attendance=("Attendance", "mean"),
        Student_Count=("Student_ID", "count")).sort_values("Average_Marks", ascending=False)


def analyse_attendance(frame):
    attendance = _numeric(frame, "Attendance")
    return frame.loc[attendance < ATTENDANCE_LIMIT].copy()


def analyse_study_hours(frame):
    valid = frame[["Study_Hours", "Marks"]].apply(pd.to_numeric, errors="coerce").dropna()
    correlation = valid["Study_Hours"].corr(valid["Marks"]) if len(valid) >= 2 else np.nan
    return {"correlation": correlation, "records_used": len(valid),
            "average_hours": valid["Study_Hours"].mean(), "average_marks": valid["Marks"].mean()}


def top_and_bottom(frame, count=5):
    valid = frame.dropna(subset=["Marks"])
    return (valid.sort_values("Marks", ascending=False).head(count),
            valid.sort_values("Marks", ascending=True).head(count))


def classify_performance(mark):
    if pd.isna(mark):
        return "Not available"
    for boundary, label in GRADE_THRESHOLDS:
        if mark >= boundary:
            return label
    return "Needs Improvement"


def detect_academic_risks(frame):
    risks = []
    for _, row in frame.iterrows():
        reasons = []
        if pd.notna(row["Marks"]) and row["Marks"] < PASS_MARK:
            reasons.append("Marks below 40")
        if pd.notna(row["Attendance"]) and row["Attendance"] < ATTENDANCE_LIMIT:
            reasons.append("Attendance below 75%")
        if pd.notna(row["Assignment_Score"]) and row["Assignment_Score"] < LOW_ASSIGNMENT_LIMIT:
            reasons.append("Assignment score below 50")
        if reasons:
            item = row.to_dict()
            item["Risk_Reason"] = "; ".join(reasons)
            risks.append(item)
    return pd.DataFrame(risks)


def actionable_insights(frame):
    insights = []
    subjects = analyse_subjects(frame)
    departments = analyse_departments(frame)
    stats = calculate_statistics(frame)
    attendance_risks = analyse_attendance(frame)
    risks = detect_academic_risks(frame)
    if not subjects.empty:
        insights.append(f"Strongest subject by average: {subjects.index[0]} ({subjects.iloc[0]['Average']:.1f}).")
        weakest = subjects.index[-1]
        insights.append(f"Weakest subject by average: {weakest} ({subjects.iloc[-1]['Average']:.1f}).")
    if not departments.empty:
        insights.append(f"Department with highest average marks: {departments.index[0]} ({departments.iloc[0]['Average_Marks']:.1f}).")
    insights.append(f"{stats['failed']} record(s) are below the pass mark of {PASS_MARK}.")
    insights.append(f"{len(attendance_risks)} record(s) have attendance below {ATTENDANCE_LIMIT}%.")
    insights.append(f"{len(risks)} record(s) meet at least one academic-risk rule.")
    correlation = analyse_study_hours(frame)["correlation"]
    if pd.notna(correlation):
        if correlation >= 0.3:
            relation = "positive"
        elif correlation <= -0.3:
            relation = "negative"
        else:
            relation = "weak"
        insights.append(f"Study-hours/marks correlation is {correlation:.2f} ({relation}); correlation does not prove causation.")
    else:
        insights.append("Study-hours/marks correlation is unavailable (not enough complete records).")
    return insights


def numpy_demonstration(frame):
    """Show explicit 1D/2D arrays, indexing, slicing and NaN-safe statistics."""
    marks = _numeric(frame, "Marks").dropna().to_numpy(dtype=float)
    pair = frame[["Marks", "Attendance"]].apply(pd.to_numeric, errors="coerce").dropna().to_numpy(dtype=float)
    stats = {"count": len(marks), "sum": np.sum(marks) if len(marks) else np.nan,
             "mean": np.mean(marks) if len(marks) else np.nan,
             "median": np.median(marks) if len(marks) else np.nan,
             "maximum": np.max(marks) if len(marks) else np.nan,
             "minimum": np.min(marks) if len(marks) else np.nan,
             "std_dev": np.std(marks) if len(marks) else np.nan,
             "array_1d": marks, "array_2d": pair}
    stats["index_1d"] = marks[0] if len(marks) else None
    stats["slice_1d"] = marks[:5]
    stats["index_2d"] = pair[0] if len(pair) else None
    stats["slice_2d"] = pair[:3]
    study_marks = frame[["Study_Hours", "Marks"]].apply(pd.to_numeric, errors="coerce").dropna()
    stats["study_correlation"] = study_marks["Study_Hours"].corr(study_marks["Marks"]) if len(study_marks) >= 2 else np.nan
    return stats


def pandas_explorer(frame):
    """Bundle commonly demonstrated DataFrame views and missing-data counts."""
    numeric = frame[["Marks", "Attendance", "Study_Hours", "Assignment_Score"]].apply(pd.to_numeric, errors="coerce")
    return {"head": frame.head(), "tail": frame.tail(),
            "selected_columns": frame[["Name", "Marks", "Attendance", "Study_Hours"]],
            "missing_counts": frame.isna().sum(),
            "imputed_means": numeric.fillna(numeric.mean()),
            "statistics": numeric.describe().T,
            "above_80": frame.loc[numeric["Marks"] > 80],
            "attendance_below_75": frame.loc[numeric["Attendance"] < 75],
            "failed": frame.loc[numeric["Marks"] < PASS_MARK],
            "study_above_4": frame.loc[numeric["Study_Hours"] > 4],
            "sorted_marks": frame.sort_values("Marks", ascending=False),
            "sorted_attendance": frame.sort_values("Attendance", ascending=False),
            "sorted_study_hours": frame.sort_values("Study_Hours", ascending=False)}
