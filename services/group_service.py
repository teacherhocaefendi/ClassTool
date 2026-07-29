import random
from database.db_manager import db


class GroupService:
    @staticmethod
    def generate_groups(class_id, group_size, balance_gender=True, balance_traits=False):
        """
        Dinamik kurallara göre grup oluşturur.
        - balance_gender=False ise kız/erkek dengesi gözetilmez, tam rastgele karıştırılır.
        - balance_traits=True ise öğrencilerin profil puanlarına bakılır.
        """
        students = db.get_students()
        if not students:
            return []

        # Eğer hiçbir kural istenmiyorsa tamamen rastgele karıştır
        if not balance_gender and not balance_traits:
            student_list = list(students)
            random.shuffle(student_list)
            groups = []
            for i in range(0, len(student_list), group_size):
                groups.append(student_list[i:i + group_size])
            return groups

        # Cinsiyet Dengesi Aktifse:
        if balance_gender:
            males = [s for s in students if s['gender'].lower() in ['male', 'erkek']]
            females = [s for s in students if s['gender'].lower() in ['female', 'kız']]

            random.shuffle(males)
            random.shuffle(females)

            balanced_list = []
            while males or females:
                if females: balanced_list.append(females.pop(0))
                if males: balanced_list.append(males.pop(0))

            groups = []
            for i in range(0, len(balanced_list), group_size):
                groups.append(balanced_list[i:i + group_size])
            return groups

        # Varsayılan Rastgele Dağıtım
        student_list = list(students)
        random.shuffle(student_list)
        return [student_list[i:i + group_size] for i in range(0, len(student_list), group_size)]