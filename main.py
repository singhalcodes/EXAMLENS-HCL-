"""Interactive terminal application for ExamLens."""

from pathlib import Path
import pandas as pd
from student_manager import (COLUMNS, DEPARTMENTS, EXAM_TYPES, NUMERIC_COLUMNS,
                             SUBJECTS, add_student, delete_student, display_students,
                             load_data, save_data, search_student, unique_values,
                             update_student)
from analytics import (actionable_insights, analyse_attendance, analyse_departments,
                       analyse_study_hours, analyse_subjects, calculate_statistics,
                       detect_academic_risks, numpy_demonstration, pandas_explorer,
                       top_and_bottom)
from report_generator import generate_summary_report, save_summary_report

DATA_FILE = Path(__file__).with_name("dataset.csv")


def heading(title):
    print("\n" + "=" * 72 + f"\n{title}\n" + "=" * 72)


def pause():
    input("\nPress Enter to return to the main menu...")


def show_table(frame):
    if frame is None or len(frame) == 0:
        print("No records to display.")
        return
    view = frame.copy()
    for column in NUMERIC_COLUMNS:
        if column in view:
            view[column] = view[column].map(lambda value: "—" if pd.isna(value) else round(float(value), 2))
    print(view.to_string(index=False, max_rows=30))
    if len(frame) > 30:
        print(f"Showing 30 of {len(frame)} records.")


def prompt_number(label, minimum=0, maximum=100):
    while True:
        raw = input(f"{label} ({minimum}–{maximum}): ").strip()
        try:
            value = float(raw)
            if minimum <= value <= maximum:
                return value
            print(f"Enter a value from {minimum} to {maximum}.")
        except ValueError:
            print("Enter a valid number.")


def prompt_choice(label, choices):
    allowed = ", ".join(choices)
    while True:
        value = input(f"{label} [{allowed}]: ").strip()
        match = next((item for item in choices if item.casefold() == value.casefold()), None)
        if match:
            return match
        print("Choose one of the listed values.")


def add_flow(frame):
    heading("ADD STUDENT")
    record = {"Student_ID": input("Student ID: ").strip(), "Name": input("Name: ").strip(),
              "Department": prompt_choice("Department", DEPARTMENTS),
              "Subject": prompt_choice("Subject", SUBJECTS),
              "Marks": prompt_number("Marks"), "Attendance": prompt_number("Attendance (%)"),
              "Study_Hours": prompt_number("Study hours per day", 0, 24),
              "Assignment_Score": prompt_number("Assignment score"),
              "Exam_Type": prompt_choice("Exam type", EXAM_TYPES)}
    frame, errors = add_student(frame, record, DATA_FILE)
    if errors:
        print("Could not add student: " + " ".join(errors))
    else:
        print("Student added and saved to dataset.csv.")
    return frame


def search_flow(frame):
    heading("SEARCH STUDENTS")
    query = input("Enter a Student ID or part of a name: ").strip()
    results = search_student(frame, query)
    if results.empty:
        print("No matching students found.")
    else:
        show_table(results)


def update_flow(frame):
    heading("UPDATE STUDENT")
    student_id = input("Student ID to update: ").strip()
    found = search_student(frame, student_id)
    if found.empty:
        print("Student ID was not found.")
        return frame
    show_table(found)
    print("Leave a field blank to keep its current value.")
    updates = {}
    for column in COLUMNS[1:]:
        current = found.iloc[0][column]
        value = input(f"{column} [{current}]: ").strip()
        if not value:
            continue
        if column in NUMERIC_COLUMNS:
            try:
                updates[column] = float(value)
            except ValueError:
                print(f"Invalid number for {column}; update cancelled.")
                return frame
        elif column == "Department":
            updates[column] = next((item for item in DEPARTMENTS if item.casefold() == value.casefold()), value)
        elif column == "Subject":
            updates[column] = next((item for item in SUBJECTS if item.casefold() == value.casefold()), value)
        elif column == "Exam_Type":
            updates[column] = next((item for item in EXAM_TYPES if item.casefold() == value.casefold()), value)
        else:
            updates[column] = value
    frame, changed, errors = update_student(frame, student_id, updates, DATA_FILE)
    print("Student record updated." if changed else "Update failed: " + " ".join(errors))
    return frame


