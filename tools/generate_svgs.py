"""Erzeugt die Piktogramme als SVG (Gebäudeplan: tools/generate_plan.js).

Aufruf (im Projektordner):  python tools/generate_svgs.py
Ausgabe: img/icons/*.svg, img/icons/pictos.svg (Sprite)
"""
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


# Der isometrische Gebäudeplan wird von tools/generate_plan.js erzeugt.


def main():
    write_pictos()
    print("Piktogramme geschrieben.")


if __name__ == "__main__":
    main()
