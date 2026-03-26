import pyperclip
from datetime import datetime

from core.formatter import format_title
from core.tags import generate_tags
from core.lots_parser import parse_lots
from core.deals_parser import parse_and_format_deals
from core.certificate_formatter import generate_certificate_text
from integrations.airtable.mesh_sync import sync_meshok_to_airtable
from utils.datetime_tools import TimeGenerator
from utils.console import clear_console
from services.bank.bank_service import process_bank_files
from services.bank.utils.helpers import (
    search_by_amount,
    format_transactions,
    filter_by_date
)


def run_interactive():
    generator = None
    last_title = None

    while True:
        print("Скопируйте сырое название лота и нажмите Enter.")
        print("\nИли выберите пункт:")
        print("1. Форматировать название (из буфера)")
        print("2. Получить время выставления")
        print("3. Сгенерировать теги (из буфера)")
        print("4. Парсинг лотов (из буфера)")
        print("5. Парсинг сделок (из буфера)")
        print("6. Генерация текста сертификата (из буфера)")
        print("7. Модуль работы с банковскими операциями")
        print("8. Синхронизировать Airtable таблицу с лотами Мешка")
        print("0. Настроить время")

        choice = input(">>> ").strip()
        clear_console()

        # === WORKFLOW MODE (Enter) ===
        if choice == "":
            raw = pyperclip.paste()

            if not raw:
                print("Буфер пуст.\n")
                continue

            # 1. Форматирование
            formatted = format_title(raw)
            pyperclip.copy(formatted)
            last_title = formatted

            print(f"Название: {formatted}"
                  f"\nНазвание скопировано в буфер.")

            input("\nEnter - получить время")

            # 2. Время
            if not generator:
                clear_console()
                print("Сначала настройте время.\n")
                continue

            next_time = generator.next()
            pyperclip.copy(next_time)

            print(f"Время: {next_time}\n"
                  f"Время скопировано в буфер.\n")

            input("\nEnter - получить теги")

            # 3. Теги
            try:
                tags = generate_tags(last_title)
                pyperclip.copy(tags)

                print(f"Теги: {tags}\n"
                      "Теги скопированы в буфер.\n")

            except Exception as e:
                print(f"Ошибка генерации тегов: {e}\n")

            continue

        # === MENU MODE ===

        elif choice == "1":
            clear_console()

            raw = pyperclip.paste()

            if not raw:
                print("Буфер пуст.\n")
                continue

            result = format_title(raw)
            pyperclip.copy(result)
            print(f"Название: {result}\n"
                  f"Название скопировано в буфер.\n")

        elif choice == "2":
            clear_console()
            if not generator:
                print("Сначала настройте время.\n")
            else:
                result = generator.next()
                pyperclip.copy(result)
                print(f"Время: {result}\n"
                      f"Время скопировано в буфер.\n")

        elif choice == "3":
            clear_console()
            raw = pyperclip.paste()

            if not raw:
                print("Буфер пуст.\n")
                continue

            try:
                result = generate_tags(raw)
                pyperclip.copy(result)
                print(f"Теги: {result}\n"
                      "Теги скопированы в буфер.\n")
            except Exception as e:
                print(f"Ошибка: {e}\n")


        elif choice == "4":
            clear_console()

            raw = pyperclip.paste()

            if not raw.strip():
                print("Буфер пуст.\n")
                continue

            result = parse_lots(raw)

            output = "\n".join(

                f"{i}. {item}" for i, item in enumerate(result["items"], 1)

            )

            pyperclip.copy(output)

            print(f"{output}\n"
                  f"Результат скопирован в буфер.\n")


        elif choice == "5":

            raw = pyperclip.paste()

            if not raw:
                print("Буфер пуст.\n")
                continue

            result = parse_and_format_deals(raw)

            pyperclip.copy(result)

            print(f"{result}\n"
                  f"Результат скопирован в буфер.\n")

        elif choice == "6":
            clear_console()

            raw = pyperclip.paste()

            if not raw:
                print("Буфер пуст.\n")
                continue

            result = generate_certificate_text(raw)

            pyperclip.copy(result)

            print(f"{result}\n"
                  f"Результат скопирован в буфер.\n")


        elif choice == "7":
            clear_console()

            config = {
                "tinkoff": [
                    ("data/tk_acc1.pdf", "TINKOFF / acc1"),
                    ("data/tk_acc2.pdf", "TINKOFF / acc2"),
                ],
                "alfa": [
                    ("data/alfa_acc1.pdf", "ALFA / acc1"),
                ],
                "sber_txt": [
                    ("data/sber_acc1.txt", "SBER / acc1"),
                    ("data/sber_acc2.txt", "SBER / acc2"),
                ]
            }

            transactions = process_bank_files(config)

            print(f"\nЗагружено операций: {len(transactions)}")

            while True:

                user_input = input("Введите сумму или дату [YYYY-MM-DD] (0 для выхода): ").strip()

                if user_input == "0":
                    clear_console()
                    break

                # --- Поиск по сумме ---
                if user_input.isdigit():
                    amount = int(user_input)

                    found = search_by_amount(transactions, amount)

                # --- Поиск по дате ---
                else:
                    found = filter_by_date(transactions, user_input)

                result = format_transactions(found)

                pyperclip.copy(result)

                clear_console()
                print(f"{result}\n")


        elif choice == "8":
            clear_console()
            sync_meshok_to_airtable()
            print("\n")

        elif choice == "0":
            clear_console()
            raw = input("Введите старт (YYYY.MM.DD HH:MM) или (HH:MM): ")

            try:
                dt = parse_datetime_input(raw)
                step = input("Шаг (мин, default=2): ").strip()
                step = int(step) if step else 2

                generator = TimeGenerator(dt, step)
                print("Готово.\n")

            except ValueError as e:
                print(e)


        else:
            print("Неверный ввод.\n")


def parse_datetime_input(raw: str) -> datetime:
    raw = raw.strip()

    # полный формат
    try:
        return datetime.strptime(raw, "%Y.%m.%d %H:%M")
    except ValueError:
        pass

    # только время - берём сегодняшнюю дату
    try:
        time_part = datetime.strptime(raw, "%H:%M").time()
        today = datetime.now()
        return datetime(
            year=today.year,
            month=today.month,
            day=today.day,
            hour=time_part.hour,
            minute=time_part.minute
        )
    except ValueError:
        raise ValueError("Неверный формат. Используй HH:MM или YYYY.MM.DD HH:MM\n")