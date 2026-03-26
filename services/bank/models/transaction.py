from dataclasses import dataclass
from typing import Optional


@dataclass
class Transaction:
    date: str                  # "2025-07-14"
    time: Optional[str]        # "12:44" или None
    amount: int                # 1290
    bank: str                  # "Сбербанк"
    card: Optional[str]        # "****5277"
    owner: str                 # "Виталий"
    description: str           # "Перевод от ..."

    def short_str(self) -> str:
        # Форматированная строка для отображения
        time_part = f"{self.time} " if self.time else ""
        return f"{time_part}| {self.amount:>5} ₽ | {self.bank:<10} | {self.card or '—':<8} | {self.owner:<7}"
