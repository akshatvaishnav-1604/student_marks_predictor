"""
calculator.py - Business Logic & Performance Computations.

This module contains pure, reusable calculation functions for computing:
- Total Marks
- Percentage
- Grade Mapping based on percentage tiers
- Class-level Aggregate Analytics (Averages, High/Low scorers, Subject toppers)
"""

from typing import Any, Dict, List, Optional


def calculate_total(physics: float, chemistry: float, maths: float) -> float:
    """
    Computes total marks across three subjects.

    Args:
        physics (float): Physics mark (0-100).
        chemistry (float): Chemistry mark (0-100).
        maths (float): Maths mark (0-100).

    Returns:
        float: Rounded sum of marks to 2 decimal places.
    """
    return round(float(physics) + float(chemistry) + float(maths), 2)


def calculate_percentage(total: float, max_marks: float = 300.0) -> float:
    """
    Computes percentage based on total marks obtained and maximum marks.

    Args:
        total (float): Sum of marks obtained.
        max_marks (float, optional): Maximum possible total marks. Defaults to 300.0.

    Returns:
        float: Percentage rounded to 2 decimal places.

    Raises:
        ValueError: If max_marks is <= 0.
    """
    if max_marks <= 0:
        raise ValueError("Maximum marks must be greater than 0.")
    percentage = (total / max_marks) * 100.0
    return round(percentage, 2)


def calculate_grade(percentage: float) -> str:
    """
    Maps percentage score to corresponding letter grade.

    Grading Scale:
        - 90.00% to 100.00% : 'A+'
        - 80.00% to 89.99%  : 'A'
        - 70.00% to 79.99%  : 'B'
        - 60.00% to 69.99%  : 'C'
        - 50.00% to 59.99%  : 'D'
        - Below 50.00%      : 'F'

    Args:
        percentage (float): Student percentage.

    Returns:
        str: Grade letter ('A+', 'A', 'B', 'C', 'D', 'F').
    """
    if percentage >= 90.0:
        return "A+"
    elif percentage >= 80.0:
        return "A"
    elif percentage >= 70.0:
        return "B"
    elif percentage >= 60.0:
        return "C"
    elif percentage >= 50.0:
        return "D"
    else:
        return "F"


def compute_class_analytics(students: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes summary metrics for an entire cohort/class of students.

    Args:
        students (List[Dict[str, Any]]): List of student records (each record as a dict).

    Returns:
        Dict[str, Any]: Dictionary containing class metrics:
            - total_students (int)
            - class_average_percentage (float)
            - highest_scorer (dict or None)
            - lowest_scorer (dict or None)
            - physics_topper (dict or None)
            - chemistry_topper (dict or None)
            - maths_topper (dict or None)
            - grade_distribution (dict)
    """
    if not students:
        return {
            "total_students": 0,
            "class_average_percentage": 0.0,
            "highest_scorer": None,
            "lowest_scorer": None,
            "physics_topper": None,
            "chemistry_topper": None,
            "maths_topper": None,
            "grade_distribution": {"A+": 0, "A": 0, "B": 0, "C": 0, "D": 0, "F": 0},
        }

    total_count = len(students)
    total_percentage_sum = sum(s["percentage"] for s in students)
    class_average = round(total_percentage_sum / total_count, 2)

    # Find highest & lowest scorers by percentage / total
    highest_scorer = max(students, key=lambda s: s["percentage"])
    lowest_scorer = min(students, key=lambda s: s["percentage"])

    # Find subject toppers
    physics_topper = max(students, key=lambda s: s["physics"])
    chemistry_topper = max(students, key=lambda s: s["chemistry"])
    maths_topper = max(students, key=lambda s: s["maths"])

    # Grade distribution count
    grade_distribution = {"A+": 0, "A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    for s in students:
        g = s.get("grade", "F")
        if g in grade_distribution:
            grade_distribution[g] += 1
        else:
            grade_distribution[g] = 1

    return {
        "total_students": total_count,
        "class_average_percentage": class_average,
        "highest_scorer": highest_scorer,
        "lowest_scorer": lowest_scorer,
        "physics_topper": physics_topper,
        "chemistry_topper": chemistry_topper,
        "maths_topper": maths_topper,
        "grade_distribution": grade_distribution,
    }
