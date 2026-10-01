/* ==========================================================================
   Isabella-Edel-Museum – Progressive Enhancement
   Läuft nur, wenn der Inline-Test im <head> die Klasse "js" gesetzt hat. Ältere
   Browser bekommen die Basisversion: Menü sichtbar, Slider wischbar, Formular komplett.
   Bewusst kein ES-Modul, damit die Seite auch per Doppelklick (file://) funktioniert.
   Eigener Code, keine fremden Skripte oder Frameworks.
   ========================================================================== */

var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

/* ---------- Darstellung: Dunkler Modus & Barrierefreier Modus ----------
   Wahl wird in localStorage gespeichert; der Inline-Script im <head> wendet sie
   vor dem ersten Zeichnen an. Ohne Wahl gilt die Systemeinstellung. */
const root = document.documentElement;
const systemDark = window.matchMedia('(prefers-color-scheme: dark)');
const motionOff = () => reducedMotion.matches || root.dataset.a11y === 'on';

function store(key, value) {
  try { if (value === null) localStorage.removeItem(key); else localStorage.setItem(key, value); } catch (e) { /* privat/gesperrt */ }
}

function initPrefs() {
  const item = document.querySelector('.nav-prefs');
  if (!item) return;
  item.hidden = false;
  const themeBtn = item.querySelector('[data-pref="theme"]');
  const a11yBtn = item.querySelector('[data-pref="a11y"]');

  const isDark = () => root.dataset.theme ? root.dataset.theme === 'dark' : systemDark.matches;
  const sync = () => {
    themeBtn.setAttribute('aria-pressed', String(isDark()));
    a11yBtn.setAttribute('aria-pressed', String(root.dataset.a11y === 'on'));
  };

  themeBtn.addEventListener('click', () => {
    const next = isDark() ? 'light' : 'dark';
    // entspricht die Wahl dem System, keine feste Einstellung speichern
    if ((next === 'dark') === systemDark.matches) { delete root.dataset.theme; store('iem-theme', null); }
    else { root.dataset.theme = next; store('iem-theme', next); }
    sync();
  });

  a11yBtn.addEventListener('click', () => {
    if (root.dataset.a11y === 'on') { delete root.dataset.a11y; store('iem-a11y', null); }
    else { root.dataset.a11y = 'on'; store('iem-a11y', 'on'); }
    sync();
    window.dispatchEvent(new Event('iem:motion'));
  });

  systemDark.addEventListener('change', sync);
  sync();
}

/* ---------- Navigation: Burger-Menü < 1400 px ---------- */
function initNavigation() {
  const toggle = document.querySelector('.nav-toggle');
  const nav = document.getElementById('hauptmenue');
  if (!toggle || !nav) return;

  toggle.hidden = false;

  const setOpen = (open) => {
    toggle.setAttribute('aria-expanded', String(open));
    nav.classList.toggle('is-open', open);
  };

  toggle.addEventListener('click', () => setOpen(toggle.getAttribute('aria-expanded') !== 'true'));

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && nav.classList.contains('is-open')) {
      setOpen(false);
      toggle.focus();
    }
  });

  // Klick außerhalb schließt das Menü
  document.addEventListener('click', (e) => {
    if (nav.classList.contains('is-open') && !nav.contains(e.target) && !toggle.contains(e.target)) setOpen(false);
  });
}

