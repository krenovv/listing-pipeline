import re
from core.tag_data import TAGS_DICT

TYPES = [
    "Александрит", "Аметист", "Аметрин", "Аммолит", "Андалузит", "Андезин", "Адуляр",
    "Апатит", "Аквамарин", "Берил", "Бирюза", "Грандидерьит", "Гранат", "Диаспор",
    "Жемчуг", "Изумруд", "Иолит", "Кианит", "Коралл", "Кунцит", "Кварц", "Оникс", "Опал",
    "Перидот", "Рубин", "Сапфир", "Сфен", "Танзанит", "Топаз", "Фианит", "Турмалин",
    "Флюорит", "Циркон", "Цитрин", "Морганит", "Лабрадорит", "Хромдиопсид", "Шпинель",
    "Кольцо", "Серьги", "Кулон", "Брошь", "Комплект", "Микс", "Амулет", "Колье", "Браслет",
    "Необработанный", "Перстень"
]


def detect_type(text: str) -> str | None:
    for t in TYPES:
        if re.search(rf"\b{t}\b", text, re.IGNORECASE):
            return t
    return None


def generate_default_tags(item_type: str) -> str:
    return (
        f"{item_type}, {item_type}ы, Природный {item_type}, Натуральный {item_type}, "
        f"{item_type} Природный, {item_type} Натуральный, Купить {item_type}, "
        f"Ювелирный {item_type}, Драгоценный {item_type}, Негретый {item_type}, "
        f"Камень, Камни, IF, VVS, Корунд, Распродажа, С Рубля, Аукцион, Редкость, "
        f"Камень Природный, Камень Натуральный, Минерал, Коллекция"
    )


def trim_tags(tags: str, max_length: int = 300) -> str:
    if len(tags) <= max_length:
        return tags

    parts = tags.split(", ")
    result = []

    for part in parts:
        candidate = ", ".join(result + [part])
        if len(candidate) > max_length:
            break
        result.append(part)

    return ", ".join(result)


def generate_tags(text: str) -> str:
    item_type = detect_type(text)

    if not item_type:
        raise ValueError("Не удалось определить тип товара из текста")

    key = item_type.lower()

    if key in TAGS_DICT:
        tags = TAGS_DICT[key]
    else:
        tags = generate_default_tags(item_type)

    return trim_tags(tags)