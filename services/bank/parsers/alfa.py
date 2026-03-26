import pdfplumber
import re

from services.bank.models.transaction import Transaction


def parse_alfa_pdf(path: str, owner_name: str) -> list[Transaction]:
    transactions = []
    bank_name = "Альфа-Банк"

    with pdfplumber.open(path) as pdf:
        all_lines = []

        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines = text.strip().split("\n")
                all_lines.extend(lines)

    for line in all_lines:
        line = line.strip()

        # Пропускаем списания (отрицательные суммы)
        if "-" in line or "RUR" not in line:
            continue

        # Ищем дату в формате дд.мм.гггг или дд.мм.гг
        date_match = re.match(r"(\d{2}\.\d{2}\.\d{4}|\d{2}\.\d{2}\.\d{2})", line)
        if not date_match:
            continue

        date_str = date_match.group(1)
        date_formatted = convert_date(date_str)

        # Ищем сумму (в конце строки перед 'RUR')
        sum_match = re.search(r"([\d\s]+(?:[.,]\d{2})?)\s*RUR", line)
        if not sum_match:
            continue

        amount_str = sum_match.group(1).replace("\xa0", "").replace(" ", "").replace(",", ".")
        amount = int(float(amount_str))

        # Пропускаем нулевые или сомнительные суммы
        if amount == 0:
            continue

        card = None  # У Альфы только одна карта, номер не нужен

        # Описание — вся строка, без даты и суммы
        # Удалим дату в начале и сумму в конце
        desc = re.sub(r"^(\d{2}\.\d{2}\.\d{2,4})\s*", "", line)
        desc = re.sub(r"\s*[\d\s]+[.,]\d{2}\s*RUR$", "", desc)
        desc = re.sub(r"Операция по карте:.*?\d{4}", "", desc)
        desc = re.sub(r"Без НДС", "", desc)
        description = ""

        transactions.append(Transaction(
            date=date_formatted,
            time=None,
            amount=amount,
            bank=bank_name,
            card=card,
            owner=owner_name,
            description=description
        ))

    return transactions


def convert_date(date_str: str) -> str:
    # Преобразует '18.06.25' или '18.06.2025' в '2025-06-18'
    parts = date_str.split(".")
    day = int(parts[0])
    month = int(parts[1])
    year = int(parts[2])
    if year < 100:
        year += 2000
    return f"{year:04d}-{month:02d}-{day:02d}"
