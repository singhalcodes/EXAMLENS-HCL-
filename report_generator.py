"""Dynamic text summary report generation for ExamLens."""

from analytics import (actionable_insights, analyse_departments, analyse_subjects,
                       calculate_statistics, detect_academic_risks, top_and_bottom,
                       analyse_attendance)


def _number(value, digits=2):
    return "N/A" if value is None or value != value else f"{value:.{digits}f}"


def generate_summary_report(frame):
    """Create a current-data report as a list of terminal-ready lines."""
    stats = calculate_statistics(frame)
    subjects = analyse_subjects(frame)
    departments = analyse_departments(frame)
    top, bottom = top_and_bottom(frame)
    risks = detect_academic_risks(frame)
    lines = ["EXAMLENS | STUDENT PERFORMANCE & ACADEMIC INTELLIGENCE SYSTEM",
             "=" * 68, f"Dataset records: {stats['total_records']}  |  Valid marks: {stats['valid_marks']}",
             f"Average marks: {_number(stats['average_marks'])}  |  Median: {_number(stats['median_marks'])}",
             f"Highest: {_number(stats['highest_marks'])}  |  Lowest: {_number(stats['lowest_marks'])}  |  Std dev: {_number(stats['marks_std'])}",
             f"Pass rate: {_number(stats['pass_percentage'])}% ({stats['passed']} pass, {stats['failed']} below {40})",
             f"Average attendance: {_number(stats['average_attendance'])}%  |  Average study hours: {_number(stats['average_study_hours'])}",
             "", "SUBJECT PERFORMANCE"]
    if subjects.empty:
        lines.append("No valid subject marks available.")
    for subject, row in subjects.iterrows():
        lines.append(f"  {subject:<20} avg {_number(row['Average'])} | high {_number(row['Highest'])} | low {_number(row['Lowest'])} | n={int(row['Count'])}")
    lines.extend(["", "DEPARTMENT PERFORMANCE"])
    for department, row in departments.iterrows():
        lines.append(f"  {department:<8} marks {_number(row['Average_Marks'])} | attendance {_number(row['Average_Attendance'])}% | n={int(row['Student_Count'])}")
    lines.extend(["", "TOP PERFORMERS"])
    for _, row in top.iterrows():
        lines.append(f"  {row['Student_ID']}  {row['Name']} — {_number(row['Marks'])} ({row['Subject']})")
    lines.extend(["", "LOW PERFORMERS"])
    for _, row in bottom.iterrows():
        lines.append(f"  {row['Student_ID']}  {row['Name']} — {_number(row['Marks'])} ({row['Subject']})")
    lines.extend(["", f"Attendance-risk records (<75%): {len(analyse_attendance(frame))}",
                  f"Academic-risk records: {len(risks)}", "", "DATA-DERIVED INSIGHTS"])
    lines.extend("  • " + insight for insight in actionable_insights(frame))
    lines.extend(["", "Missing numeric values are excluded from each metric; no missing mark is treated as zero."])
    return "\n".join(lines)


def save_summary_report(frame, file_path="summary_report.txt"):
    report = generate_summary_report(frame)
    with open(file_path, "w", encoding="utf-8") as report_file:
        report_file.write(report + "\n")
    return file_path
