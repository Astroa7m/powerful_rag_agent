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


def extract_sql(text: str):
    match = re.search(r"```sql(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    match = re.search(r"(SELECT\s+.*?;)", text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else None
