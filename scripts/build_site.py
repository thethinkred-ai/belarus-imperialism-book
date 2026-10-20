# -*- coding: utf-8 -*-
"""Сборка публикационной HTML-версии книги для thinkred.ru/library.

Стиль — по образцу библиотеки ThinkRed (bezrukova.html/morozova.html):
- индексная страница с плашками-карточками на каждую главу (details с параграфами);
- отдельная страница на главу: сайтбар, крошка, статья, prev/next, футер;
- JSON-LD Book; SEO-мета; honesty-плашка о статусе черновика v0.7.

Запуск:  python scripts/build_site.py   →  site_out/*.html
"""
import re, os, json, html as html_mod
import sys as _sys
_sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import diagrams
import widgets

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CH = os.path.join(ROOT, "chapters")
OUT = os.path.join(ROOT, "site_out")
os.makedirs(OUT, exist_ok=True)

BOOK_TITLE = "Место современной Республики Беларусь в системе мирового империализма"
BOOK_SLUG = "belarus-imperialism.html"
BASE = "https://thinkred.ru/library/"
VERSION_NOTE = ("черновик v0.8, часть I (экономическая); политическая часть издаётся отдельной брошюрой; публикация в развитии. Места, отмеченные [задание], требуют "
                "документального подтверждения — реестр открыт ({n_src}, {n_clm}).")

# (файл, выходной html, короткое имя для навигации, описание для плашки)
PARTS = [
 ("00-vvedenie.md", "bel-v00.html", "Введение",
  "Актуальность, метод и адресаты: зачем нужна марксистская классификация Беларуси и как устроено исследование"),
 ("01-kategorii-i-kriterij.md", "bel-g01.html", "Глава 1. Категории и критерий",
  "Пять признаков Ленина как система отношений; критерий К + В + Г + Р; две оси; четыре гипотезы; семь ловушек"),
 ("02-metod-i-periodizaciya.md", "bel-g02.html", "Глава 2. Метод, источники и периодизация",
  "Цепочка доказательства «показатель → отношение → механизм»; свежие данные 2014–2026; сравнительный контроль"),
 ("03-sobstvennost-i-centry-kontrolya.md", "bel-g03.html", "Глава 3. Собственность, труд и центры контроля",
  "Карта контуров накопления: госконтур, российский капитал, частные; карточки К + В + Г + Р по семи контурам"),
 ("04-gosudarstvo-i-organizaciya-nakopleniya.md", "bel-g04.html", "Глава 4. Государство и организация накопления",
  "Госкапитализм: мобилизация через бюджет, кредит и принуждение; директорат; «социальное государство» как компромисс"),
 ("05-banki-kredit-finansovyj-kapital.md", "bel-g05.html", "Глава 5. Банки, кредит и финансово-промышленные связи",
  "Финансовый капитал в государственной форме; национальная олигархия не установлена; госдолг как канал зависимости"),
 ("06-vosproizvodstvo-trud-vnutrennij-rynok.md", "bel-g06.html", "Глава 6. Воспроизводство, труд и внутренний рынок",
  "Стоимость рабочей силы частично вне зарплаты; GINI 24 как компромисс, не социализм; демография и миграция"),
 ("07-promyshlennye-i-resursnye-monopolii.md", "bel-g07.html", "Глава 7. Промышленные и ресурсные монополии",
  "Калийный картель BPC и мировая олигопсония; нефтепереработка; машиностроение — сопоставимые кейсы"),
 ("08-agroprom-it-transport-logistika.md", "bel-g08.html", "Глава 8. Агропром, IT, транспорт и логистика",
  "Три формы включения в чужие цепи: монопсония РФ, аутсорсинг с эмигрировавшим центром прибыли, рухнувший транзит"),
 ("09-vyvoz-i-vvoz-kapitala.md", "bel-g09.html", "Глава 9. Вывоз и ввоз капитала",
  "flow/stock/income/balance разведены; баланс первичных доходов — фон, не тест; итог по размеру данных"),
 ("10-mezhdunarodnaya-zavisimost-i-integraciya.md", "bel-g10.html", "Глава 10. Международная зависимость и интеграция",
  "Три уровня зависимости; матрица узлов со статусами; три кейса конфликтов; санкционный сдвиг А/Б/В"),
 ("11-gosudarstvennaya-sila-vpk.md", "bel-g11.html", "Глава 11. Государственная сила, безопасность и ВПК",
  "Военно-политическая интеграция установлена; экономическое присвоение — гипотеза [Л-5R]; расходы 2024–2025"),
 ("12-sintez-i-klassifikaciya.md", "bel-g12.html", "Глава 12. Синтез и классификация",
  "Статусы знаний; вердикты [Л-1…Л-5] после рецензий; тип III с пониженной уверенностью; таблица опровержимости"),
 ("zaklyuchenie.md", "bel-zakl.html", "Заключение", "Таблица доказанности; предварительный ответ; лакуны и продолжение работы"),
 ("prilozhenie-b-reestr.md", "bel-pril-b.html", "Приложение Б. Реестр SRC и CLM: как читать ссылки книги",
  "Как читать ссылки книги; открытый реестр: {n_src} и {n_clm} со статусами"),
 ("prilozhenie-v-kak-pisalas.md", "bel-pril-v.html", "Приложение В. Как писалась эта книга",
  "Методологический ассистент, внешнее рецензирование GPT-6 Astra Pro ($5.54), найденные и исправленные ошибки, честный список лакун"),
 ("prilozhenie-g-pravovoj-risk.md", "bel-pril-g.html", "Приложение Г. Правовой риск-обзор (законодательство РБ об экстремизме)",
  "Сверка 2026-10-09: источники в перечнях госорганов, содержательные тезисы повышенного внимания, юрисдикция хостинга и доступность из РБ, принятые и возможные меры; не юридическая консультация"),
]

# ---------------- markdown → html ----------------

