// model.js – rechnet alle abgeleiteten Werte aus params.json.
// Wird von build_v2.js (Node) UND von tool.html (Browser) verwendet: eine Rechenlogik für beide.
// Aufruf: `node model.js` zeigt die Kennzahlen und prüft die Konsistenz.
(function (root) {
function berechne(P) {

  function v(key) {
    if (!(key in P)) throw new Error("Parameter fehlt in params.json: " + key);
    return P[key].wert;
  }
  const round10 = (x) => Math.round(x / 10) * 10;
  const schwelle = (x) => Math.floor(x / 10) * 10 - 1; // Schwellenpreis: 1'201.67 -> 1'199, 653 -> 649
  const netto = (brutto, mwst) => brutto / (1 + mwst);
  const sum = (a) => a.reduce((x, y) => x + y, 0);

  const M = { P, v };
  const jahre = v("jahre");
  M.jahre = jahre;
  const jIdx = (jahr) => jahre.indexOf(jahr);

  // ---------- Kosten und Cost-Plus ----------
  M.hk = v("herstellkosten");
  M.weitereVar = v("kosten_logistik") + v("kosten_garantie") + v("kosten_projektsupport");
  M.varKosten = M.hk + M.weitereVar;
  M.gemeinkostenProGeraet = v("gemeinkosten_pro_geraet");
  M.vollkosten = M.varKosten + M.gemeinkostenProGeraet;
  M.marge = v("ziel_ebitda_marge");
  M.costPlusExakt = M.vollkosten / (1 - M.marge);
  M.preisCostPlus = round10(M.costPlusExakt);

  M.p1 = v("preis_phase1");
  M.pG1 = v("preis_stufe_g1");
  M.ebitda = (p) => p - M.vollkosten;
  M.schritt1 = M.pG1 / M.p1 - 1;
  M.schritt2 = M.preisCostPlus / M.pG1 - 1;
  M.penetrationsInvest = M.preisCostPlus - M.p1;

  // ---------- Preisanker und Wettbewerb ----------
  const mw = v("mwst_ch");
  M.netto = (b) => netto(b, mw);
  M.anker = {
    renova: M.netto(v("anker_renova_set")),
    design: M.netto(v("anker_designkeramik")),
    laden: M.netto(v("alba_ladenpreis")),
    richt: M.netto(v("alba_richtpreis")),
  };
  M.peers = v("peers").map((p) => Object.assign({}, p, { netto: M.netto(p.brutto) })).sort((a, b) => a.netto - b.netto);
  M.peerMin = M.peers[0];
  const pn = M.peers.map((p) => p.netto);
  M.peerMedianNetto = pn.length % 2 ? pn[(pn.length - 1) / 2] : (pn[pn.length / 2 - 1] + pn[pn.length / 2]) / 2;

  // ---------- Pakete ----------
  M.fleetPaket = schwelle(M.peerMin.netto);            // knapp unter dem günstigsten Peer
  M.preisFleet = M.fleetPaket - M.preisCostPlus;       // Wettbewerbsresidual
  M.preisPredict = v("preis_predict");
  M.preisCare = v("preis_care");
  M.carePaket = v("preis_care_paket");
  M.einzel = { fleet: v("einzelpreis_fleet"), predict: v("einzelpreis_predict"), care: v("einzelpreis_care") };
  M.vollEinzel = M.preisCostPlus + M.einzel.fleet + M.einzel.predict + M.einzel.care;
  M.vollFleet = M.fleetPaket + M.preisPredict + M.preisCare;
  M.vollCare = M.carePaket;
  M.vorteilFleet = M.vollFleet / M.vollEinzel - 1;
  M.vorteilCare = M.vollCare / M.vollEinzel - 1;

  // ---------- Mindestpreise (Kosten ÷ (1 − Marge)) ----------
  const fk = { fleet: v("featurekosten_fleet"), predict: v("featurekosten_predict"), care: v("featurekosten_care"), careBundle: v("featurekosten_care_bundle") };
  M.featureKosten = fk;
  M.mindest = {
    fleet: fk.fleet / (1 - M.marge),
    predict: fk.predict / (1 - M.marge),
    care: fk.care / (1 - M.marge),
    careBundle: fk.careBundle / (1 - M.marge),
  };
  M.careImPaket = M.carePaket - M.fleetPaket - M.preisPredict; // impliziter Care-Anteil im Care-Paket

  // ---------- Hotelnutzen (Barwert) ----------
  const i = v("kalkulationszins"), n = v("nutzen_jahre");
  M.rbf = (1 - Math.pow(1 + i, -n)) / i;
  const vf = v("vorfaelle_pro_jahr"), kv = v("kosten_pro_vorfall");
  M.nutzen = {
    fleet: (vf * kv * v("vermeidbar_fleet") + v("admin_ersparnis_jahr")) * M.rbf,
    predict: (vf * kv * v("vermeidbar_predict") + vf * v("naechte_ausfall_vorfall") * v("zimmer_db_nacht") * v("vermeidbar_predict")) * M.rbf,
    care: (vf * kv + v("admin_ersparnis_jahr")) * M.rbf,
  };

  // ---------- Value Message ----------
  M.mehrinvestition = M.p1 + v("kosten_elektroanschluss") - v("preis_standard_wc");
  M.naechte = v("nutzungsdauer_jahre") * 365 * v("auslastung");
  M.rappenProNacht = (M.mehrinvestition / M.naechte) * 100;
  M.rappenGerundet = Math.round(M.rappenProNacht / 5) * 5;

  // ---------- Markt und Gates ----------
  M.zielsegment = v("hotelstars_zimmer") * v("anteil_dach") / v("renovationszyklus") * v("anteil_zielsegment");
  const ga = v("gate_anteile");
  M.gateGeraete = ga.map((a) => a * M.zielsegment);
  const prog = v("programmkosten");
  if (prog.length !== jahre.length) throw new Error("programmkosten braucht " + jahre.length + " Werte");

  // ---------- Diffusion nach Bass mit Wettbewerb (zwei Anbieter, ein Marktpotenzial) ----------
  // a = Alba-Anteil, w = Anteil Konkurrenz an den jährlich renovierten/neu gebauten Bädern im Zielsegment.
  //   frei_t = s_max − a − w                                   (noch nicht besetztes Kategoriepotenzial)
  //   Δa = (p + q · a/s_max) · frei · (Preis/ZB)^(−ε)            (Alba: Innovatoren + eigene Referenzen)
  //   Δw = (p_W + q · (w + θ·a)/s_max) · frei                    (Konkurrenz: profitiert zu θ von Albas Kategorieaufbau)
  //   ZB = Referenzpreis · (1 + δ · (a + w)/s_max)               (Zahlungsbereitschaft wächst mit der Kategorie)
  // Wer schneller Referenzen aufbaut, besetzt das Potenzial, bevor die Konkurrenz es holt (First-Mover).
  const B = { p: v("bass_p"), q: v("bass_q"), smax: v("bass_smax"), eps: v("bass_eps"), delta: v("bass_delta"), ref: v("bass_referenzpreis"), pW: v("wettbewerb_p"), theta: v("wettbewerb_spillover") };
  M.bass = B;
  M.dbOptimalKurzfristig = B.eps > 1 ? (M.varKosten * B.eps) / (B.eps - 1) : Infinity; // Amoroso-Robinson ohne Diffusion
  const featDB = {
    fleet: v("takerate_fleet") * (M.preisFleet - fk.fleet),
    wert: v("takerate_predict") * (M.preisPredict - fk.predict) + v("takerate_care") * (M.preisCare - fk.care),
  };
  // preisRegel(t, sVorjahr, stufe) → { preis, stufe }
  function diffusion(preisRegel, qFaktor) {
    const q = B.q * (qFaktor || 1);
    let s = 0, w = 0, stufe = 0, fleet = false, wert = false;
    const r = { preise: [], vol: [], anteil: [], wettbewerb: [], stufe: [], fleet: [], wert: [], zb: [], db: [] };
    jahre.forEach((jahr, t) => {
      const x = preisRegel(t, s, stufe); stufe = x.stufe;
      // Features erst, wenn technisch verfügbar UND die Kategorie reif ist (Gate G3/G4) – höchstens ein Schritt pro Jahr
      if (!fleet && jahr >= v("fleet_ab_jahr") && s >= ga[2]) fleet = true;
      else if (fleet && !wert && jahr >= v("wert_ab_jahr") && s >= ga[3]) wert = true;
      const frei = Math.max(0, B.smax - s - w);
      const zb = B.ref * (1 + B.delta * (s + w) / B.smax);
      const z = Math.pow(x.preis / zb, -B.eps);
      const dA = (B.p + q * s / B.smax) * frei * z;
      const dW = (B.pW + q * (w + B.theta * s) / B.smax) * frei;
      const k = dA + dW > frei ? frei / (dA + dW) : 1;          // nicht mehr verteilen, als frei ist
      s += dA * k; w += dW * k;
      r.preise.push(x.preis); r.anteil.push(s); r.wettbewerb.push(w); r.vol.push(s * M.zielsegment); r.stufe.push(stufe);
      r.fleet.push(fleet); r.wert.push(wert); r.zb.push(zb);
      r.db.push(x.preis - M.varKosten + (fleet ? featDB.fleet : 0) + (wert ? featDB.wert : 0));
    });
    return r;
  }
  function ergebnis(r) {
    const dbTotal = r.vol.map((x, k) => x * r.db[k]);
    const erg = dbTotal.map((x, k) => x - prog[k]);
    const kum = []; erg.reduce((a, x, k) => (kum[k] = a + x), 0);
    const be = kum.findIndex((x) => x >= 0);
    return Object.assign(r, { dbTotal, programm: prog, ergebnis: erg, kum, breakEvenJahr: be >= 0 ? jahre[be] : null, maxInvest: -Math.min(0, ...kum), endwert: kum[kum.length - 1] });
  }
  // Penetration: Preisstufe steigt, sobald der Anteil des Vorjahres das nächste Gate erreicht (max. ein Schritt pro Jahr)
  const stufenPreise = [M.p1, M.pG1, M.preisCostPlus];
  const penetrationsRegel = (t, s, stufe) => {
    if (t > 0 && stufe < 2 && s >= ga[stufe]) stufe += 1;
    return { preis: stufenPreise[stufe], stufe };
  };
  const fix = (preise) => (t) => ({ preis: preise[t], stufe: 0 });

  M.plan = ergebnis(diffusion(penetrationsRegel));
  M.halb = ergebnis(diffusion(penetrationsRegel, v("risiko_faktor_imitation")));
  M.preisPfad = M.plan.preise;
  M.volumen = M.plan.vol;
  M.anteil = M.plan.anteil;
  M.pilotGeraete = M.volumen[0];
  // Jahr-Index, ab dem eine Stufe gilt (−1 = im Horizont nicht erreicht)
  M.phasen = {
    g1: M.plan.stufe.indexOf(1), g2: M.plan.stufe.indexOf(2),
    g3: M.plan.fleet.indexOf(true), g4: M.plan.wert.indexOf(true),
  };

  // ---------- Preisszenarien ----------
  const konstant = v("szenario_konstant_preis") > 0 ? v("szenario_konstant_preis") : v("alba_listenpreis_privat_netto");
  const skim = v("szenario_skimming_preise");
  if (skim.length !== jahre.length) throw new Error("szenario_skimming_preise braucht " + jahre.length + " Werte");
  M.szenarien = [
    Object.assign({ key: "penetration", name: "Penetration (unsere Strategie)", kurz: "Penetration" }, M.plan),
    Object.assign({ key: "skimming", name: "Skimming: hoch einsteigen, dann senken", kurz: "Skimming" }, ergebnis(diffusion(fix(skim)))),
    Object.assign({ key: "konstant", name: `Konstant: Privatkunden-Listenpreis ${Math.round(konstant)} halten`, kurz: "Konstant" }, ergebnis(diffusion(fix(jahre.map(() => konstant))))),
  ];
  M.szenario = (key) => M.szenarien.find((s) => s.key === key);
  M.pilotBudget = prog[0];

  // ---------- International ----------
  const de = v("strassenpreis_de_eur");
  M.deStrasseNetto = netto((de[0] + de[1]) / 2, v("mwst_de"));
  M.preisDE = schwelle(M.deStrasseNetto * v("faktor_strassenpreis"));
  M.atStrasseNetto = netto(v("strassenpreis_at_eur"), v("mwst_at"));
  M.preisAT = schwelle(M.atStrasseNetto * v("faktor_strassenpreis"));
  M.chStrasseNetto = M.anker.laden;

  // ---------- Pay-per-Flush ----------
  M.ppfKostenJahr = (M.hk + v("ppf_installation")) / v("ppf_abschreibung_jahre") + v("ppf_service_jahr") + v("ppf_connectivity_jahr");
  M.ppfBreakEven = M.ppfKostenJahr / v("ppf_gebuehr");
  M.ppfProNacht = M.ppfBreakEven / (365 * v("auslastung"));

  // ---------- Konsistenzprüfungen ----------
  M.checks = [];
  const chk = (ok, msg) => M.checks.push({ ok, msg });
  chk(M.p1 > M.varKosten, `Phase-1-Preis ${M.p1} über variablen Kosten ${M.varKosten}`);
  chk(M.p1 >= M.vollkosten, `Phase-1-Preis ${M.p1} deckt Vollkosten ${M.vollkosten}`);
  chk(M.p1 < M.chStrasseNetto, `Phase-1-Preis unter Ladenpreis netto ${M.chStrasseNetto.toFixed(0)}`);
  chk(M.pG1 > M.p1 && M.pG1 < M.preisCostPlus, `Zwischenstufe ${M.pG1} liegt zwischen ${M.p1} und ${M.preisCostPlus}`);
  chk(M.schritt1 <= v("max_preisschritt") && M.schritt2 <= v("max_preisschritt"), `Preisschritte ${(M.schritt1 * 100).toFixed(1)} % / ${(M.schritt2 * 100).toFixed(1)} % ≤ ${v("max_preisschritt") * 100} %`);
  chk(M.preisFleet >= M.mindest.fleet, `Fleet ${M.preisFleet} ≥ Mindestpreis ${M.mindest.fleet.toFixed(0)}`);
  chk(M.preisPredict >= M.mindest.predict, `Predict ${M.preisPredict} ≥ Mindestpreis ${M.mindest.predict.toFixed(0)}`);
  chk(M.preisCare >= M.mindest.care, `Care ${M.preisCare} ≥ Mindestpreis ${M.mindest.care.toFixed(0)}`);
  chk(M.careImPaket >= M.mindest.careBundle, `Care-Anteil im Care-Paket ${M.careImPaket} ≥ Mindestpreis bei Bündelung ${M.mindest.careBundle.toFixed(0)}`);
  chk(M.preisFleet <= M.nutzen.fleet && M.preisPredict <= M.nutzen.predict && M.preisCare <= M.nutzen.care, "Alle Featurepreise unter dem Hotelnutzen");
  chk(M.vollEinzel > M.vollFleet && M.vollFleet > M.vollCare, `Staffel fallend: ${M.vollEinzel} > ${M.vollFleet} > ${M.vollCare}`);
  chk(B.eps > 1, `Preisreaktion elastisch (ε = ${B.eps} > 1) – Voraussetzung für Penetration Pricing`);
  chk(M.phasen.g1 >= 0 && M.phasen.g2 >= 0, `Gates G1/G2 werden im Horizont erreicht (${M.phasen.g1 >= 0 ? jahre[M.phasen.g1] : "–"} / ${M.phasen.g2 >= 0 ? jahre[M.phasen.g2] : "–"})`);
  chk(M.phasen.g3 >= 0 && M.phasen.g4 >= 0, `Features starten im Horizont (Fleet ${M.phasen.g3 >= 0 ? jahre[M.phasen.g3] : "–"}, Care ${M.phasen.g4 >= 0 ? jahre[M.phasen.g4] : "–"})`);
  chk(M.preisCostPlus < M.dbOptimalKurzfristig, `Endpreis ${M.preisCostPlus} unter dem kurzfristig DB-optimalen Preis ${Math.round(M.dbOptimalKurzfristig)} (bewusster Verzicht zugunsten der Diffusion)`);
  M.szenarien.slice(1).forEach((s) => chk(M.plan.endwert > s.endwert, `Penetration schlägt ${s.kurz} (${Math.round(M.plan.endwert / 1000)} vs. ${Math.round(s.endwert / 1000)} TCHF kumuliert ${jahre[jahre.length - 1]})`));
  chk(M.einzel.fleet > M.preisFleet && M.einzel.predict > M.preisPredict && M.einzel.care > M.preisCare, "Einzelpreise über Bundle-Preisen");

  return M;
}

if (typeof module !== "undefined" && module.exports) {
  const M = berechne(require("./params.json"));
  M.berechne = berechne;
  module.exports = M;
  if (require.main === module) {
    const f = (x) => Math.round(x).toLocaleString("de-CH");
    console.log("Vollkosten", f(M.vollkosten), "| Cost-Plus", f(M.preisCostPlus), "| Fleet-Paket", M.fleetPaket, "(Fleet", M.preisFleet + ")", "| Care-Paket", M.carePaket);
    console.log("Mindestpreise F/P/C", f(M.mindest.fleet), f(M.mindest.predict), f(M.mindest.care), "| Hotelnutzen F/P/C", f(M.nutzen.fleet), f(M.nutzen.predict), f(M.nutzen.care));
    console.log("Value Message:", M.rappenProNacht.toFixed(1), "Rp. pro Nacht | Zielsegment", f(M.zielsegment), "Bäder/Jahr | DE", M.preisDE, "AT", M.preisAT);
    console.log("Anteil Plan:", M.anteil.map((x) => (x * 100).toFixed(1) + "%").join(" / "));
    M.szenarien.forEach((z) => console.log("  Endanteil", z.kurz.padEnd(12), "Alba", (z.anteil[M.jahre.length - 1] * 100).toFixed(1) + "%", "Konkurrenz", (z.wettbewerb[M.jahre.length - 1] * 100).toFixed(1) + "%"));
    console.log("Bass: p", M.bass.p, "q", M.bass.q, "s_max", M.bass.smax, "ε", M.bass.eps, "δ", M.bass.delta, "| Gates G1–G4:", ["g1", "g2", "g3", "g4"].map((g) => (M.phasen[g] >= 0 ? M.jahre[M.phasen[g]] : "–")).join(" / "), "| kurzfr. DB-opt.", Math.round(M.dbOptimalKurzfristig));
    M.szenarien.forEach((s) => console.log(s.kurz.padEnd(12), "Preis", s.preise.map((x) => f(x)).join(" / "), "| Absatz", s.vol.map((x) => f(x)).join(" / "), "| kum. TCHF", s.kum.map((x) => f(x / 1000)).join(" / "), "| BE", s.breakEvenJahr));
    console.log("\nPrüfungen:");
    M.checks.forEach((c) => console.log((c.ok ? "  OK    " : "  WARN  ") + c.msg));
  }
} else {
  root.AlbaModell = { berechne };
}
})(this);
