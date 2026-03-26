def generate_certificate_text(raw: str) -> str:
    """
    Форматирует строку из таблицы в текст для сертификата (CorelDRAW).
    """

    lines = [ln for ln in raw.splitlines() if ln.strip() != ""]
    if not lines:
        return ""

    parts = lines[0].split("\t")

    while len(parts) < 12:
        parts.append("")

    lot_id = parts[0]
    stone = parts[2]
    color = parts[3]
    shape = parts[4]
    carat = parts[5]
    size = parts[6]
    clarity = parts[7]
    origin = parts[10]
    price = parts[11]

    output_lines = [
        lot_id,
        stone,
        color,
        carat,
        size,
        shape,
        clarity,
        origin,
        f"{price} US dollars".strip(),
    ]

    return "\r\n".join(output_lines)