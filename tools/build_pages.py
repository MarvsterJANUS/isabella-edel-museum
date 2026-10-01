"""Erzeugt die statischen HTML-Seiten der Website (einmalig, kein Build zur Laufzeit).

Aufruf (im Projektordner):  python tools/build_pages.py
Header, Footer und responsive Bilder werden so auf allen Seiten identisch erzeugt.
Alle Texte stammen wortgleich aus „Website-content.docx“.
"""
import re
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "img"

NAV = [
    ("index.html", "Startseite"),
    ("veranstaltungen.html", "Veranstaltungen"),
    ("kuenstlerinnen.html", "Künstlerinnen"),
    ("raeume.html", "Räume"),
    ("gruenderin.html", "Die Gründerin"),
    ("museumscafe.html", "Museumscafé"),
    ("tickets.html", "Tickets"),
]
NAV_FOOTER = [("impressum.html", "Impressum"), ("datenschutz.html", "Datenschutz")]


# ---------------------------------------------------------------------------
# Bausteine
# ---------------------------------------------------------------------------
def picture(name, alt, sizes="100vw", cls="", lazy=True, priority=False):
    """<picture> mit WebP + JPG-Fallback in allen vorhandenen Breiten."""
    widths = [w for w in (640, 1280, 2000) if (IMG / f"{name}-{w}.jpg").exists()]
    fallback = 1280 if 1280 in widths else widths[-1]
    with Image.open(IMG / f"{name}-{fallback}.jpg") as im:
        w, h = im.size
    webp = ", ".join(f"img/{name}-{x}.webp {x}w" for x in widths)
    jpg = ", ".join(f"img/{name}-{x}.jpg {x}w" for x in widths)
    loading = ' loading="lazy" decoding="async"' if lazy else ""
    prio = ' fetchpriority="high"' if priority else ""
    cls_attr = f' class="{cls}"' if cls else ""
    return (f'<picture{cls_attr}>'
            f'<source type="image/webp" srcset="{webp}" sizes="{sizes}">'
            f'<img src="img/{name}-{fallback}.jpg" srcset="{jpg}" sizes="{sizes}" '
            f'width="{w}" height="{h}" alt="{alt}"{loading}{prio}>'
            f'</picture>')


def zoom(name, alt, sizes):
    """Bild mit Link auf die größte Version. Ohne JS öffnet der Link das Bild,
    mit JS erscheint es in einer Lightbox (<dialog>)."""
    big = max(w for w in (640, 1280, 2000) if (IMG / f"{name}-{w}.jpg").exists())
    return (f'<a class="zoom" href="img/{name}-{big}.jpg" aria-label="{alt} – Bild vergrößern">'
            f'{picture(name, alt, sizes=sizes)}</a>')


def ratio(name):
    """Breite/Höhe eines Bildes – steuert die Breite in der Hängung (gleiche Höhe, kein Beschnitt)."""
    with Image.open(IMG / f"{name}-640.jpg") as im:
        return round(im.width / im.height, 3)


def picto(key, alt=""):
    return f'<img class="picto" src="img/icons/{key}.svg" width="48" height="48" alt="{alt}">'


def quote(text, cite="", cls=""):
    cap = f"<figcaption>{cite}</figcaption>" if cite else ""
    return f'<figure class="quote {cls}"><blockquote><p>{text}</p></blockquote>{cap}</figure>'


STEPS = ["Ticketart wählen", "Persönliche Angaben", "Bestätigung"]


def stepper(current):
    """Ablauf der Ticketreservierung; current = 1, 2 oder 3."""
    items = "".join(
        f'<li{" aria-current=\"step\"" if i == current else ""}{" class=\"is-done\"" if i < current else ""}>'
        f'<span class="stepper__num" aria-hidden="true">{i}</span>{label}</li>'
        for i, label in enumerate(STEPS, 1))
    return f'<ol class="stepper" aria-label="Ablauf der Reservierung">{items}</ol>'


def quote_band(img, alt, text, cite="", label="Zitat", cls=""):
    """Randloses Band: Bild links, violette Fläche mit Zitat rechts (Startseite, Gründerin)."""
    extra = f" {cls}" if cls else ""
    return f"""<section class="quote-band{extra}" aria-label="{label}">
  <div class="quote-band__media">{picture(img, alt, sizes="(min-width: 576px) 50vw, 100vw")}</div>
  <div class="quote-band__panel">
    {quote(text, cite, "quote--band")}
  </div>
</section>"""


def page_hero(name, alt, title, kicker=""):
    k = f'<p class="page-intro__kicker">{kicker}</p>' if kicker else ""
    return (f'<div class="page-hero">{picture(name, alt, lazy=False, priority=True)}</div>'
            f'<header class="page-intro container">{k}<h1>{title}</h1></header>')


ICON_THEME = ('<svg class="pref-btn__icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
              '<path class="icon-moon" transform="translate(0.7 -0.6)" d="M11.28 4.03A8 8 0 1 0 19.8 13.77A6.5 6.5 0 0 1 11.28 4.03z"/>'
              '<g class="icon-sun"><circle cx="12" cy="12" r="4"/>'
              '<path d="M12 2.5v2.2M12 19.3v2.2M4.2 4.2l1.6 1.6M18.2 18.2l1.6 1.6M2.5 12h2.2M19.3 12h2.2M4.2 19.8l1.6-1.6M18.2 5.8l1.6-1.6"/></g></svg>')
