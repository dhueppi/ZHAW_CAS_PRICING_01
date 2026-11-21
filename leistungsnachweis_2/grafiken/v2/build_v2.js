// build_v2.js – baut das LN2-Slidedoc v2 vollständig aus params.json (über model.js).
// Aufruf: node build_v2.js [Ausgabepfad]   (Standard: zwei Ordner höher, neben der v1)
const path = require("path");
const M = require("./model.js");
const OUT = process.argv[2] || path.join(__dirname, "..", "..", "LN2_AquaClean_Alba_Hotel_Preiskonzept_2026_v2.pptx");
const v = M.v, J = M.jahre;
// ---------- Formatierung (Schweizer Schreibweise) ----------
const f = (x, d = 0) => { const s = Math.abs(x).toFixed(d).replace(/\B(?=(\d{3})+(?!\d))/g, "'"); return (Math.round(Math.abs(x) * 10 ** d) === 0 ? "" : x < 0 ? "−" : "") + s; };
const k3 = (x) => f(Math.round(x / 1000) * 1000);
const chf = (x) => "CHF " + f(x);
const pct = (x, d = 1) => { let s = (x * 100).toFixed(d); if (s.endsWith(".0")) s = s.slice(0, -2); return s + " %"; };
const tchf = (x) => f(x / 1000);
const mio = (x) => (x / 1e6).toFixed(1) + " Mio.";
const nextRound = (x) => Math.ceil((x + 1) / 100) * 100;
const L = J.length - 1;
const nx = (i) => (i >= 0 ? i : L + 1);                       // Gate nicht erreicht → nach dem Horizont
const iG1 = nx(M.phasen.g1), iFleet = nx(M.phasen.g3), iWert = nx(M.phasen.g4);
const yr = (i) => (i <= L ? String(J[i]) : "nach " + J[L]);
const span = (a, b) => (a > L ? "nach " + J[L] : b <= a ? String(J[a]) : `${J[a]}–${String(J[Math.min(b, L)]).slice(2)}`);
const cp = M.preisCostPlus, p1 = M.p1, pG1 = M.pG1;
const pilotRund = Math.round(M.pilotGeraete / 10) * 10;
const pfad = `CHF ${f(p1)} → ${f(cp)} → ${f(M.fleetPaket)} → ${f(M.carePaket)}`;
const beJ = (s) => (s.breakEvenJahr ? String(s.breakEvenJahr) : "nach " + J[J.length - 1]);
const ga = v("gate_anteile");
const pptxgen = require("pptxgenjs");

const HEX = {
  navy: "13293D", text: "1F2A36", teal: "00797A", gold: "D9A441", lteal: "7FB8B4",
  gray: "5B6B7A", red: "B5473A", tint: "EAF3F2", grid: "E3E8EC", white: "FFFFFF", mute: "AEBBC4",
};
const THEME = {
  name: "AquaClean Pricing",
  headFontFace: "Arial",
  bodyFontFace: "Arial",
  colors: {
    dk1: HEX.text, lt1: HEX.white, dk2: HEX.navy, lt2: HEX.tint,
    accent1: HEX.teal, accent2: HEX.gold, accent3: HEX.lteal, accent4: HEX.gray,
    accent5: HEX.red, accent6: HEX.mute, hlink: HEX.teal, folHlink: HEX.gray,
  },
};

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.author = "Dominic Hüpp, Marilena Marraffino";
pres.title = "Preiskonzept AquaClean Alba Hotel B2B v2";
const C = { text1: HEX.text, text2: HEX.navy, background1: HEX.white, background2: HEX.tint, accent1: HEX.teal, accent2: HEX.gold, accent3: HEX.lteal, accent4: HEX.gray, accent5: HEX.red, accent6: HEX.mute };

// ---------- Layouts ----------
pres.defineSlideMaster({
  title: "DARK",
  background: { color: HEX.navy },
  objects: [
    { placeholder: { options: { name: "kicker", type: "body", x: 0.8, y: 0.7, w: 11, h: 0.4, fontSize: 12, bold: true, color: C.accent3 }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 1.2, w: 11.7, h: 1.5, fontSize: 36, bold: true, color: C.background1, valign: "top", align: "left" }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: HEX.white },
  objects: [
    { placeholder: { options: { name: "kicker", type: "body", x: 0.6, y: 0.32, w: 10.8, h: 0.3, fontSize: 11, bold: true, color: C.accent1, margin: 0 }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.62, w: 12.1, h: 0.85, fontSize: 24, bold: true, color: C.text2, valign: "top", align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "source", type: "body", x: 0.6, y: 6.68, w: 11.4, h: 0.36, fontSize: 10, color: C.accent4, margin: 0, valign: "top" }, text: "" } },
    { text: { text: "AquaClean Alba · Preiskonzept Hotel B2B · v2", options: { x: 0.6, y: 7.1, w: 6, h: 0.25, fontSize: 9, color: HEX.mute, margin: 0 } } },
  ],
  slideNumber: { x: 12.3, y: 7.08, w: 0.45, h: 0.25, fontSize: 10, color: HEX.gray, align: "right" },
});

// ---------- Helpers ----------
let n = 0;
const id = (p) => `${p}_${++n}`;
function txt(s, text, o) {
  s.addText(text, Object.assign({ isTextBox: true, fontSize: 14, color: C.text1, valign: "top", margin: 0.05, objectName: id("txt") }, o));
}
function card(s, x, y, w, h, fill) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: fill || C.background2 }, line: { type: "none" }, objectName: id("card") });
}
function circ(s, label, x, y, d, fill, fs) {
  s.addText(String(label), { isTextBox: true, shape: pres.shapes.OVAL, x, y, w: d, h: d, fill: { color: fill || C.accent1 }, color: C.background1, fontSize: fs || 12, bold: true, align: "center", valign: "middle", margin: 0, objectName: id("circ") });
}
function bullets(s, items, o) {
  const arr = items.map((it, i) => {
    const runs = [];
    if (typeof it === "string") runs.push({ text: it, options: { bullet: { indent: 14 }, breakLine: i < items.length - 1 } });
    else {
      runs.push({ text: it.b + " ", options: { bold: true, bullet: { indent: 14 } } });
      runs.push({ text: it.t, options: { breakLine: i < items.length - 1 } });
    }
    return runs;
  }).flat();
  txt(s, arr, Object.assign({ paraSpaceAfter: 6 }, o));
}
function head(s, text, x, y, w, color) {
  txt(s, text, { x, y, w, h: 0.32, fontSize: 14, bold: true, color: color || C.text2, margin: 0 });
}
function pitch(s) { return; return;
  s.addText("PITCH", { isTextBox: true, shape: pres.shapes.ROUNDED_RECTANGLE, rectRadius: 0.06, x: 11.9, y: 0.3, w: 0.82, h: 0.28, fill: { color: C.accent1 }, color: C.background1, fontSize: 10, bold: true, align: "center", valign: "middle", margin: 0, objectName: id("pitch") });
}
function content(section, kicker, title, source, isPitch) {
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: section });
  s.addText(kicker, { placeholder: "kicker" });
  s.addText(title, { placeholder: "title" });
  if (source) s.addText(source, { placeholder: "source" });
  if (isPitch) pitch(s);
  return s;
}
function chartOpts(extra) {
  return Object.assign({
    catAxisLabelColor: HEX.gray, valAxisLabelColor: HEX.gray,
    catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt",
    catAxisLabelFontSize: 11, valAxisLabelFontSize: 10,
    dataLabelFontFace: "+mn-lt", dataLabelFontSize: 11, dataLabelColor: HEX.text,
    valGridLine: { color: HEX.grid, size: 0.5 }, catGridLine: { style: "none" },
    legendFontFace: "+mn-lt", legendFontSize: 11, legendColor: HEX.text,
    titleFontFace: "+mn-lt", titleFontSize: 13, titleColor: HEX.navy,
    catAxisLineShow: false, valAxisLineShow: false,
  }, extra);
}
function table(s, rows, o, colW, opts) {
  opts = opts || {};
  const data = rows.map((r, ri) => r.map((c, ci) => {
    const isHead = ri === 0;
    const hl = opts.hlRows && opts.hlRows.includes(ri);
    return {
      text: String(c),
      options: {
        bold: isHead || (opts.boldFirstCol && ci === 0) || hl,
        color: isHead ? C.background1 : C.text1,
        fill: { color: isHead ? C.text2 : (hl ? C.background2 : (ri % 2 === 0 ? "F6F9FA" : C.background1)) },
        fontSize: opts.fs || 12, valign: "middle",
        align: opts.align && ci > 0 ? opts.align : "left",
        margin: [3, 5, 3, 5],
      },
    };
  }));
  if (o.h) o.rowH = o.h / rows.length;
  s.addTable(data, Object.assign({ colW, border: { type: "solid", pt: 0.5, color: HEX.grid }, objectName: id("table") }, o));
}

// =====================================================================

