import re
from pathlib import Path

# Sürüm numarası güncellenecek kritik dosyalar ve regex desenleri
FILES_TO_UPDATE = {
    "config.py": [
        (r'APP_VERSION\s*=\s*"[^"]+"', 'APP_VERSION = "{version}"')
    ],
    "main.py": [
        (r'Class Tool Uygulaması Başlatılıyor \[Sürüm [^\]]+\]', 'Class Tool Uygulaması Başlatılıyor [Sürüm {version}]')
    ],
    "services/language_service.py": [
        (r'Class Tool - Akıllı Tahta Öğrenci Takip \[Sürüm [^\]]+\]',
         'Class Tool - Akıllı Tahta Öğrenci Takip [Sürüm {version}]'),
        (r'Class Tool - Smart Board Tracker \[v[^\]]+\]', 'Class Tool - Smart Board Tracker [v{version}]')
    ],
    "ui/main_window.py": [
        (r'Class Tool - Smart Board Tracker \[Alpha [^\]]+\]', 'Class Tool - Smart Board Tracker [Alpha {version}]'),
        (r'QLabel\("Class Tool v[^"]+"\)', 'QLabel("Class Tool v{version}")')
    ]
}


def update_version():
    print("=" * 50)
    print("🚀 CLASS TOOL - OTOMATİK SÜRÜM GÜNCELLEYİCİ")
    print("=" * 50)

    new_version = input("\nYeni Sürüm Numarasını Girin (Örn: 1.2.2 veya 1.3.0): ").strip()

    if not new_version:
        print("❌ Hata: Sürüm numarası boş bırakılamaz!")
        return

    base_dir = Path(__file__).parent
    updated_files_count = 0

    for file_rel_path, patterns in FILES_TO_UPDATE.items():
        file_path = base_dir / file_rel_path

        if not file_path.exists():
            print(f"⚠️ Uyarı: {file_rel_path} bulunamadı, atlanıyor...")
            continue

        try:
            content = file_path.read_text(encoding="utf-8")
            original_content = content

            for pattern, replacement_template in patterns:
                replacement = replacement_template.format(version=new_version)
                content = re.sub(pattern, replacement, content)

            if content != original_content:
                file_path.write_text(content, encoding="utf-8")
                print(f"✅ Güncellendi: {file_rel_path}")
                updated_files_count += 1
            else:
                print(f"ℹ️ Değişiklik yok (Desen bulunamadı): {file_rel_path}")

        except Exception as e:
            print(f"❌ Hata ({file_rel_path}): {e}")

    print("-" * 50)
    print(f"🎉 İşlem Tamamlandı! Toplam {updated_files_count} dosyada sürüm v{new_version} yapıldı.")
    print("=" * 50)


if __name__ == "__main__":
    update_version()