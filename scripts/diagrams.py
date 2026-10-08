# -*- coding: utf-8 -*-
"""Инлайн-SVG графики и схемы для сборки книги (build_site.py вставляет по {{SVG:name}}).
Все числа — из sources/data и реестра (SRC-ids в подписях на страницах)."""

INK, MUT, ACC, BLU, GRN, GRID, SOFT = "#111827", "#6b7280", "#e11d2a", "#1d4ed8", "#047857", "#e5e7eb", "#f9fafb"

def _svg(w, h, body):
    return (f'<svg viewBox="0 0 {w} {h}" role="img" style="width:100%;height:auto;display:block" '
            f'font-family="system-ui,Segoe UI,Arial,sans-serif">{body}</svg>')

def _txt(x, y, s, size=12, fill=INK, anchor="start", weight="normal", style=""):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
            f'font-weight="{weight}" {style}>{s}</text>')

def _axes(w, h, pad, ymax, ytitle, fmt=lambda v: f"{v:g}"):
    x0, y0, x1, y1 = pad, h - pad, w - pad, pad + 14
    out = [f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" stroke="{GRID}"/>',
           f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="{GRID}"/>',
           _txt(x0 - 6, y1 + 4, fmt(ymax), 10, MUT, "end"),
           _txt(x0 - 6, y0 + 4, "0", 10, MUT, "end"),
           _txt(6, y1 + 2, ytitle, 10, MUT)]
    return out, (x0, y0, x1, y1, ymax)

def _nice(x):
    import math
    if x <= 0: return 1
    k = 10 ** math.floor(math.log10(x))
    for m in (1, 2, 2.5, 5, 10):
        if x <= m * k: return m * k
    return 10 * k

def bars(data, w=300, h=180, color=ACC, ytitle="", fmt=lambda v: f"{v:g}", pad=34):
    ymax = _nice(max(v for _, v in data) * 1.12)
    body, (x0, y0, x1, y1, ymax) = _axes(w, h, pad, ymax, ytitle, fmt)
    bw = (x1 - x0 - 10) / len(data) * 0.62
    step = (x1 - x0) / len(data)
    for k, (lab, v) in enumerate(data):
        bh = (y0 - y1) * v / ymax
        x = x0 + 6 + k * step + (step - bw) / 2
        body.append(f'<rect x="{x:.1f}" y="{y0 - bh:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="2" fill="{color}"/>')
        body.append(_txt(x + bw / 2, y0 - bh - 3, fmt(v), 9, INK, "middle"))
        body.append(_txt(x + bw / 2, y0 + 12, lab, 9.5, MUT, "middle"))
    return _svg(w, h, "".join(body))

def donut(pct, label, w=170, h=170):
    r, cx, cy = 62, w / 2, h / 2
    import math
    a = pct / 100 * 2 * math.pi - math.pi / 2
    x, y = cx + r * math.cos(a), cy + r * math.sin(a)
    large = 1 if pct > 50 else 0
    body = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{GRID}" stroke-width="26"/>',
            f'<path d="M {cx} {cy - r} A {r} {r} 0 {large} 1 {x:.1f} {y:.1f}" fill="none" stroke="{ACC}" stroke-width="26"/>',
            _txt(cx, cy - 2, f"{pct}%", 22, INK, "middle", "700"),
            _txt(cx, cy + 20, label, 10, MUT, "middle")]
    return _svg(w, h, "".join(body))

