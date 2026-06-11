"""
models.py - Data models for the Student Result Management System.
Uses Python dataclasses for clean, structured data representation.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Student:
    """Represents a student entity in the system."""
    roll_number: str
    name: str
    email: str = ""
    phone: str = ""
    class_name: str = ""
    id: Optional[int] = None
    created_at: Optional[str] = None

    def __str__(self):
        return f"{self.roll_number} - {self.name}"


@dataclass
class Marks:
    """
    Represents marks for a student across 5 subjects.
    Each subject has a maximum of 100 marks, total max = 500.
    Provides computed properties for total, percentage, grade, and pass/fail status.
    """
    student_id: int
    subject1: float = 0.0
    subject2: float = 0.0
    subject3: float = 0.0
    subject4: float = 0.0
    subject5: float = 0.0
    subject1_name: str = "Mathematics"
    subject2_name: str = "Science"
    subject3_name: str = "English"
    subject4_name: str = "History"
    subject5_name: str = "Computer Science"
    id: Optional[int] = None

    @property
    def total(self) -> float:
        """Calculate total marks across all 5 subjects (max 500)."""
        return self.subject1 + self.subject2 + self.subject3 + self.subject4 + self.subject5

    @property
    def percentage(self) -> float:
        """Calculate percentage based on total marks out of 500."""
        return round((self.total / 500) * 100, 2)

    @property
    def grade(self) -> str:
        """Assign grade automatically based on percentage thresholds."""
        p = self.percentage
        if p >= 90:
            return "A+"
        elif p >= 80:
            return "A"
        elif p >= 70:
            return "B+"
        elif p >= 60:
            return "B"
        elif p >= 50:
            return "C"
        elif p >= 40:
            return "D"
        else:
            return "F"

    @property
    def status(self) -> str:
        """Determine pass/fail. Student must score >= 33 in every subject to pass."""
        subjects = [self.subject1, self.subject2, self.subject3, self.subject4, self.subject5]
        if all(s >= 33 for s in subjects):
            return "PASS"
        return "FAIL"

    @property
    def subject_names(self) -> list:
        """Get ordered list of subject names."""
        return [
            self.subject1_name, self.subject2_name, self.subject3_name,
            self.subject4_name, self.subject5_name,
        ]

    @property
    def subject_marks(self) -> list:
        """Get ordered list of marks corresponding to subject_names."""
        return [self.subject1, self.subject2, self.subject3, self.subject4, self.subject5]

    def get_subjects_dict(self) -> dict:
        """Get a dictionary mapping each subject name to its marks."""
        return dict(zip(self.subject_names, self.subject_marks))
