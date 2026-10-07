#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Деплой HTML-версии книги на thinkred.ru/library по FTP (запускается из GitHub Actions:
локальная сеть режет исходящий 21-й порт). Аналог ml-research-assistant/scripts/ftp_deploy.py.
Upload-only; перед перезаписью удалённая версия уходит в backup/ (артефакт запуска).
Использование: python scripts/ftp_deploy.py <локальный каталог> <удалённый каталог>
"""
import sys, os, datetime as dt
from ftplib import FTP
from pathlib import Path

LOCAL_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("site_out")
REMOTE_DIR = (sys.argv[2] if len(sys.argv) > 2 else "/library").rstrip("/")
BACKUP_DIR = Path("backup")
HOSTS = [h.strip() for h in os.environ.get("FTP_HOSTS", "").split(",") if h.strip()]
USER = os.environ.get("FTP_USER", "")
PWD = os.environ.get("FTP_PASS", "")
if not (HOSTS and USER and PWD):
    raise SystemExit("FTP_HOSTS / FTP_USER / FTP_PASS не заданы")
if not LOCAL_DIR.is_dir():
    raise SystemExit(f"нет каталога {LOCAL_DIR}")

def connect():
    last = None
    for host in HOSTS:
        try:
            ftp = FTP(); ftp.connect(host, 21, timeout=60); ftp.login(USER, PWD)
            print(f"подключились: {host}")
            return ftp
        except Exception as e:
            print(f"{host}: недоступен ({type(e).__name__}: {e})")
            last = e
    raise SystemExit(f"FTP недоступен: {type(last).__name__}")

def main():
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    ftp = connect()
    files = sorted(p for p in LOCAL_DIR.iterdir() if p.is_file() and p.suffix == ".html")
    print(f"к загрузке в {REMOTE_DIR}: {[p.name for p in files]}")
    failed = []
    for lp in files:
        remote = f"{REMOTE_DIR}/{lp.name}"
        BACKUP_DIR.mkdir(exist_ok=True)
        bak = BACKUP_DIR / f"{stamp}-{lp.name}"
        try:
            with bak.open("wb") as f:
                ftp.retrbinary(f"RETR {remote}", f.write)
        except Exception:
            pass  # файла ещё нет — нормально
        with open(lp, "rb") as f:
            ftp.storbinary(f"STOR {remote}", f)
        size = ftp.size(remote)
        ok = size == lp.stat().st_size
        print(f"загружен {remote}: {size} байт [{'ok' if ok else 'РАЗМЕР СБОЙ'}]")
        if not ok:
            failed.append(lp.name)
    ftp.quit()
    if failed:
        raise SystemExit(f"сбой размера: {failed}")
    print("готово")

if __name__ == "__main__":
    main()