def fdi():
    infl = [("2014", 1862), ("2019", 1273), ("2020", 1393), ("2022", 1606), ("2023", 1992), ("2024", 1737), ("2025", 1602)]
    stock = [("01.01.22", 1338), ("01.01.24", 1549), ("01.01.26", 2664)]
    w, h, pad = 620, 210, 40
    body, (x0, y0, x1, y1, ymax) = _axes(w, h, pad, 2800, "млн $", lambda v: f"{v/1000:g}к" if v else "0")
    # bars: чистый приток
    vals = [v for _, v in infl]; sc = (y0 - y1) / 2800
    bw, step = 26, (x1 - x0) / len(infl)
    for k, (lab, v) in enumerate(infl):
        x = x0 + 10 + k * step + (step - bw) / 2
        body.append(f'<rect x="{x:.1f}" y="{y0 - v*sc:.1f}" width="{bw}" height="{v*sc:.1f}" rx="2" fill="{BLU}" opacity=".85"/>')
        body.append(_txt(x + bw / 2, y0 - v*sc - 4, f"{v:,}".replace(",", " "), 8.5, BLU, "middle"))
        body.append(_txt(x + bw / 2, y0 + 12, lab, 9, MUT, "middle"))
    # line: запас за рубежом
    sx0 = x0 + 10 + 0 * step + step / 2
    pts = [(x0 + 10 + i * step + step / 2, y0 - v * sc) for i, (_, v) in enumerate(stock)]
    # запас на первые три позиции года (22,24,26 -> позиции 3,5,6?) — отдельная мини-линия справа
    lx0 = x1 - 150
    body.append(f'<line x1="{lx0}" y1="{y1}" x2="{lx0}" y2="{y0}" stroke="{GRID}" stroke-dasharray="3 3"/>')
    for i, (lab, v) in enumerate(stock):
        px = lx0 + 8 + i * 62
        body.append(f'<circle cx="{px}" cy="{y0 - v*sc:.1f}" r="4" fill="{ACC}"/>')
        if i: body.append(f'<line x1="{pts_old[0]}" y1="{pts_old[1]}" x2="{px}" y2="{y0 - v*sc:.1f}" stroke="{ACC}" stroke-width="1.6"/>')
        body.append(_txt(px, y0 - v*sc - 8, f"{v:,}".replace(",", " "), 8.5, ACC, "middle"))
        body.append(_txt(px, y0 + 12, lab, 8.5, MUT, "middle"))
        pts_old = (px, y0 - v*sc)
    body.append(_txt(x0 + 10, y1 + 2, "чистый приток ПИИ (flow)", 9, BLU, "start", "600"))
    body.append(_txt(lx0 + 8, y1 + 2, "запас за рубежом (stock)", 9, ACC, "start", "600"))
    return _svg(w, h, "".join(body))

def iip():
    dates = ["01.01.2022", "01.01.2024", "01.01.2026"]
    assets = [28305, 32051, 39522]; liab = [55154, 50319, 55960]; net = [-26849, -18268, -16438]
    w, h, pad = 560, 230, 44
    body, (x0, y0, x1, y1, _) = _axes(w, h, pad, 60000, "млн $", lambda v: f"{v/1000:g}к" if v else "0")
    ymid = y0 - (y0 - y1) * 60000 / 130000
    body.append(f'<line x1="{x0}" y1="{ymid:.1f}" x2="{x1}" y2="{ymid:.1f}" stroke="{GRID}"/>')
    body.append(_txt(x0 - 6, ymid + 3, "−70к", 10, MUT, "end"))
    step = (x1 - x0 - 16) / 3
    for i, d in enumerate(dates):
        cx = x0 + 16 + step * i + step / 2
        ha = (y0 - ymid) * assets[i] / 60000
        hl = (y0 - ymid) * liab[i] / 60000
        hn = (ymid - y0) * 0  # net вниз от средней: рисуем от ymid вниз пропорц. 70к
        hn = (y0 - ymid) * (-net[i]) / 70000
        body.append(f'<rect x="{cx-40:.1f}" y="{y0-ha:.1f}" width="24" height="{ha:.1f}" rx="2" fill="{GRN}" opacity=".9"/>')
        body.append(f'<rect x="{cx-12:.1f}" y="{y0-hl:.1f}" width="24" height="{hl:.1f}" rx="2" fill="{BLU}" opacity=".75"/>')
        body.append(f'<rect x="{cx+16:.1f}" y="{ymid:.1f}" width="24" height="{hn:.1f}" rx="2" fill="{ACC}" opacity=".85"/>')
        body.append(_txt(cx + 28, ymid + hn + 10, f"−{-net[i]:,}".replace(",", " "), 8.5, ACC, "middle"))
        body.append(_txt(cx, y0 + 12, d, 9, MUT, "middle"))
    body.append(_txt(x0 + 16, y1 - 2, "■ активы  ■ обязательства  ■ чистая позиция (должник)", 9, MUT))
    return _svg(w, h, "".join(body))

def energy():
    d = [("2014", 87.8), ("2019", 85.3), ("2020", 83.8), ("2022", 77.1)]
    return bars(d, 330, 190, ACC, "% энергопотребления", lambda v: f"{v:g}%")

def trade():
    d = [("РФ", 66.6), ("ЕС", 10.6), ("прочие", 22.8)]
    return bars(d, 270, 190, BLU, "% товарной торговли, 2025", lambda v: f"{v:g}%")

def milex():
    a = bars([("2024", 1.49), ("2025", 1.94)], 260, 185, ACC, "SIPRI, млрд $", lambda v: f"{v:g}")
    b = bars([("2024 исп.", 3.58), ("2025 исп.", 4.5), ("2025 план", 4.73)], 320, 185, BLU, "бюджет «Нац. оборона», млрд BYN", lambda v: f"{v:g}")
    body = (f'<rect width="610" height="200" fill="{SOFT}" rx="8"/>'
            f'<g transform="translate(12,8)">{a}</g><g transform="translate(292,8)">{b}</g>')
    return _svg(610, 200, body)

