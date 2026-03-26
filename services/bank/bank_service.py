from services.bank.parsers.sber import parse_multiple_sber
from services.bank.parsers.tinkoff import parse_multiple_tinkoff
from services.bank.parsers.alfa import parse_alfa_pdf
from services.bank.parsers.sber_text import parse_sber_text
from services.bank.models.transaction import Transaction


def process_bank_files(config: dict):
    """
    config пример:
    {
        "tinkoff": [("file.pdf", "account_1")],
        "alfa": [("file.pdf", "account_2")],
        "sber_txt": [("file.txt", "account_1")]
    }
    """

    transactions: list[Transaction] = []

    if "tinkoff" in config:
        transactions += parse_multiple_tinkoff(config["tinkoff"])

    if "alfa" in config:
        for file, owner in config["alfa"]:
            transactions += parse_alfa_pdf(file, owner_name=owner)

    if "sber_txt" in config:
        for file, owner in config["sber_txt"]:
            transactions += parse_sber_text(file, owner_name=owner)

    return transactions