// =====================================================================
// 1 TITEL
pres.addSection({ title: "Einstieg" });
{
  const s = pres.addSlide({ masterName: "DARK", sectionTitle: "Einstieg" });
  s.addText("CAS PRICING · LEISTUNGSNACHWEIS 2 · VERSION 2", { placeholder: "kicker" });
  s.addText("Preiskonzept für B2B-Kunden im Hotelbereich", { placeholder: "title" });
  txt(s, "Geberit AquaClean Alba: tief einsteigen, mit der Marktdurchdringung den Preis steigern", { x: 0.8, y: 2.55, w: 11.5, h: 0.6, fontSize: 22, color: C.accent3 });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.8, y: 3.6, w: 11.7, h: 1.5, rectRadius: 0.08, fill: { color: "1E3A52" }, line: { type: "none" }, objectName: "rec_box" });
  txt(s, [
    { text: "Empfehlung an die Geschäftsleitung: ", options: { bold: true, color: C.accent2 } },
    { text: `Penetrationsstrategie in vier Preisphasen freigeben – Start ${J[0]} mit ${chf(p1)} netto pro Gerät, zwei Jahre Einführungsangebot, danach Cost-Plus; Feature-Stufen erst nach erreichtem Durchdringungs-Gate, Pilotbudget ${chf(M.pilotBudget)}, Break-even ${beJ(M.plan)}.`, options: { color: C.background1 } },
  ], { x: 1.1, y: 3.8, w: 11.1, h: 1.1, fontSize: 18 });
  const steps = [["PHASE 1", "Basis-Pricing", chf(p1)], ["PHASE 2", "Cost-Plus", chf(cp)], ["PHASE 3", "Mitbewerber", chf(M.fleetPaket)], ["PHASE 4", "Wertorientiert", chf(M.carePaket)]];
  steps.forEach((st, i) => {
    const x = 0.8 + i * 2.95;
    txt(s, [{ text: st[0] + " · " + st[1], options: { fontSize: 11, bold: true, color: C.accent3, breakLine: true } }, { text: st[2], options: { fontSize: 20, bold: true, color: C.background1 } }], { x, y: 5.4, w: 2.8, h: 0.8 });
    if (i < 3) txt(s, "→", { x: x + 2.45, y: 5.62, w: 0.4, h: 0.4, fontSize: 20, color: C.accent2, bold: true });
  });
  txt(s, "Dominic Hüpp · Marilena Marraffino  |  Abgabe 04.12.2026 · Pitch 10 Min + Q&A 10 Min  |  Preise netto pro Gerät, exkl. MwSt. und Montage", { x: 0.8, y: 6.75, w: 11.7, h: 0.35, fontSize: 11, color: HEX.mute });
}

// 2 BIG PICTURE
pres.addSection({ title: "Big Picture" });
{
  const s = content("Big Picture", "BIG PICTURE · PENETRATIONSSTRATEGIE (LEITFRAGE 9: PREISVERÄNDERUNGEN)", "Tief einsteigen, dann den Preis in drei Schritten anheben – zweimal nur mit neuer Leistung",
    `Durchdringung = Alba-Anteil an jährlich renovierten oder neu gebauten Bädern im Zielsegment DACH (rund ${k3(M.zielsegment)} pro Jahr = ${k3(M.renovationen)} Renovation + ${k3(M.neubau)} Neubau). Verlauf aus dem Bass-Diffusionsmodell (Folie 9), Obergrenze ${pct(M.bass.smax, 0)} = Hotelstars-Kriterium 147. Schritt 1 = Kalender (Ende Einführungsangebot), G2/G3 = Gate im Modell erreicht; Preise netto. Gates: A1.`);
  txt(s, [
    { text: "So lesen: ", options: { bold: true } },
    { text: `Jede Stufe folgt einem anderen Preismodell aus dem Unterricht. Schritt 1 ist das Ende des Einführungsangebots «Geberit AquaClean Jahre» (${span(0, iG1 - 1)}) – Rückkehr zum regulären Hotelpreis, keine Preiserhöhung. Schritte 2 und 3 kommen nur mit neuer Leistung und erst nach erreichtem Gate. Gesenkt wird nie.` },
  ], { x: 0.6, y: 1.55, w: 6.0, h: 1.5, fontSize: 13 });
  const V = M.volumen, A = M.anteil;
  const rng = (a, b) => { if (a > L) return "–"; const x = f(V[a]), y = f(V[Math.min(b, L)]); return b <= a || x === y ? x : `${x}–${y}`; };
  const rngA = (a, b) => { if (a > L) return "–"; const x = pct(A[a]), y = pct(A[Math.min(b, L)]); return b <= a || x === y ? x : `${x.replace(" %", "")}–${y}`; };
  const ph = [
    { h: 1.35, fill: C.accent2, fc: C.text2, p: `PHASE 1 · ${span(0, iG1 - 1)}`, price: chf(p1), model: "Basis-Pricing", anchor: `Liste −${pct(M.einfuehrungRabatt, 0)} · Anker: Standard-WC`, kpi: `${rng(0, iG1 - 1)} Geräte/Jahr · ${rngA(0, iG1 - 1)}`, gate: `Ende Einführungsangebot ${J[iG1 - 1]} → ${chf(cp)} (${yr(iG1)})` },
    { h: 2.0, fill: C.accent3, fc: C.text2, p: `PHASE 2 · ${span(iG1, iFleet - 1)}`, price: chf(cp), model: "Cost-Plus", anchor: `Projektpreis ab 5 Geräten (Liste −${pct(M.projektRabatt, 0)})`, kpi: `${rng(iG1, iFleet - 1)} Geräte/Jahr · ${rngA(iG1, iFleet - 1)}`, gate: `G2 → Fleet: ≥${pct(ga[1])} Anteil (${yr(iFleet)}), Feldtest bestanden` },
    { h: 2.65, fill: C.accent1, fc: C.background1, p: `PHASE 3 · ${span(iFleet, iWert - 1)}`, price: chf(M.fleetPaket), model: "Mitbewerber-Pricing", anchor: "Fleet-Paket · Anker: günstigster Peer", kpi: `${rng(iFleet, iWert - 1)} Geräte/Jahr · ${rngA(iFleet, iWert - 1)}`, gate: `G3 → Care: ≥${pct(ga[2])} Anteil (${yr(iWert)}), Nutzen gemessen` },
    { h: 3.3, fill: C.text2, fc: C.background1, p: `PHASE 4 · AB ${yr(iWert)}`, price: chf(M.carePaket), model: "Wertorientiert", anchor: "Care-Paket · Anker: Hotelnutzen", kpi: `${rng(iWert, L)} Geräte/Jahr · ${rngA(iWert, L)}`, gate: `Endanteil Alba ${pct(A[L])}, Konkurrenz ${pct(M.plan.wettbewerb[L])}; Upselling Sela/Mera` },
  ];
  const base = 5.25;
  ph.forEach((p, i) => {
    const x = 0.6 + i * 3.06, w = 2.94, y = base - p.h;
    s.addShape(pres.shapes.RECTANGLE, { x, y, w, h: p.h, fill: { color: p.fill }, line: { type: "none" }, objectName: id("step") });
    txt(s, [
      { text: p.p, options: { fontSize: 11, bold: true, breakLine: true } },
      { text: p.price, options: { fontSize: 22, bold: true, breakLine: true } },
      { text: p.model, options: { fontSize: 13, bold: true, breakLine: true } },
      { text: p.anchor, options: { fontSize: 11 } },
    ], { x: x + 0.12, y: y + 0.08, w: w - 0.24, h: 1.2, color: p.fc, margin: 0.02 });
    txt(s, [
      { text: "Durchdringung: ", options: { bold: true } }, { text: p.kpi, options: { breakLine: true } },
      { text: p.gate, options: { color: C.accent4 } },
    ], { x, y: base + 0.1, w, h: 1.2, fontSize: 11 });
    if (i > 0) circ(s, i === 1 ? "1" : "G" + i, x - 0.25, y - 0.2, 0.38, C.accent5, 10);
  });
  s.addShape(pres.shapes.LINE, { x: 0.6, y: base, w: 12.12, h: 0, line: { color: HEX.navy, width: 1 }, objectName: "baseline" });
}

