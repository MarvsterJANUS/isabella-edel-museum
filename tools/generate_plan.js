/* Erzeugt den isometrischen Gebäudeplan als SVG (Grundlage: Skizze Gebaeudeplan.jpg/.pdf).

   Aufruf (im Projektordner):  node tools/generate_plan.js
   Ausgabe: img/gebaeudeplan.svg (nicht anklickbar, Smartphone),
            partials/gebaeudeplan-inline.svg (klickbare Variante) und
            aktualisiert den Plan direkt in raeume.html.

   Planachsen wie in der Skizze: a läuft nach rechts oben, b nach rechts unten, z nach oben.
   Grundriss laut Skizze:
   - links der lange Flügel: R3 vorne, R4 hinten
   - rechts daneben ein L-förmiger Gebäudeteil ohne Trennwand: R2 (parallel zum Flügel)
     und R1 (nach vorne rechts)
   - zwischen Café und R2/R1 der Eingang: Glasfront, Ticketverkauf, flaches Podest davor
   - vorne links das L-förmige Museumscafé mit Toiletten */
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const VIOLET = '#443189';
const TINT = '#ECE9F4';
const INK = '#2B2B2A';
const WHITE = '#FFFFFF';

const U = 38;                         // Pixel pro Planeinheit
const C = Math.cos(Math.PI / 6), S = 0.5;
const H = 1.2;                        // Wandhöhe der Räume

const p = (a, b, z = 0) => [(a + b) * C * U, (b - a) * S * U - z * U];
const line = ([x1, y1], [x2, y2], cls) => `<line x1="${x1.toFixed(1)}" y1="${y1.toFixed(1)}" x2="${x2.toFixed(1)}" y2="${y2.toFixed(1)}" class="${cls}"/>`;
const poly = (pts, cls) => `<polygon points="${pts.map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join(' ')}" class="${cls}"/>`;

/* Ein Kasten = rechteckiger Raumteil. walls: welche der vier Wände gezeichnet werden
   (bei L-Formen und gemeinsamen Wänden wird eine Seite weggelassen).
   b0/a1 = hintere Wände (Innenseite sichtbar), b1/a0 = vordere Wände (Außenseite sichtbar).
   Ein Wert [von, bis] zeichnet die Wand nur auf einem Teilstück. */
function box({ a0, a1, b0, b1, h = H, walls = {} }) {
  const w = { b0: true, a1: true, b1: true, a0: true, ...walls };
  const seg = (v, from, to) => (v === true ? [from, to] : v);
  let out = poly([p(a0, b0), p(a1, b0), p(a1, b1), p(a0, b1)], 'pl-floor');
  if (w.b0) { const [s, e] = seg(w.b0, a0, a1); out += poly([p(s, b0), p(e, b0), p(e, b0, h), p(s, b0, h)], 'pl-wall-back-a'); }
  if (w.a1) { const [s, e] = seg(w.a1, b0, b1); out += poly([p(a1, s), p(a1, e), p(a1, e, h), p(a1, s, h)], 'pl-wall-back-b'); }
  if (w.a0) { const [s, e] = seg(w.a0, b0, b1); out += poly([p(a0, s), p(a0, e), p(a0, e, h), p(a0, s, h)], 'pl-wall-front-b'); }
  if (w.b1) { const [s, e] = seg(w.b1, a0, a1); out += poly([p(s, b1), p(e, b1), p(e, b1, h), p(s, b1, h)], 'pl-wall-front-a'); }
  return out;
}

/* Rampe vor dem Eingang: steigt von vorne (b1, Bodenhöhe) frontal zur Glastür (b0, Höhe h) an */
function ramp({ a0, a1, b0, b1, h }) {
  const z = (b) => h * (b1 - b) / (b1 - b0);
  let out = poly([p(a0, b0), p(a0, b0, h), p(a0, b1)], 'pl-wall-front-b')          // seitlicher Keil
    + poly([p(a0, b0, h), p(a1, b0, h), p(a1, b1), p(a0, b1)], 'pl-slab');         // Lauffläche
  for (let i = 1; i < 4; i++) {                                                     // Rillen quer zur Laufrichtung
    const bb = b0 + (b1 - b0) * i / 4;
    out += line(p(a0 + 0.15, bb, z(bb)), p(a1 - 0.15, bb, z(bb)), 'pl-ramp-line');
  }
  return out;
}

const PICTO = 46;
const picto = (key, a, b, z = H * 0.5) => {
  const [x, y] = p(a, b, z);
  return `<use href="#picto-${key}" x="${(x - PICTO / 2).toFixed(1)}" y="${(y - PICTO / 2).toFixed(1)}" width="${PICTO}" height="${PICTO}"/>`;
};

