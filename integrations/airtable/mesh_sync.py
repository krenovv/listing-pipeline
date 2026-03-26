import os, re, time
from urllib.parse import urljoin
import requests
from pyairtable.api import Api




def fetch_html(url: str) -> str:
    r = requests.get(url, headers={"User-Agent": UA, "Accept-Language": "ru,en;q=0.8"},
                     timeout=HTTP_TIMEOUT, allow_redirects=True)
    r.raise_for_status()
    return r.text

def re_pick(pattern, text, flags=re.I|re.S):
    m = re.search(pattern, text, flags)
    return m.group(1).strip() if m else None

def pick_og(html, key):
    # <meta property="og:title" content="...">
    return re_pick(rf'<meta[^>]+(?:property|name)=["\']og:{re.escape(key)}["\'][^>]*?content=["\']([^"\']+)["\']', html)

def pick_title(html):
    return re_pick(r'<title[^>]*>(.*?)</title>', html)

def pick_first_img(html, base_url):
    src = re_pick(r'<img[^>]+src=["\']([^"\']+)["\']', html)
    if not src:
        return None
    try:
        return urljoin(base_url, src)
    except Exception:
        return None

def clean_title(t):
    if not t: return t
    t = re.sub(r'\s+', ' ', t).strip()
    for sep in (" | ", " — ", " – ", " • "):
        if sep in t:
            t = t.split(sep)[0].strip()
            break
    return t


def sync_meshok_to_airtable():
    AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")
    BASE_ID = os.getenv("AIRTABLE_BASE")
    TABLE_NAME = os.getenv("AIRTABLE_TABLE")

    if not AIRTABLE_TOKEN or not BASE_ID or not TABLE_NAME:
        raise ValueError("Airtable config is not set. Check environment variables.")

    FIELD_LINK = "Ссылка"
    FIELD_TITLE = "Название"
    FIELD_PHOTO = "Фото"

    MAX_RECORDS_PER_RUN = 200  # здравый предел
    HTTP_TIMEOUT = 20
    SLEEP_BETWEEN_BATCHES = 0.5  # лимит 5 rps

    UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
          "(KHTML, like Gecko) Chrome/124 Safari/537.36")

    api = Api(AIRTABLE_TOKEN)
    table = api.table(BASE_ID, TABLE_NAME)

    FIELD_PHOTO_URL = "Фото_URL"   # тип URL
    FIELD_STATUS    = "Статус"     # тип Single line text

    # Нужен ли прокси для загрузки в Attachment
    def needs_proxy(u: str) -> bool:
        if not u:
            return False
        host = u.lower()
        bad_fragments = (
            "meshok",
            "ebaystatic",
            "avatars.",
            "fbcdn",
            "vkuser",
            "x-frame-options",
        )
        return any(b in host for b in bad_fragments)

    # 1) Выберем кандидатов: есть ссылка и нет названия
    formula = f"AND(NOT({{{FIELD_LINK}}} = ''), {{{FIELD_TITLE}}} = '')"
    records = table.all(formula=formula, page_size=100)
    print(f"Найдено кандидатов: {len(records)}")
    if not records:
        return

    work = records[:MAX_RECORDS_PER_RUN]
    updates = []

    for rec in work:
        rid = rec["id"]
        fields = rec.get("fields", {})
        link = fields.get(FIELD_LINK)
        if isinstance(link, list):
            link = link[0] if link else ""
        print(f"\n=> Обрабатываю {rid}, ссылка: {link}")

        payload = {}
        status  = "no_changes"

        try:
            html = fetch_html(link)
            title = pick_og(html, "title") or pick_title(html)
            img = pick_og(html, "image") or pick_first_img(html, link)
            if img:
                # делаем абсолютной на базе страницы лота
                img = urljoin(link, img)
                # у Meshok миниатюры вида .208x208.jpg, оставляем только .jpg
                img = re.sub(r'\.\d+x\d+\.jpg$', '.jpg', img)
            title = clean_title(title)

            if title:
                payload[FIELD_TITLE] = title
                status = "title_ok"

            # Всегда сохраняем URL
            payload["Фото_URL"] = img if img else ""
            if img:
                payload["Фото"] = [{"url": img}]

            # URL всегда пишем для дебага и экономии места
            if FIELD_PHOTO_URL is not None:
                payload[FIELD_PHOTO_URL] = img or ""

            # Attachment: прямой url или через прокси, если Мешок лагает
            attachment_url = None
            if img:
                attachment_url = img
                if needs_proxy(img):
                    from urllib.parse import quote
                    attachment_url = f"https://images.weserv.nl/?url={quote(img, safe='')}&output=jpg"

            if attachment_url:
                payload[FIELD_PHOTO] = [{"url": attachment_url}]


        except Exception as e:
            print(f"   Ошибка: {e}")
            status = f"error: {e}"

        # В любом случае ставим статус
        payload[FIELD_STATUS] = status
        updates.append({"id": rid, "fields": payload})
        time.sleep(0.1)


    # 2) Отправим апдейты батчами по 10
    updated_total = 0
    for i in range(0, len(updates), 10):
        batch = updates[i:i+10]
        res = table.batch_update(batch)
        updated_total += len(res)
        print(f"   Отправлен батч {i//10+1}, записей: {len(res)}")
        time.sleep(0.4)

    print(f"\nИТОГО: отправлено обновлений (вкл. статус): {updated_total} для {len(work)} записей")

    # 3) Контрольное чтение первой изменённой записи
    try:
        test_id = work[0]["id"]
        fresh = table.get(test_id)
        print("\nПеречитал первую запись после апдейта:")
        print(fresh["fields"])
    except Exception as e:
        print("Не удалось перечитать запись:", e)