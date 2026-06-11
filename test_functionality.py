#!/usr/bin/env python3
"""
Test script to validate Student Result Management System core functionality.
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import Database
from models import Student, Marks

def test_database_operations():
    """Test basic database operations."""
    print("\n=== Testing Database Operations ===\n")

    # Use a test database
    db_path = "test_students.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    db = Database(db_path=db_path)
    print("[OK] Database initialized")

    # Test adding a student
    student = Student(roll_number="CS001", name="Alice Smith", email="alice@example.com", phone="9876543210", class_name="10-A")
    sid = db.add_student(student)
    print(f"[OK] Student added with ID: {sid}")

    # Test adding marks
    marks = Marks(sid, 85, 92, 78, 88, 90)
    db.add_marks(marks)
    print(f"[OK] Marks added")

    # Test retrieving student
    retrieved = db.get_student_by_id(sid)
    print(f"[OK] Retrieved student: {retrieved.name}")

    # Test retrieving marks
    retrieved_marks = db.get_marks(sid)
    print(f"[OK] Total: {retrieved_marks.total}, Grade: {retrieved_marks.grade}, Status: {retrieved_marks.status}")

    # Test statistics
    count = db.get_student_count()
    print(f"[OK] Total students: {count}")

    pass_count, fail_count = db.get_pass_fail_counts()
    print(f"[OK] Pass: {pass_count}, Fail: {fail_count}")

    avg = db.get_average_percentage()
    print(f"[OK] Average percentage: {avg}%")

    # Test ranking
    ranked = db.get_ranked_students()
    print(f"[OK] Ranked students: {len(ranked)}")

    # Test add another student who fails
    student2 = Student(roll_number="CS002", name="Bob Jones", email="bob@example.com", class_name="10-A")
    sid2 = db.add_student(student2)
    marks2 = Marks(sid2, 25, 30, 32, 28, 29)  # Will fail
    db.add_marks(marks2)
    print(f"[OK] Added failing student")

    # Test grade distribution
    dist = db.get_grade_distribution()
    print(f"[OK] Grade distribution: {dist}")

    # Test subject averages
    averages = db.get_subject_averages()
    print(f"[OK] Subject averages: {averages}")

    db.close()
    os.remove(db_path)
    print(f"\n[OK] All tests passed!")

if __name__ == "__main__":
    try:
        test_database_operations()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
