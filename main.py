"""
main.py - Interactive CLI Interface for Student Marks & Performance Manager.

Provides a clean, terminal-based user menu to perform:
1. Add New Student Record
2. View All Student Records (Formatted Table)
3. Search Student by Roll Number
4. Update Student Marks
5. Delete Student Record
6. View Class Performance Summary
7. Export Data to CSV
8. Exit
"""

import os
import sys
from typing import Any, Dict, List

import operations
from database import DEFAULT_DB_NAME, init_db


def clear_screen() -> None:
    """Utility to clear terminal screen cleanly across OS."""
    # Kept simple for standard CLI interaction
    pass


def print_header(title: str) -> None:
    """Prints a styled section header."""
    print("\n" + "=" * 65)
    print(f"  {title.upper()}")
    print("=" * 65)


def print_student_table(students: List[Dict[str, Any]]) -> None:
    """
    Renders student records in a formatted ASCII table.

    Args:
        students (List[Dict[str, Any]]): List of student dictionaries.
    """
    if not students:
        print("\n[!] No student records found.")
        return

    separator = "+-------+----------------------+---------+---------+---------+---------+---------+-------+"
    header = f"| {'Roll':<5} | {'Name':<20} | {'Phy':<7} | {'Chem':<7} | {'Math':<7} | {'Total':<7} | {'%':<7} | {'Grade':<5} |"

    print(separator)
    print(header)
    print(separator)

    for s in students:
        row = (
            f"| {s['roll_no']:<5} "
            f"| {s['name'][:20]:<20} "
            f"| {s['physics']:>7.2f} "
            f"| {s['chemistry']:>7.2f} "
            f"| {s['maths']:>7.2f} "
            f"| {s['total']:>7.2f} "
            f"| {s['percentage']:>6.2f}% "
            f"| {s['grade']:^5} |"
        )
        print(row)

    print(separator)
    print(f"Total Records: {len(students)}\n")


def print_single_student_card(s: Dict[str, Any]) -> None:
    """Displays a single student's record as a formatted profile card."""
    print("\n" + "-" * 40)
    print(f"  STUDENT RECORD - ROLL NO: {s['roll_no']}")
    print("-" * 40)
    print(f"  Name        : {s['name']}")
    print(f"  Physics     : {s['physics']:.2f} / 100")
    print(f"  Chemistry   : {s['chemistry']:.2f} / 100")
    print(f"  Maths       : {s['maths']:.2f} / 100")
    print(f"  Total Marks : {s['total']:.2f} / 300.00")
    print(f"  Percentage  : {s['percentage']:.2f}%")
    print(f"  Grade       : {s['grade']}")
    print("-" * 40 + "\n")


def prompt_int(prompt_text: str, min_val: int = 1) -> int:
    """Prompts user for an integer with input validation."""
    while True:
        user_input = input(prompt_text).strip()
        try:
            val = int(user_input)
            if val < min_val:
                print(f"[!] Please enter a value >= {min_val}.")
                continue
            return val
        except ValueError:
            print("[!] Invalid input. Please enter a valid integer.")


def prompt_float(prompt_text: str, min_val: float = 0.0, max_val: float = 100.0) -> float:
    """Prompts user for a float within range [min_val, max_val]."""
    while True:
        user_input = input(prompt_text).strip()
        try:
            val = float(user_input)
            if val < min_val or val > max_val:
                print(f"[!] Please enter a mark between {min_val} and {max_val}.")
                continue
            return round(val, 2)
        except ValueError:
            print("[!] Invalid input. Please enter a numeric mark.")


def prompt_string(prompt_text: str) -> str:
    """Prompts user for a non-empty string."""
    while True:
        user_input = input(prompt_text).strip()
        if not user_input:
            print("[!] Value cannot be empty. Please try again.")
            continue
        return user_input


def handle_add_student() -> None:
    """Handles CLI workflow for adding a new student."""
    print_header("Add New Student Record")
    roll_no = prompt_int("Enter Roll Number: ")
    name = prompt_string("Enter Student Name: ")
    phy = prompt_float("Enter Physics Marks (0-100): ")
    chem = prompt_float("Enter Chemistry Marks (0-100): ")
    math = prompt_float("Enter Maths Marks (0-100): ")

    try:
        new_student = operations.add_student(roll_no, name, phy, chem, math)
        print("\n[+] Student record created successfully!")
        print_single_student_card(new_student)
    except ValueError as e:
        print(f"\n[X] Error: {e}")


def handle_view_all() -> None:
    """Handles displaying all student records in table format."""
    print_header("All Student Records")
    students = operations.view_all_students()
    print_student_table(students)


def handle_search_student() -> None:
    """Handles searching for a student record by roll number."""
    print_header("Search Student by Roll Number")
    roll_no = prompt_int("Enter Roll Number to search: ")
    student = operations.search_student(roll_no)
    if student:
        print_single_student_card(student)
    else:
        print(f"\n[!] Student with Roll Number {roll_no} not found.")


