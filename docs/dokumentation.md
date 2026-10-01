# Dokumentation zur Gestaltung – Website Isabella-Edel-Museum

Prüfling: [Name] · Kenn-Nummer: [Nummer]

## 1. Gestaltungsidee: „Macherin statt Muse“

Die Website versteht sich als weiße Galeriewand: Sie nimmt sich zurück und überlässt den Werken der Künstlerinnen die Bühne. Edel wirkt sie durch Ruhe, großzügigen Weißraum und klassische Typografie. Lebendig wird sie durch großformatige Bilder, die zwischen Kunstwerken und Menschen im Museum wechseln, und durch Zitate, die als typografische Bilder eingesetzt werden. Als wiederkehrendes Stilelement dient der senkrechte violette Balken aus dem Logo. Er markiert Überschriften, Zitate, den aktiven Menüpunkt und den Rand der Piktogramme und verbindet so alle Seiten mit der Marke.

## 2. Seitenaufbau und Raster

Jede Seite hat dieselbe Abfolge: Kopfzeile mit Logo und Hauptmenü → Slider (Startseite) bzw. Bildstreifen mit Seitentitel (Unterseiten) → Inhalt → dunkle Fußzeile mit Adresse, Öffnungszeiten, Impressum und Datenschutz. Die Kopfzeile bleibt beim Scrollen stehen, „Tickets“ ist als Button hervorgehoben.

- **< 576 px (Smartphone):** einspaltig, 16 px Seitenrand, Menü hinter einem „Menü“-Button. Bilder stehen über dem Text.
- **≥ 576 px (Tablet):** zweispaltige Bild-Text-Kombinationen und Teaser-Raster, 32 px Rand.
- **≥ 1400 px (Desktop):** komplette horizontale Navigation, Inhaltsbreite maximal 1320 px, asymmetrische Spalten (7:5), vier Teaser nebeneinander. Slider und Bildstreifen laufen immer über die volle Breite.

Alle Breiten sind fließend angelegt, damit jedes Gerät seine native Breite nutzt.

## 3. Farbe

| Farbe | Wert | Einsatz |
|---|---|---|
| Galerieweiß | #F8F6F2 | Hintergrund, warm statt kaltem Reinweiß |
| Anthrazit | #2B2B2A | Text, Fußzeile (aus dem Logo) |
| Violett | #443189 | einzige Akzentfarbe: Links, Buttons, Balken, Piktogramme (aus dem Logo) |
| Violett hell | #ECE9F4 | Flächen, Böden im Gebäudeplan |

Die Palette ist bewusst zurückhaltend, denn die Farbigkeit liefern die Gemälde. Violett steht für Würde und ist historisch die Farbe der Frauenbewegung. Damit passt es inhaltlich zum Museum. Violett auf Galerieweiß erreicht einen Kontrast von etwa 10:1 und erfüllt damit WCAG AA.

## 4. Typografie

- **Cormorant Garamond** (Serif) für Überschriften, Zitate und Zahlen: Die klassische Garalde schlägt die Brücke zur Kunstgeschichte von der Renaissance bis heute und wirkt elegant. Sie wird nur ab 24 px eingesetzt, damit die feinen Serifen gut lesbar bleiben. Ziffern werden als Versalziffern gesetzt („R1“ statt „Rı“).
- **Source Sans 3** (serifenlose Linear-Antiqua) für Fließtext, Menü und Formulare: neutral, offen und auch auf kleinen Bildschirmen sehr gut lesbar.
- **Raumaufteilung und Lesbarkeit:** Fließtext 17–19 px (fluid), Zeilenabstand 1,6, Zeilenlänge maximal ca. 65 Zeichen, linksbündiger Flattersatz mit automatischer Silbentrennung. Großzügige Abstände zwischen den Abschnitten (48–96 px) schaffen Ruhe.
- Beide Schriften liegen lokal im Projekt (woff2, SIL Open Font License). Dadurch läuft die Seite offline und lädt keine Daten von Google.

## 5. Bilder

- **Bildsprache:** zwei Ebenen im Wechsel. Kunstwerke zeigen die Sammlung, Menschen beim Betrachten zeigen ein lebendiges, offenes Museum.
- **Anordnung:** Slider und Bildstreifen randabfallend über die volle Breite. Im Inhalt stehen Bilder neben dem Text. In den Ausstellungsräumen hängen die Werke wie an einer Museumswand nebeneinander auf gleicher Höhe (Desktop), zweispaltig (Tablet) bzw. untereinander (Smartphone) – immer unbeschnitten.
- **Bildausschnitt:** Fotos von Räumen und Menschen werden per `object-fit` auf das Format zugeschnitten, mit gesetztem Bildschwerpunkt (z. B. das Gesicht der Gründerin). Kunstwerke werden **nie beschnitten**, sondern immer im Originalformat gezeigt (Werktreue).
- **Modifikation:** Im Slider liegt ein dunkler Verlauf über dem unteren Bildrand, damit die weiße Schrift lesbar bleibt. Alle Bilder wurden für das Web skaliert und als WebP mit JPG-Fallback in drei Größen (640/1280/2000 px) exportiert. Der Browser lädt über `srcset` nur die passende Größe.

