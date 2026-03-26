import re
from collections import defaultdict
from typing import Dict, List


"""
Парсинг списка сделок из текста, скопированного из интерфейса Мешка.

Агрегирует суммы по покупателям.
Основан на фиксированных позициях строк и ключевых маркерах,
поэтому чувствителен к изменениям структуры страницы.
"""


def extract_amount(line: str) -> int | None:
    if "₽" not in line:
        return None
    value = re.sub(r"[^\d]", "", line)
    return int(value) if value else None


def normalize_name(name: str) -> str:
    return re.sub(r"[^a-zA-Zа-яА-Я0-9]", "", name).lower()


def parse_deals(raw_text: str) -> Dict[str, int]:
    lines = [line.strip() for line in raw_text.split("\n")]

    buyers = defaultdict(int)

    for i, line in enumerate(lines):
        if "Незавершенная" in line:
            if i < 3:
                continue

            buyer = lines[i - 3]
            if not buyer:
                continue

            amount = None
            for j in range(i - 1, -1, -1):
                amount = extract_amount(lines[j])
                if amount:
                    break

            if amount:
                buyers[buyer] += amount

    return dict(buyers)


def sort_buyers(buyers: Dict[str, int]) -> List[tuple]:
    return sorted(
        buyers.items(),
        key=lambda x: (normalize_name(x[0]), x[0])
    )


def format_deals(buyers: Dict[str, int]) -> str:
    sorted_data = sort_buyers(buyers)
    return "\n".join(f"{name}\t{amount}" for name, amount in sorted_data)


def parse_and_format_deals(raw_text: str) -> str:
    data = parse_deals(raw_text)
    return format_deals(data)