"""
operations.py - Database Operations & CRUD Business Logic.

This module provides functions to:
- Add a new student record with input validation
- View all student records
- Search student by roll number
- Update student marks in a specific subject
- Delete student record
- Export student records to a CSV file
- Retrieve class performance metrics
"""

import csv
import os
import sqlite3
from typing import Any, Dict, List, Optional

from database import DEFAULT_DB_NAME, get_db_connection, init_db
import calculator

VALID_SUBJECTS = ("physics", "chemistry", "maths")


def validate_marks(mark: float, subject_name: str = "Subject") -> float:
    """
    Validates that a given subject mark is a number within [0, 100].

    Args:
        mark (float): Mark obtained.
        subject_name (str): Name of subject for error messages.

    Returns:
        float: Validated mark.

    Raises:
        ValueError: If mark is less than 0 or greater than 100.
    """
    try:
        val = float(mark)
    except (TypeError, ValueError):
        raise ValueError(f"{subject_name} marks must be a valid number.")

    if val < 0.0 or val > 100.0:
        raise ValueError(f"{subject_name} marks must be between 0 and 100. Received: {val}")
    return round(val, 2)


def validate_roll_no(roll_no: int) -> int:
    """
    Validates that roll number is a positive integer.

    Args:
        roll_no (int): Roll number.

    Returns:
        int: Validated roll number.

    Raises:
        ValueError: If roll number is not a positive integer.
    """
    try:
        val = int(roll_no)
    except (TypeError, ValueError):
        raise ValueError("Roll number must be an integer.")

    if val <= 0:
        raise ValueError("Roll number must be a positive integer greater than 0.")
    return val


def validate_name(name: str) -> str:
    """
    Validates student name.

    Args:
        name (str): Student full name.

    Returns:
        str: Stripped student name.

    Raises:
        ValueError: If name is empty or contains only whitespace.
    """
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Student name cannot be empty.")
    return name.strip()


def row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    """Helper function to convert sqlite3.Row to a standard Python dictionary."""
    return {
        "roll_no": row["roll_no"],
        "name": row["name"],
        "physics": row["physics"],
        "chemistry": row["chemistry"],
        "maths": row["maths"],
        "total": row["total"],
        "percentage": row["percentage"],
        "grade": row["grade"],
    }


def add_student(
    roll_no: int,
    name: str,
    phy: float,
    chem: float,
    math: float,
    db_name: str = DEFAULT_DB_NAME,
) -> Dict[str, Any]:
    """
    Validates inputs, calculates total/percentage/grade, and inserts student record.

    Args:
        roll_no (int): Unique roll number.
        name (str): Student name.
        phy (float): Physics marks (0-100).
        chem (float): Chemistry marks (0-100).
        math (float): Maths marks (0-100).
        db_name (str): Database file path.

    Returns:
        Dict[str, Any]: Newly created student record.

    Raises:
        ValueError: If validation fails or roll number already exists.
    """
    init_db(db_name)

    # Input validations
    v_roll_no = validate_roll_no(roll_no)
    v_name = validate_name(name)
    v_phy = validate_marks(phy, "Physics")
    v_chem = validate_marks(chem, "Chemistry")
    v_math = validate_marks(math, "Maths")

    # Computations
    total = calculator.calculate_total(v_phy, v_chem, v_math)
    percentage = calculator.calculate_percentage(total, max_marks=300.0)
    grade = calculator.calculate_grade(percentage)

    insert_query = """
    INSERT INTO students (roll_no, name, physics, chemistry, maths, total, percentage, grade)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """

    try:
        with get_db_connection(db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                insert_query,
                (v_roll_no, v_name, v_phy, v_chem, v_math, total, percentage, grade),
            )
            conn.commit()
    except sqlite3.IntegrityError:
        raise ValueError(f"Student with Roll Number '{v_roll_no}' already exists.")

    return {
        "roll_no": v_roll_no,
        "name": v_name,
        "physics": v_phy,
        "chemistry": v_chem,
        "maths": v_math,
        "total": total,
        "percentage": percentage,
        "grade": grade,
    }