## 6. Piktogramme

Alle acht Piktogramme bauen auf demselben System auf: 48 × 48-px-Raster, quadratischer Rahmen mit 3 px Eckenradius, 2,5 px Strichstärke mit runden Enden, links der violette Balken aus dem Logo.

- **R1–R4:** einheitlich, violett gefüllt, weiße konstruierte Ziffern. So sind sie als zusammengehörige Gruppe „Ausstellungsräume“ erkennbar.
- **Museumscafé (Tasse), Toiletten (Figuren), Ticketverkauf (Eintrittskarte)** sowie ergänzend **Öffnungszeiten (Uhr):** gleicher Rahmen, aber als Kontur. Sie gehören sichtbar zur selben Familie und sind trotzdem als Service-Kategorie unterscheidbar. Die Formen sind bewusst reduziert, damit sie auch bei 24 px lesbar bleiben.

## 7. Gebäudeplan unter „Räume“ (viewportabhängig)

Der Plan wurde nach der Skizze als isometrisches SVG (30°) neu gezeichnet: langer Flügel mit R3/R4, R2 und R1 als L-förmiger Gebäudeteil, in dessen Innenecke der Eingang mit Ticketverkauf liegt, vorne Café und Toiletten. Die Räume sind oben offen dargestellt, die Böden sind hell eingefärbt, und die Piktogramme stehen auf den Räumen. Er liegt in zwei Varianten im HTML. Die Umschaltung erfolgt **nur per CSS-Media-Query** und funktioniert damit auch ohne JavaScript:

- **< 576 px:** Angezeigt wird `<img src="gebaeudeplan.svg">`, eine reine, nicht anklickbare Grafik. Darunter steht die Legende als Liste mit Piktogramm und Raumnamen. Jeder Raumpunkt ist ein Sprunglink (`#r1` … `#r4`), Café und Tickets verlinken auf ihre Unterseiten. Große Tippflächen (mind. 56 px hoch).
- **≥ 576 px:** Die Grafik wird mit `display: none` ausgeblendet. Sichtbar ist stattdessen das inline eingebundene SVG, in dem jeder Raum ein `<a href="#r1">` ist. Bei Mausberührung oder Tastaturfokus färbt sich der Raum violett, und ein Namensschild mit dem Raumtitel erscheint (CSS `:has()`). `display: none` entfernt die jeweils unsichtbare Variante auch aus der Tab-Reihenfolge und für Screenreader. Ab 1400 px steht die Legende neben dem Plan; fährt man mit der Maus über einen Legendenpunkt, hebt JavaScript den Raum im Plan hervor.
- Der angesprungene Raum wird per CSS `:target` mit dem violetten Balken markiert und leuchtet kurz auf, damit klar ist, wo man gelandet ist.
- Der Plan-Abschnitt hat `id="gebaeudeplan"`. Jede Raumbeschreibung endet mit „Zurück zum Gebäudeplan“ sowie Links zum vorherigen und nächsten Raum. Beim Rücksprung markiert JavaScript den zuletzt besuchten Raum im Plan und in der Legende. `scroll-margin-top` verhindert, dass die feste Kopfzeile das Sprungziel verdeckt.

## 8. Mobile First und Progressive Enhancement

Das CSS beschreibt zuerst die Smartphone-Ansicht und erweitert sie mit `min-width`-Media-Queries (576 px, 1400 px). Die Basis ist semantisches HTML5 (`header`, `nav`, `main`, `article`, `figure`, `form`/`fieldset`), das auch ohne CSS und JavaScript in sinnvoller Reihenfolge lesbar und bedienbar ist. Ein kleiner Test im `<head>` („Cutting the Mustard“) setzt nur in modernen Browsern die Klasse `js`. Nur dann wird erweitert:

| Funktion | ohne JavaScript | mit JavaScript |
|---|---|---|
| Menü | Linkliste immer sichtbar | Menü-Button mit Overlay, Esc schließt |
| Slider | wischbare Bildleiste (CSS Scroll-Snap) mit Linien-Paginierung als Sprunglinks, alle Links nutzbar | Endlosschleife, Autoplay, Pfeile, Punkte, Pause; stoppt bei Hover/Fokus und bei „reduzierter Bewegung“ |
| Gebäudeplan | Klick, Legende, Hover-Namensschild und `:target`-Markierung per HTML/CSS | Legende hebt Räume im Plan hervor, Rücksprung markiert den zuletzt besuchten Raum |
| Tickets | komplettes Formular mit Pflichtfeldprüfung des Browsers, Bestätigungsseite | Schrittanzeige, Live-Summe, Prüfung „mind. ein Ticket“, Schritt 2 nach „Auswahl bestätigen“, Ticket auf der Bestätigungsseite, Druck nur des Tickets (Print-CSS), Download als PDF (Canvas + selbst erzeugte PDF-Datei, ohne Bibliothek) |
| Galerien | Link öffnet die große Bilddatei | Lightbox (`<dialog>`) mit Blättern, Esc schließt |

Für alte Browser gibt es Fallbacks: zuerst eine feste Angabe, dann `clamp()`/`min()`; JPG neben WebP; Systemschriften als Ersatz.