const LABELS = {
  r1: 'R1: Renaissance bis Rokoko', r2: 'R2: Klassizismus bis Realismus',
  r3: 'R3: Das 20. Jahrhundert', r4: 'R4: Künstlerinnen der Gegenwart',
  eingang: 'Eingang mit Ticketverkauf', cafe: 'Museumscafé und Toiletten',
};

/* Maße in Planeinheiten. Grundriss von oben: hinten der lange Flügel (R3/R4 ohne Trennwand),
   davor ein U-förmiger, offener Bereich: links Café, Mitte Eingangshalle, rechts R2 und R1.
   a = 4.4 / 5.9  Kanten von Durchgang und Eingangsnische
   a = 7.7  Beginn R1; b = 7 vordere Kante R2 / Café-Rücksprung; b = 7.8 Glasfront */
const A_CAFE = 4.4, A_R2 = 5.9, A_R1 = 7.7, B_GLAS = 7.8;

/* Klickbare Service-Bereiche (zusätzlich zu R1–R4): führen auf die jeweilige Unterseite.
   Die Bereiche bestehen wegen der Zeichenreihenfolge aus mehreren Teilen; nur der erste
   Teil ist per Tastatur erreichbar, die übrigen sind für Screenreader ausgeblendet. */
const LINKS = {
  cafe: { href: 'museumscafe.html', label: 'Museumscafé', aria: 'Museumscafé und Toiletten – zur Seite Museumscafé', at: [2.2, 5.75] },
  eingang: { href: 'tickets.html', label: 'Ticketverkauf', aria: 'Eingang mit Ticketverkauf – zur Seite Tickets', at: [(A_CAFE + A_R2) / 2, 5.9] },
};
const GROUPS = ['r1', 'r2', 'r3', 'r4', 'cafe', 'eingang'];

/* Zeichenreihenfolge von hinten nach vorne (Maleralgorithmus) */
const PARTS = [
  // R3 und R4 bilden einen durchgehenden Saal – die Grenze ist nur auf dem Boden markiert.
  // Die Vorderwand ist zwischen A_CAFE und A_R2 offen: dort schließt der Durchgang an.
  { id: 'r4', room: true, at: [8, 1.7],
    body: box({ a0: A_R2, a1: 10, b0: 0, b1: 3.4, walls: { a0: false } }) },
  { id: 'r3', room: true, at: [3, 1.7],
    body: box({ a0: 0, a1: A_R2, b0: 0, b1: 3.4, walls: { a1: false, b1: [0, A_CAFE] } }) },
  // Durchgang von der Eingangshalle zum langen Flügel (Wände links und rechts)
  { id: 'durchgang', group: 'eingang', parts: [
    box({ a0: A_CAFE, a1: A_R2, b0: 3.4, b1: 4.5, walls: { b0: false, b1: false } }),
  ] },
  { id: 'r2', room: true, at: [7.8, 5.75],                                         // zur Halle (a0) und zu R1 hin offen
    body: box({ a0: A_R2, a1: 10, b0: 4.5, b1: 7, walls: { a0: false, b1: [A_R2, A_R1] } }) },
  { id: 'r1', room: true, at: [8.85, 8.6],
    body: box({ a0: A_R1, a1: 10, b0: 7, b1: 10.2, walls: { b0: false } }) },
  { id: 'eingang', parts: [
    // Eingangshalle mit Ticketverkauf, offen zu Café, R2 und Durchgang; vorne die Eingangsnische
    // mit Seitenwänden und frontaler Glastür
    box({ a0: A_CAFE, a1: A_R2, b0: 4.5, b1: B_GLAS, walls: { b0: false, a1: [7, B_GLAS], a0: [7, B_GLAS], b1: false } })
      + poly([p(A_CAFE, B_GLAS), p(A_R2, B_GLAS), p(A_R2, B_GLAS, H), p(A_CAFE, B_GLAS, H)], 'pl-door')
      + line(p((A_CAFE + A_R2) / 2, B_GLAS), p((A_CAFE + A_R2) / 2, B_GLAS, H), 'pl-door-line'),  // Mittelpfosten der Glastür
  ], pictos: [picto('tickets', (A_CAFE + A_R2) / 2, 5.9)] },
  { id: 'cafe', parts: [
    // hinterer, breiter Teil – zur Eingangshalle und zu R2 hin offen
    box({ a0: 0, a1: A_CAFE, b0: 4.5, b1: 7, walls: { a1: false, b1: [2.2, A_CAFE] } }),
  ], pictos: [picto('cafe', 2.2, 5.75)] },
  { id: 'rampe', group: 'eingang', parts: [ramp({ a0: A_CAFE, a1: A_R2, b0: B_GLAS, b1: 10, h: 0.35 })] },
  { id: 'cafe-vorn', group: 'cafe', parts: [
    box({ a0: 0, a1: 2.2, b0: 7, b1: 10.4, walls: { b0: false } }),             // vorderer, schmaler Teil
  ], pictos: [picto('toiletten', 1.1, 8.7)] },
];