// 3 AUSGANGSLAGE & ZIELKUNDE
pres.addSection({ title: "Angebot & Wert" });
{
  const s = content("Angebot & Wert", "LEITFRAGE 1 · ANGEBOT, ZIELKUNDE UND WETTBEWERB", "Dusch-WCs fehlen im Hotel – Alba macht sie zum Preis eines guten Standard-WCs möglich",
    "Quellen: Projekt-Marktanalyse Abschn. 1–5, 8, 11–12 (CH-Händlerpreise inkl. MwSt., SBZ 2021); Geberit Geschäftsbericht 2025; Hotelstars Union Kriterien 2025; TOPHOTELPROJECTS 11/2026; CoStar 2023.");
  const stats = [["~1 %", "der Haushalte in DE haben ein Dusch-WC (CH ~10 %)"], [`${f(M.zimmerDACH / 1e6, 2)} Mio.`, `Hotelzimmer in DACH, rund ${pct(v("anteil_zielsegment"), 0)} davon 4/5★`], [`~${k3(M.zielsegment)}`, "Zielsegment-Bäder pro Jahr in DACH (Renovation + Neubau)"], [`+${v("hotelstars_punkte")} Punkte`, `Hotelstars Union (Kriterium 147) ab ${pct(v("hotelstars_schwelle"))} der Zimmer mit Dusch-WC`]];
  stats.forEach((st, i) => {
    const x = 0.6 + i * 3.08;
    txt(s, st[0], { x, y: 1.55, w: 2.9, h: 0.5, fontSize: 26, bold: true, color: C.accent1, margin: 0 });
    txt(s, st[1], { x, y: 2.07, w: 2.9, h: 0.5, fontSize: 12, color: C.accent4, margin: 0 });
  });
  const peerTxt = M.peers.map((p) => `${p.kurz} ${f(p.brutto)}`).join(", ");
  const cols = [
    ["Das Angebot", [
      "Komplettanlage mit Warmwasser-Dusche, Entkalkung und App; Anschlüsse für Gäste verdeckt",
      `Seit 2024 Geberits günstigstes Dusch-WC (CH-Ladenpreis ${chf(v("alba_ladenpreis"))})`,
      "Passt auf Geberit-Unterputztechnik ab 2013 – Renovation ohne Wandeingriff",
    ]],
    ["Zielkunde und Vertrieb", [
      { b: "B2B-Objektgeschäft:", t: "Geberit verhandelt direkt mit Hotel oder Kettenzentrale; Lieferung über Grosshandel, Montage durch Installateure." },
      { b: "Zielsegment:", t: `4-Sterne-Ketten bei Renovation oder Neubau in DACH; Pipeline: ${f(M.pipeline.projekte)} Projekte, ${pct(M.pipeline.anteil45, 0)} davon 4/5★.` },
      { b: `Pilot ${J[0]}:`, t: `${v("pilot_hotels")} Hotels, rund ${f(pilotRund)} Geräte.` },
    ]],
    ["Wettbewerb", [
      { b: "Indirekt (Phase 1–2):", t: `das normale Hotel-WC – z. B. Geberit iCon Wand-WC-Set ${chf(v("anker_hotel_wc"))}.` },
      { b: "Direkt (ab Phase 3):", t: `${peerTxt} (CHF); TOTO im Luxussegment.` },
      { b: "Intern:", t: "Sela/Mera 2.7- bis 5.2-mal teurer – kaum Kannibalisierung." },
    ]],
  ];
  cols.forEach((c, i) => {
    const x = 0.6 + i * 4.1;
    card(s, x, 2.8, 3.95, 3.75);
    head(s, c[0], x + 0.22, 2.95, 3.5);
    bullets(s, c[1], { x: x + 0.22, y: 3.35, w: 3.55, h: 3.1, fontSize: 13 });
  });
}

// 4 POSITIONIERUNG & VALUE
{
  const rp = M.rappenGerundet;
  const s = content("Angebot & Wert", "LEITFRAGE 2 · PREISPOSITIONIERUNG UND VALUE MESSAGE", "Mehr Leistung für wenig Aufpreis: erst unter dem Markt, dann an ihn heran",
    `Value Message: Mehrinvestition ${chf(M.mehrinvestition)} (Alba ${f(p1)} + Elektroanschluss ~${f(v("kosten_elektroanschluss"))} − Hotel-WC Geberit iCon ${f(M.anker.hotelWC)} netto) ÷ ${f(M.naechte)} belegte Nächte (${v("nutzungsdauer_jahre")} J. × 365 × ${pct(v("auslastung"))}) = CHF ${(M.rappenProNacht / 100).toFixed(2)}. LN1-Gästedaten zeigten keinen Gästeaufpreis – daher Argumentation über Klassifizierung und Betrieb.`);
  const X0 = 0.95, Y0 = 4.85, WW = 4.6, HH = 3.0;
  s.addShape(pres.shapes.LINE, { x: X0, y: Y0, w: WW, h: 0, line: { color: HEX.gray, width: 1 }, objectName: "ax_x" });
  s.addShape(pres.shapes.LINE, { x: X0, y: Y0 - HH, w: 0, h: HH, line: { color: HEX.gray, width: 1 }, objectName: "ax_y" });
  s.addShape(pres.shapes.LINE, { x: X0, y: Y0 - HH, w: WW, h: HH, flipV: true, line: { color: HEX.mute, width: 1.25, dashType: "dash" }, objectName: "fairline" });
  txt(s, "Wertäquivalenzlinie", { x: X0 + 0.04 * WW, y: Y0 - 0.42 * HH, w: 1.6, h: 0.3, fontSize: 10, color: C.accent4, margin: 0 });
  txt(s, "Leistung →", { x: X0 + WW - 1.2, y: Y0 + 0.05, w: 1.2, h: 0.25, fontSize: 10, color: C.accent4, align: "right", margin: 0 });
  txt(s, "Preis ↑", { x: X0 - 0.05, y: Y0 - HH - 0.3, w: 1.0, h: 0.25, fontSize: 10, color: C.accent4, margin: 0 });
  const pts = [
    [0.1, 0.08, "Hotel-WC (iCon)", HEX.mute, 0.24], [0.42, 0.2, "Alba Phase 1", HEX.gold, 0.32], [0.72, 0.4, "Alba Care-Paket", HEX.teal, 0.32],
    [0.55, 0.55, "VitrA / Duravit", HEX.gray, 0.24], [0.7, 0.76, "Grohe / Laufen", HEX.gray, 0.24], [0.95, 0.96, "Mera", HEX.navy, 0.24],
  ];
  pts.forEach(([px, py, l, col, d]) => {
    const cx = X0 + px * WW, cy = Y0 - py * HH;
    s.addShape(pres.shapes.OVAL, { x: cx - d / 2, y: cy - d / 2, w: d, h: d, fill: { color: col }, line: { type: "none" }, objectName: id("pt") });
    const right = px < 0.8;
    txt(s, l, { x: right ? cx + d / 2 + 0.05 : cx - 1.5 - d / 2, y: cy - 0.15, w: 1.5, h: 0.3, fontSize: 11, bold: col === HEX.gold || col === HEX.teal, color: C.text1, margin: 0, align: right ? "left" : "right" });
  });
  s.addShape(pres.shapes.LINE, { x: X0 + 0.42 * WW + 0.18, y: Y0 - 0.4 * HH + 0.12, w: 0.3 * WW - 0.36, h: 0.2 * HH - 0.24, flipV: true, line: { color: HEX.teal, width: 2, endArrowType: "triangle", dashType: "sysDot" }, objectName: "pathArrow" });
  txt(s, "Penetrationspfad", { x: X0 + 0.5 * WW, y: Y0 - 0.15 * HH, w: 1.5, h: 0.28, fontSize: 10, italic: true, color: C.accent1, margin: 0 });
  head(s, "Value Proposition für den Hotelier", 6.15, 1.55, 6.6);
  const vp = [
    ["Gäste:", "Dusch-WC schon im Standardzimmer – bisher meist Suiten vorbehalten."],
    ["Klassifizierung:", `+${v("hotelstars_punkte")} Punkte nach Hotelstars-Kriterium 147 ab ${pct(v("hotelstars_schwelle"))} der Zimmer.`],
    ["Betrieb:", "verdeckte Anschlüsse, Ersatzteilgarantie; ab Phase 3 Flottenüberwachung."],
  ];
  vp.forEach((x, i) => {
    const y = 1.92 + i * 0.5;
    circ(s, i + 1, 6.15, y + 0.02, 0.32, C.accent1, 10);
    txt(s, [{ text: x[0] + " ", options: { bold: true } }, { text: x[1] }], { x: 6.6, y, w: 6.15, h: 0.45, fontSize: 13, margin: 0 });
  });
  card(s, 6.15, 3.5, 3.2, 1.55);
  card(s, 9.55, 3.5, 3.2, 1.55, "FBEDEA");
  txt(s, [{ text: "Chancen", options: { bold: true, color: C.accent1, breakLine: true } }, { text: "Referenzbasis vor TOTO im Mittelsegment; Hotel als Testfläche für Privatkäufe; Upselling auf Sela/Mera." }], { x: 6.3, y: 3.58, w: 2.95, h: 1.42, fontSize: 12 });
  txt(s, [{ text: "Risiken", options: { bold: true, color: C.accent5, breakLine: true } }, { text: `Tiefer Preis verankert sich (→ befristet kommunizieren); ${chf(M.penetrationsInvest)} Margenverzicht pro Gerät in Phase 1; Peers ziehen nach.` }], { x: 9.7, y: 3.58, w: 2.95, h: 1.42, fontSize: 12 });
  card(s, 0.6, 5.3, 12.15, 1.25, C.text2);
  txt(s, [
    { text: "Value Message  ", options: { bold: true, color: C.accent2, fontSize: 13 } },
    { text: `«Bieten Sie Ihren Gästen schon im Standardzimmer ein Dusch-WC – für rund ${rp} Rappen pro belegter Nacht, mit ${v("hotelstars_punkte")} Punkten mehr in der Klassifizierung und auf der Geberit-Technik, die bereits in Ihrer Wand steckt.»`, options: { color: C.background1, fontSize: 15 } },
  ], { x: 0.85, y: 5.35, w: 11.7, h: 1.15, valign: "middle" });
}

