from typing import List
from services.bank.models.transaction import Transaction


def search_by_amount(transactions: List[Transaction], amount: int, tolerance: int = 0) -> List[Transaction]:
    """
    Ищет транзакции по сумме.

    tolerance — допустимое отклонение (например ±1 рубль)
    """
    result = []

    for tx in transactions:
        if abs(tx.amount - amount) <= tolerance:
            result.append(tx)

    return result


def filter_by_date(transactions: List[Transaction], date: str) -> List[Transaction]:
    """
    Фильтрация по дате
    """
    return [tx for tx in transactions if date in tx.date]


def format_transactions(transactions: List[Transaction]) -> str:
    """
    Преобразует список транзакций в текст для вывода / буфера
    """
    if not transactions:
        return "Ничего не найдено."

    lines = []

    for tx in transactions:
        lines.append(
            f"{tx.date} | {tx.amount} | {tx.description} | {tx.owner}"
        )

    return "\n".join(lines)


def summarize_by_account(transactions: List[Transaction]) -> str:
    """
    Суммирует операции по аккаунтам
    """
    totals = {}

    for tx in transactions:
        totals[tx.account] = totals.get(tx.account, 0) + tx.amount

    lines = [f"{acc}: {total}" for acc, total in totals.items()]
    return "\n".join(lines)