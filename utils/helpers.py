def turkish_capitalize(text: str) -> str:
    """Türkçe karakter kurallarına uygun olarak baş harfleri büyütür (örn: ibiş -> İbiş)."""
    if not text:
        return ""

    words = text.strip().split()
    capitalized_words = []

    for word in words:
        if not word:
            continue
        first_char = word[0]
        rest = word[1:]

        # Türkçe küçük i -> İ dönüşümü
        if first_char == 'i':
            first_char = 'İ'
        elif first_char == 'ı':
            first_char = 'I'
        else:
            first_char = first_char.upper()

        # Kalan harfleri Türkçe mantıkla küçültme
        rest = rest.replace('İ', 'i').replace('I', 'ı').lower()
        capitalized_words.append(first_char + rest)

    return " ".join(capitalized_words)