def potash():
    return donut(86, "к рос. портам")

def axes_diag():
    w, h = 640, 250
    body = [f'<rect width="{w}" height="{h}" rx="10" fill="{SOFT}"/>',
            f'<rect x="24" y="30" width="250" height="120" rx="8" fill="#fff" stroke="{BLU}" stroke-width="1.5"/>',
            _txt(149, 56, "Ось I — собственная", 13, BLU, "middle", "700"),
            _txt(149, 74, "субъектность капитала", 13, BLU, "middle", "700"),
            _txt(149, 100, "критерий К∧В∧Г∧Р:", 11.5, INK, "middle"),
            _txt(149, 117, "центр командования · внешнее", 10.5, MUT, "middle"),
            _txt(149, 132, "господство · гос. закрепление ·", 10.5, MUT, "middle"),
            _txt(149, 147, "воспроизводимость", 10.5, MUT, "middle"),
            f'<rect x="366" y="30" width="250" height="120" rx="8" fill="#fff" stroke="{ACC}" stroke-width="1.5"/>',
            _txt(491, 56, "Ось II — структурная", 13, ACC, "middle", "700"),
            _txt(491, 74, "зависимость", 13, ACC, "middle", "700"),
            _txt(491, 100, "четыре компонента узла:", 11.5, INK, "middle"),
            _txt(491, 117, "значимость · концентрация ·", 10.5, MUT, "middle"),
            _txt(491, 132, "незаменимость · устойчивость", 10.5, MUT, "middle"),
            _txt(491, 147, "механизм воздействия", 10.5, MUT, "middle"),
            f'<path d="M 274 90 C 310 90 330 90 366 90" stroke="{MUT}" fill="none" stroke-dasharray="5 4" marker-end="url(#arw)"/>',
            _txt(320, 78, "аналитически различные,", 9.5, MUT, "middle"),
            _txt(320, 108, "не независимые", 9.5, MUT, "middle"),
            f'<defs><marker id="arw" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="{MUT}"/></marker></defs>',
            _txt(320, 185, "классификация страны — по обеим осям вместе;", 12, INK, "middle", "600"),
            _txt(320, 204, "контур накопления — единица анализа, не страновой агрегат", 11, MUT, "middle")]
    return _svg(w, h, "".join(body))

def contour():
    labels = ["Центр\nкомандования", "Мобилизация\nресурсов", "Производство", "Присвоение", "Реинвест", "Гос.\nобеспечение"]
    w, h, bw, bh, gap, x0, y0 = 640, 150, 88, 54, 14, 16, 30
    body = []
    for i, lab in enumerate(labels):
        x = x0 + i * (bw + gap)
        body.append(f'<rect x="{x}" y="{y0}" width="{bw}" height="{bh}" rx="8" fill="#fff" stroke="{BLU}" stroke-width="1.4"/>')
        for j, line in enumerate(lab.split("\n")):
            body.append(_txt(x + bw / 2, y0 + 24 + j * 15, line, 10.5, INK, "middle"))
        if i < len(labels) - 1:
            body.append(f'<line x1="{x+bw}" y1="{y0+bh/2}" x2="{x+bw+gap}" y2="{y0+bh/2}" stroke="{MUT}" marker-end="url(#arw2)"/>')
    body.append(f'<rect x="{x0}" y="{y0+bh+18}" width="{6*bw+5*gap}" height="36" rx="8" fill="none" stroke="{ACC}" stroke-dasharray="5 4"/>')
    body.append(_txt((x0*2+6*bw+5*gap)/2, y0+bh+41, "7-й вопрос рамки: кто контролирует условия доступа к каждому звену контура?", 11, ACC, "middle", "600"))
    body.append(f'<defs><marker id="arw2" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="{MUT}"/></marker></defs>')
    return _svg(w, h, "".join(body))