function pictoSymbols() {
  // Piktogramme aus den fertigen Einzeldateien übernehmen (img/icons/*.svg)
  return ['r1', 'r2', 'r3', 'r4', 'cafe', 'toiletten', 'tickets'].map((k) => {
    const svg = fs.readFileSync(path.join(ROOT, 'img', 'icons', `${k}.svg`), 'utf8');
    const inner = svg.replace(/^[\s\S]*?<\/title>/, '').replace(/<\/svg>\s*$/, '');
    return `<symbol id="picto-${k}" viewBox="0 0 48 48">${inner}</symbol>`;
  }).join('');
}

const CSS = `
.pl-floor{fill:${TINT};stroke:${INK};stroke-width:1}
.pl-wall-back-a{fill:#C9C4D6;stroke:${INK};stroke-width:1}
.pl-wall-back-b{fill:#B3ADC4;stroke:${INK};stroke-width:1}
.pl-wall-front-a,.pl-wall-front-b{fill:${WHITE};stroke:${INK};stroke-width:1.5;stroke-linejoin:round}
.pl-wall-front-b{fill:#F4F2EE}
.pl-slab{fill:${WHITE};stroke:${INK};stroke-width:1.5;stroke-linejoin:round}
.pl-door{fill:#DDE6EE;fill-opacity:.85;stroke:${INK};stroke-width:1.5}
.pl-door-line{stroke:${INK};stroke-width:1.5}
.pl-ramp-line{stroke:${INK};stroke-width:1;stroke-opacity:.45}
`;
const CSS_INTERACTIVE = `
.pl-room{cursor:pointer;outline:none}
.pl-room polygon{transition:fill .25s ease}
.pl-room:hover .pl-floor,.pl-room:focus-visible .pl-floor,.pl-room.is-active .pl-floor{fill:${VIOLET}}
.pl-room:hover .pl-wall-back-a,.pl-room:focus-visible .pl-wall-back-a,.pl-room.is-active .pl-wall-back-a{fill:#7D6FB5}
.pl-room:hover .pl-wall-back-b,.pl-room:focus-visible .pl-wall-back-b,.pl-room.is-active .pl-wall-back-b{fill:#6A5BA6}
.pl-room:focus-visible .pl-wall-front-a,.pl-room:focus-visible .pl-wall-front-b{stroke:${VIOLET};stroke-width:3}
.pl-label{opacity:0;transition:opacity .2s ease;pointer-events:none}
.pl-label rect{fill:${INK}}
.pl-label text{fill:${WHITE};font:600 15px "Source Sans 3","Segoe UI",Arial,sans-serif}
@media (prefers-reduced-motion:reduce){.pl-room polygon,.pl-label{transition:none}}
` + GROUPS.map((g) => {
  // Bereiche aus mehreren Teilen werden gemeinsam hervorgehoben (CSS :has)
  const on = `.plan-svg:has(.pl-grp-${g}:hover,.pl-grp-${g}:focus-visible,.pl-grp-${g}.is-active)`;
  return `${on} .pl-grp-${g} .pl-floor{fill:${VIOLET}}${on} .pl-grp-${g} .pl-wall-back-a{fill:#7D6FB5}`
    + `${on} .pl-grp-${g} .pl-wall-back-b{fill:#6A5BA6}${on} .pl-grp-${g} .pl-slab{fill:#C9C4D6}${on} #label-${g}{opacity:1}`;
}).join('');

function label(id, [a, b], text = LABELS[id]) {
  const [x, y] = p(a, b, H * 0.5);
  const w = text.length * 7.6 + 24, h = 30, top = y - PICTO / 2 - 10 - h;
  return `<g class="pl-label" id="label-${id}"><rect x="${(x - w / 2).toFixed(1)}" y="${top.toFixed(1)}" width="${w.toFixed(1)}" height="${h}" rx="2"/>`
    + `<text x="${x.toFixed(1)}" y="${(top + 20).toFixed(1)}" text-anchor="middle">${text}</text></g>`;
}

