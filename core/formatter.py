import re


CLARITY_GRADES = [
    "IF", "VVS", "VS", "SI", "S1", "S2", "SI1", "SI2", "I1", "I2", "I3"
]


def normalize_units(text: str) -> str:
    text = re.sub(r'(?i)(\d+)(\s*)(cts|ct|карат|carat)', r'\1 кт', text)
    text = re.sub(r'(?i)(\d+)(\s*)(mm)', r'\1 мм', text)
    return text


def fix_spacing(text: str) -> str:
    text = re.sub(r'(\d)(\s*)(мм)', r'\1 \3', text)
    text = re.sub(r'(\d)(\s*)(кт)', r'\1 \3', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()


def add_commas(text: str) -> str:
    text = re.sub(r'(\d мм)(?!,)(?!$)', r'\1, ', text)
    text = re.sub(r'(\d кт)(?!,)(?!$)', r'\1, ', text)
    return text


def normalize_keywords(text: str) -> str:
    replacements = {
        r'(?i)\bбольшая\b': 'БОЛЬШАЯ',
        r'(?i)\bредкость\b': 'РЕДКОСТЬ',
        r'(?i)\bс рубля\b': 'С РУБЛЯ',
        r'(?i)\bогромный\b': 'Огромный',
        r'(?i)\bприродный\b': 'Природный',
        r'(?i)\bколлекционный\b': 'Коллекционный',
        r'(?i)\bсертификат\b': 'СЕРТИФИКАТ',
    }

    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text)

    return text


def normalize_pcs(text: str) -> str:
    text = re.sub(r'(?i)(\d+)(\s*)(pcs)', r'\1 шт', text)
    text = re.sub(r'(\d)(\s*)(шт)', r'\1 \3', text)
    return text


def capitalize_after_phrase(text: str) -> str:
    return re.sub(
        r'(?i)(с рубля)\s+(\S+)',
        lambda m: f'{m.group(1)} {m.group(2).capitalize()}',
        text
    )


def merge_clarity_grades(text: str) -> str:
    words = text.split()
    i = 0

    while i < len(words) - 1:
        if words[i].upper() in CLARITY_GRADES and words[i + 1].upper() in CLARITY_GRADES:
            words[i] = f"{words[i]}-{words[i + 1]}"
            words.pop(i + 1)
        i += 1

    return ' '.join(words)


def format_title(text: str) -> str:
    text = normalize_units(text)
    text = fix_spacing(text)
    text = add_commas(text)
    text = normalize_pcs(text)
    text = normalize_keywords(text)
    text = capitalize_after_phrase(text)
    text = merge_clarity_grades(text)

    return text