import datetime
import os
import re

from services.bank.models.transaction import Transaction


def parse_sber_text(path: str, owner_name: str) -> list[Transaction]:
    transactions = []

    with open(path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    # Получаем дату создания файла
    base_date = datetime.date.fromtimestamp(os.path.getmtime(path))
    current_date = base_date

    def resolve_relative_date(text: str) -> str:
        lowered = text.lower()
        if "сегодня" in lowered:
            return base_date
        elif "вчера" in lowered:
            return base_date - datetime.timedelta(days=1)
        elif "позавчера" in lowered:
            return base_date - datetime.timedelta(days=2)
        else:
            # Пробуем парсить строки типа "12 июля, суббота"
            match = re.match(r"(\d{1,2}) (\w+)", lowered)
            if match:
                day, month_name = match.groups()
                months = {
                    "января": 1, "февраля": 2, "марта": 3, "апреля": 4, "мая": 5,
                    "июня": 6, "июля": 7, "августа": 8, "сентября": 9,
                    "октября": 10, "ноября": 11, "декабря": 12
                }
                if month_name in months:
                    try:
                        return datetime.date(base_date.year, months[month_name], int(day))
                    except ValueError:
                        pass
        return base_date

    i = 0
    while i < len(lines):
        line = lines[i]
        if any(x in line.lower() for x in ["сегодня", "вчера", "позавчера"]) or re.match(r"\d{1,2} \w+", line.lower()):
            current_date = resolve_relative_date(line)
            i += 1
            continue

        amount_match = re.search(r"\+([\d\s]+) ₽", line)
        if amount_match:
            try:
                amount = int(amount_match.group(1).replace(" ", ""))
            except ValueError:
                i += 1
                continue

            sender = lines[i - 1] if i >= 1 else ""
            comment = lines[i + 1] if i + 1 < len(lines) else ""
            description = f"{sender.strip()} / {comment.strip()}".strip(" /")

            transactions.append(Transaction(
                date=current_date.strftime("%Y-%m-%d"),
                time=None,
                amount=amount,
                bank="Сбербанк",
                card=None,
                owner=owner_name,
                description=description
            ))
            i += 2
        else:
            i += 1

    return transactions
