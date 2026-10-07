#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Обновление /sitemap.xml на thinkred.ru: добавляет URL книги, если их ещё нет.
Запускается из GitHub Actions (env FTP_* как у ftp_deploy.py)."""
import os, io, re
from ftplib import FTP
from pathlib import Path

HOSTS = [h.strip() for h in os.environ.get("FTP_HOSTS", "").split(",") if h.strip()]
USER = os.environ.get("FTP_USER", "")
PWD = os.environ.get("FTP_PASS", "")
BASE = "https://thinkred.ru/library/"
FILES = ["belarus-imperialism.html"] + [f"bel-g{i:02d}.html" for i in range(1, 15)] + \
        ["bel-zakl.html", "bel-pril-a.html"]
REMOTE = "/sitemap.xml"

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
buf = io.BytesIO()
try:
    ftp.retrbinary(f"RETR {REMOTE}", buf.write)
    src = buf.getvalue().decode("utf-8")
    print(f"sitemap получен: {len(src)} байт")
except Exception as e:
    raise SystemExit(f"не удалось скачать {REMOTE}: {e}")

changed = False
for f in FILES:
    url = BASE + f
    if url in src:
        continue
    entry = f"  <url><loc>{url}</loc><changefreq>weekly</changefreq><priority>0.7</priority></url>\n"
    if "</urlset>" in src:
        src = src.replace("</urlset>", entry + "</urlset>")
        changed = True
        print("+", url)

if changed:
    data = src.encode("utf-8")
    ftp.storbinary(f"STOR {REMOTE}", io.BytesIO(data))
    Path("backup").mkdir(exist_ok=True)
    (Path("backup") / "sitemap-previous.xml").write_bytes(buf.getvalue())
    print(f"sitemap обновлён и сохранён ({len(data)} байт)")
else:
    print("изменений нет")
ftp.quit()