function planSvg(interactive) {
  const out = [];
  const seen = new Set();
  for (const part of PARTS) {
    if (part.room) {
      const body = part.body + picto(part.id, ...part.at);
      out.push(interactive
        ? `<a href="#${part.id}" class="pl-room pl-grp-${part.id}" id="plan-${part.id}" aria-label="${LABELS[part.id]}"><title>${LABELS[part.id]}</title>${body}</a>`
        : `<g id="plan-${part.id}"><title>${LABELS[part.id]}</title>${body}</g>`);
    } else {
      const g = part.group || part.id;
      const title = LABELS[g];
      const content = `${title ? `<title>${title}</title>` : ''}${part.parts.join('')}${(part.pictos || []).join('')}`;
      if (interactive && LINKS[g]) {
        const first = !seen.has(g); seen.add(g);
        out.push(`<a href="${LINKS[g].href}" class="pl-room pl-grp-${g}"`
          + (first ? ` id="plan-${g}" aria-label="${LINKS[g].aria}"` : ' tabindex="-1" aria-hidden="true"')
          + `>${content}</a>`);
        continue;
      }
      out.push(`<g${part.group ? '' : ` id="plan-${part.id}"`}>${title ? `<title>${title}</title>` : ''}${part.parts.join('')}${(part.pictos || []).join('')}</g>`);
    }
  }
  if (interactive) {
    out.push('<g class="pl-labels" aria-hidden="true">'
      + PARTS.filter((x) => x.room).map((x) => label(x.id, x.at)).join('')
      + Object.entries(LINKS).map(([g, l]) => label(g, l.at, l.label)).join('') + '</g>');
  }
  // Ausschnitt: alle Eckpunkte + Platz für Piktogramme und Namensschilder
  const xs = [], ys = [];
  for (const a of [0, 10]) for (const b of [0, 10.4]) for (const z of [0, H]) { const [x, y] = p(a, b, z); xs.push(x); ys.push(y); }
  const padX = 24, padTop = 56, padBottom = 24;  // oben Platz für die Namensschilder
  const minX = Math.min(...xs) - padX, minY = Math.min(...ys) - padTop;
  const w = Math.max(...xs) - Math.min(...xs) + 2 * padX, h = Math.max(...ys) - Math.min(...ys) + padTop + padBottom;
  const vb = `${minX.toFixed(0)} ${minY.toFixed(0)} ${w.toFixed(0)} ${h.toFixed(0)}`;
  const attrs = interactive ? 'class="plan-svg" role="group" aria-labelledby="plan-title"' : 'role="img" aria-labelledby="plan-title"';
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${vb}" ${attrs}>`
    + '<title id="plan-title">Isometrischer Gebäudeplan des Isabella-Edel-Museums</title>'
    + `<defs><style>${CSS}${interactive ? CSS_INTERACTIVE : ''}</style>${pictoSymbols()}</defs>`
    + out.join('') + '</svg>\n';
  return { svg, width: Math.round(w), height: Math.round(h) };
}

const ALT = 'Isometrischer Gebäudeplan: Im langen Flügel links liegen R3 (vorne) und R4 (hinten). '
  + 'Rechts daneben bilden R2 und R1 einen L-förmigen Gebäudeteil. Vorne links liegt das Museumscafé mit Toiletten, '
  + 'zwischen Café und R1 der Eingang mit Glasfront und Ticketverkauf.';

const still = planSvg(false);
const live = planSvg(true);
fs.writeFileSync(path.join(ROOT, 'img', 'gebaeudeplan.svg'), still.svg);
fs.mkdirSync(path.join(ROOT, 'partials'), { recursive: true });
fs.writeFileSync(path.join(ROOT, 'partials', 'gebaeudeplan-inline.svg'), live.svg);

// raeume.html direkt aktualisieren (statisches Bild + klickbare Variante)
const file = path.join(ROOT, 'raeume.html');
let html = fs.readFileSync(file, 'utf8');
html = html.replace(/<img class="plan__static"[^>]*>/,
  `<img class="plan__static" src="img/gebaeudeplan.svg" width="${still.width}" height="${still.height}" alt="${ALT}">`);
html = html.replace(/(<div class="plan__interactive">)[\s\S]*?(<\/div>\n    <\/figure>)/,
  (_, open, close) => `${open}${live.svg}${close}`);
fs.writeFileSync(file, html);
console.log(`Gebäudeplan geschrieben (${still.width} × ${still.height}).`);
