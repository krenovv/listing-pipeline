from typing import List, Dict

"""
Парсинг списка лотов из текста, скопированного из интерфейса Мешка.

Использует фиксированные позиции строк,
поэтому чувствителен к изменениям структуры страницы.
"""


def split_records(raw_text: str) -> List[str]:
    parts = raw_text.split("№ ")
    return parts[1:]  # первый элемент пустой


def parse_record(record: str) -> Dict:
    lines = [line.strip() for line in record.strip().split("\n")]

    has_note = len(lines) > 19 and lines[13] == "Заметка (видна только Вам):"

    if has_note:
        time = lines[1] if len(lines) > 1 else "Без времени"
        price = lines[2] if len(lines) > 2 else "Без цены"
        number = lines[18] if len(lines) > 18 else "Без номера"
        name = lines[19] if len(lines) > 19 else "Без имени"
    else:
        time = lines[1] if len(lines) > 1 else "Без времени"
        price = lines[2] if len(lines) > 2 else "Без цены"
        number = lines[17] if len(lines) > 17 else "Без номера"
        name = lines[18] if len(lines) > 18 else "Без имени"

    return {
        "name": name,
        "number": number,
        "time": time,
        "price": price,
    }


def format_record(record: Dict) -> str:
    return f"{record['name']} (№{record['number']}) от {record['time']} - {record['price']}"


def parse_lots(raw_text: str) -> Dict:
    records = split_records(raw_text)

    parsed = []
    errors = []

    for record in records:
        data = parse_record(record)
        formatted = format_record(data)

        parsed.append(formatted)

        if "С РУБЛЯ" not in formatted:
            errors.append(formatted)

    return {
        "items": parsed,
        "errors": errors
    }