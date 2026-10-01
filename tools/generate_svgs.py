"""Erzeugt Piktogramme und den isometrischen Gebäudeplan als SVG.

Aufruf (im Projektordner):  python tools/generate_svgs.py
Ausgabe: img/icons/*.svg, img/icons/pictos.svg (Sprite), img/gebaeudeplan.svg,
         partials/gebaeudeplan-inline.svg (klickbare Variante für raeume.html)
"""
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VIOLET = "#443189"
TINT = "#ECE9F4"
INK = "#2B2B2A"
PAPER = "#FFFFFF"

# ---------------------------------------------------------------------------
# Piktogramme – 48×48-Raster, Rahmen 4..44, Logo-Balken links (x 4..11)
# ---------------------------------------------------------------------------
STROKE = 'fill="none" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"'

# Konstruierte Ziffern (Strichzeichnung, Höhe 16 px, y 16..32)
GLYPH_R = "M16 32V16h5.5a4 4 0 0 1 0 8H16m5 0 4 8"
DIGITS = {
    "1": "M29 19.5 32.5 16v16",
    "2": "M28.5 19.5a4 4 0 0 1 8 0c0 3-8 7.5-8 12.5h8",
    "3": "M28.5 16h7.5l-4.5 6a5 5 0 1 1-3.5 8.5",
    "4": "M34.5 32V16l-6.5 11h9",
}

# Service-Piktogramme: Inhaltsfläche x 13..41, Mitte x 27
SERVICE = {
    "cafe": ('<path d="M17 21h15v7a6 6 0 0 1-6 6h-3a6 6 0 0 1-6-6z"/>'
             '<path d="M32 23h2a3 3 0 0 1 0 6h-2"/>'
             '<path d="M15 37.5h20"/>'
             '<path d="M21.5 17c-1.2-1.5 1.2-2.5 0-4m5 4c-1.2-1.5 1.2-2.5 0-4"/>'),
    "toiletten": ('<circle cx="19.5" cy="13.5" r="2.6"/>'
                  '<path d="M19.5 19 14.5 31h10z"/><path d="M19.5 31v6"/>'
                  '<circle cx="34" cy="13.5" r="2.6"/>'
                  '<path d="M30.5 19h7v10h-7z"/><path d="M34 29v8"/>'),
    "tickets": ('<path d="M14 17h26v5a3 3 0 0 0 0 6v5H14v-5a3 3 0 0 0 0-6z"/>'
                '<path d="M31 18.5v4m0 5v4"/>'),
    "oeffnungszeiten": ('<circle cx="27" cy="25" r="11.5"/>'
                        '<path d="M27 18v7.5l5 3"/>'),
}
SERVICE_TITLES = {"cafe": "Museumscafé", "toiletten": "Toiletten", "tickets": "Ticketverkauf",
                  "oeffnungszeiten": "Öffnungszeiten"}


def room_body(n: str) -> str:
    return (f'<rect x="4" y="4" width="40" height="40" rx="3" fill="{VIOLET}"/>'
            f'<path d="M11.5 4v40" stroke="{PAPER}" stroke-width="1.5"/>'
            f'<g stroke="{PAPER}" {STROKE}><path d="{GLYPH_R}"/><path d="{DIGITS[n]}"/></g>')


def service_body(key: str) -> str:
    return (f'<rect x="5" y="5" width="38" height="38" rx="2.5" fill="{PAPER}" stroke="{VIOLET}" stroke-width="2"/>'
            f'<path d="M4 7a3 3 0 0 1 3-3h4.5v40H7a3 3 0 0 1-3-3z" fill="{VIOLET}"/>'
            f'<g stroke="{VIOLET}" {STROKE}>{SERVICE[key]}</g>')


PICTOS = {f"r{n}": (f"Raum R{n}", room_body(n)) for n in "1234"}
PICTOS.update({k: (SERVICE_TITLES[k], service_body(k)) for k in SERVICE})