def handle_update_marks() -> None:
    """Handles updating marks for a student in a specific subject."""
    print_header("Update Student Marks")
    roll_no = prompt_int("Enter Roll Number of student to update: ")
    student = operations.search_student(roll_no)

    if not student:
        print(f"\n[!] Student with Roll Number {roll_no} not found.")
        return

    print(f"\nFound Student: {student['name']} (Roll: {student['roll_no']})")
    print(f"Current Marks -> Physics: {student['physics']}, Chemistry: {student['chemistry']}, Maths: {student['maths']}")

    print("\nSelect Subject to Update:")
    print("  1. Physics")
    print("  2. Chemistry")
    print("  3. Maths")

    choice = input("Enter choice (1-3): ").strip()
    subject_map = {"1": "physics", "2": "chemistry", "3": "maths"}

    if choice not in subject_map:
        print("[!] Invalid subject choice.")
        return

    subject = subject_map[choice]
    new_mark = prompt_float(f"Enter new {subject.capitalize()} marks (0-100): ")

    try:
        updated = operations.update_marks(roll_no, subject, new_mark)
        if updated:
            print("\n[+] Record updated successfully! Recalculated result:")
            print_single_student_card(updated)
        else:
            print("[!] Could not update record.")
    except ValueError as e:
        print(f"\n[X] Error: {e}")


def handle_delete_student() -> None:
    """Handles deleting a student record with confirmation."""
    print_header("Delete Student Record")
    roll_no = prompt_int("Enter Roll Number to delete: ")
    student = operations.search_student(roll_no)

    if not student:
        print(f"\n[!] Student with Roll Number {roll_no} not found.")
        return

    confirm = input(f"Are you sure you want to delete {student['name']} (Roll: {roll_no})? (y/N): ").strip().lower()
    if confirm == "y":
        success = operations.delete_student(roll_no)
        if success:
            print(f"\n[+] Student with Roll Number {roll_no} was successfully deleted.")
        else:
            print("\n[!] Failed to delete record.")
    else:
        print("\n[-] Deletion cancelled.")


def handle_class_summary() -> None:
    """Displays comprehensive class analytics and topper details."""
    print_header("Class Performance & Analytics Summary")
    summary = operations.get_class_summary()

    if summary["total_students"] == 0:
        print("\n[!] No student records in database to analyze.")
        return

    print(f"\n  Cohort Overview:")
    print(f"  ----------------")
    print(f"  Total Students Registered : {summary['total_students']}")
    print(f"  Class Average Percentage  : {summary['class_average_percentage']:.2f}%")

    if summary["highest_scorer"]:
        h = summary["highest_scorer"]
        print(f"\n  Highest Overall Scorer    : {h['name']} (Roll: {h['roll_no']}) - {h['percentage']:.2f}% ({h['grade']})")

    if summary["lowest_scorer"]:
        l = summary["lowest_scorer"]
        print(f"  Lowest Overall Scorer     : {l['name']} (Roll: {l['roll_no']}) - {l['percentage']:.2f}% ({l['grade']})")

    print(f"\n  Subject-wise Toppers:")
    print(f"  ---------------------")
    if summary["physics_topper"]:
        p = summary["physics_topper"]
        print(f"  Physics   : {p['name']} (Roll: {p['roll_no']}) with {p['physics']:.2f}/100")
    if summary["chemistry_topper"]:
        c = summary["chemistry_topper"]
        print(f"  Chemistry : {c['name']} (Roll: {c['roll_no']}) with {c['chemistry']:.2f}/100")
    if summary["maths_topper"]:
        m = summary["maths_topper"]
        print(f"  Maths     : {m['name']} (Roll: {m['roll_no']}) with {m['maths']:.2f}/100")

    print(f"\n  Grade Breakdown:")
    print(f"  ----------------")
    for grade, count in summary["grade_distribution"].items():
        bar = "#" * count
        print(f"  Grade {grade:<2} : {count:>2} student(s)  {bar}")
    print()


def handle_export_csv() -> None:
    """Handles CSV export of student records."""
    print_header("Export Records to CSV")
    default_filename = "student_records.csv"
    user_file = input(f"Enter target filename [default: {default_filename}]: ").strip()
    target_file = user_file if user_file else default_filename

    if not target_file.endswith(".csv"):
        target_file += ".csv"

    try:
        path = operations.export_to_csv(target_file)
        print(f"\n[+] Successfully exported records to:")
        print(f"    {path}")
    except Exception as e:
        print(f"\n[X] Export failed: {e}")


def display_menu() -> None:
    """Renders the main CLI menu options."""
    print("\n" + "=" * 45)
    print("   STUDENT MARKS & PERFORMANCE MANAGER")
    print("=" * 45)
    print("  1. Add New Student Record")
    print("  2. View All Student Records")
    print("  3. Search Student by Roll Number")
    print("  4. Update Student Marks")
    print("  5. Delete Student Record")
    print("  6. View Class Performance Summary")
    print("  7. Export Data to CSV")
    print("  8. Exit Application")
    print("=" * 45)


def main() -> None:
    """Main CLI execution loop."""
    # Ensure database is initialized on startup
    init_db()

    while True:
        display_menu()
        choice = input("Enter your choice (1-8): ").strip()

        if choice == "1":
            handle_add_student()
        elif choice == "2":
            handle_view_all()
        elif choice == "3":
            handle_search_student()
        elif choice == "4":
            handle_update_marks()
        elif choice == "5":
            handle_delete_student()
        elif choice == "6":
            handle_class_summary()
        elif choice == "7":
            handle_export_csv()
        elif choice == "8":
            print("\nThank you for using Student Marks Manager. Goodbye!\n")
            sys.exit(0)
        else:
            print("\n[!] Invalid choice! Please select a number between 1 and 8.")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