/* ---------- Endlos-Slider ---------- */
function initSlider(sliderRoot) {
  const track = sliderRoot.querySelector('.slider__track');
  const slides = [...track.children];
  const count = slides.length;
  if (count < 2) return;

  // Klone am Anfang und Ende für die nahtlose Endlosschleife
  const firstClone = slides[0].cloneNode(true);
  const lastClone = slides[count - 1].cloneNode(true);
  for (const clone of [firstClone, lastClone]) {
    clone.setAttribute('aria-hidden', 'true');
    clone.removeAttribute('id');
    clone.inert = true;
    clone.querySelectorAll('img').forEach((img) => { img.loading = 'eager'; img.removeAttribute('fetchpriority'); });
  }
  track.append(firstClone);
  track.prepend(lastClone);

  sliderRoot.classList.add('is-enhanced');
  track.scrollLeft = 0;

  let index = 1;               // Position im Track inkl. Klone (1 = erstes echtes Bild)
  let timer = null;
  let paused = false;
  let userPaused = false;

  // Steuerelemente erzeugen
  const controls = document.createElement('div');
  controls.className = 'slider__controls';
  controls.innerHTML = `
    <ol class="slider__dots">${slides.map((s, i) =>
      `<li><button class="slider__dot" type="button" aria-label="Bild ${i + 1}: ${s.querySelector('.slider__title').textContent}"></button></li>`).join('')}
    </ol>
    <button class="slider__btn" type="button" data-action="pause" aria-label="Automatischen Wechsel anhalten">❚❚</button>
    <button class="slider__btn" type="button" data-action="prev" aria-label="Vorheriges Bild">←</button>
    <button class="slider__btn" type="button" data-action="next" aria-label="Nächstes Bild">→</button>`;
  sliderRoot.append(controls);
  const dots = [...controls.querySelectorAll('.slider__dot')];
  const pauseBtn = controls.querySelector('[data-action="pause"]');

  const realIndex = () => (index - 1 + count) % count;

  function render(animate = true) {
    track.classList.toggle('no-transition', !animate || motionOff());
    track.style.transform = `translateX(${-index * 100}%)`;
    const current = realIndex();
    dots.forEach((dot, i) => dot.setAttribute('aria-current', String(i === current)));
    slides.forEach((slide, i) => { slide.inert = i !== current; });
  }

  function goTo(newIndex) {
    index = newIndex;
    render(true);
    if (motionOff()) jumpIfClone();
  }

  // Nach der Animation auf einem Klon: unsichtbar zum echten Bild springen
  function jumpIfClone() {
    if (index === 0) index = count;
    else if (index === count + 1) index = 1;
    else return;
    render(false);
    void track.offsetWidth; // Reflow, damit der Sprung ohne Animation passiert
    track.classList.remove('no-transition');
  }
  track.addEventListener('transitionend', (e) => { if (e.target === track) jumpIfClone(); });

  const next = () => goTo(index + 1);
  const prev = () => goTo(index - 1);

  function start() {
    stop();
    if (!paused && !userPaused && !motionOff()) timer = window.setInterval(next, 6000);
  }
  window.addEventListener('iem:motion', () => { render(false); start(); });
  function stop() { window.clearInterval(timer); timer = null; }

  function setUserPaused(value) {
    userPaused = value;
    pauseBtn.textContent = value ? '▶' : '❚❚';
    pauseBtn.setAttribute('aria-label', value ? 'Automatischen Wechsel starten' : 'Automatischen Wechsel anhalten');
    start();
  }

  controls.addEventListener('click', (e) => {
    const btn = e.target.closest('button');
    if (!btn) return;
    if (btn.classList.contains('slider__dot')) goTo(dots.indexOf(btn) + 1);
    else if (btn.dataset.action === 'next') next();
    else if (btn.dataset.action === 'prev') prev();
    else if (btn.dataset.action === 'pause') { setUserPaused(!userPaused); return; }
    start();
  });

  // Pausieren bei Maus über dem Slider oder Tastaturfokus darin (WCAG 2.2.2)
  sliderRoot.addEventListener('mouseenter', () => { paused = true; stop(); });
  sliderRoot.addEventListener('mouseleave', () => { paused = false; start(); });
  sliderRoot.addEventListener('focusin', () => { paused = true; stop(); });
  sliderRoot.addEventListener('focusout', (e) => { if (!sliderRoot.contains(e.relatedTarget)) { paused = false; start(); } });

  // Wischgesten
  let startX = null;
  track.addEventListener('pointerdown', (e) => { startX = e.clientX; });
  track.addEventListener('pointerup', (e) => {
    if (startX === null) return;
    const dx = e.clientX - startX;
    startX = null;
    if (Math.abs(dx) > 50) { dx < 0 ? next() : prev(); start(); }
  });
  // Klick nach Wischen nicht als Link-Klick werten
  track.addEventListener('click', (e) => { if (track.dataset.swiped) { e.preventDefault(); delete track.dataset.swiped; } });
  track.addEventListener('pointermove', (e) => { if (startX !== null && Math.abs(e.clientX - startX) > 10) track.dataset.swiped = '1'; });
  track.addEventListener('dragstart', (e) => e.preventDefault());

  render(false);
  start();
}

