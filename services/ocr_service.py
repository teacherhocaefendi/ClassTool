from google.genai import client as genai_client
from google.genai import types
from PIL import Image
from services.theme_and_log_service import logger
API_KEY = "BURAYA_KENDI_API_ANAHTARINI_YAZ"

class OCRService:
    @staticmethod
    def extract_text_from_image(image_path):
        if API_KEY == "BURAYA_KENDI_API_ANAHTARINI_YAZ":
            raise ValueError("Lütfen Google AI Studio'dan bir API key alıp ocr_service.py dosyasına ekleyin.")

        try:
            logger.info(f"Initializing Gemini Client for image: {image_path}")
            client = genai_client.Client(api_key=API_KEY)
            img = Image.open(image_path)
            img.thumbnail((1200, 1200))

            prompt = """
            Bu görselde bir sınıf/öğrenci listesi bulunmaktadır. 
            Lütfen listedeki öğrencileri analiz et ve her öğrenci için şu bilgileri çıkar: Numara, Ad, Soyad, Cinsiyet.

            Kurallar:
            1. Sadece her öğrenci için bir satır oluştur.
            2. Satır formatı kesinlikle şu şekilde olmalıdır: [Numara] [Ad] [Soyad] [Cinsiyet]
            3. Cinsiyet tespiti kritik öneme sahiptir: 
               - Tabloda K/E, Kız/Erkek veya Kadın/Erkek kısaltmaları/ifadeleri varsa birebir baz al.
               - Eğer görselde cinsiyet sütunu yoksa veya okunmuyorsa, öğrencinin adına dikkatle bak ve "Kız" veya "Erkek" olarak tam yaz.
            4. Başına veya sonuna hiçbir markdown (``` vb.), başlık veya ekstra açıklama ekleme. Sadece saf metin döndür.
            """

            response = client.models.generate_content(
                model='models/gemini-3.1-flash-lite',
                contents=[prompt, img]
            )
            logger.info("Gemini AI OCR request completed successfully.")
            return response.text.strip()

        except Exception as e:
            logger.error(f"AI OCR Crash Error: {str(e)}", exc_info=True)
            raise Exception(f"Yapay Zeka İşleme Hatası: {str(e)}")