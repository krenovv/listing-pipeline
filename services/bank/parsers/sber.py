import re

from typing import List
from PyPDF2 import PdfReader

from services.bank.models.transaction import Transaction

def parse_sber_pdf(path: str, owner_name: str = "Неизвестно") -> List[Transaction]:
    reader = PdfReader(path)
    all_lines = []

    for page in reader.pages:
        text = page.extract_text()
        if text:
            lines = text.strip().split("\n")
            all_lines.extend(lines)

    transactions = []
    card_number = None
    i = 0

    while i < len(all_lines):
        line = all_lines[i].strip()

        # Сохраняем номер карты, если нашли
        if not card_number:
            card_match = re.search(r"Visa.*?•{4}\s?(\d{4})", line)
            if card_match:
                card_number = card_match.group(1)

        # Ищем строку с датой и временем операции
        match = re.match(r"(\d{2}\.\d{2}\.\d{4}) (\d{2}:\d{2})", line)
        if match:
            date_str = match.group(1)
            time_str = match.group(2)

            # Следующая строка - описание
            i += 1
            if i >= len(all_lines):
                break

            # Описание может содержать дату + код - удалим их
            description = all_lines[i].strip()

            # Удалим дату + 6-значный код в начале (если есть)
            description = re.sub(r"^\d{2}\.\d{2}\.\d{4} \d{6} ?", "", description)

            # Попробуем найти сумму: ищем что-то вроде "+1 234,56"
            amount_match = re.search(r"([\+\-]?\d[\d\s]*,\d{2})", line)
            if amount_match:
                amount_str = amount_match.group(1).replace("\xa0", "").replace(" ", "").replace(",", ".")
                amount = float(amount_str)
            else:
                amount = 0.0

            # Очистим от неразрывных пробелов
            description = description.replace("\xa0", " ")

            # Вытаскиваем номер карты/счета из описания (если не был найден ранее)
            if not card_number:
                desc_card_match = re.search(r"по карте \*{4}(\d{4})", description)
                if desc_card_match:
                    card_number = desc_card_match.group(1)

                else:
                    desc_account_match = re.search(r"по счету \*{4}(\d{4})", description)
                    if desc_account_match:
                        card_number = desc_account_match.group(1)

            description = re.sub(r"Операция по карте(\s\*{4}\d{4})?", "", description).strip()
            description = re.sub(r"Операция по счету(\s\*{4}\d{4})?", "", description).strip()

            transactions.append(Transaction(
                date=convert_date(date_str),
                time=time_str,
                amount=int(amount),
                bank="Сбербанк",
                card=card_number or "—",
                owner=owner_name,
                description=description
            ))

        i += 1

    return transactions



def convert_date(date_str: str) -> str:
    # Преобразует '14.07.2025' - '2025-07-14'
    day, month, year = map(int, date_str.split('.'))
    return f"{year:04d}-{month:02d}-{day:02d}"



def convert_date(date_str: str) -> str:
    # Преобразует '14.07.2025' - '2025-07-14'
    day, month, year = map(int, date_str.split('.'))
    return f"{year:04d}-{month:02d}-{day:02d}"



def parse_multiple_sber(files: list[tuple[str, str]]) -> list[Transaction]:
    """
    Принимает список: (путь_к_pdf, владелец)
    Возвращает общий список всех транзакций по всем картам.
    """
    all_transactions = []
    for path, owner in files:
        all_transactions.extend(parse_sber_pdf(path, owner_name=owner))
    return all_transactions