/* ---------- Gebäudeplan: Legende hebt Raum im Plan hervor ---------- */
function initPlan() {
  const legend = document.querySelector('.plan__legend');
  if (!legend) return;
  legend.querySelectorAll('a[href^="#r"]').forEach((link) => {
    const room = document.getElementById(`plan-${link.hash.slice(1)}`);
    if (!room) return;
    const on = () => room.classList.add('is-active');
    const off = () => room.classList.remove('is-active');
    link.addEventListener('mouseenter', on);
    link.addEventListener('mouseleave', off);
    link.addEventListener('focus', on);
    link.addEventListener('blur', off);
  });

  // „Zurück zum Gebäudeplan“: Raum, aus dem man kommt, im Plan und in der Legende markieren
  let timer = null;
  document.querySelectorAll('.room__back[data-room]').forEach((back) => {
    back.addEventListener('click', () => {
      const id = back.dataset.room;
      const room = document.getElementById(`plan-${id}`);
      const item = legend.querySelector(`a[href="#${id}"]`);
      document.querySelectorAll('.pl-room.is-active, .plan__legend .is-recent')
        .forEach((el) => el.classList.remove('is-active', 'is-recent'));
      if (room) room.classList.add('is-active');
      if (item) item.classList.add('is-recent');
      window.clearTimeout(timer);
      timer = window.setTimeout(() => {
        if (room) room.classList.remove('is-active');
        if (item) item.classList.remove('is-recent');
      }, 3000);
    });
  });
}

/* ---------- Ticketformular: Summe & schrittweise Anzeige ---------- */
function initTicketForm() {
  const form = document.querySelector('.ticket-form');
  if (!form) return;

  const rows = [...form.querySelectorAll('.ticket-row')];
  const step1 = form.querySelector('#ticketart');
  const step2 = form.querySelector('#persoenliche-angaben');
  const confirm = form.querySelector('[data-confirm]');
  const steps = [...document.querySelectorAll('.stepper li')];

  // Gesamtsumme
  const total = document.createElement('p');
  total.className = 'ticket-total';
  total.innerHTML = 'Summe: <output aria-live="polite">0 Euro</output>';
  confirm.before(total);
  const output = total.querySelector('output');

  // Hinweis, wenn kein Ticket gewählt ist
  const error = document.createElement('p');
  error.className = 'form-error';
  error.setAttribute('role', 'alert');
  error.hidden = true;
  error.textContent = 'Bitte wählen Sie mindestens ein Ticket aus.';
  total.after(error);

  const update = () => {
    const sum = rows.reduce((acc, row) => {
      const price = Number(row.querySelector('[data-price]').dataset.price);
      const qty = Math.max(0, parseInt(row.querySelector('input').value, 10) || 0);
      return acc + price * qty;
    }, 0);
    output.textContent = `${sum} Euro`;
    if (sum > 0) error.hidden = true;
    return sum;
  };
  form.addEventListener('input', update);

  const setStep = (n) => steps.forEach((li, i) => {
    if (i + 1 === n) li.setAttribute('aria-current', 'step');
    else li.removeAttribute('aria-current');
    li.classList.toggle('is-done', i + 1 < n);
  });

  // true, wenn mindestens ein Ticket gewählt ist – sonst Fehlermeldung
  const checkTickets = () => {
    if (update() > 0) return true;
    error.hidden = false;
    step1.scrollIntoView({ behavior: reducedMotion.matches ? 'auto' : 'smooth', block: 'start' });
    rows[0].querySelector('input').focus({ preventScroll: true });
    return false;
  };

  // Schritt 2 erst nach „Auswahl bestätigen“ zeigen
  step2.hidden = true;
  confirm.addEventListener('click', (e) => {
    e.preventDefault();
    if (!checkTickets()) return;
    step2.hidden = false;
    setStep(2);
    step2.scrollIntoView({ behavior: reducedMotion.matches ? 'auto' : 'smooth', block: 'start' });
    step2.querySelector('input').focus({ preventScroll: true });
  });

  // Absenden: Pflichtfelder prüft der Browser, die Ticketanzahl prüfen wir
  form.addEventListener('submit', (e) => {
    if (!checkTickets()) e.preventDefault();
  });
}

