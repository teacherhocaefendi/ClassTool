from dataclasses import dataclass
from typing import Optional

# ==========================================
# SQL SCHEMA DEFINITION
# ==========================================
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS Classes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    academic_year TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id INTEGER,
    student_number TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    gender TEXT,
    seat_row INTEGER DEFAULT 0,
    seat_column INTEGER DEFAULT 0,
    selection_count INTEGER DEFAULT 0,
    FOREIGN KEY(class_id) REFERENCES Classes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS StudentProfiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER UNIQUE,
    sociability_score INTEGER DEFAULT 3,
    focus_score INTEGER DEFAULT 3,
    participation_score INTEGER DEFAULT 3,
    personality_tags TEXT,
    teacher_notes TEXT,
    FOREIGN KEY(student_id) REFERENCES Students(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    type TEXT, -- e.g., '+' or '-'
    category_tag TEXT,
    comment TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(student_id) REFERENCES Students(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS GroupHistory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id INTEGER,
    group_structure_json TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(class_id) REFERENCES Classes(id) ON DELETE CASCADE
);
"""

# ==========================================
# DATA MODELS
# ==========================================
@dataclass
class ClassModel:
    name: str
    academic_year: str
    id: Optional[int] = None

@dataclass
class StudentModel:
    class_id: int
    student_number: str
    first_name: str
    last_name: str
    gender: str
    seat_row: int = 0
    seat_column: int = 0
    selection_count: int = 0
    id: Optional[int] = None

@dataclass
class StudentProfileModel:
    student_id: int
    sociability_score: int = 3
    focus_score: int = 3
    participation_score: int = 3
    personality_tags: str = ""
    teacher_notes: str = ""
    id: Optional[int] = None