ICON_A11Y = ('<svg class="pref-btn__icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
             '<circle cx="12" cy="12" r="10"/>'
             # Figur um 0,53 angehoben: ihre Mitte liegt so exakt in der Kreismitte
             '<g transform="translate(0 -0.53)"><circle class="icon-fill" cx="12" cy="7.2" r="1.5"/>'
             '<path d="M7.5 10l4.5 1 4.5-1M12 11v3.3l-2.4 4.2M12 14.3l2.4 4.2"/></g></svg>')


def layout(file, title, description, main_html, body_class="", nav_file=None):
    nav_file = nav_file or file
    nav = "".join(
        f'<li{" class=\"nav-item--cta\"" if href == "tickets.html" else ""}>'
        f'<a href="{href}"{" class=\"nav-cta\"" if href == "tickets.html" else ""}'
        f'{" aria-current=\"page\"" if href == nav_file else ""}>{label}</a></li>'
        for href, label in NAV)
    # Darstellungs-Einstellungen (nur mit JS sichtbar, siehe main.js → initPrefs)
    nav += f'''<li class="nav-prefs" hidden>
        <button class="pref-btn" type="button" data-pref="theme" aria-pressed="false">{ICON_THEME}<span class="pref-btn__label">Dunkler Modus</span></button>
        <button class="pref-btn" type="button" data-pref="a11y" aria-pressed="false">{ICON_A11Y}<span class="pref-btn__label">Barrierefreier Modus</span></button>
      </li>'''
    fnav = "".join(
        f'<li><a href="{href}"{" aria-current=\"page\"" if href == file else ""}>{label}</a></li>'
        for href, label in NAV_FOOTER)
    full_title = "Isabella-Edel-Museum" if file == "index.html" else f"{title} | Isabella-Edel-Museum"
    bc = f' class="{body_class}"' if body_class else ""
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{full_title}</title>
<meta name="description" content="{description}">
<link rel="icon" href="img/icons/favicon.svg" type="image/svg+xml">
<meta name="color-scheme" content="light dark">
<link rel="stylesheet" href="css/style.css">
<!-- Progressive Enhancement ("Cutting the Mustard"): Die Klasse "js" wird nur in modernen
     Browsern gesetzt. Nur dann führt js/main.js seine Erweiterungen aus. -->
<script>
(function (d) {{
  if ('noModule' in HTMLScriptElement.prototype && 'IntersectionObserver' in window) d.classList.add('js');
  try {{ /* gespeicherte Darstellung vor dem ersten Zeichnen anwenden */
    var t = localStorage.getItem('iem-theme'); if (t === 'light' || t === 'dark') d.setAttribute('data-theme', t);
    if (localStorage.getItem('iem-a11y') === 'on') d.setAttribute('data-a11y', 'on');
  }} catch (e) {{}}
}})(document.documentElement);
</script>
<script defer src="js/main.js"></script>
</head>
<body{bc}>
<a class="skip-link" href="#inhalt">Zum Inhalt springen</a>
<header class="site-header">
  <div class="container site-header__inner">
    <a class="site-logo" href="index.html"><img class="logo-light" src="img/logo.svg" width="121" height="84" alt="Isabella-Edel-Museum – zur Startseite"><img class="logo-dark" src="img/logo-hell.svg" width="121" height="84" alt="Isabella-Edel-Museum – zur Startseite"></a>
    <a class="header-cta" href="tickets.html"{" aria-current=\"page\"" if nav_file == "tickets.html" else ""}>Tickets</a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="hauptmenue" hidden>
      <span class="nav-toggle__bars" aria-hidden="true"></span><span class="nav-toggle__label">Menü</span>
    </button>
    <nav class="main-nav" id="hauptmenue" aria-label="Hauptmenü">
      <ul>{nav}</ul>
    </nav>
  </div>
</header>
<main id="inhalt">
{main_html}
</main>
<footer class="site-footer">
  <div class="container site-footer__inner">
    <div class="site-footer__col">
      <a class="site-footer__logo" href="index.html"><img src="img/logo-hell.svg" width="121" height="84" alt="Isabella-Edel-Museum – zur Startseite"></a>
      <address>Isabella-Edel-Stiftung<br>Brixener Straße 5<br>28215 Bremen</address>
    </div>
    <div class="site-footer__col">
      <p class="site-footer__label">{picto("oeffnungszeiten")}Öffnungszeiten</p>
      <p>Dienstag–Sonntag: 11–17 Uhr</p>
    </div>
    <nav class="site-footer__col footer-nav" aria-label="Rechtliches">
      <ul>{fnav}</ul>
    </nav>
  </div>
  <p class="site-footer__exam container">Mediengestalter-Abschlussprüfung Winter 2024/25, ZFA Kassel</p>
</footer>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Seiten
# ---------------------------------------------------------------------------
SLIDES = [
    ("gruenderin.html", "gruenderin", "Isabella Edel, lächelnde ältere Dame mit weißem Haar",
     "Die Gründerin", "Jahrzehntelang hat Isabella Edel Kunstwerke gesammelt."),
    ("raeume.html", "besucherin-salon", "Besucherin betrachtet goldgerahmte Gemälde in einem klassischen Ausstellungssaal",
     "Räume", "Eine Auswahl aus über 300 Kunstwerken von 42 Künstlerinnen ist in vier Räumen zu sehen."),
    ("museumscafe.html", "museumscafe", "Gemütlicher Innenraum des Museumscafés mit Holztischen",
     "Museumscafé", "Hinter jeder erfolgreichen Frau steht eine beeindruckende Menge Kaffee"),
]