// 5 PHASE 1 + 2
pres.addSection({ title: "Preisfestsetzung" });
function phaseHead(s, x, label, fill, fc) {
  s.addText(label, { isTextBox: true, shape: pres.shapes.ROUNDED_RECTANGLE, rectRadius: 0.06, x, y: 1.55, w: 5.95, h: 0.38, fill: { color: fill }, color: fc, fontSize: 13, bold: true, valign: "middle", margin: [0, 8, 0, 8], objectName: id("ph") });
}
{
  const s = content("Preisfestsetzung", "LEITFRAGE 4 · PREISFESTSETZUNG · PHASEN 1 UND 2", `Einstieg mit ${chf(p1)} (Basis-Pricing), dann Cost-Plus auf ${chf(cp)}`,
    `Vergleichspreise: CH-Händlerpreise ÷ ${(1 + v("mwst_ch")).toFixed(3)} (ohne MwSt.); Hotel-WC Geberit iCon 503.045.00.8 = Reuter.com CHF ${v("anker_hotel_wc").toFixed(2)}. Kosten: HK ${chf(M.hk)} = Teaminput; übrige Kosten und Gemeinkosten ${chf(M.gemeinkostenProGeraet)} pro Gerät = Annahmen (Anhang A3). ${pct(M.marge, 0)} ≈ Geberit-EBITDA-Marge 2025 (${pct(v("geberit_ebitda_2025"))}).`);
  phaseHead(s, 0.6, `PHASE 1 · BASIS-PRICING · ${span(0, iG1 - 1)}`, C.accent2, C.text2);
  const labels = ["Hotel-WC Geberit iCon", "Alba Hotel-Einführung", "Alba Ladenpreis", "Alba Privatkunden-Liste", `${M.peerMin.kurz} (günstigster Peer)`];
  s.addChart(pres.charts.BAR, [
    { name: "Vergleich", labels, values: [M.anker.hotelWC, 0, M.anker.laden, v("alba_listenpreis_privat_netto"), M.peerMin.netto].map(Math.round) },
    { name: "Alba Hotel", labels, values: [0, p1, 0, 0, 0] },
  ], chartOpts({
    x: 0.5, y: 2.0, w: 6.1, h: 2.7, barDir: "bar", barGrouping: "stacked", catAxisOrientation: "maxMin", catAxisLabelFontSize: 10,
    chartColors: [HEX.mute, HEX.gold], showValue: true, dataLabelPosition: "inEnd", dataLabelFormatCode: "#,##0;;", dataLabelColor: HEX.navy, dataLabelFontSize: 10,
    showLegend: false, showTitle: true, title: "Preisanker, CHF netto pro Gerät", titleFontSize: 11, valAxisHidden: true, valGridLine: { style: "none" }, barGapWidthPct: 40,
  }));
  bullets(s, [
    { b: "Ein Preis:", t: `${chf(p1)} netto = ${pct(M.einfuehrungRabatt, 0)} Einführungsrabatt auf den Listenpreis ${chf(M.liste)}; keine weiteren Rabatte.` },
    { b: "Anker Hotel-WC:", t: `${chf(p1 - Math.round(M.anker.hotelWC))} mehr als das Hotel-Standard-WC Geberit iCon (${chf(M.anker.hotelWC)} netto) – für die Duschfunktion; unter dem Ladenpreis.` },
    { b: "Floor:", t: `Geberit erhält nach ${pct(1 - M.kanal, 0)} Kanalmarge ${chf(M.netto_(p1))}: DB ${chf(M.dbGeraet(p1))} positiv, Vollkosten noch nicht gedeckt (Penetrationsinvestition); Einführungsangebot nur bis ${J[iG1 - 1]}, Kampagne «Geberit AquaClean Jahre».` },
  ], { x: 0.6, y: 4.8, w: 5.95, h: 1.8, fontSize: 13 });

  phaseHead(s, 6.8, `PHASE 2 · COST-PLUS · ${span(iG1, iFleet - 1)}`, C.accent3, C.text2);
  const l2 = [`Einführung · ${f(p1)}`, `Cost-Plus · ${f(cp)}`];
  const pr = [p1, cp];
  s.addChart(pres.charts.BAR, [
    { name: `Kanalmarge (${pct(1 - M.kanal, 0)})`, labels: l2, values: pr.map((p) => Math.round(M.kanalmarge(p))) },
    { name: "Herstellkosten", labels: l2, values: pr.map(() => M.hk) },
    { name: "Weitere var. Kosten", labels: l2, values: pr.map(() => M.weitereVar) },
    { name: "DB Geberit", labels: l2, values: pr.map((p) => Math.round(M.dbGeraet(p))) },
  ], chartOpts({
    x: 6.7, y: 2.0, w: 6.1, h: 2.7, barDir: "bar", barGrouping: "stacked", catAxisOrientation: "maxMin", catAxisLabelFontSize: 10,
    chartColors: [HEX.mute, HEX.gold, "E8C987", HEX.teal], showValue: true, dataLabelPosition: "ctr", dataLabelColor: HEX.navy, dataLabelFontSize: 10,
    showLegend: true, legendPos: "b", legendFontSize: 10, showTitle: true, title: "Hotelpreis aufgeteilt, CHF pro Gerät", titleFontSize: 11, valAxisHidden: true, barGapWidthPct: 35,
  }));
  bullets(s, [
    { b: "Formel:", t: `(Vollkosten ${chf(M.vollkosten)} + ${pct(M.zuschlag, 0)} Gewinnzuschlag) ÷ Kanalanteil ${pct(M.kanal, 0)} = ${chf(cp)} = Projektpreis ab 5 Geräten (Liste −${pct(M.projektRabatt, 0)}).` },
    { b: "Ein Schritt:", t: `${f(p1)} → ${f(cp)} (+${pct(M.schritt1, 0)}) Ende ${J[iG1 - 1]}: Aktion endet, Projektrabatt bleibt.` },
    { b: "Zwei Kostensichten:", t: `Cost-Plus mit Vollkosten (inkl. ${chf(M.gemeinkostenProGeraet)} Vertrieb/Overhead), Business Case nur mit Zusatzkosten (~${chf(Math.round(M.programmkosten[L] / M.volumen[L]))}/Gerät).` },
  ], { x: 6.8, y: 4.8, w: 5.95, h: 1.8, fontSize: 13 });
}

// 6 PHASE 3 + 4
{
  const s = content("Preisfestsetzung", "LEITFRAGE 4 · PREISFESTSETZUNG · PHASEN 3 UND 4", `Features nach Hotelnutzen: Geberit schöpft ${pct(M.wertanteil, 0)} ab – Fleet-Paket klar unter dem günstigsten Peer`,
    `Peers: CH-Händlerpreise ohne MwSt. (Momentaufnahme). Nutzen = Kosten/Vorfall × Vorfälle/Jahr × vermeidbarer Anteil, Barwert ${v("nutzen_jahre")} J. @ ${pct(v("kalkulationszins"), 0)}; ${chf(v("kosten_pro_vorfall"))} pro Vorfall (Anhang A3).`);
  phaseHead(s, 0.6, `PHASE 3 · MITBEWERBER-PRICING · ${span(iFleet, iWert - 1)}`, C.accent1, C.background1);
  const labels = ["Alba Grundgerät", "Alba Fleet-Paket"].concat(M.peers.map((p) => p.kurz));
  s.addChart(pres.charts.BAR, [
    { name: "Peers", labels, values: [0, 0].concat(M.peers.map((p) => Math.round(p.netto))) },
    { name: "Alba", labels, values: [cp, M.fleetPaket].concat(M.peers.map(() => 0)) },
  ], chartOpts({
    x: 0.5, y: 2.0, w: 6.1, h: 2.7, barDir: "bar", barGrouping: "stacked", catAxisOrientation: "maxMin", catAxisLabelFontSize: 10,
    chartColors: [HEX.mute, HEX.teal], showValue: true, dataLabelPosition: "inEnd", dataLabelFormatCode: "#,##0;;", dataLabelColor: HEX.white, dataLabelFontSize: 10,
    showLegend: false, showTitle: true, title: "CHF netto pro Gerät", titleFontSize: 11, valAxisHidden: true, valGridLine: { style: "none" }, barGapWidthPct: 40,
  }));
  bullets(s, [
    { b: "Ankerwechsel:", t: `ab ≥${pct(ga[1])} Anteil vergleicht der Hotelier mit anderen Dusch-WCs.` },
    { b: `Fleet-Paket ${chf(M.fleetPaket)}:`, t: `Gerät + Flottenmonitoring, ${pct(1 - M.fleetPaket / M.peerMin.netto, 0)} unter dem günstigsten Peer (${chf(M.peerMin.netto)}).` },
    { b: "Floor:", t: `Fleet-Kosten ~${chf(M.featureKosten.fleet)} → Mindestpreis ${chf(M.mindest.fleet)}, Fleet-Aufpreis ${chf(M.preisFleet)}.` },
  ], { x: 0.6, y: 4.8, w: 5.95, h: 1.8, fontSize: 13 });

  phaseHead(s, 6.8, `PHASE 4 · WERTORIENTIERT · AB ${yr(iWert)}`, C.text2, C.background1);
  const l4 = ["Fleet", "Predict", `Care ${v("nutzen_jahre")} J.`];
  s.addChart(pres.charts.BAR, [
    { name: "Mindestpreis", labels: l4, values: [M.mindest.fleet, M.mindest.predict, M.mindest.care].map(Math.round) },
    { name: "Unser Preis", labels: l4, values: [M.preisFleet, M.preisPredict, M.preisCare] },
    { name: "Hotelnutzen", labels: l4, values: [M.nutzen.fleet, M.nutzen.predict, M.nutzen.care].map(Math.round) },
  ], chartOpts({
    x: 6.7, y: 2.0, w: 6.1, h: 2.7, barDir: "col", barGrouping: "clustered", catAxisLabelFontSize: 10,
    chartColors: [HEX.mute, HEX.teal, HEX.navy], showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 10,
    showLegend: true, legendPos: "r", legendFontSize: 10, showTitle: true, title: "CHF netto pro Gerät, einmalig", titleFontSize: 11, valAxisHidden: true, valGridLine: { style: "none" }, valAxisMinVal: 0, barGapWidthPct: 50,
  }));
  bullets(s, [
    { b: "Regel:", t: `Preis = ${pct(M.wertanteil, 0)} des Hotelnutzens, über dem Mindestpreis; ${pct(1 - M.wertanteil, 0)} bleiben als Kaufanreiz beim Hotel.` },
    { b: `Care-Paket ${chf(M.carePaket)}:`, t: `ab ${v("staffel_care_ab")} Geräten alles inklusive – statt ${chf(M.vollFleet)} mit Predict (${chf(M.preisPredict)}) und Care (${chf(M.preisCare)}) als Optionen.` },
    { b: "Beleg:", t: "Hotelnutzen wird im Pilot gemessen, bevor Gate G3 öffnet." },
  ], { x: 6.8, y: 4.8, w: 5.95, h: 1.8, fontSize: 13 });
}

