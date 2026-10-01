# Dokumentation zur Gestaltung – Website Isabella-Edel-Museum

Prüfling: [Name] · Kenn-Nummer: [Nummer]

## 1. Gestaltungsidee: „Macherin statt Muse“

Die Website ist als weiße Galeriewand gedacht, die den Werken der Künstlerinnen die Bühne überlässt. Edel wirkt sie durch Ruhe, Weißraum und klassische Typografie, lebendig durch großformatige Bilder und Zitate als typografische Bilder. Stilelement ist der senkrechte violette Balken aus dem Logo: Er markiert Seitentitel, Zitate, den aktiven Menüpunkt und die Piktogramme.

## 2. Seitenaufbau und Raster

Jede Seite folgt derselben Abfolge: feste Kopfzeile mit Logo, Menü und „Tickets“-Button → Slider bzw. Bildstreifen mit Seitentitel → Inhalt → dunkle Fußzeile. Unterseiten nutzen dieselben Bausteine: Text neben Bild oder Infokarte, Karten mit Piktogramm, violettes Zitatband als Abschluss.

- **< 576 px:** einspaltig, 20 px Rand, Menü hinter „Menü“-Button, „Tickets“ bleibt sichtbar.
- **≥ 576 px:** zweispaltige Bild-Text-Kombinationen, 40 px Rand.
- **≥ 1400 px:** horizontale Navigation, Inhalt max. 1320 px, asymmetrische Spalten (7 : 5), 64 px Rand.

Alle Breiten sind fließend, jedes Gerät nutzt seine native Breite.

## 3. Farbe

| Farbe | Wert | Einsatz |
|---|---|---|
| Galerieweiß | #F8F6F2 | Hintergrund, wärmer als Reinweiß |
| Anthrazit | #2B2B2A | Text, Fußzeile (aus dem Logo) |
| Violett | #443189 | einzige Akzentfarbe (aus dem Logo) |
| Violett hell | #ECE9F4 | Flächen, Böden im Gebäudeplan |

Die Farbigkeit liefern die Gemälde, daher bleibt die Palette zurückhaltend. Violett steht für Würde und ist die Farbe der Frauenbewegung. Kontrast Violett auf Galerieweiß ca. 10 : 1 (WCAG AA). Alle Farben sind CSS-Variablen. Der **dunkle Modus** tauscht nur diese Variablen. Standard ist die Systemeinstellung, ein Umschalter überschreibt sie.

## 4. Typografie

- **Cormorant Garamond** (Garalde) für Überschriften, Zitate und Zahlen: elegant, mit Bezug zur Kunstgeschichte. Nur ab 24 px, mit Versalziffern.
- **Source Sans 3** (serifenlose Linear-Antiqua) für Fließtext, Menü und Formulare: neutral und gut lesbar.
- **Lesbarkeit:** 17–19 px (fluid), Zeilenabstand 1,7, ca. 65 Zeichen pro Zeile, linksbündiger Flattersatz. Abschnittsabstände von 64–128 px schaffen Ruhe.
- Beide Schriften liegen lokal vor (woff2, SIL Open Font License, Quelle: fontsource.org), die Seite läuft so offline.

## 5. Bilder

- **Bildsprache:** Kunstwerke zeigen die Sammlung, Menschen beim Betrachten ein lebendiges Museum.
- **Anordnung:** Slider, Bildstreifen und Zitatbänder randabfallend. In den Räumen hängen die Werke wie an einer Museumswand auf gleicher Höhe (Desktop), zweispaltig (Tablet) oder untereinander (Smartphone).
- **Bildausschnitt:** Fotos werden per `object-fit` mit gesetztem Schwerpunkt zugeschnitten. Kunstwerke werden **nie beschnitten** (Werktreue).
- **Modifikation:** Verlauf im Slider für lesbare Schrift. Export als WebP mit JPG-Fallback in drei Größen, per `srcset` lädt der Browser nur die passende.

## 6. Piktogramme

Alle acht Piktogramme folgen einem System: 48-px-Raster, quadratischer Rahmen, 2,5 px Strich mit runden Enden, links der Logo-Balken. **R1–R4** sind violett gefüllt mit konstruierten Ziffern. **Museumscafé, Toiletten, Ticketverkauf** und **Öffnungszeiten** nutzen denselben Rahmen als Kontur. Sie gehören sichtbar zur Familie und sind trotzdem als Service-Kategorie unterscheidbar.

## 7. Gebäudeplan unter „Räume“ (viewportabhängig)

Der Plan wurde nach der Skizze als isometrisches SVG neu gezeichnet, mit den Piktogrammen auf den Räumen. Er liegt in zwei Varianten im HTML. Umgeschaltet wird **nur per CSS-Media-Query**, also auch ohne JavaScript:

- **< 576 px:** `<img>` als nicht anklickbare Grafik. Darunter steht eine Legende mit Sprunglinks (`#r1` … `#r4`) und großen Tippflächen.
- **≥ 576 px:** Die Grafik ist ausgeblendet (`display: none`), sichtbar ist das Inline-SVG. Jeder Raum ist ein Link `<a href="#r1">`. Bei Maus oder Tastaturfokus färbt er sich violett und zeigt ein Namensschild (`:has()`).
- `display: none` nimmt die unsichtbare Variante auch aus Tab-Reihenfolge und Screenreader. Der angesprungene Raum wird per `:target` markiert. Jede Beschreibung endet mit „Zurück zum Gebäudeplan“ und Links zum Nachbarraum. `scroll-margin-top` hält das Ziel unter der festen Kopfzeile sichtbar.

## 8. Mobile First, Progressive Enhancement, Barrierefreiheit

Das CSS beschreibt zuerst die Smartphone-Ansicht und erweitert sie per `min-width` (576 px, 1400 px). Basis ist semantisches HTML5, das auch ohne CSS und JavaScript bedienbar ist. Ein Test im `<head>` („Cutting the Mustard“) aktiviert die Erweiterungen nur in modernen Browsern:

| Funktion | ohne JavaScript | mit JavaScript |
|---|---|---|
| Menü | Linkliste sichtbar | Menü-Button mit Overlay |
| Slider | wischbare Leiste, Linien als Sprunglinks | Endlosschleife, Autoplay mit Pause |
| Gebäudeplan | Klick, Legende, `:target` | Legende hebt Räume hervor |
| Tickets | Formular, Bestätigungsseite | Live-Summe, Ticket mit Druck/PDF |

Ein **barrierefreier Modus** vergrößert die Schrift, setzt alles serifenlos, erhöht den Kontrast, unterstreicht Links und schaltet Animationen ab. Ergänzte Bedientexte (z. B. „Zum Raum“) verändern den vorgegebenen Text nicht.