/* ---------- Bestätigungsseite: Ticket aus den Formulardaten, Druck & Download ---------- */
function initConfirmation() {
  const ticket = document.querySelector('.ticket');
  if (!ticket) return;
  const params = new URLSearchParams(window.location.search);
  if (![...params.keys()].length) return; // direkt aufgerufen: allgemeine Bestätigung

  const field = (name) => ticket.querySelector(`[data-field="${name}"]`);
  const qty = (key) => Math.max(0, parseInt(params.get(key), 10) || 0);
  const data = { rows: [], sum: 0 };

  ticket.querySelectorAll('[data-price]').forEach((dd) => {
    const n = qty(dd.dataset.field);
    const price = Number(dd.dataset.price);
    const label = dd.previousElementSibling.textContent;
    data.sum += n * price;
    dd.textContent = `${n} × ${price} Euro`;
    if (n === 0) dd.parentElement.hidden = true;
    else data.rows.push([label, dd.textContent]);
  });
  field('summe').textContent = `${data.sum} Euro`;

  const vorname = (params.get('vorname') || '').trim();
  data.name = `${vorname} ${(params.get('name') || '').trim()}`.trim();
  field('name').textContent = data.name;

  // Reservierungsnummer: aus den Daten abgeleitet (Demo, kein Server)
  const now = new Date();
  data.date = now.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' });
  let hash = 5381;
  for (const ch of `${params.toString()}|${now.toISOString().slice(0, 16)}`) hash = ((hash * 33) ^ ch.charCodeAt(0)) >>> 0;
  data.number = `IEM-${hash.toString(36).toUpperCase().padStart(6, '0').slice(-6)}`;
  field('nummer').textContent = data.number;
  field('datum').textContent = data.date;

  // Persönliche Anrede (textContent: Eingaben werden nie als HTML interpretiert)
  if (vorname) document.getElementById('bestaetigung-titel').textContent = `Vielen Dank, ${vorname}!`;

  ticket.hidden = false;
  document.body.classList.add('has-ticket');
  const actions = document.querySelector('.confirmation__ticket-actions');
  actions.hidden = false;
  actions.querySelector('[data-ticket="print"]').addEventListener('click', () => window.print());
  actions.querySelector('[data-ticket="download"]').addEventListener('click', () => downloadTicket(ticket, data));

  // Formulardaten nicht in Adresszeile und Verlauf stehen lassen
  window.history.replaceState(null, '', window.location.pathname);
}

/* Ticket als PDF herunterladen (eigener Code, keine Bibliothek):
   1. Ticket auf ein Canvas zeichnen. Das Logo wird aus dem Inline-SVG als Pfade
      nachgezeichnet – so bleibt der Canvas auch bei file:// „sauber“ und darf exportiert werden.
   2. Canvas als JPEG exportieren und in eine minimale PDF-Datei (A4) einbetten. */