def map12():
    w, h, x0, y0, x1, y1 = 640, 400, 60, 30, 600, 340
    body = [f'<rect width="{w}" height="{h}" rx="10" fill="{SOFT}"/>',
            f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="{INK}" marker-end="url(#a3)"/>',
            f'<line x1="{x0}" y1="{y1}" x2="{x0}" y2="{y0}" stroke="{INK}" marker-end="url(#a3)"/>',
            _txt(x1, y1 + 16, "структурная зависимость →", 11, INK, "end", "600"),
            _txt(x0 - 8, y0 + 10, "собственная субъектность ↑", 11, INK, "600")]
    def zone(x, y, t1, t2, col):
        return [f'<circle cx="{x}" cy="{y}" r="26" fill="#fff" stroke="{col}" stroke-width="1.6"/>',
                _txt(x, y + 4, t1, 12, col, "middle", "700"),
                _txt(x, y + 44, t2, 10, MUT, "middle")]
    body += zone(150, 90, "I", "империалистический центр", BLU)
    body += zone(430, 80, "II", "подчинённый участник", GRN)
    body += zone(450, 200, "III", "зависимая с монопозициями", BLU)
    body += zone(450, 300, "IV", "зависимая без субъектности", MUT)
    body.append(f'<circle cx="460" cy="252" r="14" fill="{ACC}"/>')
    body.append(_txt(460, 256, "РБ", 10, "#fff", "middle", "700"))
    body.append(f'<path d="M 300 300 C 360 300 400 285 440 262" stroke="{ACC}" fill="none" stroke-width="1.6" stroke-dasharray="6 4" marker-end="url(#a3)"/>')
    body.append(_txt(300, 322, "смещение 2020→2026:", 10, ACC, "middle"))
    body.append(_txt(300, 335, "углубление зависимости", 10, ACC, "middle"))
    body.append(_txt(505, 258, "рабочая:", 9.5, MUT, "start"))
    body.append(_txt(505, 270, "между III и IV", 9.5, ACC, "start", "700"))
    body.append(_txt(320, 385, "схема качественная (гл. 1–2): положение зон — не измерение", 10, MUT, "middle"))
    body.append('<defs><marker id="a3" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="#111827"/></marker></defs>')
    return _svg(w, h, "".join(body))

def program():
    w, h = 640, 210
    steps = [("Минимальная", "треб. 1–3, 8 — оборонительные", "в рамках системы", BLU),
             ("Переходная (контрольная)", "треб. 4–7, 9–11 — органы контроля", "конфликт с режимом собственности; исход не предрешён", ACC),
             ("Максимальная", "власть рабочего класса, план-хоз", "нормативная цель, не прогноз", INK)]
    body = [f'<rect width="{w}" height="{h}" rx="10" fill="{SOFT}"/>']
    for i, (t1, t2, t3, col) in enumerate(steps):
        x = 20 + i * 205
        y = 120 - i * 34
        body.append(f'<rect x="{x}" y="{y}" width="185" height="64" rx="8" fill="#fff" stroke="{col}" stroke-width="1.5"/>')
        body.append(_txt(x + 92, y + 20, t1, 12, col, "middle", "700"))
        body.append(_txt(x + 92, y + 37, t2, 9.5, INK, "middle"))
        body.append(_txt(x + 92, y + 52, t3, 9, MUT, "middle"))
        if i < 2:
            body.append(f'<line x1="{x+185}" y1="{y+20}" x2="{x+205}" y2="{y-14+20}" stroke="{MUT}" marker-end="url(#a4)"/>')
    body.append(_txt(320, 190, "программа = анализ + нормативная посылка §14.0, не логическое следствие классификации", 10.5, MUT, "middle"))
    body.append('<defs><marker id="a4" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="#6b7280"/></marker></defs>')
    return _svg(w, h, "".join(body))

ALL = {
    "axes": (axes_diag, "Рис. 1.1. Две аналитически различные оси классификации (схема; критерий и ловушки — в тексте главы)."),
    "contour": (contour, "Рис. 2.1. Контур накопления как единица анализа (схема; цепочка доказательства — §2.2)."),
    "fdi": (fdi, "Рис. 9.1. ПИИ: чистый приток по годам — flow (WDI — SRC-032) и запас прямых инвестиций резидентов за рубежом — stock (IIP НБРБ — SRC-013). Показатели не смешиваются."),
    "iip": (iip, "Рис. 9.2. Международная инвестиционная позиция на 1 января (НБРБ — SRC-013): активы, обязательства, чистая позиция должника."),
    "energy": (energy, "Рис. 10.1. Чистый импорт энергии, % энергопотребления (WDI — SRC-032): внешняя энергозависимость вообще — не зависимость от РФ (см. уровни §10.1)."),
    "trade": (trade, "Рис. 10.2. Товарная внешняя торговля Беларуси, 2025, по контрагентам (Еврокомиссия — SRC-055)."),
    "milex": (milex, "Рис. 11.1. Военные расходы в двух несмешиваемых измерениях: SIPRI (SRC-060) и бюджетная статья «Национальная оборона» (SRC-059)."),
    "map": (map12, "Рис. 12.1. Рабочая позиция Беларуси на осях классификации (схема качественная; статусы — в карточке §12.5)."),
    "program": (program, "Рис. 14.1. Три блока программы и их логика (схема; полный канон — в тексте главы)."),
    "potash": (potash, "Рис. 12.2. Железнодорожные отправки Belaruskali к российским портовым станциям, 2025 (SRC-062)."),
}
