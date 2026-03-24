import pyperclip
from datetime import datetime

from core.formatter import format_title
from core.tags import generate_tags
from core.parser import parse_lots
from utils.datetime_tools import TimeGenerator


def run_interactive():
    generator = None
    last_title = None

    print("=== LISTING PIPELINE ===")

    while True:
        print("\nНажмите Enter для работы с лотом")
        print("Или выберите пункт:")
        print("1. Форматировать название")
        print("2. Получить время")
        print("3. Сгенерировать теги")
        print("4. Парсинг лотов")
        print("5. Настроить время")
        print("0. Выход")

        choice = input(">>> ").strip()

        # === WORKFLOW MODE (Enter) ===
        if choice == "":
            raw = pyperclip.paste()

            if not raw:
                print("Буфер пуст.")
                continue

            # 1. Форматирование
            formatted = format_title(raw)
            pyperclip.copy(formatted)
            last_title = formatted

            print("\nНазвание:")
            print(formatted)

            input("\nEnter → получить время")

            # 2. Время
            if not generator:
                print("Сначала настройте время (пункт 5).")
                continue

            next_time = generator.next()
            pyperclip.copy(next_time)

            print("Время:")
            print(next_time)

            input("\nEnter → получить теги")

            # 3. Теги
            try:
                tags = generate_tags(last_title)
                pyperclip.copy(tags)

                print("Теги:")
                print(tags)

            except Exception as e:
                print(f"Ошибка генерации тегов: {e}")

            continue

        # === MENU MODE ===

        elif choice == "1":
            text = input("Введите текст: ")
            result = format_title(text)
            pyperclip.copy(result)
            print(result)

        elif choice == "2":
            if not generator:
                print("Сначала настройте время (пункт 5).")
            else:
                result = generator.next()
                pyperclip.copy(result)
                print(result)

        elif choice == "3":
            if not last_title:
                print("Нет сохранённого названия.")
            else:
                try:
                    result = generate_tags(last_title)
                    pyperclip.copy(result)
                    print(result)
                except Exception as e:
                    print(f"Ошибка: {e}")

        elif choice == "4":
            text = input("Вставьте текст лотов: ")
            result = parse_lots(text)

            print("\n==========")
            for i, item in enumerate(result["items"], 1):
                print(f"{i}. {item}")

        elif choice == "5":
            raw = input("Введите старт (YYYY.MM.DD HH:MM) или (HH:MM): ")

            try:
                dt = parse_datetime_input(raw)
                step = input("Шаг (мин, default=2): ").strip()
                step = int(step) if step else 2

                generator = TimeGenerator(dt, step)
                print("Готово.")

            except ValueError as e:
                print(e)

        elif choice == "0":
            print("Выход.")
            break

        else:
            print("Неверный ввод.")


def parse_datetime_input(raw: str) -> datetime:
    raw = raw.strip()

    # полный формат
    try:
        return datetime.strptime(raw, "%Y.%m.%d %H:%M")
    except ValueError:
        pass

    # только время → берём сегодняшнюю дату
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
        raise ValueError("Неверный формат. Используй HH:MM или YYYY.MM.DD HH:MM")