def view_all_students(db_name: str = DEFAULT_DB_NAME) -> List[Dict[str, Any]]:
    """
    Fetches all student records ordered by roll number.

    Args:
        db_name (str): Database file path.

    Returns:
        List[Dict[str, Any]]: List of all student records.
    """
    init_db(db_name)
    query = "SELECT * FROM students ORDER BY roll_no ASC;"
    with get_db_connection(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        return [row_to_dict(row) for row in rows]


def search_student(roll_no: int, db_name: str = DEFAULT_DB_NAME) -> Optional[Dict[str, Any]]:
    """
    Searches for a student by roll number.

    Args:
        roll_no (int): Roll number to search.
        db_name (str): Database file path.

    Returns:
        Optional[Dict[str, Any]]: Student record dictionary if found, else None.
    """
    init_db(db_name)
    v_roll_no = validate_roll_no(roll_no)
    query = "SELECT * FROM students WHERE roll_no = ?;"
    with get_db_connection(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (v_roll_no,))
        row = cursor.fetchone()
        return row_to_dict(row) if row else None


def update_marks(
    roll_no: int,
    subject: str,
    new_mark: float,
    db_name: str = DEFAULT_DB_NAME,
) -> Optional[Dict[str, Any]]:
    """
    Updates the marks of a specific subject for a student and recalculates metrics.

    Args:
        roll_no (int): Student roll number.
        subject (str): Subject name ('physics', 'chemistry', or 'maths').
        new_mark (float): New marks to update (0-100).
        db_name (str): Database file path.

    Returns:
        Optional[Dict[str, Any]]: Updated student record, or None if student not found.

    Raises:
        ValueError: If subject is invalid or marks are out of bounds.
    """
    normalized_subject = subject.strip().lower()
    if normalized_subject not in VALID_SUBJECTS:
        raise ValueError(
            f"Invalid subject '{subject}'. Allowed subjects: {', '.join(VALID_SUBJECTS)}"
        )

    v_new_mark = validate_marks(new_mark, normalized_subject.capitalize())
    current_student = search_student(roll_no, db_name=db_name)

    if not current_student:
        return None

    # Update the target subject mark in memory to recalculate total, %, and grade
    phy = v_new_mark if normalized_subject == "physics" else current_student["physics"]
    chem = v_new_mark if normalized_subject == "chemistry" else current_student["chemistry"]
    math = v_new_mark if normalized_subject == "maths" else current_student["maths"]

    new_total = calculator.calculate_total(phy, chem, math)
    new_percentage = calculator.calculate_percentage(new_total, max_marks=300.0)
    new_grade = calculator.calculate_grade(new_percentage)

    update_query = f"""
    UPDATE students
    SET {normalized_subject} = ?, total = ?, percentage = ?, grade = ?
    WHERE roll_no = ?;
    """

    with get_db_connection(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute(
            update_query,
            (v_new_mark, new_total, new_percentage, new_grade, roll_no),
        )
        conn.commit()

    return {
        "roll_no": roll_no,
        "name": current_student["name"],
        "physics": phy,
        "chemistry": chem,
        "maths": math,
        "total": new_total,
        "percentage": new_percentage,
        "grade": new_grade,
    }


def delete_student(roll_no: int, db_name: str = DEFAULT_DB_NAME) -> bool:
    """
    Deletes a student record by roll number.

    Args:
        roll_no (int): Roll number of student to delete.
        db_name (str): Database file path.

    Returns:
        bool: True if record was found and deleted, False otherwise.
    """
    init_db(db_name)
    v_roll_no = validate_roll_no(roll_no)
    query = "DELETE FROM students WHERE roll_no = ?;"
    with get_db_connection(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (v_roll_no,))
        conn.commit()
        return cursor.rowcount > 0


def export_to_csv(filename: str = "student_records.csv", db_name: str = DEFAULT_DB_NAME) -> str:
    """
    Exports all student records to a CSV file.

    Args:
        filename (str): Target CSV filename.
        db_name (str): Database file path.

    Returns:
        str: The path to the created CSV file.
    """
    records = view_all_students(db_name=db_name)
    fieldnames = ["roll_no", "name", "physics", "chemistry", "maths", "total", "percentage", "grade"]

    with open(filename, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for rec in records:
            writer.writerow(rec)

    return os.path.abspath(filename)


def get_class_summary(db_name: str = DEFAULT_DB_NAME) -> Dict[str, Any]:
    """
    Retrieves all students and computes class-level analytics.

    Args:
        db_name (str): Database file path.

    Returns:
        Dict[str, Any]: Computed class analytics summary.
    """
    records = view_all_students(db_name=db_name)
    return calculator.compute_class_analytics(records)