def slugify(s):
    s = s.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    s = re.sub(r"[\s_]+", "-", s)
    return s.strip("-")

def inline(s):
    s = html_mod.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\w)\*([^*\n]+)\*(?!\w)", r"<em>\1</em>", s)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', s)
    # автоссылки на открытый реестр: SRC-013 / CLM-033 -> registry.html#ID
    s = re.sub(r"\b((?:SRC|CLM)-\d{2,3})\b", r'<a class="ref" href="registry.html#\1">\1</a>', s)
    s = s.replace("sources/registry.json", '<a href="registry.html">sources/registry.json</a>')
    return s

def md_to_html(md):
    lines_ = md.splitlines()
    out, ids = [], {}
    def hid(text):
        base = slugify(text)
        n = ids.get(base, 0); ids[base] = n + 1
        return base if n == 0 else f"{base}-{n}"
    BOLD_LINE = re.compile(r"^\*\*[^*].*\*\*:?\s*$")
    BLOCK_START = re.compile(r"^(#{1,4}\s|>|\||```|\s*[-*]\s+\S|\s*\d+[.)]\s+\S|\s*(-{3,}|\*{3,})\s*$)")
    i = 0
    while i < len(lines_):
        ln = lines_[i]
        if ln.startswith("```"):
            i += 1; code = []
            while i < len(lines_) and not lines_[i].startswith("```"):
                code.append(lines_[i]); i += 1
            out.append("<pre>" + html_mod.escape("\n".join(code)) + "</pre>"); i += 1; continue
        m = re.match(r"^(#{1,4})\s+(.*)$", ln)
        if m:
            lvl = len(m.group(1)); text = m.group(2).strip()
            out.append(f'<h{lvl} id="{hid(text)}">' + inline(text) + f"</h{lvl}>")
            i += 1; continue
        if re.match(r"^\s*(-{3,}|\*{3,})\s*$", ln):
            out.append("<hr/>"); i += 1; continue
        if ln.startswith(">"):
            q = []
            while i < len(lines_) and lines_[i].startswith(">"):
                q.append(re.sub(r"^>\s?", "", lines_[i])); i += 1
            out.append("<blockquote>" + inline(" ".join([x for x in q if x.strip()])) + "</blockquote>"); continue
        if ln.strip().startswith("|") and i + 1 < len(lines_) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines_[i+1]):
            rows = []
            while i < len(lines_) and lines_[i].strip().startswith("|"):
                cells = [c.strip() for c in lines_[i].strip().strip("|").split("|")]
                rows.append(cells); i += 1
            header, bodyr = rows[0], rows[2:]
            t = '<div class="tblwrap"><table><thead><tr>' + "".join(f"<th>{inline(c)}</th>" for c in header) + "</tr></thead><tbody>"
            for r in bodyr:
                t += "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>"
            out.append(t + "</tbody></table></div>"); continue
        m_u = re.match(r"^\s*[-*]\s+(.*)$", ln)
        m_o = re.match(r"^\s*(\d+)[.)]\s+(.*)$", ln)
        if m_u or m_o:
            ordered = bool(m_o)
            pat = re.compile(r"^\s*(\d+)[.)]\s+(.*)$") if ordered else re.compile(r"^\s*[-*]\s+(.*)$")
            items = [m_o.group(2) if m_o else m_u.group(1)]
            i += 1
            while i < len(lines_):
                s2 = lines_[i]
                mp = pat.match(s2)
                if mp:
                    items.append(mp.group(2) if ordered else mp.group(1)); i += 1
                elif s2.strip() and not BLOCK_START.match(s2) and not BOLD_LINE.match(s2.strip()):
                    items[-1] += " " + s2.strip(); i += 1  # перенос строки внутри пункта
                elif not s2.strip():
                    j = i
                    while j < len(lines_) and not lines_[j].strip(): j += 1
                    if j < len(lines_) and pat.match(lines_[j]):
                        i = j; continue  # список продолжается после пустой строки
                    break
                else:
                    break
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>")
            continue
        if not ln.strip():
            i += 1; continue
        if BOLD_LINE.match(ln.strip()):  # строка-заголовок требования — свой абзац
            out.append("<p>" + inline(ln.strip()) + "</p>"); i += 1; continue
        para = [ln.strip()]; i += 1
        while i < len(lines_) and lines_[i].strip() and not BLOCK_START.match(lines_[i]) and not BOLD_LINE.match(lines_[i].strip()):
            para.append(lines_[i].strip()); i += 1
        out.append("<p>" + inline(" ".join(para)) + "</p>")
    return "\n".join(out)


def render_widgets(body_html):
    def _wid(mo):
        item = widgets.ALL.get(mo.group(1))
        if not item:
            return ""
        return item[1]
    return re.sub(r"<p>\{\{WIDGET:(\w+)\}\}</p>", _wid, body_html)

def render_figures(body_html):
    def _fig(mo):
        fn, cap = diagrams.ALL.get(mo.group(1), (None, None))
        if not fn:
            return ""
        mno = re.match(r"(Рис\.\s*\d+\.\d+\.)\s*(.*)", cap, re.S)
        if mno:
            cap_html = ('<b class="fno">' + html_mod.escape(mno.group(1)) + "</b> "
                        + html_mod.escape(mno.group(2)))
        else:
            cap_html = html_mod.escape(cap)
        return f'<figure class="figure">{fn()}<figcaption>{cap_html}</figcaption></figure>'
    return re.sub(r"<p>\{\{SVG:(\w+)\}\}</p>", _fig, body_html)

def headings(md, lvl=2):
    res = []
    for ln in md.splitlines():
        m = re.match(r"^#{%d}\s+(.*)$" % lvl, ln)
        if m:
            t = m.group(1).strip()
            res.append((slugify(t), t))
    return res

# ---------------- шаблоны ----------------

