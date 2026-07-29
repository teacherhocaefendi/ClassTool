import re
from database.db_manager import db


class EOkulParserService:
    @staticmethod
    def parse_raw_text(class_id, raw_text):
        """
        Parses raw text (from clipboard or OCR) into the database.
        Expects format: [Number] [First Name] [Last Name] [Gender]
        """
        if not raw_text.strip():
            raise ValueError("The text area is empty.")

        lines = raw_text.strip().split('\n')
        students_data = []

        for line in lines:
            cleaned_line = re.sub(r'\t+', ' ', line).strip()
            # Skip empty lines
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
                    last_name = name_parts[-1].capitalize()
                    first_name = " ".join(name_parts[:-1]).title()
                else:
                    first_name = full_name.title()
                    last_name = ""

                students_data.append({
                    'number': student_number,
                    'first_name': first_name,
                    'last_name': last_name,
                    'gender': gender
                })

        if not students_data:
            raise ValueError(
                "Could not find any valid student data formatting. \nEnsure format is: Number Name Surname Gender")

        db.add_multiple_students(class_id, students_data)
        return len(students_data)