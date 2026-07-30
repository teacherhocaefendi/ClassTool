import re
from database.db_manager import db
from utils.helpers import turkish_capitalize # YENİ IMPORT

class EOkulParserService:
    @staticmethod
    def parse_raw_text(class_id, raw_text):
        if not raw_text.strip():
            raise ValueError("Metin alanı boş.")

        lines = raw_text.strip().split('\n')
        students_data = []

        for line in lines:
            cleaned_line = re.sub(r'\t+', ' ', line).strip()
            if not cleaned_line:
                continue

            match = re.match(r'^(\d+)\s+(.+?)\s+(Kız|Erkek|K|E)$', cleaned_line, re.IGNORECASE)

            if match:
                student_number = match.group(1)
                full_name = match.group(2).strip()
                raw_gender = match.group(3).strip().lower()

                gender = "Female" if raw_gender in ['kız', 'k'] else "Male"

                name_parts = full_name.split()
                if len(name_parts) > 1:
                    last_name = turkish_capitalize(name_parts[-1])
                    first_name = turkish_capitalize(" ".join(name_parts[:-1]))
                else:
                    first_name = turkish_capitalize(full_name)
                    last_name = ""

                students_data.append({
                    'number': student_number,
                    'first_name': first_name,
                    'last_name': last_name,
                    'gender': gender
                })

        if not students_data:
            raise ValueError("Geçerli bir öğrenci listesi formatı bulunamadı.")

        db.add_multiple_students(class_id, students_data)
        return len(students_data)