// 7 DIFFERENZIERUNG & BEHAVIORAL
pres.addSection({ title: "Markt & Umsetzung" });
{
  const s = content("Markt & Umsetzung", "LEITFRAGEN 5 UND 6 · PREISDIFFERENZIERUNG UND BEHAVIORAL PRICING", "Grosse Flotten zahlen weniger pro Gerät – Anker und Framing tragen die Preisstufen",
    `Staffel ab Phase 3/4, Mengen je Standort, 12 Monate kumulierbar; Bündelung senkt die Care-Kosten bei ≥${v("staffel_care_ab")} Geräten auf ~${chf(M.featureKosten.careBundle)}. Schwellen ${v("staffel_fleet_ab")}/${v("staffel_care_ab")} werden im Pilot geprüft. Konzepte: Zatta, Value Pricing und Value Selling (14.11.2026).`);
  const fa = v("staffel_fleet_ab"), ca = v("staffel_care_ab");
  table(s, [
    ["CHF netto pro Gerät", `1–${fa - 1} Geräte`, `ab ${fa} · Fleet`, `ab ${ca} · Care`],
    ["Alba-Grundgerät", f(cp), "inkl.", "inkl."],
    ["Fleet-Monitoring", "+" + f(M.einzel.fleet), "inkl.", "inkl."],
    ["Predict", "+" + f(M.einzel.predict), "+" + f(M.preisPredict), "inkl."],
    [`Care ${v("nutzen_jahre")} Jahre`, "+" + f(M.einzel.care), "+" + f(M.preisCare), "inkl."],
    ["Vollausstattung", f(M.vollEinzel), f(M.vollFleet), f(M.vollCare)],
  ], { x: 0.6, y: 1.55, w: 6.3, h: 2.7 }, [2.1, 1.4, 1.4, 1.4], { fs: 13, align: "center", boldFirstCol: true, hlRows: [5] });
  card(s, 0.6, 4.4, 6.3, 2.15);
  txt(s, [
    { text: "Weitere Dimensionen: ", options: { bold: true, color: C.accent1 } },
    { text: `Zeit (Einführungspreis ${span(0, iG1 - 1)}), Referenzstatus (nur gegen Referenzfreigabe), Kette vs. Einzelhotel (Rahmenvertrag), Land (lokal hergeleitet).`, options: { breakLine: true } },
    { text: "Online: ", options: { bold: true, color: C.accent1 } },
    { text: `kein Online-Gerätepreis, weil Hotels projektbezogen kaufen. Features (Fleet, Predict, Care) werden separat pro Gerät bepreist und von Geberit direkt verkauft.` },
  ], { x: 0.8, y: 4.5, w: 5.9, h: 1.95, fontSize: 12, paraSpaceAfter: 6, valign: "middle" });
  head(s, "Behavioral Pricing", 7.3, 1.55, 5.4);
  const items = [
    ["Ankerwechsel:", "Phase 1–2 Standard-WC, Phase 3–4 Peers und Mera."],
    ["Referenzpreis:", `${chf(p1)} als befristeter Einführungspreis neben Listenpreis ${f(cp)} – die Erhöhung wirkt als Ende eines Vorteils.`],
    ["Framing:", `«${M.rappenGerundet} Rappen pro Gästenacht» statt «${chf(p1)} pro Gerät».`],
    ["Kompromisseffekt:", "Einzel – Fleet – Care; die Mitte wirkt als sichere Wahl."],
    ["Schwellenpreise:", `${f(p1)} / ${f(M.fleetPaket)} / ${f(M.carePaket)} unter ${f(nextRound(p1))} / ${f(nextRound(M.fleetPaket))} / ${f(nextRound(M.carePaket))}.`],
    ["Vertrauenssignal:", "tiefer Care-Preis = «wir erwarten kaum Defekte»."],
  ];
  items.forEach((it, i) => {
    const y = 1.95 + i * 0.77;
    circ(s, i + 1, 7.3, y + 0.03, 0.32, C.accent1, 10);
    txt(s, [{ text: it[0] + " ", options: { bold: true } }, { text: it[1] }], { x: 7.75, y, w: 5.0, h: 0.72, fontSize: 12, margin: 0 });
  });
}

// 8 UMSETZUNG & INTERNATIONAL
{
  const s = content("Markt & Umsetzung", "LEITFRAGEN 7 UND 8 · UMSETZUNG UND INTERNATIONALE PREISPOLITIK", "Klare Preishoheit, Anreize auf Nettopreis – und Deutschland als erstes Zielland",
    `Voraussetzungen: Vollkosten aus dem Controlling, CRM-Erfassung jedes Hotelprojekts, Fleet-Technik bis ${yr(iFleet)}, Referenzrechte. DE/AT-Einführungspreis: gleicher Abstand zum lokalen Strassenpreis netto wie in CH (${pct(M.faktorStrasse, 0)}), vor Start zu prüfen. Konzepte: Seyfang (Net Price, Sales Waterfall).`);
  const cols = [
    ["Verantwortung", ["Pricing Lead AquaClean: Listenpreise, Korridore, Gate-Anträge", "GL gibt jede Preisstufe frei; Deal Desk ab 5 % Abweichung"]],
    ["Konditionen", ["Hotelpreis ab 5 Geräten; Einführungsangebot nur für registrierte Projekte, Lieferung nach Bauprogramm", `Staffel ${v("staffel_fleet_ab")}/${v("staffel_care_ab")} je Standort, Kettenrahmenvertrag, keine Zusatzrabatte`]],
    ["Vertriebssteuerung", ["Bonus pro installiertem Gerät UND auf Nettopreis, nicht auf Umsatz", `B2B-PM je Land: ${f(M.pipeline.planung)} DACH-Projekte in (Vor-)Planung vor der Sanitärspezifikation ansprechen`]],
    ["Kommunikation und Controlling", ["Value-Selling-Kit; Preisstufen 6 Monate vorher ankündigen", "Price Waterfall; Quartals-Review der Gate-KPIs"]],
  ];
  cols.forEach((c, i) => {
    const x = 0.6 + (i % 2) * 3.5, y = 1.55 + Math.floor(i / 2) * 2.55;
    card(s, x, y, 3.35, 2.4);
    circ(s, i + 1, x + 0.15, y + 0.15, 0.36, C.accent1, 11);
    txt(s, c[0], { x: x + 0.6, y: y + 0.15, w: 2.65, h: 0.36, fontSize: 13, bold: true, color: C.text2, margin: 0, valign: "middle" });
    bullets(s, c[1], { x: x + 0.15, y: y + 0.65, w: 3.1, h: 1.7, fontSize: 13 });
  });
  head(s, "International: lokal hergeleitet, nicht umgerechnet", 7.85, 1.55, 4.9, C.accent1);
  const de = v("strassenpreis_de_eur");
  table(s, [
    ["", "CH", "DE", "AT"],
    ["Einstieg netto", chf(p1), "€ " + f(M.preisDE), "€ " + f(M.preisAT)],
    ["Strassenpreis", chf(v("alba_ladenpreis")), `€ ${f(de[0])}–${f(de[1])}`, "UVP € " + f(v("uvp_at_eur"))],
    ["Dusch-WC Haushalte", "~10 %", "~1 %", "k. A."],
    ["Potenzial", "mittel", "hoch", "mittel"],
  ], { x: 7.85, y: 1.95, w: 4.9, h: 1.9 }, [1.7, 1.0, 1.1, 1.1], { fs: 12, align: "center", boldFirstCol: true, hlRows: [1] });
  bullets(s, [
    "Deutschland zuerst: grösster Geberit-Markt (29 % Umsatz), erst ~1 % Verbreitung",
    "Hotelpreis bleibt unter dem sichtbaren Online-Strassenpreis",
    "Korridor DE/AT ±5 % gegen Ketten-Arbitrage; CH eigenständig; Fokus DACH",
  ], { x: 7.85, y: 4.0, w: 4.9, h: 2.55, fontSize: 12 });
}