SITEBAR = '''<div class="sitebar"><div class="in">
  <a class="logo" href="https://thinkred.ru/">Think<span>Red</span></a>
  <nav>
    <a href="https://thinkred.ru/course/">Курс</a>
    <a href="https://thinkred.ru/blog/">Блог</a>
    <a href="https://thinkred.ru/assistant/">Ассистент</a>
    <a href="/library/{slug}">Оглавление книги</a>
    <a href="/library/bezrukova.html">Безрукова</a>
    <a href="/library/registry.html">Реестр SRC/CLM</a>
    <a href="https://t.me/thinkred_marx" target="_blank" rel="noopener">Telegram</a>
  </nav>
</div></div>'''

SITEFOOT = '''<div class="sitefoot">
  © ThinkRed · 2026 ·
  <a href="https://thinkred.ru/">Главная</a> ·
  <a href="https://thinkred.ru/library/morozova.html">Книга Е. Морозовой</a> ·
  <a href="https://thinkred.ru/blog/retsenziya-mesto-rossii-v-imperializme.html">Рецензия на неё</a> ·
  <a href="https://thinkred.ru/privacy/">Конфиденциальность</a>
</div>'''

CH_CSS = """<style>
:root{--fg:#1f2328;--muted:#5b636e;--bg:#ffffff;--card:#f6f7f9;--line:#e3e6ea;--hair:#eef0f3;--accent:#e11d2a;--accent-soft:rgba(225,29,42,.08)}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--fg);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue","Noto Sans",Arial,"Noto Sans Cyrillic",sans-serif;font-size:17px;line-height:1.7;-webkit-font-smoothing:antialiased}
.layout{display:block;max-width:860px;margin:0 auto;padding:0 18px 40px}
.hero{padding:44px 0 24px;border-bottom:1px solid var(--line);margin-bottom:8px}
.hero h1{font-size:28px;line-height:1.25;margin:0 0 10px}
.hero p{margin:0;color:var(--muted);font-size:15px}
article{max-width:760px}
h1,h2,h3{line-height:1.25;scroll-margin-top:16px}
h1{font-size:26px;margin:44px 0 16px}
article>h1:first-child{margin-top:8px}
h2{font-size:21px;margin:34px 0 12px}
h3{font-size:17.5px;margin:26px 0 10px;color:#2b3138}
a{color:var(--accent)}
p{margin:0 0 14px}
blockquote{margin:18px 0;padding:12px 18px;border-left:3px solid var(--accent);background:var(--accent-soft);border-radius:0 10px 10px 0;color:#2a313b;font-size:15.5px;line-height:1.65}
.tblwrap{margin:20px 0;border:1px solid var(--line);border-radius:12px;background:#fff;overflow-x:auto;-webkit-overflow-scrolling:touch}
table{border-collapse:separate;border-spacing:0;width:100%;font-size:14.2px;min-width:520px}
thead th{background:var(--card);font-weight:700;font-size:12.6px;color:#3c434d;text-align:left;padding:10px 12px;border-bottom:2px solid #d9dde3;white-space:nowrap;vertical-align:bottom}
tbody td{padding:9px 12px;border-bottom:1px solid var(--hair);vertical-align:top;line-height:1.55}
tbody tr:last-child td{border-bottom:0}
tbody tr:nth-child(even) td{background:#fafbfd}
tbody tr:hover td{background:#f4f7ff}
td code,th code{white-space:nowrap;background:transparent;padding:0;font-size:.92em;color:#3c434d;font-weight:600}
code{background:var(--card);border-radius:5px;padding:1px 6px;font-size:.9em}
pre{background:#0f1115;color:#e6edf3;padding:14px;border-radius:10px;overflow:auto;font-size:13px;white-space:pre-wrap}
hr{border:0;border-top:1px solid var(--line);margin:34px 0}
.status{background:#fff8e6;border:1px solid #f0ddb0;color:#7a5a00;border-radius:10px;padding:10px 14px;font-size:13.5px;margin:14px 0}
.crumb{max-width:860px;margin:0 auto;padding:14px 18px 0;font-size:13px;color:#5b636e}
.crumb a{color:var(--accent);text-decoration:none}
.pnav{display:flex;justify-content:space-between;gap:12px;max-width:860px;margin:34px auto 0;padding:0 18px 30px}
.pnav a{flex:1;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 14px;text-decoration:none;color:var(--accent);font-size:14px;font-weight:600}
.pnav a.next{text-align:right}
.pnav a:hover{border-color:var(--accent)}
.pnav a small{display:block;color:var(--muted);font-weight:400;font-size:11.5px}
.backtop{display:block;text-align:center;margin:30px auto 10px;color:var(--muted);font-size:13px;text-decoration:none}
.sitebar{background:#fff;border-bottom:1px solid rgba(17,24,39,.08)}
.sitebar .in{max-width:860px;margin:0 auto;padding:12px 18px;display:flex;align-items:center;gap:18px;flex-wrap:wrap}
.sitebar .logo{font-weight:800;font-size:20px;text-decoration:none;color:#111118;font-family:Georgia,serif}
.sitebar .logo span{color:#e11d2a}
.sitebar nav{display:flex;gap:14px;flex-wrap:wrap}
.sitebar nav a{color:#4a4a5a;text-decoration:none;font-size:14px}
.sitebar nav a:hover{color:#e11d2a}
.sitefoot{border-top:1px solid rgba(17,24,39,.08);background:#fff;margin-top:40px;padding:20px 18px;text-align:center;color:#7a7a8a;font-size:13px}
.sitefoot a{color:#4a4a5a;text-decoration:none;margin:0 8px}
.figure{margin:26px 0;background:#fcfdfe;border:1px solid var(--hair);border-radius:14px;padding:16px 16px 4px}
.figure svg{display:block;width:100%;height:auto}
.figure figcaption{font-size:13px;color:var(--muted);margin-top:12px;padding:10px 4px 10px;border-top:1px solid var(--hair);line-height:1.55}
.figure .fno{color:var(--fg);font-weight:700}
a.ref{white-space:nowrap}
.badge{display:inline-block;border-radius:999px;padding:2px 10px;font-size:12px;white-space:nowrap;border:1px solid rgba(16,24,40,.07)}
.b-ok{background:#e7f5ee;color:#047857}
.b-part{background:#fff4e0;color:#9a6700}
.b-na{background:#eef0f3;color:#5b636e}
.b-no{background:#fde8e8;color:#c11d2a}
.src{border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin:12px 0}
.src .m{color:var(--muted);font-size:13px;margin:4px 0}
.src div{font-size:14px}
.widget{margin:26px 0;border:1px solid var(--line);border-radius:16px;background:#fff;padding:18px 20px;box-shadow:0 1px 3px rgba(16,24,40,.05)}
.widget h4{margin:0 0 8px;font-size:15.5px;display:flex;align-items:baseline;gap:9px}
.widget h4::before{content:"";width:9px;height:9px;border-radius:3px;background:var(--accent);flex:0 0 auto;transform:translateY(1px)}
.widget .hint{font-size:13.5px;color:var(--muted);margin:0 0 14px;line-height:1.55}
.wrow{display:flex;align-items:center;gap:12px;margin:10px 0;flex-wrap:wrap}
.wrow label{flex:0 0 268px;font-size:13.8px;color:#333a44}
.wrow input[type=range]{flex:1 1 150px;accent-color:#2c5fc4;height:20px}
.wrow output{flex:0 0 64px;font-size:13px;font-variant-numeric:tabular-nums;background:var(--card);border:1px solid var(--hair);border-radius:8px;padding:2px 6px;text-align:center}
.wstatus{display:inline-flex;align-items:center;justify-content:center;gap:6px;min-width:126px;border-radius:999px;padding:3px 9px;font-size:11.5px;font-weight:600;border:1px solid transparent}
.wstatus::before{content:"●";font-size:8px;line-height:1}
.s-prov{background:#e9f7f0;color:#0b6e4f;border-color:#c4e8d6}
.s-na{background:#f1f3f6;color:#5b636e;border-color:#e0e3e8}
.s-ref{background:#fdecec;color:#b3252f;border-color:#f5c9c9}
.wverdict{margin-top:14px;background:#fbfcfe;border:1px solid var(--hair);border-left:3px solid var(--accent);border-radius:0 10px 10px 0;padding:12px 16px;font-size:14.5px;line-height:1.6}
.wbtns{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0}
.wbtns button{border:1px solid var(--line);background:#fff;border-radius:9px;padding:6px 13px;font-size:13px;cursor:pointer;color:#333a44;transition:border-color .15s,color .15s}
.wbtns button:hover{border-color:var(--accent);color:var(--accent)}
.wsel{font-size:13px;padding:5px 8px;border-radius:8px;border:1px solid var(--line);background:#fff;color:#333a44}
.wnote{font-size:12.5px;color:var(--muted);margin-top:10px}
@media (max-width:640px){.wrow label{flex:1 1 100%}}
@media print{.sitebar,.pnav,.backtop,.sitefoot,.crumb{display:none}}
</style>"""

