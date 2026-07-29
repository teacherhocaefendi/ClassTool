import os

# Okunacak klasörler ve dosya uzantıları
TARGET_EXTENSIONS = ['.py']
IGNORE_DIRS = ['.venv', '.git', '__pycache__', '.idea']

output_file = "tum_proje_kodlari.txt"

with open(output_file, "w", encoding="utf-8") as outfile:
    for root, dirs, files in os.walk("."):
        # Yoksayılacak klasörleri filtrele
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for file in files:
            if any(file.endswith(ext) for ext in TARGET_EXTENSIONS):
                file_path = os.path.join(root, file)
                outfile.write(f"\n{'=' * 50}\n")
                outfile.write(f"DOSYA: {file_path}\n")
                outfile.write(f"{'=' * 50}\n\n")

                try:
                    with open(file_path, "r", encoding="utf-8") as infile:
                        outfile.write(infile.read())
                except Exception as e:
                    outfile.write(f"Hata oluştu: {str(e)}\n")

print(f"Bütün kodlar '{output_file}' dosyasına yazıldı!")