def index():
    def pager(active):
        # Ohne JS: Linien je Folie, die eigene ist hervorgehoben; Links springen zur Folie
        return ('<ol class="slider__pager" aria-label="Bildauswahl">' + "".join(
            f'<li><a class="slider__dot" href="#folie-{j + 1}" aria-label="Bild {j + 1}: {t}"'
            f'{" aria-current=\"true\"" if j == active else ""}></a></li>'
            for j, (_, _, _, t, _) in enumerate(SLIDES)) + "</ol>")
    slides = "".join(
        f'<li class="slider__slide" id="folie-{i + 1}" aria-roledescription="Folie" aria-label="{i + 1} von {len(SLIDES)}: {title}">'
        f'<a class="slider__link" href="{href}">'
        f'{picture(img, alt, lazy=i > 0, priority=i == 0, cls="slider__media")}'
        f'<span class="slider__caption"><span class="slider__title">{title}</span>'
        f'<span class="slider__text">{text}</span></span></a>{pager(i)}</li>'
        for i, (href, img, alt, title, text) in enumerate(SLIDES))
    teasers = [
        ("kuenstlerinnen.html", "kuenstlerin", "Künstlerin im Gespräch vor ihren farbenfrohen Bildern",
         "Künstlerinnen", "Das Isabella-Edel-Museum vereint die Werke von insgesamt 42 Künstlerinnen."),
        ("raeume.html", "r1-dame-hermelin", "Renaissance-Porträt einer Dame mit Hermelin",
         "Räume", "Im Isabella-Edel-Museum finden Sie die vier Ausstellungsräume"),
        ("museumscafe.html", "museumscafe", "Innenraum des Museumscafés",
         "Museumscafé", "Entspannen Sie sich bei gemütlichem Ambiente, einer heißen Tasse Kaffee und einem selbst gebackenen Stück Kuchen."),
        ("tickets.html", "paar-galerie", "Zwei Besucher betrachten abstrakte Bilder",
         "Tickets", "Ihr Besuch im Isabella-Edel-Museum"),
    ]
    teaser_html = "".join(
        f'<li class="teaser"><a href="{href}" class="teaser__link">'
        f'{picture(img, alt, sizes="(min-width: 1400px) 330px, (min-width: 576px) 50vw, 100vw", cls="teaser__media")}'
        f'<span class="teaser__title">{title}</span><span class="teaser__text">{text}</span></a></li>'
        for href, img, alt, title, text in teasers)
    main = f"""
<section class="slider" aria-roledescription="Karussell" aria-label="Einblicke ins Museum">
  <ul class="slider__track">{slides}</ul>
</section>

<div class="container home-intro">
  <h1 class="home-title">Das Isabella-Edel-Museum <span class="home-title__sub">– Übersehene Frauen und ihre Werke</span></h1>
  {quote("„Natürlich finden wir Frauen in sämtlichen Museen: Als Besucherinnen. Und als Aktmodelle. Manchmal habe ich den Eindruck, als Frau kommt man dort am besten rein, wenn man nackt ist.“", "Isabella Edel", "quote--large")}
</div>

<section class="container split split--home" aria-labelledby="macherin">
  <div class="split__media">{picture("malerin", "Nahaufnahme einer Hand, die mit dem Pinsel kräftige Farben auf eine Leinwand aufträgt", sizes="(min-width: 576px) 50vw, 100vw")}</div>
  <div class="split__text">
    <h2 id="macherin" class="section-title">Macherin statt Muse</h2>
    <p>Frauen sind in deutschen Kunstmuseen noch immer unterrepräsentiert: Weniger als 10 Prozent der ausgestellten Bilder wurden von Künstlerinnen gemalt. Das Isabella-Edel-Museum gibt nun ausschließlich Frauen eine Bühne: Eine Auswahl aus über 300 Kunstwerken von 42 Künstle&shy;rinnen ist in vier Räumen zu sehen.</p>
    <ul class="facts" aria-label="Zahlen">
      <li><span class="facts__num">300</span><span class="facts__label">Kunstwerke</span></li>
      <li><span class="facts__num">42</span><span class="facts__label">Künstlerinnen</span></li>
      <li><span class="facts__num">4</span><span class="facts__label">Räume</span></li>
    </ul>
  </div>
</section>

{quote_band("betrachterin", "Besucherin sitzt vor einer Wand mit farbenfrohen Gemälden",
            "„Wann immer wir auf Beschriftungen in einem Museum „Werkstatt“ oder „unbekannter Künstler“ lesen, sollten wir in Betracht ziehen, dass dieses Bild möglicherweise von einer Frau stammt, deren Leistung nicht gewürdigt wurde.“",
            "Isabella Edel", "Zitat von Isabella Edel")}

<section class="container teasers" aria-label="Entdecken">
  <ul class="teasers__list">{teaser_html}</ul>
</section>

<aside class="container visit-box" aria-label="Öffnungszeiten">
  {picto("oeffnungszeiten")}
  <p class="visit-box__label">Öffnungszeiten:</p>
  <p class="visit-box__hours">Dienstag–Sonntag: 11–17 Uhr</p>
  <a class="button" href="tickets.html">Tickets</a>
</aside>
"""
    return layout("index.html", "Startseite",
                  "Das Isabella-Edel-Museum in Bremen – Übersehene Frauen und ihre Werke.", main, "page-home")


