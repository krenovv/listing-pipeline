import pdfplumber
import re

from services.bank.models.transaction import Transaction


def parse_tinkoff_pdf(path: str, owner_name: str) -> list[Transaction]:
    transactions = []
    bank_name = "Т-Банк"

    with pdfplumber.open(path) as pdf:
        all_lines = []

        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines = text.strip().split("\n")
                all_lines.extend(lines)

    i = 0
    while i < len(all_lines) - 1:
        line = all_lines[i].strip()

        # Ищем строку, начинающуюся с даты + сумма + карта
        if re.match(r"\d{2}\.\d{2}\.\d{4}", line):
            # Пример: "15.07.2025 15.07.2025 +12 000.00 ₽ +12 000.00 ₽ Пополнение. Система 3370"
            parts = line.split()
            if len(parts) < 6:
                i += 1
                continue

            date_raw = parts[0]
            # Извлекаем сумму
            sum_match = re.search(r"\+([\d\s]+(?:[.,]\d{2})) ₽", line)
            if not sum_match:
                i += 1
                continue
            amount_str = sum_match.group(1).replace("\xa0", "").replace(" ", "").replace(",", ".")
            amount = int(float(amount_str))

            # Извлекаем номер карты (последнее слово - 4 цифры)
            card_match = re.search(r"(\d{4})$", line)
            card = card_match.group(1) if card_match else "—"

            # Описание - всё, что после второй суммы
            descr_match = re.split(r"\+[\d\s]+[.,]\d{2} ₽ \+[\d\s]+[.,]\d{2} ₽", line)
            description = descr_match[1].strip() if len(descr_match) > 1 else ""
            description = re.sub(r"\b" + re.escape(card) + r"\b$", "", description).strip()

            # Следующая строка: время (берём 2-е время, если есть)
            time_line = all_lines[i + 1].strip()
            time_match = re.findall(r"\d{2}:\d{2}", time_line)
            time = time_match[1] if len(time_match) >= 2 else time_match[0] if time_match else None

            transactions.append(Transaction(
                date=convert_date(date_raw),
                time=time,
                amount=amount,
                bank=bank_name,
                card=card,
                owner=owner_name,
                description=description
            ))
            i += 2  # переходим к следующей операции
        else:
            i += 1

    return transactions


def convert_date(date_str: str) -> str:
    # Преобразует '14.07.2025' - '2025-07-14'
    day, month, year = map(int, date_str.split('.'))
    return f"{year:04d}-{month:02d}-{day:02d}"

def parse_multiple_tinkoff(files: list[tuple[str, str]]) -> list[Transaction]:
    """
    Принимает список: (путь_к_pdf, владелец)
    Возвращает общий список всех транзакций по всем файлам Т-Банка.
    """
    all_transactions = []
    for path, owner in files:
        all_transactions.extend(parse_tinkoff_pdf(path, owner_name=owner))
    return all_transactions