// 9 BUSINESS CASE · PREISSZENARIEN IM BASS-DIFFUSIONSMODELL
pres.addSection({ title: "Entscheid" });
{
  const S = M.szenarien, P = M.plan, B = M.bass;
  const COL = { penetration: HEX.teal, skimming: HEX.red, konstant: HEX.gold };
  const best = S.reduce((a, b) => (b.barwert > a.barwert ? b : a));
  const titel = best.key === "penetration"
    ? (best.barwert >= 0 ? `Create the Category: die Penetration bringt den höchsten Barwert – auch nach Kanal und Kannibalisierung` : `Create the Category: im DACH-Mix ist die Penetration klar die beste Variante – positiv aber erst nach ${J[L]}`)
    : `Szenarienvergleich: «${best.kurz}» bringt bis ${J[L]} mehr als die Penetration – Preispfad prüfen`;
  const s = content("Entscheid", "BUSINESS CASE · PREISSZENARIEN (BASS-DIFFUSIONSMODELL)", titel,
    `▲ = Feature-Paket: Fleet ${f(M.fleetPaket)} ab ${yr(iFleet)}, Care ${f(M.carePaket)} ab ${yr(iWert)}. DACH-Mix nach Zimmern (DE ${pct(M.laenderAnteil.de, 0)} / AT ${pct(M.laenderAnteil.at, 0)} / CH ${pct(M.laenderAnteil.ch, 0)}), DE/AT zu lokalen Preisen = Ø ${pct(M.preisfaktorDACH, 0)} des CH-Preises. DB nach ${pct(1 - M.kanal, 0)} Kanalmarge (Gerät) und Kannibalisierung; Features direkt. Absatz: Bass mit Wettbewerb, Obergrenze ${pct(M.bass.smax, 0)} = Kriterium 147; A3.`);
  const labels = J.map(String);
  const base = (extra) => chartOpts(Object.assign({ lineSize: 2.5, lineDataSymbol: "circle", lineDataSymbolSize: 4, showLegend: true, legendPos: "b", legendFontSize: 9, catAxisLabelFontSize: 8, valAxisLabelFontSize: 9, showTitle: true, titleFontSize: 11, valAxisLabelFormatCode: "#,##0" }, extra));
  // Zeitachse mit Markierung der Feature-Preiserhöhungen (Penetration): ▲ Fleet-Paket, ▲ Care-Paket
  const mark = (t) => (t === iFleet ? `${J[t]} ▲Fleet` : t === iWert ? `${J[t]} ▲Care` : String(J[t]));
  const labelsM = J.map((_, t) => mark(t));
  s.addChart(pres.charts.LINE, S.map((z) => ({ name: z.kurz, labels: labelsM, values: z.preise.map(Math.round) })),
    base({ x: 0.5, y: 1.6, w: 3.85, h: 2.95, chartColors: S.map((z) => COL[z.key]), title: "Preis Grundgerät (CH-Liste), CHF netto", valAxisMinVal: 600, valAxisMaxVal: 1200, valAxisMajorUnit: 100 }));
  s.addChart(pres.charts.LINE, S.map((z) => ({ name: z.kurz, labels: labelsM, values: z.vol.map(Math.round) })),
    base({ x: 4.35, y: 1.6, w: 3.85, h: 2.95, chartColors: S.map((z) => COL[z.key]), title: "Absatz Geräte über Zeit, pro Jahr" }));
  const yrsT = [0, 2, 4, 6, L].filter((x, k, a) => x <= L && a.indexOf(x) === k);
  table(s, [
    ["Kumulierter DB (TCHF)"].concat(yrsT.map((t) => String(J[t])), ["Break-even", `Barwert ${pct(v("kalkulationszins_bc"), 0)}`]),
  ].concat(S.map((z) => [z.kurz].concat(yrsT.map((t) => tchf(z.kum[t])), [beJ(z), tchf(z.barwert)]))), { x: 0.6, y: 4.62, w: 7.6, h: 1.35 }, [1.6].concat(yrsT.map(() => 4.0 / yrsT.length), [1.0, 1.0]), { fs: 11, align: "center", boldFirstCol: true, hlRows: [1 + S.indexOf(best)] });
  txt(s, S.map((z, k) => ({ text: `${z.kurz}: ${z.key === "penetration" ? `${f(z.preise[0])} (${M.einfuehrungJahre} J.) → ${f(z.preise[L])}, Features ab Gate` : z.name.replace(/^[^:]*: ?/, "")}${k < S.length - 1 ? "  ·  " : ""}`, options: { color: COL[z.key] === HEX.gold ? "8A6A1F" : COL[z.key] } })), { x: 0.6, y: 6.1, w: 7.6, h: 0.45, fontSize: 10, margin: 0 });
  S.forEach((z, k) => {
    const y = 1.5 + k * 0.82;
    txt(s, "CHF " + mio(z.barwert), { x: 8.5, y, w: 4.25, h: 0.45, fontSize: 24, bold: true, color: COL[z.key] === HEX.gold ? "B8862B" : COL[z.key], margin: 0 });
    txt(s, `${z.kurz} · Barwert ${pct(v("kalkulationszins_bc"), 0)} · kumuliert ${mio(z.endwert)} · BE ${beJ(z)}`, { x: 8.5, y: y + 0.44, w: 4.25, h: 0.3, fontSize: 11, color: C.accent4, margin: 0 });
  });
  const sk = M.szenario("skimming"), ko = M.szenario("konstant");
  bullets(s, [
    { b: "Create the Category:", t: `Tiefer Einstieg = schnellere Referenzen. ${J[3]}: ${f(P.vol[3])} Geräte bei Penetration, ${f(ko.vol[3])} bei «Konstant», ${f(sk.vol[3])} bei Skimming.` },
    { b: "First-Mover:", t: `Wer langsam ist, verliert den Markt: Endanteil Alba ${pct(P.anteil[L])} (Konkurrenz ${pct(P.wettbewerb[L])}) gegenüber ${pct(ko.anteil[L])} bei «Konstant» (Konkurrenz ${pct(ko.wettbewerb[L])}).` },
    { b: "Ernten:", t: `Nach der Einführung Cost-Plus ${chf(cp)}; Fleet ab ${yr(iFleet)} und Care ab ${yr(iWert)} verkauft Geberit direkt – ohne Kanalmarge.` },
    { b: "Risiko:", t: `halber Referenzeffekt (q × ${v("risiko_faktor_imitation")}) → Break-even ${beJ(M.halb)}.` },
  ], { x: 8.5, y: 3.95, w: 4.25, h: 2.65, fontSize: 11 });
}

// 10 ENTSCHEID
{
  const s = pres.addSlide({ masterName: "DARK", sectionTitle: "Entscheid" });
  s.addText("ENTSCHEID HEUTE", { placeholder: "kicker" });
  s.addText(`Pilot ${J[0]} freigeben und den Penetrationspfad als Leitplanke beschliessen`, { placeholder: "title" });
  const asks = [
    ["1", "Strategie", `Penetrationspfad ${pfad}: Einführungsangebot ${span(0, iG1 - 1)}, Features über Gates G2/G3.`],
    ["2", "Budget", `${chf(M.pilotBudget)} für ${J[0]}: ${v("pilot_hotels")} Hotels, rund ${f(pilotRund)} Geräte, B2B-PM-Zeit, Referenzprogramm, Interviews, Fleet-Feldtest.`],
    ["3", "Governance", `GL-Freigabe pro Gate; quartalsweiser Pricing Review; Stopp bei < ${v("exit_min_geraete")} Geräten oder negativem DB.`],
  ];
  asks.forEach((a, i) => {
    const x = 0.8 + i * 3.95;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 2.85, w: 3.75, h: 2.0, rectRadius: 0.08, fill: { color: "1E3A52" }, line: { type: "none" }, objectName: id("ask") });
    circ(s, a[0], x + 0.2, 3.02, 0.42, C.accent2, 13);
    txt(s, a[1], { x: x + 0.75, y: 3.05, w: 2.8, h: 0.36, fontSize: 16, bold: true, color: C.background1, margin: 0 });
    txt(s, a[2], { x: x + 0.2, y: 3.6, w: 3.4, h: 1.2, fontSize: 13, color: C.background1, margin: 0 });
  });
  txt(s, `Nächste Schritte ${J[0]}`, { x: 0.8, y: 5.15, w: 6, h: 0.35, fontSize: 14, bold: true, color: C.accent3, margin: 0 });
  const nx = [["Q1", "Vollkosten validieren, Pilotverträge"], ["Q2", "Hotel-Interviews, Gabor-Granger"], ["Q3", "Fleet-Feldtest auswerten"], ["Q4", `Review Einführung, Pipeline ${J[1]}`]];
  nx.forEach((q, i) => {
    const x = 0.8 + i * 2.95;
    txt(s, [{ text: q[0] + "  ", options: { bold: true, color: C.accent2 } }, { text: q[1], options: { color: C.background1 } }], { x, y: 5.55, w: 2.85, h: 0.7, fontSize: 13, margin: 0 });
  });
}