def placeholder_page(file, title, img, alt, impressions=()):
    row = ""
    if impressions:
        items = "".join(f"<li>{picture(n, a, sizes='(min-width: 576px) 33vw, 100vw')}</li>" for n, a in impressions)
        row = f'<section class="container impressions" aria-label="Eindrücke"><ul class="impressions__list">{items}</ul></section>'
    main = f"""
{page_hero(img, alt, title)}
<div class="container prose">
  <p class="placeholder" role="note"><strong>Platzhalter:</strong> Für den Menüpunkt „{title}“ liegt im vorgegebenen Text (Website.docx) noch kein Inhalt vor. Diese Seite ist im Layout angelegt und wird ergänzt, sobald der Text geliefert wird.</p>
</div>
{row}
"""
    return layout(file, title, f"{title} – Isabella-Edel-Museum Bremen.", main)


# Künstlerinnen je Raum – nur Namen, die im Text des jeweiligen Raums genannt werden
ARTISTS = {
    "r1": ["Artemisia Gentileschi", "Lavinia Fontana", "Magdalena Haussmann", "Rosaba Carriera", "Anastasia Unterberg"],
    "r2": ["Adélaide Labille-Guiard"],
    "r3": ["Käthe Kollwitz", "Meret Oppenheim"],
    "r4": ["Mahbuba Elham Maqsoodi", "Irina Ojovan", "Joëlle Dubois", "Milja Laurila"],
}


def kuenstlerinnen():
    cards = "".join(
        f"""<li class="card artist-room">
      <div class="artist-room__head">{picto(rid)}<div><h3 class="artist-room__title">{title}</h3>
      <p class="artist-room__subtitle">{sub}</p></div></div>
      <ul class="artist-room__names">{"".join(f"<li>{n}</li>" for n in ARTISTS[rid])}</ul>
      <a class="artist-room__link" href="raeume.html#{rid}">Zum Raum<span class="visually-hidden"> {title}</span></a>
    </li>"""
        for rid, title, sub, *_ in ROOMS)
    main = f"""
{page_hero("kuenstlerin", "Eine Künstlerin präsentiert lachend ihre farbenfrohen Bilder vor Publikum", "Künstlerinnen")}
<div class="container split split--artists">
  <div class="split__text">
    <p class="lead">Das Isabella-Edel-Museum vereint die Werke von insgesamt 42 Künstlerinnen. Darunter befinden sich bekannte Größen wie Käthe Kollwitz und Berthe Morisot. Andere Künstlerinnen wurden aber auch vollkommen übersehen, ihre Bilder sind nun zum ersten Mal öffentlich zugänglich, darunter Karima Arat und Hafsa Khumalo. Das Besondere: Im Isabella-Edel-Museum können sich Besucher/-innen umfangreich über die Künstlerinnen informieren. Dafür sorgen hochspannende Biografien, die durch verschiedene Medien präsentiert werden.</p>
    <ul class="facts" aria-label="Zahlen">
      <li><span class="facts__num">42</span><span class="facts__label">Künstlerinnen</span></li>
      <li><span class="facts__num">300</span><span class="facts__label">Kunstwerke</span></li>
      <li><span class="facts__num">4</span><span class="facts__label">Räume</span></li>
    </ul>
  </div>
  <figure class="split__aside figure artwork">
    {zoom("r4-tinte", "Figur einer Frau aus violetter Tinte, die sich im Wind auflöst", sizes="(min-width: 1400px) 480px, (min-width: 576px) 45vw, 100vw")}
  </figure>
</div>

<section class="container artist-rooms" aria-labelledby="kuenstlerinnen-raeume">
  <h2 id="kuenstlerinnen-raeume" class="section-title">Im Isabella-Edel-Museum finden Sie die vier Ausstellungsräume</h2>
  <ul class="artist-rooms__list">{cards}
  </ul>
</section>

{quote_band("raeume", "Heller Ausstellungssaal mit Gemälden an weißen Wänden",
            "„Wann immer wir auf Beschriftungen in einem Museum „Werkstatt“ oder „unbekannter Künstler“ lesen, sollten wir in Betracht ziehen, dass dieses Bild möglicherweise von einer Frau stammt, deren Leistung nicht gewürdigt wurde.“",
            "Isabella Edel", "Zitat von Isabella Edel", cls="quote-band--end")}
"""
    return layout("kuenstlerinnen.html", "Künstlerinnen",
                  "42 Künstlerinnen – von Käthe Kollwitz bis zu bisher übersehenen Malerinnen.", main)