def chapter_page(idx, title, body_html, next_ref, prev_ref):
    return f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{html_mod.escape(title)} — {html_mod.escape(BOOK_TITLE)} — ThinkRed</title>
<meta name="description" content="{html_mod.escape(title)} из книги «{html_mod.escape(BOOK_TITLE)}» (ThinkRed, черновик v0.8)."/>
<link rel="canonical" href="{BASE}bel-g{idx:02d}.html"/>
<link rel="icon" href="https://thinkred.ru/favicon.png"/>
{CH_CSS}
</head>
<body>
{SITEBAR.format(slug=BOOK_SLUG)}
<div class="crumb"><a href="/library/{BOOK_SLUG}">{html_mod.escape(BOOK_TITLE)}</a> → {html_mod.escape(title)}</div>
<div class="layout">
<article>
<div class="status">Черновик v0.8; публикация в развитии. Места <b>[задание]</b> требуют документального подтверждения. Ссылки <b>SRC-/CLM-</b> в тексте ведут в <a href="registry.html">открытый реестр</a>.</div>
{body_html}
</article>
</div>
<nav class="pnav">
{prev_ref}
{next_ref}
</nav>
<a class="backtop" href="/library/{BOOK_SLUG}">↑ Оглавление книги</a>
{SITEFOOT}
</body>
</html>
"""

# ---------------- сборка ----------------

built = []
# счётчики реестра — до сборки карточек: подставляются в VERSION_NOTE и описания PARTS;
# числа не вписываются руками, чтобы не расходиться с registry.json
_reg0 = json.load(open(os.path.join(ROOT, "sources", "registry.json"), encoding="utf-8"))
# ЧАСТЬ I (сайт) — только записи экономической части; политическая часть (гл. 13–14,
# прил. А) публикуется отдельной брошюрой и на сайте не показывается (прил. Г §Г.5 п. 0)
PART2_CLM_CH = {"13", "14", "ч. II", "ч. II (гл. 13)", "ч. II (гл. 14)"}
def _is_part2_clm(c):
    ch = str(c.get("chapter", "")).strip()
    return ch in PART2_CLM_CH or ch.startswith("прил.А") or ch.startswith("ч. II")
REG_CLM = [c for c in _reg0["claims"] if not _is_part2_clm(c)]
_part1_src = set()
for c in REG_CLM:
    _part1_src.update(c.get("sourceIds", []))
# плюс SRC, процитированные прямо в текстах части I
for _pf in PARTS:
    _pt = open(os.path.join(CH, _pf[0]), encoding="utf-8").read()
    _part1_src.update(re.findall(r"SRC-\d{3}", _pt))
REG_SRC = [s for s in _reg0["sources"] if s["id"] in _part1_src]
N_SRC, N_CLM = len(REG_SRC), len(REG_CLM)

def ru_plural(n, one, few, many):
    n = abs(n) % 100
    if 11 <= n <= 14:
        return many
    n %= 10
    return one if n == 1 else (few if 2 <= n <= 4 else many)

SRC_P = "%d %s" % (N_SRC, ru_plural(N_SRC, "источник", "источника", "источников"))
CLM_P = "%d %s" % (N_CLM, ru_plural(N_CLM, "утверждение", "утверждения", "утверждений"))
VERSION_NOTE = VERSION_NOTE.replace("{n_src}", SRC_P).replace("{n_clm}", CLM_P)

TYPE_RU = {"definition": "определение", "theoretical": "теоретическое", "textual": "текстуальное (цитата)",
           "causal": "причинное", "quantitative": "количественное", "empirical": "эмпирическое",
           "historical": "историческое", "normative": "нормативное"}

def registry_list_md():
    """Список источников части I для прил. Б §Б.6 (генерируется при сборке)."""
    rows = ["| ID | Источник | Тип | Годы |", "|---|---|---|---|"]
    for s in REG_SRC:
        rows.append("| %s | %s | %s | %s |" % (
            s["id"], s.get("title", ""), TYPE_RU.get(s.get("type", ""), s.get("type", "")),
            s.get("year", "")))
    return "\n".join(rows)

toc_cards = []
toc_app_cards = []
jsonld_parts = []
for n, (md_file, out_file, name, desc) in enumerate(PARTS):
    desc = desc.replace("{n_src}", SRC_P).replace("{n_clm}", CLM_P)
    md = open(os.path.join(CH, md_file), encoding="utf-8").read()
    if md_file == "prilozhenie-b-reestr.md":
        md = md.replace("{{REGISTRY_LIST}}", registry_list_md())
    # отрезать статус-строки (> Статус:...) в начале — они уходят в плашку/мета
    body = re.sub(r"^>\s*Статус:[^\n]*\n(>.*\n)*", "", md.lstrip("# " + md_file), count=0) if False else md
    body = re.sub(r"^(> Статус:[^\n]*(?:\n>[^\n]*)*)\n+", "", body, flags=re.M)
    body = re.sub(r"^# .+?\n", "", body, count=1)  # h1 страницы сгенерируем сами
    body_html = render_widgets(render_figures(md_to_html(body)))
    h1 = name
    body_html = f'<h1 id="{slugify(h1)}">{html_mod.escape(h1)}</h1>\n' + body_html

    prev_ref = next_ref = '<span style="flex:1"></span>'
    if n > 0:
        p = PARTS[n-1]
        prev_ref = f'<a href="{p[1]}"><small>← Предыдущий раздел</small>{html_mod.escape(p[2])}</a>'
    if n < len(PARTS) - 1:
        nx = PARTS[n+1]
        next_ref = f'<a class="next" href="{nx[1]}"><small>Следующий раздел →</small>{html_mod.escape(nx[2])}</a>'

    page = chapter_page(n + 1, h1, body_html, next_ref, prev_ref)
    # canonical для не-глав (закл./прилож.)
    page = page.replace(f'href="{BASE}bel-g{n+1:02d}.html"', f'href="{BASE}{out_file}"')
    open(os.path.join(OUT, out_file), "w", encoding="utf-8", newline="\n").write(page)
    built.append(out_file)

    paras = headings(body, 2)
    det = ""
    if paras:
        det = "<details><summary>Параграфы</summary><ul>" + "".join(
            f'<li><a href="{out_file}#{a}">{html_mod.escape(t)}</a></li>' for a, t in paras[:14]) + "</ul></details>"
    card = (f'<div class="toc-card"><b><a href="{out_file}">{html_mod.escape(name)}</a></b>'
            f"<span>{html_mod.escape(desc)}</span>{det}</div>")
    if out_file.startswith("bel-pril"):
        toc_app_cards.append(card)
    else:
        toc_cards.append(card)
    jsonld_parts.append({"@type": "Chapter", "name": name, "url": BASE + out_file})

# ---------------- страница реестра (registry.html) ----------------

STATUS_RU = {"supported": "подтверждено", "partial": "частично", "unverified": "не проверено",
             "refuted": "опровергнуто", "monitoring": "мониторинг", "controversial": "спорное"}
STATUS_CLS = {"supported": "b-ok", "partial": "b-part", "unverified": "b-na",
              "refuted": "b-no", "monitoring": "b-na", "controversial": "b-part"}

def build_registry_page():
    reg = json.load(open(os.path.join(ROOT, "sources", "registry.json"), encoding="utf-8"))
    # глава(i) каждого CLM — из цитирований CLM-xxx в текстах глав
    clm_chapters = {}
    ch_files = sorted(f for f in os.listdir(CH) if f.endswith(".md"))
    for f in ch_files:
        mnum = re.match(r"(\d{2})-", f)
        label = ({"13": "ч. II (гл. 13)", "14": "ч. II (гл. 14)"}.get(mnum.group(1), str(int(mnum.group(1)))) if mnum else
                 {"zaklyuchenie.md": "закл.", "prilozhenie-a-tezisy-programmy.md": "ч. II (прил. А)",
                  "prilozhenie-b-reestr.md": "прил.Б", "prilozhenie-v-kak-pisalas.md": "прил.В"}.get(f, f))
        text_f = open(os.path.join(CH, f), encoding="utf-8").read()
        ids_found = set(re.findall(r"CLM-\d{2,3}", text_f))
        # разворот диапазонов вида CLM-044…047 / CLM-033–035 (охват ≤ 12)
        for lo_s, hi_s in re.findall(r"CLM-(\d{2,3})\s*[\u2013\u2014\u2026-]{1,3}\s*(\d{2,3})", text_f):
            lo, hi = int(lo_s), int(hi_s)
            if 0 < hi - lo <= 12:
                ids_found.update("CLM-%03d" % k for k in range(lo, hi + 1))
        for cid in ids_found:
            clm_chapters.setdefault(cid, [])
            if label not in clm_chapters[cid]:
                clm_chapters[cid].append(label)
    src_cards = []
    # ключи конспектов (схема ассистента) → русские названия пунктов карточки
    NOTES_RU = {"concepts": "основные понятия", "positions": "положения", "theses": "тезисы",
                "facts": "факты", "authorHypotheses": "гипотезы автора", "conclusions": "выводы",
                "quotes": "цитаты", "remarks": "примечания", "tasks": "связь с задачами книги",
                "sections": "связь с параграфами", "link-status": "статус ссылки",
                "summary": "обзор"}
    for srcref in REG_SRC:
        notes = srcref.get("notes", {}) or {}
        nk = "".join(f"<div><b>{html_mod.escape(NOTES_RU.get(str(k), str(k)))}:</b> {html_mod.escape(str(v)[:400])}</div>"
                     for k, v in notes.items() if v)
        url = (f'<a href="{srcref["url"]}" target="_blank" rel="noopener">{html_mod.escape(srcref["url"])}</a>'
               if srcref.get("url") else "—")
        src_cards.append(
            f'<div class="src" id="{srcref["id"]}"><b><code>{srcref["id"]}</code> '
            f'{html_mod.escape(str(srcref.get("title","")))}</b>'
            f'<div class="m">{html_mod.escape(str(srcref.get("author","")))} · '
            f'{html_mod.escape(str(srcref.get("year","")))} · тип: {html_mod.escape(str(srcref.get("type","")))} · '
            f'надёжность: {html_mod.escape(str(srcref.get("reliability","")))}</div>'
            f'<div>{url}</div>{nk}</div>')
    rows = []
    for c in REG_CLM:
        cid = c["id"]
        st = c.get("status", "")
        st_ru = STATUS_RU.get(st, st or "—")
        st_cls = STATUS_CLS.get(st, "b-na")
        st_span = f'<span class="badge {st_cls}">{st_ru}</span>' if st else "—"
        ch_list = clm_chapters.get(cid, [])
        if not ch_list:
            m_note = re.search(r"гл\.\s*(\d+)", str(c.get("note", "")))
            if m_note:
                ch_list = [m_note.group(1)]
        chs = ", ".join(ch_list) or "—"
        srcs = " ".join(f'<a href="#{x}">{x}</a>' for x in c.get("sourceIds", []))
        srcs = srcs if srcs else '<span class="m">прямая привязка не заполнена — задание</span>'
        typ = TYPE_RU.get(c.get("type", ""), "")
        typ_html = f'<div class="m">тип: {typ}</div>' if typ else ""
        corr = ""
        if c.get("notes", {}).get("review-correction"):
            corr = ('<div class="m">правка по рецензии: '
                    + html_mod.escape(str(c["notes"]["review-correction"])) + '</div>')
        rows.append(f'<tr id="{cid}"><td><code>{cid}</code></td><td>{chs}</td>'
                    f'<td>{st_span}</td>'
                    f'<td>{html_mod.escape(str(c.get("text","")))}{typ_html}{corr}</td><td>{srcs}</td></tr>')
    head = ("<!doctype html>\n<html lang=\"ru\">\n<head>\n<meta charset=\"utf-8\"/>\n"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"/>\n"
            "<title>Реестр SRC и CLM — " + html_mod.escape(BOOK_TITLE) + " — ThinkRed</title>\n"
            "<meta name=\"description\" content=\"Открытый реестр книги: " + str(len(reg["sources"]))
            + " источников (SRC) и " + str(len(reg["claims"]))
            + " утверждений (CLM) со статусами доказательности и конспектами.\"/>\n"
            "<link rel=\"canonical\" href=\"" + BASE + "registry.html\"/>\n"
            "<link rel=\"icon\" href=\"https://thinkred.ru/favicon.png\"/>\n"
            + CH_CSS + "\n</head>\n<body>\n" + SITEBAR.format(slug=BOOK_SLUG) + "\n"
            "<div class=\"crumb\"><a href=\"/library/" + BOOK_SLUG + "\">" + html_mod.escape(BOOK_TITLE)
            + "</a> → Реестр SRC/CLM</div>\n<div class=\"layout\">\n<article>\n"
            "<h1 id=\"реестр-src-и-clm\">Реестр источников (SRC) и утверждений (CLM)</h1>\n"
            "<p>Каждая ссылка вида <a class=\"ref\" href=\"#SRC-013\">SRC-013</a> / "
            "<a class=\"ref\" href=\"#CLM-033\">CLM-033</a> в главах ведёт на якорь этой страницы. "
            "Реестр — экспорт <a href=\"https://thinkred.ru/assistant/\" target=\"_blank\" rel=\"noopener\">"
            "Методологического ассистента</a>; исходный JSON — "
            "<a href=\"https://github.com/thethinkred-ai/belarus-imperialism-book/blob/main/sources/registry.json\" "
            "target=\"_blank\" rel=\"noopener\">sources/registry.json</a> в репозитории книги.</p>\n"
            "<h2 id=\"источники-src\">Источники (SRC) — " + str(len(reg["sources"])) + "</h2>\n"
            "<p class=\"m\">Карточка источника: автор, год, тип, надёжность, ссылка на публикацию и конспект "
            "(основные понятия, факты, гипотезы автора, замечания). Реестр заполняется в ассистенте по мере работы над главами.</p>\n"
            + "".join(src_cards))
    page = (head
            + "\n<h2 id=\"утверждения-clm\">Утверждения (CLM) — " + str(len(reg["claims"])) + "</h2>\n"
            + "<p><b>Как читать таблицу.</b> <b>ID</b> — идентификатор утверждения, под которым оно цитируется "
            "в главах (CLM-033 и т.д.). <b>Главы</b> — где утверждение используется (собирается автоматически "
            "из текста глав при каждой сборке). <b>Статус</b> — состояние доказательности в реестре: "
            "<span class=\"badge b-ok\">подтверждено</span> — есть прямые источники; "
            "<span class=\"badge b-part\">частично</span> — источники покрывают часть утверждения; "
            "<span class=\"badge b-na\">не проверено</span> — формулировка внесена, проверка впереди. "
            "<b>Текст</b> — формулировка утверждения книги; "
            "строкой ниже — тип утверждения (определение, причинное, количественное и т.д.). "
            "<b>Источники</b> — SRC-id, на которые опирается утверждение (кликабельны, "
            "ведут в раздел выше); пометка «прямая привязка не заполнена — задание» означает, что связь "
            "конкретного SRC с этим утверждением ещё не проставлена в реестре — это открытые задания, "
            "а не отсутствие данных в принципе.</p>\n"
            "<table><thead><tr><th>ID</th><th>Главы</th><th>Статус</th><th>Текст утверждения</th><th>Источники</th></tr></thead><tbody>"
            + "".join(rows) + "</tbody></table>\n</article>\n</div>\n" + SITEFOOT + "\n</body>\n</html>\n")
    open(os.path.join(OUT, "registry.html"), "w", encoding="utf-8", newline="\n").write(page)
    return len(reg["sources"]), len(reg["claims"])


N_SRC, N_CLM = build_registry_page()
toc_app_cards.append(
    f'<div class="toc-card"><b><a href="registry.html">Реестр SRC и CLM — открытые данные книги</a></b>'
    f'<span>{SRC_P} и {CLM_P} со статусами (часть I); каждая ссылка SRC-/CLM- в главах ведёт сюда. '
    f'Записи политической части — в реестре брошюры (по запросу)</span></div>')


# ---------------- индексная страница ----------------

jsonld = {
 "@context": "https://schema.org", "@type": "Book",
 "name": BOOK_TITLE,
 "author": {"@type": "Organization", "name": "ThinkRed"},
 "inLanguage": "ru", "url": BASE + BOOK_SLUG,
 "isAccessibleForFree": True,
 "abstract": "Исследование места Республики Беларусь в системе мирового империализма по методологии Ленина: пять признаков как отношения, критерий субъектности, контуры накопления, классы и программные выводы для самостоятельной рабочей организации.",
 "hasPart": jsonld_parts,
}

index = f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Место современной Республики Беларусь в системе мирового империализма — ThinkRed</title>
<meta name="description" content="Исследование места Беларуси в системе мирового империализма по Ленину: пять признаков как отношения, критерий субъектности К + В + Г + Р, контуры накопления, классовая структура и проект программных тезисов. Черновик v0.8 — под открытым рецензированием."/>
<meta property="og:title" content="Место современной Республики Беларусь в системе мирового империализма"/>
<meta property="og:description" content="Книга ThinkRed: критерий прежде вывода; политика из экономики; черновик v0.8 — под открытым рецензированием."/>
<meta property="og:type" content="book"/>
<link rel="canonical" href="{BASE}{BOOK_SLUG}"/>
<link rel="icon" href="https://thinkred.ru/favicon.png"/>
<style>
:root{{--fg:#1f2328;--muted:#5b636e;--bg:#ffffff;--card:#f6f7f9;--line:#e3e6ea;--accent:#e11d2a;--accent-soft:rgba(225,29,42,.08)}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--fg);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Noto Sans",Arial,sans-serif;line-height:1.6}}
.hero{{background:linear-gradient(135deg,#8f1215,#e11d2a);color:#fff;padding:44px 18px}}
.hero .in{{max-width:900px;margin:0 auto}}
.hero h1{{margin:0 0 10px;font-size:27px;line-height:1.25;max-width:820px}}
.hero p{{margin:0;opacity:.92;font-size:15px;max-width:760px}}
.hero .meta{{margin-top:14px;font-size:13px;opacity:.85}}
.wrap{{max-width:900px;margin:0 auto;padding:26px 18px 10px}}
.wrap h2{{font-size:20px;margin:22px 0 14px}}
.blurb{{max-width:900px;margin:26px auto 0;background:#fff;border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:12px;padding:16px 22px;font-family:Georgia,serif;font-size:17px;line-height:1.55;font-style:italic;color:#333}}
.about{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px 22px;margin:16px 0 0;font-size:14.5px}}
.about h3{{margin:0 0 8px;font-size:16px}}
.about p{{margin:0 0 10px}}
.toc-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:12px}}
.toc-card{{display:block;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px;text-decoration:none;color:var(--fg);transition:border-color .15s}}
.toc-card:hover{{border-color:var(--accent)}}
.toc-card b{{display:block;color:var(--accent);margin-bottom:4px;font-size:15px}}
.toc-card b a{{color:inherit;text-decoration:none}}
.toc-card span{{font-size:13px;color:var(--muted);line-height:1.45;display:block}}
.toc-card details{{margin-top:8px}}
.toc-card summary{{font-size:12px;color:var(--muted);cursor:pointer}}
.toc-card details ul{{margin:6px 0 0;padding-left:16px}}
.toc-card details li{{margin:3px 0;font-size:12.5px}}
.toc-card details a{{color:var(--muted)}}
.note{{background:var(--accent-soft);border:1px solid #f5c2c5;border-radius:12px;padding:14px 18px;margin:22px 0;font-size:14px}}
.note a{{color:var(--accent);font-weight:600}}
.status{{background:#fff8e6;border:1px solid #f0ddb0;color:#7a5a00;border-radius:10px;padding:10px 14px;font-size:13.5px;margin:14px 0}}
.cta-read{{display:flex;gap:10px;flex-wrap:wrap;margin:20px 0 6px}}
.cta-read a{{background:var(--accent);color:#fff;border-radius:10px;padding:12px 18px;text-decoration:none;font-weight:600;font-size:15px}}
.cta-read a.o{{background:#fff;color:var(--accent);border:1px solid var(--accent)}}
.sitebar{{background:#fff;border-bottom:1px solid rgba(17,24,39,.08)}}
.sitebar .in{{max-width:900px;margin:0 auto;padding:12px 18px;display:flex;align-items:center;gap:18px;flex-wrap:wrap}}
.sitebar .logo{{font-weight:800;font-size:20px;text-decoration:none;color:#111118;font-family:Georgia,serif}}
.sitebar .logo span{{color:#e11d2a}}
.sitebar nav{{display:flex;gap:14px;flex-wrap:wrap}}
.sitebar nav a{{color:#4a4a5a;text-decoration:none;font-size:14px}}
.sitebar nav a:hover{{color:#e11d2a}}
.sitefoot{{border-top:1px solid rgba(17,24,39,.08);background:#fff;margin-top:40px;padding:20px 18px;text-align:center;color:#7a7a8a;font-size:13px}}
.sitefoot a{{color:#4a4a5a;text-decoration:none;margin:0 8px}}
</style>
<script type="application/ld+json">
{json.dumps(jsonld, ensure_ascii=False, indent=1)}
</script>
</head>
<body>
{SITEBAR.format(slug=BOOK_SLUG)}
<div class="hero"><div class="in">
  <h1>{html_mod.escape(BOOK_TITLE)}</h1>
  <p>Исследование места Беларуси в системе мирового империализма по методологии «Империализма как высшей стадии капитализма»: пять признаков Ленина как система отношений, критерий субъектности К + В + Г + Р, контуры накопления и рабочая классификация с удержанием открытых альтернатив. Первая (экономическая) часть двухчастного исследования.</p>
  <div class="meta">ThinkRed · 2026 · черновик v0.8 · под открытым рецензированием</div>
</div></div>
<div class="wrap">
  <div class="status"><b>Публикуется в развитии.</b> {VERSION_NOTE}</div>
  <div class="blurb">Книга начинает там, где закончилась наша <a href="https://thinkred.ru/blog/retsenziya-mesto-rossii-v-imperializme.html">рецензия на книгу Е.&nbsp;Морозовой</a>: рецензия показала, что из количественной слабости капитала не выведено его качественное качество. Здесь критерий классификации строится <b>до</b> эмпирики, применяется формально — и итог честно удерживает неустранённые альтернативы. Работа разделена на две части: экономическая (главы 1–12) — на этом сайте; политическая (классы и программа) издаётся отдельной брошюрой (см. заключение).</div>
  <div class="about">
    <h3>О книге</h3>
    <p><b>Три принципа.</b> Критерий прежде вывода: пять признаков Ленина разобраны как система отношений
    присвоения, а не как чек-лист показателей; собственная субъектность страны проверяется критерием
    <b>К + В + Г + Р</b>. Политика из экономики: гл.&nbsp;1–12 (экономика) → гл.&nbsp;13 (классы и организации)
    → гл.&nbsp;14 (программа); каждое программное требование проходит девятишаговый канон выводимости, и тезис
    без цепочки «отношение → субъект → механизм → условия → граница» в книгу не включается. Данные — насколько
    свежие, насколько существуют: ряды до 2025–2026, 2020 и 2022 — контрольные точки, не границы.</p>
    <p><b>Итог (рабочая классификация).</b> Беларусь — зависимая капиталистическая страна с отдельными внешними
    монопольными позициями, после 2014–2022 — углубление зависимости с концентрацией на России; внутреннее
    устройство — государственно-монополистический капитализм. Рабочий тип — <b>тип&nbsp;III</b> (уверенность
    повышена); разграничение с альтернативами (собственный подчинённый контур — включая квалификацию
    «второй&nbsp;мир» теории трёх миров, разобранную в §12.3; совместный контур) не устранено — см. таблицу
    опровержимости в гл.&nbsp;12.</p>
    <p><b>Две части.</b> На сайте публикуется экономическая часть: введение, главы 1–12, заключение
    и приложения Б–Г. Вторая часть — «Классы, организации и программные вопросы» (главы 13–14 и проект
    тезисов) — обращена к политической организации и действию, поэтому издаётся отдельной брошюрой
    и распространяется отдельно (см. заключение).</p>
    <p><b>Что в книге.</b> Введение, 12 глав и заключение, приложения и открытый реестр источников и утверждений
    со статусами доказанности. Отдельно: правовой риск-обзор (приложение&nbsp;Г), схемы к главам и интерактивные
    дашборды к гл.&nbsp;1–2.</p>
  </div>
  <div class="cta-read">
    <a href="bel-v00.html">Введение</a><a href="bel-g01.html">Читать с главы 1 →</a>
    <a class="o" href="bel-g12.html">Вывод (глава 12)</a>
    <a class="o" href="bel-pril-b.html">Реестр SRC/CLM</a>
    <a class="o" href="bel-pril-v.html">Как писалась книга</a>
    <a class="o" href="https://thinkred.ru/library/morozova.html">Книга Морозовой</a>
    <a class="o" href="https://thinkred.ru/library/bezrukova.html">Безрукова: методика</a>
  </div>
  <h2>Оглавление</h2>
  <div class="toc-grid">
  {chr(10).join(toc_cards)}
  </div>
  <h2>Приложения — прозрачность методологии</h2>
  <div class="toc-grid">
  {chr(10).join(toc_app_cards)}
  </div>
  <div class="note">Книга собрана и рецензирована с помощью <a href="https://thinkred.ru/assistant/">Методологического ассистента</a> ThinkRed: реестр из {N_SRC} источников и {N_CLM} проверяемых утверждений с конспектами — конвейер книги. Найдёте ошибку — напишите в <a href="https://t.me/thinkred_marx" target="_blank" rel="noopener">Telegram</a>.</div>
</div>
{SITEFOOT}
</body>
</html>
"""
open(os.path.join(OUT, BOOK_SLUG), "w", encoding="utf-8", newline="\n").write(index)

print("собрано файлов:", len(built) + 1)
for f in [BOOK_SLUG] + built:
    print(" ", f, os.path.getsize(os.path.join(OUT, f)), "байт")
