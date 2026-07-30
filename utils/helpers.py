def turkish_capitalize(text: str) -> str:
    """Türkçe karakter kurallarına %100 uygun baş harf büyütme ve düzeltme."""
    if not text:
        return ""

    words = text.strip().split()
    capitalized_words = []

    for word in words:
        if not word:
            continue

        # Kelimenin tamamı büyük harfse (Örn: NİLAYNUR, ÇEVİK, İSLAM) önce Türkçe karakterlerle küçültüyoruz
        # Türkçe Büyük I -> ı, Büyük İ -> i yapıyoruz
        clean_word = ""
        for char in word:
            if char == 'I':
                clean_word += 'ı'
            elif char == 'İ':
                clean_word += 'i'
            else:
                clean_word += char.lower()

        # Şimdi sadece ilk harfi Türkçe kurallara göre büyütüyoruz
        first_char = clean_word[0]
        if first_char == 'i':
            first_char = 'İ'
        elif first_char == 'ı':
            first_char = 'I'
        else:
            first_char = first_char.upper()

        rest = clean_word[1:]
        capitalized_words.append(first_char + rest)

    return " ".join(capitalized_words)