ROOMS = [
    ("r1", "R1: Renaissance bis Rokoko", "Wie Künstlerinnen die Antike wiederauferstehen lassen", [
        "<p>Im 15. und 16. Jahrhundert galt das Mittelalter als rückständig, viel lieber wandte man sich wieder der Kunst der Antike zu. An dieser Wiedergeburt der Antike waren nicht nur Männer, sondern auch zahlreiche Frauen beteiligt. Lernen Sie Artemisia Gentileschi kennen, die in ihrer Werkstatt auch Männer beschäftigte, und Lavinia Fontana, die in Bologna einen Doktortitel erwarb.</p>",
        "<p>Die Kunstwerke von Magdalena Haussmann sind vielerorts umstritten – die einen halten sie für eine Künstlerin der Renaissance. Die anderen sehen in ihr aufgrund ihres dramatischen Spiels mit Licht und Schatten viel eher eine frühe Vertreterin des Barocks.</p>",
        "<p>Die Verspieltheit und Leichtigkeit des Rokoko erleben Sie schließlich in den Kunstwerken von Rosaba Carriera und Anastasia Unterberg.</p>",
    ], [("r1-venus", "Renaissance-Gemälde: Frauengesicht mit wehendem, goldenem Haar"),
        ("r1-hell-dunkel", "Barockes Gemälde mit dramatischem Hell-Dunkel: eine Frau steht inmitten einer Menschenmenge"),
        ("r1-rokoko-garten", "Rokoko-Gemälde: Dame in Rüschenkleid auf einer Gartenbank zwischen Blumen")]),
    ("r2", "R2: Klassizismus bis Realismus", "Weibliche Kraft und Vitalität", [
        "<p>Der klar strukturierte und vital wirkende Klassizismus wurde seiner Zeit gemeinhin mit Männlichkeit in Verbindung gebracht. Doch die Künstlerinnen, die Sie in diesem Raum erleben, beweisen Ihnen das Gegenteil. Wir präsentieren Ihnen neben lange übersehenen und bisher unbekannten Künstlerinnen des Klassizismus und Realismus auch eine echte Berühmtheit:</p>",
        "<p>Auf Erlass des französischen Königs durften in den 1780er-Jahren nur vier Frauen Mitglieder in der königlichen Akademie werden. Eine davon war Adélaide Labille-Guiard. Später gründete sie die erste Frauenschule für Malerei in Paris und bezog als erste Frau ein Atelier im Louvre. Bekannt ist sie vor allem für ihre kraftvollen Porträts, von denen Sie eines nun sogar im Isabella-Edel-Museum bestaunen können.</p>",
    ], [("r2-portraet", "Porträt einer Dame mit gepudertem Haar an einem Tisch mit Früchten, im Stil der 1780er-Jahre"),
        ("r1-dame-hermelin", "Porträt einer jungen Frau mit einem Hermelin im Arm vor dunklem Hintergrund"),
        ("r2-landschaft", "Realistische Landschaft mit Teich unter bewölktem Himmel"),
        ("r2-garten", "Impressionistisches Gemälde: zwei Frauen im Garten")]),
    ("r3", "R3: Das 20. Jahrhundert", "Jede wirklich neue Idee ist eine Aggression", [
        '<blockquote class="quote quote--inline"><p>„Ich bitte Sie, meine Herren, eine Medaille für eine Frau. Das käme ja einer Herabwürdigung jeder hohen Auszeichnung gleich.“</p></blockquote>',
        "<p>Mit diesem Zitat reagiert Kaiser Wilhelm II. 1898 auf den Vorschlag, Käthe Kollwitz anlässlich ihres Weber-Zyklus die „Kleine Goldmedaille“ zu verleihen. Trotz seines entrüsteten Vetos wird Käthe Kollwitz eine der bedeutendsten Künstlerinnen des 20. Jahrhunderts. Erleben Sie in diesem Raum nicht nur, wie sich Kollwitz‘ Meisterwerke gegen Elend und Krieg stellen. Sondern auch, wie zahlreiche Werke weiterer Künstlerinnen die unendliche Vielfalt dieses Jahrhunderts widerspiegeln. Vertreterinnen von Expressionismus, Surrealismus, Abstrakter Kunst und Pop Art geben sich die Hand und stellen ein allein männlich geprägtes Kunstverständnis infrage. Oder, um es mit den Worten der Künstlerin Meret Oppenheim zu sagen: „Jede neue Idee ist eine Aggression.“</p>",
    ], [("r3-geometrie", "Abstrakte Komposition aus roten, blauen und grauen geometrischen Formen"),
        ("r3-vase", "Pop-Art-Grafik: schwarze Vase mit goldenen Punkten und orangefarbenen Blüten"),
        ("r3-expressiv", "Expressives Gemälde in leuchtendem Rot mit schwarzen Linien"),
        ("r3-portraet", "Porträt einer rothaarigen Frau mit langem Hals")]),
    ("r4", "R4: Künstlerinnen der Gegenwart", "Neue Brücken schaffen", [
        "<p>Die Künstlerin Mahbuba Elham Maqsoodi möchte Fragen stellen, statt Antworten zu liefern, und dabei neue Brücken schaffen. Als Kind lernte sie in ihrem Heimatland Afghanistan die persische Miniaturmalerei. Jahrzehnte später, in Deutschland, bemalte sie gewaltige Kirchenfenster. Im Isabella-Edel-Museum sind farbenprächtigen Glasmalereien von ihr zu sehen.</p>",
        "<p>Neben diesen Werken zeigen wir Ihnen außerdem zahlreiche weitere hochaktuelle Kunstwerke: Irina Ojovan setzt Emotionen in lineare und geometrische Formen um, Joëlle Dubois zeigt den Menschen in allen Formen und Größen für eine positive Körperwahrnehmung und Milja Laurila verwertet alte, von Männern verfasste Bücher und hinterfragt dabei ihren kolonialen und sexuellen Blick.</p>",
    ], [("r4-spirale", "Farbenprächtige Spirale aus bunten Pinseltupfen"),
        ("r4-figur", "Kleine Figur in rotem Kleid auf weiter, türkisfarbener Fläche"),
        ("r4-farbspritzer", "Abstraktes Bild aus bunten Farbspritzern")]),
]


