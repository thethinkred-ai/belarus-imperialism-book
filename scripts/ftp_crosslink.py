#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Перелинковка книги: баннер-ссылка на /library/belarus-imperialism.html
в страницу Морозовой и в рецензию в блоге. Идемпотентно: если ссылка уже есть — пропуск.
Запуск из GitHub Actions (env FTP_*)."""
import os, io
from ftplib import FTP

HOSTS = [h.strip() for h in os.environ.get("FTP_HOSTS", "").split(",") if h.strip()]
USER = os.environ.get("FTP_USER", "")
PWD = os.environ.get("FTP_PASS", "")
BOOK_URL = "https://thinkred.ru/library/belarus-imperialism.html"

BANNER = (
    '<div style="max-width:900px;margin:26px auto 8px;padding:16px 20px;'
    'background:rgba(225,29,42,.08);border:1px solid #f5c2c5;border-left:4px solid #e11d2a;'
    'border-radius:12px;font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;'
    'font-size:15px;line-height:1.55">\n'
    '  <b>Ответ ThinkRed на эту книгу:</b> наше исследование '
    f'<a href="{BOOK_URL}" style="color:#e11d2a;font-weight:600">«Место современной '
    'Республики Беларусь в системе мирового империализма»</a> — критерий классификации, '
    'построенный до эмпирики (по мотивам нашей рецензии), контуры накопления, классы '
    'и проект программных тезисов. 2026, черновик v0.6, открытое рецензирование.\n'
    '</div>\n'
)

TARGETS = [
    ("/library/morozova.html", "</body>"),
    ("/blog/retsenziya-mesto-rossii-v-imperializme.html", "</body>"),
]

def connect():
    for host in HOSTS:
        try:
            ftp = FTP(); ftp.connect(host, 21, timeout=60); ftp.login(USER, PWD)
            print(f"подключились: {host}")
            return ftp
        except Exception as e:
            print(f"{host}: {e}")
    raise SystemExit("FTP недоступен")

ftp = connect()
for remote, anchor in TARGETS:
    buf = io.BytesIO()
    try:
        ftp.retrbinary(f"RETR {remote}", buf.write)
        src = buf.getvalue().decode("utf-8", errors="strict")
    except Exception as e:
        print(f"{remote}: пропущен ({e})")
        continue
    if BOOK_URL in src:
        print(f"{remote}: ссылка уже есть")
        continue
    if anchor not in src:
        print(f"{remote}: якорь {anchor!r} не найден — пропуск (безопасность)")
        continue
    patched = src.replace(anchor, BANNER + anchor, 1)
    ftp.storbinary(f"STOR {remote}", io.BytesIO(patched.encode("utf-8")))
    os.makedirs("backup", exist_ok=True)
    with open(os.path.join("backup", remote.replace("/", "_")), "wb") as f:
        f.write(buf.getvalue())
    print(f"{remote}: баннер добавлен (бэкап в артефакте)")
ftp.quit()
print("готово")