async function downloadTicket(ticket, data) {
  const W = 1000, H = 440, M = 2, SPLIT = 680, scale = 3;
  const canvas = document.createElement('canvas');
  canvas.width = (W + 2 * M) * scale;
  canvas.height = (H + 2 * M) * scale;
  const ctx = canvas.getContext('2d');
  ctx.scale(scale, scale);

  const serif = '"Cormorant Garamond", Garamond, serif';
  const sans = '"Source Sans 3", "Segoe UI", Arial, sans-serif';
  await Promise.all([`600 40px ${serif}`, `400 18px ${sans}`, `600 18px ${sans}`, `700 26px ${sans}`].map((f) => document.fonts.load(f)));

  const C = { paper: '#F8F6F2', white: '#FFFFFF', ink: '#2B2B2A', soft: '#5E5C58', line: '#D9D5CE', violet: '#443189', tint: '#ECE9F4' };
  const text = (str, x, y, font, color = C.ink, align = 'left') => {
    ctx.font = font; ctx.fillStyle = color; ctx.textAlign = align; ctx.fillText(str, x, y);
  };
  const wrap = (str, x, y, maxW, lh, font, color) => {
    ctx.font = font;
    let line = '';
    for (const word of str.split(' ')) {
      const test = line ? `${line} ${word}` : word;
      if (ctx.measureText(test).width > maxW && line) { text(line, x, y, font, color); line = word; y += lh; } else line = test;
    }
    text(line, x, y, font, color);
    return y + lh;
  };

  // Hintergrund + Ticketfläche
  ctx.fillStyle = C.white; ctx.fillRect(0, 0, W + 2 * M, H + 2 * M);
  ctx.translate(M, M);
  ctx.beginPath(); ctx.roundRect(0, 0, W, H, 10); ctx.fillStyle = C.white; ctx.fill();
  ctx.save(); ctx.clip();
  ctx.fillStyle = C.tint; ctx.fillRect(SPLIT, 0, W - SPLIT, H);
  ctx.restore();
  ctx.strokeStyle = C.line; ctx.lineWidth = 1.5; ctx.stroke();

  // Perforation + Einkerbungen
  ctx.setLineDash([8, 7]); ctx.beginPath(); ctx.moveTo(SPLIT, 16); ctx.lineTo(SPLIT, H - 16); ctx.stroke(); ctx.setLineDash([]);
  for (const y of [0, H]) {
    ctx.beginPath(); ctx.arc(SPLIT, y, 14, 0, Math.PI * 2); ctx.fillStyle = C.white; ctx.fill(); ctx.stroke();
  }

  // Logo aus dem Inline-SVG
  const svg = ticket.querySelector('svg.ticket__logo');
  const vbH = Number(svg.getAttribute('viewBox').split(/\s+/)[3]);
  const logoH = 72, s = logoH / vbH;
  ctx.save(); ctx.translate(48, 40); ctx.scale(s, s);
  svg.querySelectorAll('path').forEach((p) => {
    if (p.closest('clipPath')) return;
    const path = new Path2D(p.getAttribute('d'));
    ctx.save();
    const m = (p.getAttribute('transform') || '').match(/matrix\(([^)]+)\)/);
    if (m) ctx.transform(...m[1].split(/[\s,]+/).map(Number));
    const fill = p.getAttribute('fill');
    if (fill && fill !== 'none') { ctx.fillStyle = fill; ctx.fill(path); }
    const stroke = p.getAttribute('stroke');
    if (stroke && stroke !== 'none') {
      ctx.strokeStyle = stroke;
      ctx.lineWidth = Number(p.getAttribute('stroke-width')) || 1;
      ctx.stroke(path);
    }
    ctx.restore();
  });
  ctx.restore();

  // Hauptteil
  let y = 160;
  text('RESERVIERUNGSBESTÄTIGUNG', 48, y, `600 14px ${sans}`, C.soft);
  y += 42;
  text(data.name || 'Ihre Reservierung', 48, y, `600 40px ${serif}`);
  y += 30;
  const line = (yy) => { ctx.strokeStyle = C.line; ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(48, yy); ctx.lineTo(SPLIT - 40, yy); ctx.stroke(); };
  line(y);
  for (const [label, value] of data.rows) {
    y += 34; text(label, 48, y - 8, `600 18px ${sans}`); text(value, SPLIT - 40, y - 8, `400 18px ${sans}`, C.ink, 'right'); line(y + 4); y += 4;
  }
  y += 42; text('Summe', 48, y - 10, `600 18px ${sans}`); text(`${data.sum} Euro`, SPLIT - 40, y - 8, `700 26px ${sans}`, C.ink, 'right'); // Canvas kennt keine Versalziffern-Option für Cormorant line(y + 4);
  text(`Reservierung ${data.number} · ${data.date}`, 48, H - 36, `400 15px ${sans}`, C.soft);

  // Abrissteil
  const sx = SPLIT + 36, sw = W - SPLIT - 72;
  // Piktogramm „Ticketverkauf“ (gleiche Pfade wie img/icons/tickets.svg, 48er-Raster)
  ctx.save(); ctx.translate(sx - 4, 44); ctx.scale(52 / 48, 52 / 48);
  ctx.beginPath(); ctx.roundRect(5, 5, 38, 38, 2.5); ctx.fillStyle = C.white; ctx.fill();
  ctx.strokeStyle = C.violet; ctx.lineWidth = 2; ctx.stroke();
  ctx.fillStyle = C.violet; ctx.fill(new Path2D('M4 7a3 3 0 0 1 3-3h4.5v40H7a3 3 0 0 1-3-3z'));
  ctx.lineWidth = 2.5; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  ctx.stroke(new Path2D('M14 17h26v5a3 3 0 0 0 0 6v5H14v-5a3 3 0 0 0 0-6z'));
  ctx.stroke(new Path2D('M31 18.5v4m0 5v4'));
  ctx.restore();
  let sy = 140;
  sy = wrap('Die Karten können an der Ticketkasse bei Abholung bezahlt werden.', sx, sy, sw, 26, `400 18px ${sans}`, C.ink);
  sy += 16;
  text('Öffnungszeiten:', sx, sy, `600 18px ${sans}`); sy += 26;
  text('Dienstag–Sonntag: 11–17 Uhr', sx, sy, `400 18px ${sans}`); sy += 44;
  text('Brixener Straße 5', sx, sy, `400 16px ${sans}`, C.soft); sy += 24;
  text('28215 Bremen', sx, sy, `400 16px ${sans}`, C.soft);

  const jpeg = await new Promise((resolve) => canvas.toBlob(resolve, 'image/jpeg', 0.92));
  const pdf = buildPdf(new Uint8Array(await jpeg.arrayBuffer()), canvas.width, canvas.height,
    `Ticket Isabella-Edel-Museum ${data.number}`);

  const url = URL.createObjectURL(new Blob([pdf], { type: 'application/pdf' }));
  const a = document.createElement('a');
  a.href = url;
  a.download = `Ticket-Isabella-Edel-Museum-${data.number}.pdf`;
  document.body.append(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

/* Minimale PDF-Datei (PDF 1.4) mit einer A4-Seite und einem JPEG-Bild oben auf der Seite.
   Aufbau: Katalog → Seitenbaum → Seite → Bild (DCTDecode = JPEG) + Inhaltsstrom. */
function buildPdf(jpegBytes, imgW, imgH, title) {
  const enc = new TextEncoder();
  const pageW = 595.28, pageH = 841.89, margin = 42.5;          // A4 in Punkt, 15 mm Rand
  const drawW = pageW - 2 * margin;
  const drawH = drawW * (imgH / imgW);
  const f = (n) => n.toFixed(2);
  const content = `q ${f(drawW)} 0 0 ${f(drawH)} ${f(margin)} ${f(pageH - margin - drawH)} cm /Im1 Do Q`;
  const safeTitle = title.replace(/[()\\]/g, '');

  const objects = [
    '<< /Type /Catalog /Pages 2 0 R >>',
    '<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
    `<< /Type /Page /Parent 2 0 R /MediaBox [0 0 ${pageW} ${pageH}] /Resources << /XObject << /Im1 4 0 R >> >> /Contents 5 0 R >>`,
    [`<< /Type /XObject /Subtype /Image /Width ${imgW} /Height ${imgH} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length ${jpegBytes.length} >>\nstream\n`, jpegBytes, '\nendstream'],
    `<< /Length ${content.length} >>\nstream\n${content}\nendstream`,
    `<< /Title (${safeTitle}) /Producer (Isabella-Edel-Museum Website) >>`,
  ];

  const chunks = [];
  let length = 0;
  const push = (part) => {
    const bytes = typeof part === 'string' ? enc.encode(part) : part;
    chunks.push(bytes);
    length += bytes.length;
  };
  const offsets = [];
  push('%PDF-1.4\n%\u00E2\u00E3\u00CF\u00D3\n');
  objects.forEach((obj, i) => {
    offsets.push(length);
    push(`${i + 1} 0 obj\n`);
    (Array.isArray(obj) ? obj : [obj]).forEach(push);
    push('\nendobj\n');
  });
  const xref = length;
  push(`xref\n0 ${objects.length + 1}\n0000000000 65535 f \n`);
  offsets.forEach((o) => push(`${String(o).padStart(10, '0')} 00000 n \n`));
  push(`trailer\n<< /Size ${objects.length + 1} /Root 1 0 R /Info ${objects.length} 0 R >>\nstartxref\n${xref}\n%%EOF\n`);

  const out = new Uint8Array(length);
  let pos = 0;
  chunks.forEach((c) => { out.set(c, pos); pos += c.length; });
  return out;
}

/* ---------- Lightbox für Galeriebilder ----------
   Ohne JS öffnet der Link einfach die große Bilddatei. */
function initLightbox() {
  const links = [...document.querySelectorAll('a.zoom')];
  if (!links.length || typeof HTMLDialogElement !== 'function') return;

  const dialog = document.createElement('dialog');
  dialog.className = 'lightbox';
  dialog.setAttribute('aria-label', 'Bildansicht');
  dialog.innerHTML = `
    <button class="slider__btn lightbox__close" type="button" aria-label="Schließen">✕</button>
    <img class="lightbox__img" alt="">
    <div class="lightbox__bar">
      <button class="slider__btn" type="button" data-step="-1" aria-label="Vorheriges Bild">←</button>
      <span class="lightbox__count" aria-live="polite"></span>
      <button class="slider__btn" type="button" data-step="1" aria-label="Nächstes Bild">→</button>
    </div>`;
  document.body.append(dialog);
  const img = dialog.querySelector('.lightbox__img');
  const count = dialog.querySelector('.lightbox__count');
  let group = [];
  let current = 0;

  function show(i) {
    current = (i + group.length) % group.length;
    const link = group[current];
    img.src = link.href;
    img.alt = link.querySelector('img').alt;
    count.textContent = `${current + 1} / ${group.length}`;
  }

  links.forEach((link) => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      // Blättern innerhalb derselben Galerie (Liste)
      const list = link.closest('ul');
      group = list ? [...list.querySelectorAll('a.zoom')] : [link]; // Einzelbild ohne Liste
      show(group.indexOf(link));
      dialog.querySelector('[data-step]').parentElement.hidden = group.length < 2;
      dialog.showModal();
      dialog.dataset.opener = links.indexOf(link);
    });
  });

  dialog.addEventListener('click', (e) => {
    const step = e.target.closest('[data-step]');
    if (step) show(current + Number(step.dataset.step));
    else if (e.target.closest('.lightbox__close') || e.target === dialog) dialog.close();
  });
  dialog.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight') show(current + 1);
    if (e.key === 'ArrowLeft') show(current - 1);
  });
  // Fokus nach dem Schließen zurück auf das geöffnete Bild
  dialog.addEventListener('close', () => {
    const opener = links[Number(dialog.dataset.opener)];
    if (opener) opener.focus();
  });
}

/* ---------- Nach-oben-Button auf langen Seiten ---------- */
function initToTop() {
  if (document.documentElement.scrollHeight < window.innerHeight * 2.5) return;
  const btn = document.createElement('button');
  btn.className = 'to-top';
  btn.type = 'button';
  btn.setAttribute('aria-label', 'Nach oben');
  btn.textContent = '↑';
  document.body.append(btn);

  // sichtbar ab einer Bildschirmhöhe Scrollweg (auch nach Neuladen mit gemerkter Position)
  const update = () => btn.classList.toggle('is-visible', window.scrollY > window.innerHeight);
  window.addEventListener('scroll', update, { passive: true });
  update();

  btn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: reducedMotion.matches ? 'auto' : 'smooth' });
    document.querySelector('.site-logo').focus({ preventScroll: true });
  });
}

if (document.documentElement.classList.contains('js')) {
  initPrefs();
  initNavigation();
  document.querySelectorAll('.slider').forEach(initSlider);
  initPlan();
  initTicketForm();
  initConfirmation();
  initLightbox();
  initToTop();
}