def raeume():
    plan_inline = (ROOT / "partials" / "gebaeudeplan-inline.svg").read_text(encoding="utf-8")
    legend = "".join(
        f'<li><a href="#{rid}">{picto(rid)}<span>{title}</span></a></li>' for rid, title, *_ in ROOMS)
    legend += (f'<li><a href="museumscafe.html">{picto("cafe")}<span>Museumscafé</span></a></li>'
               f'<li><a href="tickets.html">{picto("tickets")}<span>Tickets</span></a></li>'
               f'<li><span class="legend__item">{picto("toiletten")}<span>Toiletten</span></span></li>')
    articles = []
    for i, (rid, title, sub, paras, imgs) in enumerate(ROOMS):
        pager = ""
        if i > 0:
            prid, ptitle = ROOMS[i - 1][:2]
            pager += (f'<a class="room__pager-link room__pager-link--prev" href="#{prid}">'
                      f'<span class="room__pager-label">Vorheriger Raum</span>{ptitle}</a>')
        if i < len(ROOMS) - 1:
            nrid, ntitle = ROOMS[i + 1][:2]
            pager += (f'<a class="room__pager-link room__pager-link--next" href="#{nrid}">'
                      f'<span class="room__pager-label">Nächster Raum</span>{ntitle}</a>')
        wall = "".join(
            f'<li style="--r: {ratio(n)}">{zoom(n, a, sizes="(min-width: 1400px) 33vw, (min-width: 576px) 50vw, 100vw")}</li>'
            for n, a in imgs)
        articles.append(f"""
<article class="room" id="{rid}" aria-labelledby="{rid}-title">
  <div class="room__intro">
    <header class="room__header">
      {picto(rid)}
      <div><h2 id="{rid}-title" class="room__title">{title}</h2>
      <p class="room__subtitle">{sub}</p></div>
    </header>
    <div class="room__text prose">{"".join(paras)}</div>
  </div>
  <ul class="room__wall" aria-label="Werke in {title.split(":")[0]}">{wall}</ul>
  <nav class="room__nav" aria-label="Navigation {title.split(":")[0]}">
    <a class="room__back" href="#gebaeudeplan" data-room="{rid}">Zurück zum Gebäudeplan</a>
    <div class="room__pager">{pager}</div>
  </nav>
</article>""")
    main = f"""
{page_hero("besucherin-salon", "Besucherin betrachtet goldgerahmte Gemälde in einem klassischen Ausstellungssaal", "Räume")}
<section class="container plan" id="gebaeudeplan" aria-labelledby="plan-heading">
  <h2 id="plan-heading" class="plan__heading">Im Isabella-Edel-Museum finden Sie die vier Ausstellungsräume</h2>
  <div class="plan__layout">
    <figure class="plan__figure">
      <!-- Smartphone (< 576 px): nicht anklickbare Grafik -->
      <img class="plan__static" src="img/gebaeudeplan.svg" width="828" height="502" alt="Isometrischer Gebäudeplan: Die Räume R3 und R4 liegen im langen Flügel links. R2 und R1 bilden rechts davon einen L-förmigen Gebäudeteil. In der Innenecke des L liegt der Eingang mit Ticketverkauf, vorne links befinden sich Museumscafé und Toiletten.">
      <!-- Tablet/Desktop (≥ 576 px): klickbare Räume -->
      <div class="plan__interactive">{plan_inline}</div>
    </figure>
    <ul class="plan__legend" aria-label="Legende zum Gebäudeplan">{legend}</ul>
  </div>
</section>
<div class="container rooms">{"".join(articles)}
</div>
"""
    return layout("raeume.html", "Räume",
                  "Die vier Ausstellungsräume des Isabella-Edel-Museums mit Gebäudeplan.", main, "page-rooms")


def gruenderin():
    main = f"""
{page_hero("gruenderin", "Porträt von Isabella Edel", "Die Gründerin")}
<div class="container split">
  <div class="split__text prose">
    <p class="lead">Jahrzehntelang hat Isabella Edel Kunstwerke gesammelt. Ihr Fokus: Malereien von Frauen, die in der Kunstwelt übersehen wurden. Anlässlich ihres 80. Geburtstags erfüllt sie sich einen lange gehegten Wunsch und eröffnet ein Museum, in dem ausschließlich Werke von Künstlerinnen zu sehen sind: das Isabella-Edel-Museum.</p>
    <p>Isabella Edel ist 1944 in Bremen geboren. Bereits in den 60er-Jahren setzte sie sich öffentlich&shy;keitswirksam mit der Nazivergangenheit ihres Vaters, dem Kaffeefilter-Hersteller Hermann Edel auseinander. Die Firma, die sie 1984 von ihm übernahm, veräußerte sie bereits zwei Jahre später. Vom Erlös gründete sie nicht nur die Stiftung „Niemals vergessen“, sondern setzte sich auch aktiv für die Sichtbarmachung von Frauen in Kunst und Kultur ein.</p>
  </div>
  <div class="split__aside">
    <figure class="figure">{picture("bremen", "Historische Giebelhäuser in Bremen", sizes="(min-width: 576px) 40vw, 100vw")}
      <figcaption>Isabella Edel ist 1944 in Bremen geboren.</figcaption></figure>
  </div>
</div>
{quote_band("betrachterin", "Besucherin sitzt vor einer Wand mit farbenfrohen Gemälden",
            "Ihr Fokus: Malereien von Frauen, die in der Kunstwelt übersehen wurden.",
            label="Leitgedanke der Sammlung", cls="quote-band--end")}
"""
    return layout("gruenderin.html", "Die Gründerin",
                  "Isabella Edel – Kunstmäzenin aus Bremen und Gründerin des Museums.", main)


