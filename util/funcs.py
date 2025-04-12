import re


def detect_language(text):
    """
    Detects language based on presence of Arabic Unicode characters.
    Returns "ar" for Arabic, "en" otherwise.
    """
    arabic_chars = re.compile(r'[\u0600-\u06FF]')
    if arabic_chars.search(text):
        return "ar"
    return "en"