def delete_flow(frame):
    heading("DELETE STUDENT")
    student_id = input("Student ID to delete: ").strip()
    found = search_student(frame, student_id)
    if found.empty:
        print("Student ID was not found.")
        return frame
    show_table(found)
    if input("Delete this record permanently? Type YES to confirm: ").strip() != "YES":
        print("Deletion cancelled.")
        return frame
    frame, deleted = delete_student(frame, student_id, DATA_FILE)
    print("Record deleted." if deleted else "Record was not deleted.")
    return frame


def display_flow(frame):
    heading("STUDENT RECORDS")
    page_size = 20
    total_pages = max(1, (len(frame) + page_size - 1) // page_size)
    try:
        page = int(input(f"Page number (1–{total_pages}, Enter for 1): ").strip() or "1")
    except ValueError:
        page = 1
    page = min(max(page, 1), total_pages)
    show_table(pd.DataFrame(display_students(frame, page, page_size), columns=COLUMNS))
    print(f"Page {page}/{total_pages} • {len(frame)} total records")


def overall_flow(frame):
    heading("OVERALL PERFORMANCE DASHBOARD")
    stats = calculate_statistics(frame)
    labels = [("Student records", "total_records"), ("Records with marks", "valid_marks"),
              ("Average marks", "average_marks"), ("Highest marks", "highest_marks"),
              ("Lowest marks", "lowest_marks"), ("Median marks", "median_marks"),
              ("Marks standard deviation", "marks_std"), ("Pass percentage", "pass_percentage"),
              ("Passed (≥40)", "passed"), ("Below pass mark", "failed"),
              ("Average attendance (%)", "average_attendance"), ("Average study hours", "average_study_hours")]
    for label, key in labels:
        value = stats[key]
        print(f"{label:<30} {value:.2f}" if pd.notna(value) and isinstance(value, (int, float)) else f"{label:<30} {value}")
    print("Missing marks are excluded from mark metrics, not counted as zero.")


def subject_flow(frame):
    heading("SUBJECT ANALYSIS")
    print(analyse_subjects(frame).round(2).to_string() if not frame.empty else "No records available.")
    insights = actionable_insights(frame)
    print("\n" + "\n".join(insights[:2]))


def department_flow(frame):
    heading("DEPARTMENT ANALYSIS")
    print(analyse_departments(frame).round(2).to_string() if not frame.empty else "No records available.")
    print("Unique departments (set): " + ", ".join(unique_values(frame, "Department")))


def attendance_flow(frame):
    heading("ATTENDANCE ANALYSIS")
    risky = analyse_attendance(frame)
    print(f"Average attendance: {frame['Attendance'].mean():.2f}%" if frame["Attendance"].notna().any() else "Average attendance: N/A")
    print(f"Below 75%: {len(risky)} record(s)")
    show_table(risky)


def study_flow(frame):
    heading("STUDY-HOURS ANALYSIS")
    result = analyse_study_hours(frame)
    print(f"Complete study-hours/marks pairs: {result['records_used']}")
    print(f"Correlation: {result['correlation']:.3f}" if pd.notna(result["correlation"]) else "Correlation: unavailable")
    if pd.notna(result["correlation"]):
        print("Correlation describes association in these records; it does not prove that study time causes marks to change.")


def performers_flow(frame):
    heading("TOP & BOTTOM PERFORMERS")
    top, bottom = top_and_bottom(frame)
    print("TOP FIVE")
    show_table(top)
    print("\nBOTTOM FIVE")
    show_table(bottom)


def risks_flow(frame):
    heading("ACADEMIC RISK DETECTION")
    risks = detect_academic_risks(frame)
    print("Rules: marks <40, attendance <75%, assignment score <50.")
    show_table(risks)
    if not risks.empty:
        print("\n" + risks[["Student_ID", "Name", "Risk_Reason"]].to_string(index=False))


def numpy_flow(frame):
    heading("NUMPY DEMONSTRATION")
    result = numpy_demonstration(frame)
    print(f"1D marks array (first 8): {result['array_1d'][:8]}")
    print(f"1D index [0]: {result['index_1d']} | 1D slice [0:5]: {result['slice_1d']}")
    print(f"2D [Marks, Attendance] array (first 5):\n{result['array_2d'][:5]}")
    print(f"2D index [0]: {result['index_2d']} | 2D slice [0:3]:\n{result['slice_2d']}")
    print("NumPy mark calculations (missing marks excluded):")
    for key in ("count", "sum", "mean", "median", "maximum", "minimum", "std_dev"):
        print(f"  {key.replace('_', ' ').title():<12} {result[key]}")
    print(f"Study-hours/marks correlation: {result['study_correlation']}")


def pandas_flow(frame):
    heading("PANDAS DATA EXPLORER")
    print("1 First five rows  2 Last five rows  3 Selected columns  4 Missing-value counts")
    print("5 Above 80  6 Attendance below 75  7 Failed  8 Study hours above 4")
    print("9 GroupBy subject  10 GroupBy department  11 Sort records  12 Numeric statistics")
    choice = input("Choose an explorer view: ").strip()
    view = pandas_explorer(frame)
    mapping = {"1": "head", "2": "tail", "3": "selected_columns", "4": "missing_counts",
               "5": "above_80", "6": "attendance_below_75", "7": "failed", "8": "study_above_4",
               "12": "statistics"}
    if choice in mapping:
        result = view[mapping[choice]]
        print(result.to_string(index=False) if hasattr(result, "to_string") else result.to_string())
    elif choice == "9":
        print(analyse_subjects(frame).round(2).to_string())
    elif choice == "10":
        print(analyse_departments(frame).round(2).to_string())
    elif choice == "11":
        column = input("Sort by marks, attendance or study hours? ").strip().casefold()
        key = {"marks": "sorted_marks", "attendance": "sorted_attendance", "study hours": "sorted_study_hours"}.get(column)
        print(view[key].head(20).to_string(index=False) if key else "Choose marks, attendance or study hours.")
    else:
        print("Choose a listed option.")


def report_flow(frame):
    heading("SUMMARY REPORT")
    report = generate_summary_report(frame)
    print(report)
    if input("Save this report to summary_report.txt? (y/N): ").strip().casefold() == "y":
        save_summary_report(frame, DATA_FILE.with_name("summary_report.txt"))
        print("Report saved.")


MENU = {"1": ("Display All Student Records", display_flow), "2": ("Add New Student", add_flow),
        "3": ("Search Student", search_flow), "4": ("Update Student Record", update_flow),
        "5": ("Delete Student Record", delete_flow), "6": ("Overall Performance Analytics", overall_flow),
        "7": ("Subject Analysis", subject_flow), "8": ("Department Analysis", department_flow),
        "9": ("Attendance Analysis", attendance_flow), "10": ("Study-Hours Analysis", study_flow),
        "11": ("Top & Bottom Performers", performers_flow), "12": ("Academic Risk Detection", risks_flow),
        "13": ("NumPy Demonstration", numpy_flow), "14": ("Pandas Data Explorer", pandas_flow),
        "15": ("Generate Summary Report", report_flow), "16": ("Exit", None)}


def show_menu():
    print("\n" + "=" * 72)
    print("                         EXAMLENS")
    print("       STUDENT PERFORMANCE & ACADEMIC INTELLIGENCE SYSTEM")
    print("=" * 72)
    for number, (label, _) in MENU.items():
        print(f"{number:>2}. {label}")
    print("=" * 72)


def main():
    print("\n" + "=" * 72 + "\n  EXAMLENS\n  Student Performance & Academic Intelligence System\n" + "=" * 72)
    try:
        frame = load_data(DATA_FILE)
    except (OSError, ValueError) as error:
        print(f"Unable to open the dataset: {error}")
        return
    print(f"Loaded {len(frame)} student records from {DATA_FILE.name}.")
    while True:
        try:
            show_menu()
            choice = input("Enter your choice: ").strip()
            if choice == "16":
                print("Thank you for using ExamLens. Goodbye.")
                break
            action = MENU.get(choice, (None, None))[1]
            if action is None:
                print("Please enter a menu number from 1 to 16.")
                continue
            result = action(frame)
            if choice in {"1", "2", "4", "5"} and result is not None:
                frame = result
            pause()
        except KeyboardInterrupt:
            print("\nReturning to the main menu. Choose 16 to exit.")
        except (OSError, ValueError, KeyError) as error:
            print(f"This action could not be completed: {error}")
            try:
                pause()
            except KeyboardInterrupt:
                pass


if __name__ == "__main__":
    main()