// ===================== ANHANG =====================
pres.addSection({ title: "Anhang" });
// A1 GATES
{
  const s = content("Anhang", "ANHANG A1 · GATES UND KPI-COCKPIT", "Drei Preisschritte: einer nach Kalender, zwei nur mit Gate und neuer Leistung",
    `Einführungsangebot gilt für Projekte, die bis Ende ${J[iG1 - 1]} registriert und bestellt sind; Lieferung nach Bauprogramm, spätestens Ende ${J[iG1]}; Menge ≤ Zimmerzahl des Projekts (keine Vorratskäufe). Gate verfehlt → kein Feature-Schritt, keine Senkung; Ankündigung 6 Monate vorher.`);
  const g = M.gateGeraete;
  table(s, [
    ["Schritt", "Preisschritt", "Auslöser / Durchdringung", "Markt und Kunde", "Ökonomie"],
    ["1", `Ende Einführung: ${f(p1)} → ${f(cp)} (${yr(iG1)})`, `Review: ≥${pct(ga[0])} Anteil (~${f(g[0])} Geräte/Jahr), ≥6 Referenzhotels`, "≥3 Referenzfreigaben; Pipeline für Cost-Plus-Preis gesichert", "DB pro Gerät > 0; Nettopreis-Realisierung ≥95 %"],
    ["G2", `Fleet-Paket ${chf(M.fleetPaket)} (${yr(iFleet)})`, `≥${pct(ga[1])} Anteil (~${f(g[1])} Geräte/Jahr)`, "Fleet-Feldtest: Alarm < 15 Min., Ausfallquote < 2 %", `Fleet-Kosten ≤ ${chf(M.featureKosten.fleet)} pro Gerät`],
    ["G3", `Care-Paket ${chf(M.carePaket)} (${yr(iWert)})`, `≥${pct(ga[2])} Anteil (~${f(g[2])} Geräte/Jahr)`, "Hotelnutzen bestätigt (Interviews, Pilotdaten)", `Care-Kosten ≤ ${chf(M.featureKosten.care)} pro Gerät`],
  ], { x: 0.6, y: 1.6, w: 12.15, h: 2.8 }, [0.8, 2.6, 2.75, 3.2, 2.8], { fs: 13, boldFirstCol: true });
  head(s, "KPI-Cockpit für den Quartals-Review", 0.6, 4.6, 12);
  const k = [["Durchdringung", "Geräte, Hotels, Anteil Zielsegment"], ["Preis", "Nettopreis nach Rabatten, Price Waterfall"], ["Ökonomie", "DB pro Gerät und Projekt, Payback"], ["Vertrieb", "Win-Rate, Pipeline, Folgeaufträge, Take-Rate Features"]];
  k.forEach((x, i) => {
    const xx = 0.6 + i * 3.08;
    card(s, xx, 5.0, 2.94, 1.5);
    txt(s, [{ text: x[0], options: { bold: true, color: C.accent1, breakLine: true } }, { text: x[1] }], { x: xx + 0.15, y: 5.1, w: 2.65, h: 1.3, fontSize: 13 });
  });
}

// A2 INFORMATIONSGRUNDLAGEN
{
  const s = content("Anhang", "ANHANG A2 · LEITFRAGE 3: ANALYSE UND INFORMATIONSGRUNDLAGEN", "Kosten, Wettbewerb und Kunde: was wir wissen und was der Pilot liefern muss",
    "Methodik nach Seyfang (Value-Based Pricing): Floor Price aus Kosten, Positionierung aus Wettbewerb, Zielpreis aus Kundenwert, abgesichert durch Strategic Business Check.");
  table(s, [
    ["Bereich", "Vorhanden", "Lücke", "Beschaffung (bis)"],
    ["Kosten", `Herstellkosten ${chf(M.hk)} (intern); Vollkosten-Annahme ${chf(M.vollkosten)}`, "Ist-Vollkosten, Garantie- und Servicekosten", `Kalkulation mit Controlling (vor Gate G1, Q2 ${J[0]})`],
    ["Wettbewerb", `CH-Händlerpreise von ${M.peers.length} direkten Peers; Geberit-Preisleiter; Hotelreferenzen TOTO/Geberit`, "Projektpreise der Wettbewerber im Hotel", "Win/Loss-Erfassung im CRM; Interviews mit Installateuren"],
    ["Kunde (Hotelier)", "Feldtest Arlberg: 10 Geräte, 6 Monate (Betrieb); LN1-Gästedaten", "Zahlungsbereitschaft des Hoteliers für Gerät und Features", `8–10 Interviews Einkauf/Technik + Gabor-Granger im Pilot (Q1–Q3 ${J[0]})`],
    ["Markt", `Dusch-WC: CH ~10 %, DE ~1 % der Haushalte; Hotelbestand DACH ${f(M.zimmerDACH / 1e6, 2)} Mio. Zimmer (CoStar); Pipeline ${f(M.pipeline.projekte)} Projekte, ${f(M.pipeline.eroeffnungen)} Eröffnungen ${J[0]}`, "Verbreitung in Hotels; 4/5★-Anteil DE", "Hotelstars-Auswertung; Projektliste TOPHOTELPROJECTS (Zimmer, Phase)"],
  ], { x: 0.6, y: 1.6, w: 12.15, h: 3.55 }, [1.7, 3.8, 3.1, 3.55], { fs: 13, boldFirstCol: true });
  card(s, 0.6, 5.35, 12.15, 1.15);
  txt(s, [
    { text: "Wichtigste Erkenntnis: ", options: { bold: true, color: C.accent1 } },
    { text: "Kosten und Wettbewerb sind gut genug bekannt, um Phase 1–3 zu bepreisen. Für Phase 4 fehlt die Zahlungsbereitschaft des Hoteliers – genau diese Daten sammelt der Pilot, bevor Gate G3 den wertorientierten Preis freigibt." },
  ], { x: 0.85, y: 5.45, w: 11.7, h: 0.95, fontSize: 13, valign: "middle" });
}

// A3 ANNAHMENREGISTER – direkt aus params.json
{
  const s = content("Anhang", "ANHANG A3 · ANNAHMENREGISTER", "Jede Zahl mit Herkunft und Prüfschritt",
    "Typ: Fakt = Quelle vorhanden · Teaminput = interne Angabe · Annahme = begründete Modellannahme, im Pilot zu validieren. Alle Werte stammen aus params.json (grafiken/v2).");
  const T = (k) => v(k) !== undefined && M.P[k].typ;
  const prog = M.programmkosten, vol = M.volumen;
  const peersB = M.peers.map((p) => p.brutto);
  table(s, [
    ["Grösse", "Wert", "Typ", "Herleitung / Prüfung", "Folie"],
    ["Herstellkosten", `${chf(M.hk)} pro Gerät`, T("herstellkosten"), M.P.herstellkosten.herleitung, "5"],
    ["Weitere variable Kosten", `${chf(M.weitereVar)} pro Gerät`, "Teaminput", `Logistik ${v("kosten_logistik")} + Garantie ${v("kosten_garantie")} + Projektsupport ${v("kosten_projektsupport")}`, "5, 9"],
    ["Programm- und Gemeinkosten", `${chf(M.gemeinkostenProGeraet)} pro Gerät`, "Annahme", M.P.gemeinkosten_pro_geraet.herleitung, "5"],
    ["Vergleichspreise Schweiz", `CHF ${f(v("anker_hotel_wc"))}–${f(Math.max(...peersB))} inkl. MwSt.`, "Fakt", `Händlerpreise (Momentaufnahme); ÷ ${(1 + v("mwst_ch")).toFixed(3)} auf netto umgerechnet`, "3, 5, 6"],
    ["Zielsegment-Bäder DACH", `~${k3(M.zielsegment)} pro Jahr`, "Quelle/ Annahme", `Renov. ${f(M.zimmerDACH / 1e6, 2)} Mio. × ${pct(v("anteil_zielsegment"), 0)} ÷ ${v("renovationszyklus")} J. = ${k3(M.renovationen)}; Neubau ${f(M.pipeline.eroeffnungen)} × ${pct(M.pipeline.anteil45, 0)} × ${f(M.zimmerProProjekt)} = ${k3(M.neubau)}`, "2, 9"],
    ["Bass-Diffusion", `p ${M.bass.p}, q ${M.bass.q}, s_max ${pct(M.bass.smax, 0)}, ε ${M.bass.eps}, δ ${M.bass.delta}`, "Annahme", `s_max = Hotelstars-Kriterium 147; q knapp über Literatur (0.38)`, "2, 9"],
    ["Wettbewerb", `p_W = ${M.bass.pW}, Spillover θ = ${M.bass.theta}`, "Annahme", "Konkurrenz teilt das Potenzial; θ = gegenseitiger Spillover", "9"],
    ["Programmkosten, Zins", `TCHF ${tchf(prog[0])} → ${tchf(prog[prog.length - 1])}; Barwert @ ${pct(v("kalkulationszins_bc"), 0)}`, "Team/ Annahme", `Zusatzkosten: ${v("b2b_pm_anzahl")} PM × ${pct(v("b2b_pm_zeitanteil"), 0)} × ${tchf(v("b2b_pm_kosten_fte"))}k + Referenz, Schulung, Fleet`, "9, 10"],
    ["Features", `Take ${pct(v("takerate_fleet"), 0)}/${pct(v("takerate_predict"), 0)}/${pct(v("takerate_care"), 0)}; Kosten ${M.featureKosten.fleet}/${M.featureKosten.predict}/${M.featureKosten.care}`, "Annahme", `Preis = ${pct(M.wertanteil, 0)} des Hotelnutzens (${M.preisFleet}/${M.preisPredict}/${M.preisCare}); Fleet ab G2, Care ab G3`, "6, 7, 9"],
    ["Hotelnutzen", `1 Vorfall in ${f(1 / v("vorfaelle_pro_jahr"))} J.; ${chf(v("kosten_pro_vorfall"))}/Vorfall`, "Team/Annahme", `Vermeidbar: Fleet ${pct(v("vermeidbar_fleet"), 0)}, Predict +${pct(v("vermeidbar_predict"), 0)}; Barwert ${v("nutzen_jahre")} J. @ ${pct(v("kalkulationszins"), 0)}; Feldtest prüfen`, "6"],
    ["Kanal, Kannibalisierung", `${pct(M.kanal, 0)} Nettoanteil; ${pct(v("kannibalisierung_anteil"), 0)} × CHF ${v("db_geberit_keramik")}`, "Annahme", "Features direkt (100 %); 80 % der ersetzten WCs sind Konkurrenzprodukte", "5, 9"],
    ["Value Message", `${chf(M.mehrinvestition)} ÷ ${f(M.naechte)} Nächte`, "Annahme", `Alba ${f(p1)} + Elektro ~${v("kosten_elektroanschluss")} − Geberit iCon ${f(M.anker.hotelWC)}; ${v("nutzungsdauer_jahre")} J. × 365 × ${pct(v("auslastung"), 0)}`, "4"],
    ["Ländermix DE / AT / CH", `€ ${f(M.preisDE)} / € ${f(M.preisAT)} / CHF ${f(M.p1)}`, "Annahme", `Gewicht ${pct(M.laenderAnteil.de, 0)} / ${pct(M.laenderAnteil.at, 0)} / ${pct(M.laenderAnteil.ch, 0)} (Zimmer); DE/AT lokal → Ø ${pct(M.preisfaktorDACH, 0)} des CH-Preises`, "8, 9"],
    ["Preisszenarien", `Skim ${f(M.szenario("skimming").preise[0])} → ${f(M.szenario("skimming").preise[L])}; konstant ${f(M.szenario("konstant").preise[0])}`, "Annahme", "Konstant = Privatkunden-Listenpreis netto (Teaminput); gleiche Programmkosten", "9"],
  ], { x: 0.6, y: 1.4, w: 12.15, h: 5.05 }, [2.45, 2.75, 1.0, 5.3, 0.65], { fs: 10, boldFirstCol: true });
}