def museumscafe():
    main = f"""
{page_hero("museumscafe", "Innenraum des Museumscafés mit Holztischen und warmem Licht", "Museumscafé")}
<div class="container split split--cafe">
  <div class="split__text">
    <p class="lead">In unserem Museumscafé können Sie sich Ihren Rundgang Revue passieren lassen und sich erholen. Entspannen Sie sich bei gemütlichem Ambiente, einer heißen Tasse Kaffee und einem selbst gebackenen Stück Kuchen. Saisonal bieten wir zudem kleine Snacks an.</p>
    <p>Im Winter knistert ein Feuer im Kamin, im Sommer lädt unser kleines Gärtchen zum Verweilen ein.</p>
  </div>
  <aside class="split__aside card visit-card" aria-label="Ihr Besuch im Museumscafé">
    <div class="visit-card__item">{picto("oeffnungszeiten")}<div><p class="visit-card__label">Öffnungszeiten:</p><p>Dienstag–Sonntag: 11–17 Uhr</p></div></div>
    <div class="visit-card__item">{picto("cafe")}<div><p class="visit-card__label">Museumscafé</p><p><a href="raeume.html#gebaeudeplan">Lage im Gebäudeplan</a></p></div></div>
  </aside>
</div>

{quote_band("besucherinnen-gespraech", "Gruppe von Frauen im angeregten Gespräch vor einem abstrakten Gemälde",
            "Hinter jeder erfolgreichen Frau steht eine beeindruckende Menge Kaffee",
            label="Motto des Museumscafés", cls="quote-band--end")}
"""
    return layout("museumscafe.html", "Museumscafé",
                  "Kaffee, selbst gebackener Kuchen und ein kleines Gärtchen im Museumscafé.", main)


def visit_aside():
    """Infokarte „Ihr Besuch“ (rechte Spalte auf Tickets- und Bestätigungsseite)."""
    return f"""<aside class="tickets__aside" aria-label="Ihr Besuch">
    <div class="card visit-card">
      <div class="visit-card__item">{picto("oeffnungszeiten")}<div><p class="visit-card__label">Öffnungszeiten:</p><p>Dienstag–Sonntag: 11–17 Uhr</p></div></div>
      <div class="visit-card__item">{picto("tickets")}<div><p class="visit-card__label">Ticketkasse</p><p>Die Karten können an der Ticketkasse bei Abholung bezahlt werden.</p></div></div>
      <address class="visit-card__address">Isabella-Edel-Stiftung<br>Brixener Straße 5<br>28215 Bremen</address>
    </div>
  </aside>"""


def tickets():
    main = f"""
{page_hero("paar-galerie", "Zwei Besucher betrachten abstrakte Bilder in einer hellen Galerie", "Tickets")}
<div class="container tickets">
  <h2 class="tickets__title">Ihr Besuch im Isabella-Edel-Museum</h2>
  {stepper(1)}
  <form class="ticket-form" action="tickets-bestaetigung.html" method="get">
    <fieldset class="card ticket-form__step" id="ticketart">
      <legend>Ticketart wählen</legend>
      <div class="ticket-row">
        <span class="ticket-row__type" id="t-erw">Erwachsene</span>
        <span class="ticket-row__price" data-price="10">10 Euro</span>
        <label class="ticket-row__qty"><span>Anzahl der Tickets</span>
          <input type="number" name="erwachsene" min="0" max="20" value="0" inputmode="numeric" aria-describedby="t-erw"></label>
      </div>
      <div class="ticket-row">
        <span class="ticket-row__type" id="t-erm">Ermäßigte*</span>
        <span class="ticket-row__price" data-price="8">8 Euro</span>
        <label class="ticket-row__qty"><span>Anzahl der Tickets</span>
          <input type="number" name="ermaessigte" min="0" max="20" value="0" inputmode="numeric" aria-describedby="t-erm"></label>
      </div>
      <p class="form-note">*Kinder und Jugendliche bis 18 Jahren sowie Student/-innen</p>
      <a class="button" href="#persoenliche-angaben" data-confirm>Auswahl bestätigen</a>
      <p class="form-note">Die Karten können an der Ticketkasse bei Abholung bezahlt werden.</p>
    </fieldset>

    <fieldset class="card ticket-form__step" id="persoenliche-angaben">
      <legend>Persönliche Angaben</legend>
      <div class="form-grid">
        <label>Vorname**<input type="text" name="vorname" autocomplete="given-name" required></label>
        <label>Name**<input type="text" name="name" autocomplete="family-name" required></label>
        <label>E-Mail-Adresse**<input type="email" name="email" autocomplete="email" required></label>
        <label>Telefon<input type="tel" name="telefon" autocomplete="tel"></label>
        <label class="span-3">Straße<input type="text" name="strasse" autocomplete="address-line1"></label>
        <label class="span-1">Hausnummer<input type="text" name="hausnummer" inputmode="numeric"></label>
        <label class="span-1">Postleitzahl<input type="text" name="plz" autocomplete="postal-code" inputmode="numeric" pattern="[0-9]{{5}}"></label>
        <label class="span-3">Ort<input type="text" name="ort" autocomplete="address-level2"></label>
      </div>
      <p class="form-note">**Pflichtangaben</p>
      <button class="button" type="submit">Bestellung abschließen und Tickets kaufen</button>
    </fieldset>
  </form>
  {visit_aside()}
</div>
"""
    return layout("tickets.html", "Tickets",
                  "Öffnungszeiten und Ticketreservierung für das Isabella-Edel-Museum.", main, "page-tickets")


