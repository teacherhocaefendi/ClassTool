import random
from database.db_manager import db


class RandomizerService:
    @staticmethod
    def pick_random_student(class_id):
        """
        Picks a random student using a depletion pool.
        Returns a dictionary with student details, or None if class is empty.
        """
        eligible_students = db.get_eligible_students(class_id)

        if not eligible_students:
            return None

        # Pick a random student from the eligible pool
        selected = random.choice(eligible_students)

        # Update their count in the database so they aren't picked again until the next round
        db.increment_selection_count(selected['id'])

        return {
            "id": selected['id'],
            "first_name": selected['first_name'],
            "last_name": selected['last_name'],
            "selection_count": selected['selection_count'] + 1
        }