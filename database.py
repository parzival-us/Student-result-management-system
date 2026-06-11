"""
database.py - SQLite database operations for the Student Result Management System.
Handles all CRUD operations for students and marks tables with proper
foreign key relationships and error handling.
"""

import sqlite3
import os
from typing import List, Optional, Tuple
from models import Student, Marks


class Database:
    """SQLite database manager with full CRUD support for students and marks."""

    def __init__(self, db_path: str = None):
        """
        Initialize the database connection and create tables.
        
        Args:
            db_path: Path to the SQLite database file. If None, defaults to
                     'students.db' in the same directory as this script.
        """
        if db_path is None:
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "students.db")
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.connection.cursor()
        self._create_tables()

    def _create_tables(self):
        """Create the students and marks tables if they don't already exist."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                roll_number TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                email TEXT DEFAULT '',
                phone TEXT DEFAULT '',
                class_name TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS marks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL UNIQUE,
                subject1 REAL DEFAULT 0,
                subject2 REAL DEFAULT 0,
                subject3 REAL DEFAULT 0,
                subject4 REAL DEFAULT 0,
                subject5 REAL DEFAULT 0,
                subject1_name TEXT DEFAULT 'Mathematics',
                subject2_name TEXT DEFAULT 'Science',
                subject3_name TEXT DEFAULT 'English',
                subject4_name TEXT DEFAULT 'History',
                subject5_name TEXT DEFAULT 'Computer Science',
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
            )
        """)
        self.connection.commit()

    # ═══════════════════════════════════════════════════════════════
    #  Student CRUD Operations
    # ═══════════════════════════════════════════════════════════════

    def add_student(self, student: Student) -> int:
        """
        Add a new student to the database.
        
        Args:
            student: Student object with roll_number, name, and optional fields.
            
        Returns:
            The auto-generated ID of the new student.
            
        Raises:
            ValueError: If the roll number already exists.
        """
        try:
            self.cursor.execute(
                "INSERT INTO students (roll_number, name, email, phone, class_name) VALUES (?, ?, ?, ?, ?)",
                (student.roll_number, student.name, student.email, student.phone, student.class_name)
            )
            self.connection.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            raise ValueError(f"Roll number '{student.roll_number}' already exists.")

    def update_student(self, student: Student):
        """
        Update an existing student's information.
        
        Args:
            student: Student object with updated fields. Must have a valid id.
            
        Raises:
            ValueError: If the new roll number conflicts with another student.
        """
        try:
            self.cursor.execute(
                "UPDATE students SET roll_number=?, name=?, email=?, phone=?, class_name=? WHERE id=?",
                (student.roll_number, student.name, student.email, student.phone,
                 student.class_name, student.id)
            )
            self.connection.commit()
        except sqlite3.IntegrityError:
            raise ValueError(f"Roll number '{student.roll_number}' already belongs to another student.")

    def delete_student(self, student_id: int):
        """Delete a student and their marks (via foreign key CASCADE)."""
        self.cursor.execute("DELETE FROM students WHERE id=?", (student_id,))
        self.connection.commit()

    def get_student_by_id(self, student_id: int) -> Optional[Student]:
        """Retrieve a single student by their database ID."""
        self.cursor.execute("SELECT * FROM students WHERE id=?", (student_id,))
        row = self.cursor.fetchone()
        return self._row_to_student(row) if row else None

    def get_student_by_roll(self, roll_number: str) -> Optional[Student]:
        """Search for a student by their unique roll number."""
        self.cursor.execute("SELECT * FROM students WHERE roll_number=?", (roll_number,))
        row = self.cursor.fetchone()
        return self._row_to_student(row) if row else None

    def get_all_students(self) -> List[Student]:
        """Retrieve all students, ordered alphabetically by name."""
        self.cursor.execute("SELECT * FROM students ORDER BY name ASC")
        return [self._row_to_student(row) for row in self.cursor.fetchall()]

    def search_students(self, query: str) -> List[Student]:
        """
        Search students by partial match on name or roll number.
        
        Args:
            query: The search string (case-insensitive partial match).
        """
        like = f"%{query}%"
        self.cursor.execute(
            "SELECT * FROM students WHERE name LIKE ? OR roll_number LIKE ? ORDER BY name ASC",
            (like, like)
        )
        return [self._row_to_student(row) for row in self.cursor.fetchall()]

    # ═══════════════════════════════════════════════════════════════
    #  Marks CRUD Operations
    # ═══════════════════════════════════════════════════════════════

    def add_marks(self, marks: Marks):
        """
        Add marks for a student. Each student can have only one marks record.
        
        Raises:
            ValueError: If marks already exist for this student.
        """
        try:
            self.cursor.execute("""
                INSERT INTO marks (student_id, subject1, subject2, subject3, subject4, subject5,
                                  subject1_name, subject2_name, subject3_name, subject4_name, subject5_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (marks.student_id, marks.subject1, marks.subject2, marks.subject3,
                  marks.subject4, marks.subject5, marks.subject1_name, marks.subject2_name,
                  marks.subject3_name, marks.subject4_name, marks.subject5_name))
            self.connection.commit()
        except sqlite3.IntegrityError:
            raise ValueError("Marks already exist for this student. Use update_marks() instead.")

    def update_marks(self, marks: Marks):
        """Update the marks record for a given student."""
        self.cursor.execute("""
            UPDATE marks SET subject1=?, subject2=?, subject3=?, subject4=?, subject5=?,
                           subject1_name=?, subject2_name=?, subject3_name=?, subject4_name=?, subject5_name=?
            WHERE student_id=?
        """, (marks.subject1, marks.subject2, marks.subject3, marks.subject4, marks.subject5,
              marks.subject1_name, marks.subject2_name, marks.subject3_name, marks.subject4_name,
              marks.subject5_name, marks.student_id))
        self.connection.commit()

    def get_marks(self, student_id: int) -> Optional[Marks]:
        """Retrieve marks for a specific student, or None if no marks exist."""
        self.cursor.execute("SELECT * FROM marks WHERE student_id=?", (student_id,))
        row = self.cursor.fetchone()
        return self._row_to_marks(row) if row else None

    def get_all_marks(self) -> List[Marks]:
        """Retrieve all marks records."""
        self.cursor.execute("SELECT * FROM marks")
        return [self._row_to_marks(row) for row in self.cursor.fetchall()]

    # ═══════════════════════════════════════════════════════════════
    #  Statistics & Rankings
    # ═══════════════════════════════════════════════════════════════

    def get_student_count(self) -> int:
        """Return the total number of registered students."""
        self.cursor.execute("SELECT COUNT(*) FROM students")
        return self.cursor.fetchone()[0]

    def get_pass_fail_counts(self) -> Tuple[int, int]:
        """Return a tuple of (pass_count, fail_count)."""
        all_marks = self.get_all_marks()
        passed = sum(1 for m in all_marks if m.status == "PASS")
        return passed, len(all_marks) - passed

    def get_grade_distribution(self) -> dict:
        """Return a dict of {grade: count} for all students with marks."""
        all_marks = self.get_all_marks()
        dist = {"A+": 0, "A": 0, "B+": 0, "B": 0, "C": 0, "D": 0, "F": 0}
        for m in all_marks:
            dist[m.grade] = dist.get(m.grade, 0) + 1
        return dist

    def get_subject_averages(self) -> dict:
        """Return a dict of {subject_name: average_marks} across all students."""
        self.cursor.execute("""
            SELECT AVG(subject1), AVG(subject2), AVG(subject3), AVG(subject4), AVG(subject5),
                   subject1_name, subject2_name, subject3_name, subject4_name, subject5_name
            FROM marks
        """)
        row = self.cursor.fetchone()
        if row and row[0] is not None:
            return {
                row[5]: round(row[0], 1), row[6]: round(row[1], 1),
                row[7]: round(row[2], 1), row[8]: round(row[3], 1),
                row[9]: round(row[4], 1),
            }
        return {}

    def get_average_percentage(self) -> float:
        """Calculate the overall average percentage across all students."""
        all_marks = self.get_all_marks()
        if not all_marks:
            return 0.0
        return round(sum(m.percentage for m in all_marks) / len(all_marks), 2)

    def get_ranked_students(self) -> List[Tuple[Student, Marks, int]]:
        """
        Get all students with marks, ranked by total marks (descending).
        
        Returns:
            List of (Student, Marks, rank) tuples.
        """
        self.cursor.execute("""
            SELECT s.id, s.roll_number, s.name, s.email, s.phone, s.class_name, s.created_at,
                   m.id, m.student_id, m.subject1, m.subject2, m.subject3, m.subject4, m.subject5,
                   m.subject1_name, m.subject2_name, m.subject3_name, m.subject4_name, m.subject5_name
            FROM students s
            JOIN marks m ON s.id = m.student_id
            ORDER BY (m.subject1 + m.subject2 + m.subject3 + m.subject4 + m.subject5) DESC
        """)
        results = []
        for rank, row in enumerate(self.cursor.fetchall(), start=1):
            student = Student(
                id=row[0], roll_number=row[1], name=row[2], email=row[3],
                phone=row[4], class_name=row[5], created_at=row[6],
            )
            marks = Marks(
                id=row[7], student_id=row[8],
                subject1=row[9], subject2=row[10], subject3=row[11],
                subject4=row[12], subject5=row[13],
                subject1_name=row[14], subject2_name=row[15], subject3_name=row[16],
                subject4_name=row[17], subject5_name=row[18],
            )
            results.append((student, marks, rank))
        return results

    def get_top_performer(self) -> Optional[Tuple[Student, Marks]]:
        """Get the student with the highest total marks, or None."""
        ranked = self.get_ranked_students()
        if ranked:
            return ranked[0][0], ranked[0][1]
        return None

    # ═══════════════════════════════════════════════════════════════
    #  Internal Helpers
    # ═══════════════════════════════════════════════════════════════

    @staticmethod
    def _row_to_student(row) -> Student:
        """Map a raw database row tuple to a Student dataclass instance."""
        return Student(
            id=row[0], roll_number=row[1], name=row[2],
            email=row[3], phone=row[4], class_name=row[5], created_at=row[6],
        )

    @staticmethod
    def _row_to_marks(row) -> Marks:
        """Map a raw database row tuple to a Marks dataclass instance."""
        return Marks(
            id=row[0], student_id=row[1],
            subject1=row[2], subject2=row[3], subject3=row[4],
            subject4=row[5], subject5=row[6],
            subject1_name=row[7], subject2_name=row[8],
            subject3_name=row[9], subject4_name=row[10], subject5_name=row[11],
        )

    def close(self):
        """Safely close the database connection."""
        if self.connection:
            self.connection.close()