def write_pictos():
    out = ROOT / "img" / "icons"
    out.mkdir(parents=True, exist_ok=True)
    symbols = []
    for key, (title, body) in PICTOS.items():
        (out / f"{key}.svg").write_text(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="48" height="48" role="img">'
            f"<title>{title}</title>{body}</svg>\n", encoding="utf-8")
        symbols.append(f'<symbol id="picto-{key}" viewBox="0 0 48 48">{body}</symbol>')
    (out / "pictos.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg">' + "".join(symbols) + "</svg>\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Isometrischer Gebäudeplan (Grundlage: Skizze Gebaeudeplan.pdf)
# a-Achse läuft nach rechts oben, b-Achse nach rechts unten, z nach oben.
# ---------------------------------------------------------------------------
U = 34                      # Pixel pro Planeinheit
C, S = math.cos(math.radians(30)), 0.5
OX, OY = 40, 300            # Ursprung im SVG

# id, a0, a1, b0, b1, Wandhöhe, Piktogramme, Linkziel (None = nicht verlinkt)
# Wie in der Skizze: langer Flügel R3/R4 links; R2 und R1 bilden ein L
# (R2 parallel zum Flügel, R1 nach vorne rechts); in der Innenecke des L der
# Eingang mit Ticketverkauf; vorne links Museumscafé und Toiletten.
# Reihenfolge = Zeichenreihenfolge von hinten nach vorne.
BLOCKS = [
    ("r4", 6.0, 12.4, 0.0, 3.4, 1.5, ["r4"], "#r4"),
    ("r1", 11.0, 13.8, 4.4, 11.6, 1.5, ["r1"], "#r1"),
    ("r2", 4.8, 11.0, 4.4, 7.0, 1.5, ["r2"], "#r2"),
    ("r3", 0.0, 6.0, 0.0, 3.4, 1.5, ["r3"], "#r3"),
    ("foyer", 6.4, 10.4, 8.0, 11.6, 1.15, ["tickets"], None),
    ("cafe", 0.0, 5.4, 4.4, 9.4, 1.3, ["cafe", "toiletten"], None),
]
LABELS = {"r1": "R1: Renaissance bis Rokoko", "r2": "R2: Klassizismus bis Realismus",
          "r3": "R3: Das 20. Jahrhundert", "r4": "R4: Künstlerinnen der Gegenwart",
          "foyer": "Eingang mit Ticketverkauf", "cafe": "Museumscafé und Toiletten"}


def p(a, b, z=0.0):
    return (OX + (a + b) * C * U, OY + (b - a) * S * U - z * U)


def poly(points, **attrs):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    extra = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<polygon points="{pts}" {extra}/>'


def picto_center(a0, a1, b0, b1, h):
    return p((a0 + a1) / 2, (b0 + b1) / 2, h * 0.55)


def block_svg(bid, a0, a1, b0, b1, h, pictos):
    floor = poly([p(a0, b0), p(a1, b0), p(a1, b1), p(a0, b1)], **{"class": "pl-floor"})
    # Rückwände (Innenseiten sichtbar): Wand bei b0 (entlang a) und bei a1 (entlang b)
    back_a = poly([p(a0, b0), p(a1, b0), p(a1, b0, h), p(a0, b0, h)], **{"class": "pl-wall-back-a"})
    back_b = poly([p(a1, b0), p(a1, b1), p(a1, b1, h), p(a1, b0, h)], **{"class": "pl-wall-back-b"})
    # Vorderwände (Außenseiten sichtbar): Wand bei b1 (entlang a) und bei a0 (entlang b)
    front_a = poly([p(a0, b1), p(a1, b1), p(a1, b1, h), p(a0, b1, h)], **{"class": "pl-wall-front-a"})
    front_b = poly([p(a0, b0), p(a0, b1), p(a0, b1, h), p(a0, b0, h)], **{"class": "pl-wall-front-b"})
    # Piktogramme auf dem Boden, leicht angehoben, damit sie über der Vorderwand stehen
    size = 46
    icons = []
    for i, key in enumerate(pictos):
        x, y = picto_center(a0, a1, b0, b1, h)
        x += (i - (len(pictos) - 1) / 2) * (size + 6)
        icons.append(f'<use href="#picto-{key}" x="{x - size / 2:.1f}" y="{y - size / 2:.1f}" '
                     f'width="{size}" height="{size}"/>')
    extra = ""
    if bid == "foyer":  # Glastür in der Vorderwand
        d0, d1 = a0 + 1.4, a0 + 2.6
        extra = poly([p(d0, b1, 0), p(d1, b1, 0), p(d1, b1, 0.9), p(d0, b1, 0.9)], **{"class": "pl-door"})
    return floor + back_a + back_b + front_b + front_a + extra + "".join(icons)


CSS = f"""
.pl-floor{{fill:{TINT};stroke:{INK};stroke-width:1}}
.pl-wall-back-a{{fill:#C9C4D6;stroke:{INK};stroke-width:1}}
.pl-wall-back-b{{fill:#B3ADC4;stroke:{INK};stroke-width:1}}
.pl-wall-front-a,.pl-wall-front-b{{fill:#FFFFFF;stroke:{INK};stroke-width:1.5;stroke-linejoin:round}}
.pl-wall-front-b{{fill:#F4F2EE}}
.pl-door{{fill:#DDE6EE;stroke:{INK};stroke-width:1}}
"""

# zusätzliche Regeln nur für die klickbare Variante
CSS_INTERACTIVE = f"""
.pl-room{{cursor:pointer;outline:none}}
.pl-room .pl-floor,.pl-room polygon{{transition:fill .25s ease}}
.pl-room:hover .pl-floor,.pl-room:focus-visible .pl-floor,.pl-room.is-active .pl-floor{{fill:{VIOLET}}}
.pl-room:hover .pl-wall-back-a,.pl-room:focus-visible .pl-wall-back-a,.pl-room.is-active .pl-wall-back-a{{fill:#7D6FB5}}
.pl-room:hover .pl-wall-back-b,.pl-room:focus-visible .pl-wall-back-b,.pl-room.is-active .pl-wall-back-b{{fill:#6A5BA6}}
.pl-room:focus-visible .pl-wall-front-a,.pl-room:focus-visible .pl-wall-front-b{{stroke:{VIOLET};stroke-width:3}}
.pl-label{{opacity:0;transition:opacity .2s ease;pointer-events:none}}
.pl-label rect{{fill:{INK}}}
.pl-label text{{fill:#FFFFFF;font:600 15px "Source Sans 3","Segoe UI",Arial,sans-serif}}
@media (prefers-reduced-motion:reduce){{.pl-room polygon,.pl-label{{transition:none}}}}
"""
# Beschriftung erscheint, wenn der zugehörige Raum Hover/Fokus hat (CSS :has)
CSS_INTERACTIVE += "".join(
    f".plan-svg:has(#plan-{r}:hover,#plan-{r}:focus-visible,#plan-{r}.is-active) #label-{r}{{{{opacity:1}}}}"
    .replace("{{", "{").replace("}}", "}") for r in ("r1", "r2", "r3", "r4"))


def label_svg(bid, a0, a1, b0, b1, h):
    """Dunkles Namensschild über dem Piktogramm (nur klickbare Variante)."""
    text = LABELS[bid]
    x, y = picto_center(a0, a1, b0, b1, h)
    w, hgt = len(text) * 7.6 + 24, 30
    top = y - 23 - 10 - hgt
    return (f'<g class="pl-label" id="label-{bid}">'
            f'<rect x="{x - w / 2:.1f}" y="{top:.1f}" width="{w:.1f}" height="{hgt}" rx="2"/>'
            f'<text x="{x:.1f}" y="{top + 20:.1f}" text-anchor="middle">{text}</text></g>')


def plan_svg(interactive: bool) -> str:
    parts = []
    for bid, a0, a1, b0, b1, h, pictos, href in BLOCKS:
        body = block_svg(bid, a0, a1, b0, b1, h, pictos)
        if interactive and href:
            parts.append(f'<a href="{href}" class="pl-room" id="plan-{bid}" aria-label="{LABELS[bid]}">'
                         f"<title>{LABELS[bid]}</title>{body}</a>")
        else:
            parts.append(f'<g id="plan-{bid}"><title>{LABELS[bid]}</title>{body}</g>')
    if interactive:  # Beschriftungen als oberste Ebene, damit sie nichts verdeckt
        parts.append('<g class="pl-labels" aria-hidden="true">' + "".join(
            label_svg(bid, a0, a1, b0, b1, h) for bid, a0, a1, b0, b1, h, _, href in BLOCKS if href) + "</g>")
    # Bounding Box
    xs, ys = [], []
    for _, a0, a1, b0, b1, h, _, _ in BLOCKS:
        for a in (a0, a1):
            for b in (b0, b1):
                for z in (0, h):
                    x, y = p(a, b, z)
                    xs.append(x); ys.append(y)
    pad = 40
    vb = f"{min(xs) - pad:.0f} {min(ys) - pad:.0f} {max(xs) - min(xs) + 2 * pad:.0f} {max(ys) - min(ys) + 2 * pad:.0f}"
    symbols = "".join(f'<symbol id="picto-{k}" viewBox="0 0 48 48">{b}</symbol>' for k, (_, b) in PICTOS.items())
    style = CSS + (CSS_INTERACTIVE if interactive else "")
    attrs = ('class="plan-svg" role="group" aria-labelledby="plan-title"' if interactive
             else 'role="img" aria-labelledby="plan-title"')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" {attrs}>'
            f'<title id="plan-title">Isometrischer Gebäudeplan des Isabella-Edel-Museums</title>'
            f"<defs><style>{style}</style>{symbols}</defs>"
            + "".join(parts) + "</svg>\n")


def main():
    write_pictos()
    (ROOT / "img" / "gebaeudeplan.svg").write_text(plan_svg(False), encoding="utf-8", newline="\n")
    (ROOT / "partials").mkdir(exist_ok=True)
    (ROOT / "partials" / "gebaeudeplan-inline.svg").write_text(plan_svg(True), encoding="utf-8", newline="\n")
    print("SVGs geschrieben.")


if __name__ == "__main__":
    main()