def logo_inline():
    """Logo als Inline-SVG (für Ticket: Druck und PNG-Download zeichnen es exakt nach)."""
    svg = (IMG / "logo.svg").read_text(encoding="utf-8")
    svg = svg[svg.index("<svg"):]
    svg = svg.replace('<svg role="img" aria-label="Isabella Edel Museum"',
                      '<svg class="ticket__logo" role="img" aria-label="Isabella-Edel-Museum"', 1)
    svg = re.sub(r'\s(width|height)="[^"]*"', "", svg[:200], count=2) + svg[200:]
    return svg.replace('id="clip-0"', 'id="ticket-logo-clip"').replace('url(#clip-0)', 'url(#ticket-logo-clip)').strip()


def tickets_bestaetigung():
    """Ziel des Ticketformulars. Ohne JS: allgemeine Bestätigung.
    Mit JS: Ticket mit den übermittelten Formulardaten (URL-Parameter), Druck und Download."""
    main = f"""
<header class="page-intro container"><h1>Tickets</h1></header>
<div class="container tickets tickets--confirm">
  {stepper(3)}
  <section class="confirmation" aria-labelledby="bestaetigung-titel">
    <div class="confirmation__head">
      <span class="confirmation__check" aria-hidden="true"></span>
      <div>
        <h2 id="bestaetigung-titel" class="confirmation__title">Vielen Dank für Ihre Reservierung!</h2>
        <p class="confirmation__lead">Ihre Tickets für das Isabella-Edel-Museum sind für Sie zurückgelegt.</p>
      </div>
    </div>

    <article class="ticket" aria-label="Ihr Ticket" hidden>
      <div class="ticket__main">
        {logo_inline()}
        <p class="ticket__kicker">Reservierungsbestätigung</p>
        <p class="ticket__name" data-field="name"></p>
        <dl class="ticket__rows">
          <div><dt>Erwachsene</dt><dd data-field="erwachsene" data-price="10"></dd></div>
          <div><dt>Ermäßigte</dt><dd data-field="ermaessigte" data-price="8"></dd></div>
          <div class="ticket__sum"><dt>Summe</dt><dd data-field="summe"></dd></div>
        </dl>
        <p class="ticket__meta">Reservierung <strong data-field="nummer"></strong> · <span data-field="datum"></span></p>
      </div>
      <div class="ticket__stub">
        {picto("tickets")}
        <p>Die Karten können an der Ticketkasse bei Abholung bezahlt werden.</p>
        <p><strong>Öffnungszeiten:</strong><br>Dienstag–Sonntag: 11–17 Uhr</p>
        <p class="ticket__address">Brixener Straße 5<br>28215 Bremen</p>
      </div>
    </article>

    <div class="confirmation__actions">
      <div class="confirmation__ticket-actions" hidden>
        <button class="button" type="button" data-ticket="print">Ticket drucken</button>
        <button class="button button--ghost" type="button" data-ticket="download">Ticket als PDF herunterladen</button>
      </div>
      <p class="confirmation__links">
        <a href="index.html">Zur Startseite</a>
        <a href="tickets.html">Weitere Tickets reservieren</a>
      </p>
    </div>
  </section>
  {visit_aside()}
</div>
"""
    return layout("tickets-bestaetigung.html", "Bestätigung",
                  "Bestätigung Ihrer Ticketreservierung im Isabella-Edel-Museum.", main,
                  "page-confirmation", nav_file="tickets.html")


def impressum():
    main = f"""
{page_hero("bremen", "Historische Giebelhäuser in Bremen", "Impressum")}
<div class="container prose">
  <address class="imprint">
    <strong>Isabella-Edel-Stiftung</strong><br>
    Brixener Straße 5<br>
    28215 Bremen<br>
    Tel: <a href="tel:+494216658484">+49 421 6658484</a><br>
    Fax: +49 421 6658485<br>
    E-Mail: <a href="mailto:info@isabella-edel-museum.de">info@isabella-edel-museum.de</a><br>
    <a href="index.html">www.isabella-edel-museum.de</a>
  </address>
  <p>Die Isabella-Edel-Stiftung ist eine öffentliche Stiftung privaten Rechts.<br>
  Vorstandsvorsitzende: Dr. Isa Bertram</p>
</div>
"""
    return layout("impressum.html", "Impressum", "Impressum der Isabella-Edel-Stiftung.", main)


def main():
    pages = {
        "index.html": index(),
        "veranstaltungen.html": placeholder_page("veranstaltungen.html", "Veranstaltungen", "zwei-frauen-galerie",
                                                 "Zwei Frauen im Gespräch in einer Galerie mit dunklen Wänden",
                                                 [("besucherinnen-gespraech", "Gruppe junger Frauen im Gespräch vor einem abstrakten Gemälde"),
                                                  ("betrachter", "Nachdenklicher Besucher in einer Ausstellung"),
                                                  ("fotoausstellung", "Besucherin betrachtet Fotografien an einer blauen Wand")]),
        "kuenstlerinnen.html": kuenstlerinnen(),
        "raeume.html": raeume(),
        "gruenderin.html": gruenderin(),
        "museumscafe.html": museumscafe(),
        "tickets.html": tickets(),
        "tickets-bestaetigung.html": tickets_bestaetigung(),
        "impressum.html": impressum(),
        "datenschutz.html": placeholder_page("datenschutz.html", "Datenschutz", "fotoausstellung",
                                             "Besucherin betrachtet Fotografien an einer blauen Wand"),
    }
    for name, html in pages.items():
        (ROOT / name).write_text(html, encoding="utf-8", newline="\n")
    print(f"{len(pages)} Seiten geschrieben.")


if __name__ == "__main__":
    main()