// A4 PAY-PER-FLUSH
{
  const fee = v("ppf_gebuehr"), kj = M.ppfKostenJahr;
  const s = content("Anhang", "ANHANG A4 · OPTION PAY-PER-FLUSH", "Pay-per-Flush: Option für Hotels, die an der Nutzung zweifeln",
    `Illustration: (${chf(M.hk)} Herstellung + ${chf(v("ppf_installation"))} Installation) ÷ ${v("ppf_abschreibung_jahre")} Jahre + ${chf(v("ppf_service_jahr"))} Service + ${chf(v("ppf_connectivity_jahr"))} Connectivity/Admin = ${chf(kj)} pro Gerät und Jahr. Keine bestätigten Kosten oder Tarife.`);
  const xs = [0, 250, 500, 750, 1000, 1250, 1500, 1750, 2000];
  const labels = xs.map((x) => f(x));
  s.addChart(pres.charts.LINE, [
    { name: `Erlös bei CHF ${fee.toFixed(2)} pro Nutzung`, labels, values: xs.map((x) => Math.round(x * fee)) },
    { name: "Kosten Geberit pro Jahr", labels, values: xs.map(() => Math.round(kj)) },
  ], chartOpts({
    x: 0.5, y: 1.55, w: 7.0, h: 5.0, chartColors: [HEX.teal, HEX.navy], lineSize: 3, lineDataSymbol: "none",
    showLegend: true, legendPos: "b", showTitle: true, title: "CHF pro Gerät und Jahr nach Nutzungen pro Jahr", valAxisMajorUnit: 100,
    catAxisTitle: "Nutzungen pro Gerät und Jahr", showCatAxisTitle: true, catAxisTitleFontSize: 11, catAxisTitleColor: HEX.gray,
  }));
  head(s, `Break-even bei ~${f(M.ppfBreakEven)} Nutzungen pro Jahr`, 7.85, 1.6, 4.9);
  bullets(s, [
    `Entspricht ~${f(M.ppfProNacht)} Nutzungen pro belegter Nacht bei ${pct(v("auslastung"), 0)} Auslastung`,
    "Geberit bleibt Eigentümer; das Hotel zahlt nur bei Nutzung und kann das Dusch-WC trotzdem als Ausstattung bewerben",
    "Pilot begrenzt auf 10 Geräte oder 10 % der Zimmer pro Kunde",
  ], { x: 7.85, y: 2.0, w: 4.9, h: 2.4, fontSize: 13 });
  card(s, 7.85, 4.45, 4.9, 2.05);
  txt(s, [{ text: "Vor einer Freigabe zu klären", options: { bold: true, color: C.accent1, breakLine: true } },
    { text: "Was zählt als Nutzung (Sensor, Datenschutz)? Wer trägt Installation und Reparatur? Wie wird Geberits Vorleistung (Capex, Restwert) finanziert?" }], { x: 8.05, y: 4.55, w: 4.5, h: 1.85, fontSize: 13 });
}

// A5 NAVIGATOR
{
  const s = content("Anhang", "ANHANG A5 · LEITFRAGEN-NAVIGATOR UND QUELLEN", "Wo jede Leitfrage des Auftrags beantwortet wird",
    "Quellen: Aufgabenstellung CAS Pricing LN2 (Heim); Zatta, Vom Value Pricing zum Value Selling (14.11.2026); Seyfang, Value-Based Pricing (14.11.2026); Geberit Geschäftsbericht 2025; Projekt-Marktanalyse AquaClean Alba; LN1-Daten; Hotelstars Union 2025.");
  table(s, [
    ["Leitfrage", "Folien", "Kernaussage"],
    ["1 · Angebot und Geschäftsmodell", "3", "B2B-Objektgeschäft; Zielkunde Hotelier mit Flotte; Hauptgegner Standard-WC"],
    ["2 · Positionierung und Value Message", "4", `Mehr Leistung für wenig Aufpreis; ${M.rappenGerundet} Rappen pro Gästenacht`],
    ["3 · Analyse und Informationen", "A2, A3", "Kosten und Wettbewerb ausreichend; Hotelier-WTP kommt aus dem Pilot"],
    ["4 · Preisfestsetzung", "5, 6", "Ein Preismodell pro Phase: Basis, Cost-Plus, Mitbewerber, wertorientiert"],
    ["5 · Behavioral Pricing", "7", "Ankerwechsel, Referenzpreis, Framing, Kompromisseffekt, Schwellenpreise"],
    ["6 · Preisdifferenzierung und Online", "7, A4", "Mengenstaffel je Standort; Features separat bepreist; Pay-per-Flush als Option (Anhang)"],
    ["7 · Umsetzung", "8, A1", "Preishoheit, Konditionen, Vertriebsanreize, Controlling"],
    ["8 · Internationale Preispolitik", "8", "Deutschland zuerst, lokaler Euro-Preis, Korridor DE/AT"],
    ["9 · Preisveränderungen", "2, 5, 9, A1", `Einführungsangebot ${M.einfuehrungJahre} J., dann Cost-Plus; Features über Gates`],
  ], { x: 0.6, y: 1.6, w: 12.15, h: 4.8 }, [3.6, 1.3, 7.25], { fs: 13, boldFirstCol: true });
}

// ---------- Prüfungen ausgeben und schreiben ----------
const warn = M.checks.filter((c) => !c.ok);
if (warn.length) {
  console.warn("ACHTUNG – Konsistenzprüfungen nicht erfüllt:");
  warn.forEach((c) => console.warn("  WARN  " + c.msg));
}
// Datei schreiben (ohne Ordner-Einträge im ZIP, damit OneDrive/SharePoint die Datei sauber öffnen)
const fs = require("fs");
const JSZip = require(require.resolve("jszip", { paths: [__dirname, path.dirname(require.resolve("pptxgenjs"))] })); // jszip kommt mit pptxgenjs
pres.write({ outputType: "nodebuffer" }).then(async (buf) => {
  const src = await JSZip.loadAsync(buf);
  const dst = new JSZip();
  for (const [name, entry] of Object.entries(src.files)) {
    if (!entry.dir) dst.file(name, await entry.async("nodebuffer"), { createFolders: false });
  }
  fs.writeFileSync(OUT, await dst.generateAsync({ type: "nodebuffer", compression: "DEFLATE" }));
  console.log("Deck geschrieben:", OUT);
});
