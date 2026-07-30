import json
from database.db_manager import db

# Sabit Rozet Tanımları
BADGES = {
    # Otomatik Rozetler
    "star_of_week": {
        "title": "Haftanın Yıldızı",
        "icon": "⭐",
        "desc": "Katılım ve performansıyla öne çıkan öğrenci.",
        "type": "auto"
    },
    "hw_master": {
        "title": "Ödev Şampiyonu",
        "icon": "📚",
        "desc": "Ödevlerini eksiksiz ve zamanında tamamlayan öğrenci.",
        "type": "auto"
    },
    "top_progress": {
        "title": "En İyi İlerleme",
        "icon": "🚀",
        "desc": "Performansını ve çabasını en çok artıran öğrenci.",
        "type": "auto"
    },
    # Öğretmenin Manuel Verdiği Rozetler
    "leader": {
        "title": "Sınıf Lideri",
        "icon": "👑",
        "desc": "Grup çalışmalarında sorumluluk alan ve yönlendiren.",
        "type": "manual"
    },
    "problem_solver": {
        "title": "Problem Çözücü",
        "icon": "🧩",
        "desc": "Zor sorulara analitik ve farklı çözümler üreten.",
        "type": "manual"
    },
    "helper": {
        "title": "Takım Oyuncusu",
        "icon": "🤝",
        "desc": "Arkadaşlarına yardım eden, dayanışmayı teşvik eden.",
        "type": "manual"
    },
    "creative": {
        "title": "Yaratıcı Düşünür",
        "icon": "🎨",
        "desc": "Derse özgün ve yaratıcı fikirlerle katkı sunan.",
        "type": "manual"
    }
}


class BadgeService:
    @staticmethod
    def initialize_badge_tables():
        """Rozet tablosunu oluşturur (Migration)."""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS student_badges
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
                               badge_key
                               TEXT
                               NOT
                               NULL,
                               awarded_at
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
                           ) ON DELETE CASCADE,
                               UNIQUE
                           (
                               student_id,
                               badge_key
                           )
                               )
                           """)
            conn.commit()

    @staticmethod
    def get_student_badges(student_id):
        """Öğrencinin kazandığı tüm rozetleri getirir."""
        BadgeService.initialize_badge_tables()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT badge_key, awarded_at FROM student_badges WHERE student_id = ?", (student_id,))
            rows = cursor.fetchall()

            student_badges = []
            for row in rows:
                key = row['badge_key']
                if key in BADGES:
                    info = BADGES[key].copy()
                    info['key'] = key
                    info['awarded_at'] = row['awarded_at']
                    student_badges.append(info)
            return student_badges

    @staticmethod
    def toggle_student_badge(student_id, badge_key):
        """Öğrenciye rozet ekler veya varsa kaldırır."""
        BadgeService.initialize_badge_tables()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM student_badges WHERE student_id = ? AND badge_key = ?",
                           (student_id, badge_key))
            row = cursor.fetchone()

            if row:
                cursor.execute("DELETE FROM student_badges WHERE id = ?", (row['id'],))
                conn.commit()
                return False  # Rozet kaldırıldı
            else:
                cursor.execute("INSERT INTO student_badges (student_id, badge_key) VALUES (?, ?)",
                               (student_id, badge_key))
                conn.commit()
                return True  # Rozet eklendi

    @staticmethod
    def calculate_auto_badges_for_class(class_id):
        """Sınıftaki ödev ve katılım verilerini analiz edip otomatik rozetleri dağıtır."""
        BadgeService.initialize_badge_tables()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM students WHERE class_id = ?", (class_id,))
            students = cursor.fetchall()

            if not students:
                return

            student_stats = []
            for s in students:
                s_id = s['id']

                # Ödev kontrolü
                cursor.execute("SELECT status FROM homework_checks WHERE student_id = ?", (s_id,))
                hw_checks = cursor.fetchall()
                total_hw = len(hw_checks)
                done_hw = sum(1 for c in hw_checks if c['status'] == 'Done')
                hw_ratio = (done_hw / total_hw) if total_hw > 0 else 0.0

                # Net katılım puanı
                cursor.execute("SELECT log_type FROM logs WHERE student_id = ?", (s_id,))
                logs = cursor.fetchall()
                net_part = sum(1 for l in logs if l['log_type'] in ['+', 'Quick Score', 'Doğru'])
                net_part -= sum(1 for l in logs if l['log_type'] in ['-', 'Yanlış'])

                student_stats.append({
                    'id': s_id,
                    'total_hw': total_hw,
                    'done_hw': done_hw,
                    'hw_ratio': hw_ratio,
                    'net_part': net_part
                })

            # 1. Ödev Şampiyonu: En az 3 ödev verilmiş ve tam teslim etmiş öğrenciler
            for st in student_stats:
                if st['total_hw'] >= 3 and st['hw_ratio'] == 1.0:
                    cursor.execute(
                        "INSERT OR IGNORE INTO student_badges (student_id, badge_key) VALUES (?, 'hw_master')",
                        (st['id'],))

            # 2. Haftanın Yıldızı: Net katılım puanı en yüksek ilk 3 öğrenci
            student_stats.sort(key=lambda x: x['net_part'], reverse=True)
            for st in student_stats[:3]:
                if st['net_part'] > 0:
                    cursor.execute(
                        "INSERT OR IGNORE INTO student_badges (student_id, badge_key) VALUES (?, 'star_of_week')",
                        (st['id'],))

            conn.commit()