import json
from database.db_manager import db


class BackupService:
    @staticmethod
    def export_full_backup_json(file_path):
        """Veritabanındaki her şeyi tek bir JSON dosyasına dışarı aktarır."""
        data = {}
        with db.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM classes")
            data['classes'] = [dict(row) for row in cursor.fetchall()]

            cursor.execute("SELECT * FROM students")
            data['students'] = [dict(row) for row in cursor.fetchall()]

            cursor.execute("SELECT * FROM student_profiles")
            data['student_profiles'] = [dict(row) for row in cursor.fetchall()]

            cursor.execute("SELECT * FROM logs")
            data['logs'] = [dict(row) for row in cursor.fetchall()]

            cursor.execute("SELECT * FROM group_history")
            data['group_history'] = [dict(row) for row in cursor.fetchall()]

            cursor.execute("SELECT * FROM homeworks")
            data['homeworks'] = [dict(row) for row in cursor.fetchall()]

            cursor.execute("SELECT * FROM homework_checks")
            data['homework_checks'] = [dict(row) for row in cursor.fetchall()]

            cursor.execute("SELECT * FROM seating_layouts")
            data['seating_layouts'] = [dict(row) for row in cursor.fetchall()]

            cursor.execute("SELECT * FROM app_settings")
            data['app_settings'] = [dict(row) for row in cursor.fetchall()]

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True

    @staticmethod
    def import_full_backup_json(file_path):
        """Yedek JSON dosyasını okuyarak veritabanına topluca yükler."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        with db.get_connection() as conn:
            cursor = conn.cursor()

            # Önce mevcut verileri temizle
            cursor.execute("DELETE FROM homework_checks")
            cursor.execute("DELETE FROM homeworks")
            cursor.execute("DELETE FROM group_history")
            cursor.execute("DELETE FROM logs")
            cursor.execute("DELETE FROM student_profiles")
            cursor.execute("DELETE FROM seating_layouts")
            cursor.execute("DELETE FROM students")
            cursor.execute("DELETE FROM classes")
            cursor.execute("DELETE FROM app_settings")

            # Tabloları geri yükle
            for cls in data.get('classes', []):
                cursor.execute("INSERT INTO classes (id, name, academic_year) VALUES (?, ?, ?)",
                               (cls['id'], cls['name'], cls['academic_year']))

            for s in data.get('students', []):
                cursor.execute("""
                               INSERT INTO students (id, class_id, student_number, first_name, last_name, gender,
                                                     seat_row, seat_column, selection_count)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                               """, (s['id'], s['class_id'], s['student_number'], s['first_name'], s['last_name'],
                                     s['gender'], s['seat_row'], s['seat_column'], s['selection_count']))

            for p in data.get('student_profiles', []):
                cursor.execute("""
                               INSERT INTO student_profiles (id, student_id, sociability_score, focus_score,
                                                             participation_score, personality_tags, teacher_notes)
                               VALUES (?, ?, ?, ?, ?, ?, ?)
                               """, (p['id'], p['student_id'], p['sociability_score'], p['focus_score'],
                                     p['participation_score'], p['personality_tags'], p['teacher_notes']))

            for l in data.get('logs', []):
                cursor.execute("""
                               INSERT INTO logs (id, student_id, log_type, category_tag, comment, created_at)
                               VALUES (?, ?, ?, ?, ?, ?)
                               """, (l['id'], l['student_id'], l['log_type'], l['category_tag'], l['comment'],
                                     l['created_at']))

            for g in data.get('group_history', []):
                cursor.execute(
                    "INSERT INTO group_history (id, class_id, group_structure_json, created_at) VALUES (?, ?, ?, ?)",
                    (g['id'], g['class_id'], g['group_structure_json'], g['created_at']))

            for h in data.get('homeworks', []):
                cursor.execute(
                    "INSERT INTO homeworks (id, class_id, title, due_date, created_at) VALUES (?, ?, ?, ?, ?)",
                    (h['id'], h['class_id'], h['title'], h['due_date'], h['created_at']))

            for hc in data.get('homework_checks', []):
                cursor.execute("INSERT INTO homework_checks (id, homework_id, student_id, status) VALUES (?, ?, ?, ?)",
                               (hc['id'], hc['homework_id'], hc['student_id'], hc['status']))

            for sl in data.get('seating_layouts', []):
                cursor.execute("INSERT INTO seating_layouts (class_id, layout_json) VALUES (?, ?)",
                               (sl['class_id'], sl['layout_json']))

            for aset in data.get('app_settings', []):
                cursor.execute("INSERT INTO app_settings (key, value) VALUES (?, ?)",
                               (aset['key'], aset['value']))

            conn.commit()
        return True