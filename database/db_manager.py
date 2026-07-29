import sqlite3
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_PATH, DB_ENCRYPTION_KEY
from utils.crypto import decrypt_file, encrypt_file


class DBManager:
    def __init__(self):
        self.db_path = str(DB_PATH)
        self.key = DB_ENCRYPTION_KEY

    def unlock_database(self):
        """Dosya diskte kilitliyse (AES şifreliyse) kilidini açar."""
        if os.path.exists(self.db_path):
            decrypt_file(self.db_path, self.key)

    def lock_database(self):
        """Uygulama kapanırken veritabanı dosyasını diskte AES ile şifreler."""
        if os.path.exists(self.db_path):
            encrypt_file(self.db_path, self.key)

    def get_connection(self):
        try:
            # Bağlantı kurmadan önce kilidin açık olduğundan emin ol
            self.unlock_database()

            conn = sqlite3.connect(self.db_path, timeout=10)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            print(f"Database Connection Error: {e}")
            raise

    def initialize_database(self):
        # KRİTİK DÜZELTME: İlk tablo denetimi yapılmadan önce dosyanın kilidini aç!
        self.unlock_database()

        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS classes
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               name
                               TEXT
                               NOT
                               NULL,
                               academic_year
                               TEXT
                               NOT
                               NULL
                           )
                           """)

            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS students
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               class_id
                               INTEGER
                               NOT
                               NULL,
                               student_number
                               TEXT
                               NOT
                               NULL,
                               first_name
                               TEXT
                               NOT
                               NULL,
                               last_name
                               TEXT
                               NOT
                               NULL,
                               gender
                               TEXT
                               NOT
                               NULL,
                               seat_row
                               INTEGER
                               DEFAULT
                               0,
                               seat_column
                               INTEGER
                               DEFAULT
                               0,
                               selection_count
                               INTEGER
                               DEFAULT
                               0,
                               FOREIGN
                               KEY
                           (
                               class_id
                           ) REFERENCES classes
                           (
                               id
                           )
                               )
                           """)

            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS student_profiles
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               student_id
                               INTEGER
                               NOT
                               NULL,
                               sociability_score
                               INTEGER,
                               focus_score
                               INTEGER,
                               participation_score
                               INTEGER,
                               personality_tags
                               TEXT,
                               teacher_notes
                               TEXT,
                               FOREIGN
                               KEY
                           (
                               student_id
                           ) REFERENCES students
                           (
                               id
                           )
                               )
                           """)

            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS logs
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               student_id
                               INTEGER
                               NOT
                               NULL,
                               log_type
                               TEXT
                               NOT
                               NULL,
                               category_tag
                               TEXT
                               NOT
                               NULL,
                               comment
                               TEXT,
                               created_at
                               DATETIME
                               DEFAULT
                               CURRENT_TIMESTAMP,
                               FOREIGN
                               KEY
                           (
                               student_id
                           ) REFERENCES students
                           (
                               id
                           )
                               )
                           """)

            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS group_history
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               class_id
                               INTEGER
                               NOT
                               NULL,
                               group_structure_json
                               TEXT
                               NOT
                               NULL,
                               created_at
                               DATETIME
                               DEFAULT
                               CURRENT_TIMESTAMP,
                               FOREIGN
                               KEY
                           (
                               class_id
                           ) REFERENCES classes
                           (
                               id
                           )
                               )
                           """)

            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS homeworks
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               class_id
                               INTEGER
                               NOT
                               NULL,
                               title
                               TEXT
                               NOT
                               NULL,
                               due_date
                               DATE
                               NOT
                               NULL,
                               created_at
                               DATETIME
                               DEFAULT
                               CURRENT_TIMESTAMP,
                               FOREIGN
                               KEY
                           (
                               class_id
                           ) REFERENCES classes
                           (
                               id
                           )
                               )
                           """)

            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS homework_checks
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               homework_id
                               INTEGER
                               NOT
                               NULL,
                               student_id
                               INTEGER
                               NOT
                               NULL,
                               status
                               TEXT
                               NOT
                               NULL,
                               FOREIGN
                               KEY
                           (
                               homework_id
                           ) REFERENCES homeworks
                           (
                               id
                           ),
                               FOREIGN KEY
                           (
                               student_id
                           ) REFERENCES students
                           (
                               id
                           )
                               )
                           """)

            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS seating_layouts
                           (
                               class_id
                               INTEGER
                               PRIMARY
                               KEY,
                               layout_json
                               TEXT
                               NOT
                               NULL
                           )
                           """)

            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS app_settings
                           (
                               key
                               TEXT
                               PRIMARY
                               KEY,
                               value
                               TEXT
                           )
                           """)

            conn.commit()

    def add_class(self, name, academic_year):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO classes (name, academic_year) VALUES (?, ?)", (name, academic_year))
            conn.commit()
            return cursor.lastrowid

    def get_classes(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, academic_year FROM classes ORDER BY name")
            return cursor.fetchall()

    def get_students(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, student_number, first_name, last_name, gender FROM students")
            return cursor.fetchall()

    def add_student(self, class_id, student_number, first_name, last_name, gender):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                           INSERT INTO students (class_id, student_number, first_name, last_name, gender, seat_row,
                                                 seat_column)
                           VALUES (?, ?, ?, ?, ?, 0, 0)
                           """, (class_id, student_number, first_name, last_name, gender))
            conn.commit()

    def add_multiple_students(self, class_id, students_data):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            insert_query = """
                           INSERT INTO students (class_id, student_number, first_name, last_name, gender, seat_row, \
                                                 seat_column)
                           VALUES (?, ?, ?, ?, ?, 0, 0) \
                           """
            data_to_insert = [
                (class_id, s['number'], s['first_name'], s['last_name'], s['gender'])
                for s in students_data
            ]
            cursor.executemany(insert_query, data_to_insert)
            conn.commit()

    def delete_student(self, student_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
            conn.commit()

    def delete_class(self, class_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM students WHERE class_id = ?", (class_id,))
            cursor.execute("DELETE FROM classes WHERE id = ?", (class_id,))
            conn.commit()

    def update_student(self, student_id, student_number, first_name, last_name, gender):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                           UPDATE students
                           SET student_number = ?,
                               first_name     = ?,
                               last_name      = ?,
                               gender         = ?
                           WHERE id = ?
                           """, (student_number, first_name, last_name, gender, student_id))
            conn.commit()

    def get_student_profile(self, student_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM student_profiles WHERE student_id = ?", (student_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)

            cursor.execute("""
                           INSERT INTO student_profiles (student_id, sociability_score, focus_score,
                                                         participation_score, personality_tags, teacher_notes)
                           VALUES (?, 3, 3, 3, '', '')
                           """, (student_id,))
            conn.commit()
            return {
                "student_id": student_id, "sociability_score": 3,
                "focus_score": 3, "participation_score": 3,
                "personality_tags": "", "teacher_notes": ""
            }

    def update_student_profile(self, student_id, soc, foc, part, tags, notes):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                           UPDATE student_profiles
                           SET sociability_score   = ?,
                               focus_score         = ?,
                               participation_score = ?,
                               personality_tags    = ?,
                               teacher_notes       = ?
                           WHERE student_id = ?
                           """, (soc, foc, part, tags, notes, student_id))
            conn.commit()

    def get_all_logs(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT student_id, log_type, category_tag FROM logs")
            return cursor.fetchall()

    def add_log_entry(self, student_id, log_type, category_tag, comment=""):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO logs (student_id, log_type, category_tag, comment) VALUES (?, ?, ?, ?)",
                           (student_id, log_type, category_tag, comment))
            conn.commit()

    def get_eligible_students(self, class_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT MIN(selection_count) as min_count FROM students WHERE class_id = ?", (class_id,))
            min_row = cursor.fetchone()
            if not min_row or min_row['min_count'] is None:
                return []
            cursor.execute("""
                           SELECT id, first_name, last_name, selection_count
                           FROM students
                           WHERE class_id = ?
                             AND selection_count = ?
                           """, (class_id, min_row['min_count']))
            return cursor.fetchall()

    def increment_selection_count(self, student_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE students SET selection_count = selection_count + 1 WHERE id = ?", (student_id,))
            conn.commit()

    def add_homework(self, class_id, title, due_date):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO homeworks (class_id, title, due_date) VALUES (?, ?, ?)",
                           (class_id, title, due_date))
            conn.commit()
            return cursor.lastrowid

    def get_todays_homeworks(self):
        import datetime
        today = datetime.date.today().strftime("%Y-%m-%d")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                           SELECT h.id, h.title, h.due_date, c.name as class_name, h.class_id
                           FROM homeworks h
                                    JOIN classes c ON h.class_id = c.id
                           WHERE h.due_date = ?
                           """, (today,))
            return cursor.fetchall()

    def save_homework_checks(self, homework_id, checks_data):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for check in checks_data:
                cursor.execute("INSERT INTO homework_checks (homework_id, student_id, status) VALUES (?, ?, ?)",
                               (homework_id, check['student_id'], check['status']))
            conn.commit()

    def save_seating_layout(self, class_id, layout_name, layout_json):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # seating_layouts tablosunu kontrol et ve name sütununu destekle
            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS seating_layouts_v2
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               class_id
                               INTEGER
                               NOT
                               NULL,
                               layout_name
                               TEXT
                               NOT
                               NULL,
                               layout_json
                               TEXT
                               NOT
                               NULL,
                               UNIQUE
                           (
                               class_id,
                               layout_name
                           )
                               )
                           """)
            cursor.execute("""
                           INSERT INTO seating_layouts_v2 (class_id, layout_name, layout_json)
                           VALUES (?, ?, ?) ON CONFLICT(class_id, layout_name) DO
                           UPDATE SET layout_json = excluded.layout_json
                           """, (class_id, layout_name, layout_json))
            conn.commit()

    def get_seating_layouts(self, class_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS seating_layouts_v2
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               class_id
                               INTEGER
                               NOT
                               NULL,
                               layout_name
                               TEXT
                               NOT
                               NULL,
                               layout_json
                               TEXT
                               NOT
                               NULL,
                               UNIQUE
                           (
                               class_id,
                               layout_name
                           )
                               )
                           """)
            cursor.execute("SELECT layout_name, layout_json FROM seating_layouts_v2 WHERE class_id = ?", (class_id,))
            return cursor.fetchall()

    def save_oral_grade_weights(self, class_id, oral_index, hw_weight, part_weight, beh_weight):
        """1., 2. veya 3. sözlü notu için ağırlık yüzdelerini kaydeder."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS oral_grade_config
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               class_id
                               INTEGER,
                               oral_index
                               INTEGER,
                               hw_weight
                               REAL,
                               part_weight
                               REAL,
                               beh_weight
                               REAL,
                               UNIQUE
                           (
                               class_id,
                               oral_index
                           )
                               )
                           """)
            cursor.execute("""
                           INSERT INTO oral_grade_config (class_id, oral_index, hw_weight, part_weight, beh_weight)
                           VALUES (?, ?, ?, ?, ?) ON CONFLICT(class_id, oral_index) DO
                           UPDATE SET
                               hw_weight=excluded.hw_weight,
                               part_weight=excluded.part_weight,
                               beh_weight=excluded.beh_weight
                           """, (class_id, oral_index, hw_weight, part_weight, beh_weight))
            conn.commit()

    def get_oral_grade_weights(self, class_id, oral_index):
        """Varsayılan veya sınıfa özel sözlü ağırlıklarını getirir."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS oral_grade_config
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               class_id
                               INTEGER,
                               oral_index
                               INTEGER,
                               hw_weight
                               REAL,
                               part_weight
                               REAL,
                               beh_weight
                               REAL,
                               UNIQUE
                           (
                               class_id,
                               oral_index
                           )
                               )
                           """)
            cursor.execute(
                "SELECT hw_weight, part_weight, beh_weight FROM oral_grade_config WHERE class_id = ? AND oral_index = ?",
                (class_id, oral_index))
            row = cursor.fetchone()
            if row:
                return row['hw_weight'], row['part_weight'], row['beh_weight']
            # Varsayılan değerler
            return (50.0, 30.0, 20.0) if oral_index == 2 else (100.0, 0.0, 0.0)

db = DBManager()