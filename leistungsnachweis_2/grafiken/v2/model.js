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
  M.kanal = v("kanal_nettoanteil");
  M.kanalF = v("kanal_nettoanteil_features");
  M.netto_ = (hotelpreis) => hotelpreis * M.kanal;                 // Geberit-Nettoerlös Grundgerät
  // Cost-Plus = (Vollkosten + Gewinnzuschlag) inkl. Kanal: Hotelpreis, bei dem Geberit nach Kanalmarge Vollkosten plus Zuschlag erhält
  M.zuschlag = v("costplus_zuschlag");
  M.costPlusExakt = M.vollkosten * (1 + M.zuschlag) / M.kanal;
  M.preisCostPlus = round10(M.costPlusExakt);

  M.liste = v("alba_listenpreis_privat_netto");
  M.einfuehrungRabatt = v("einfuehrung_rabatt");
  M.p1 = round10(M.liste * (1 - M.einfuehrungRabatt));   // Einführungsangebot = Listenpreis − Rabatt
  // Preispfad Grundgerät: Einführungsangebot (befristet) → Cost-Plus (Hotelpreis ab 5 Geräten)
  M.einfuehrungJahre = v("einfuehrung_jahre");
  M.stufenPreise = [M.p1, M.preisCostPlus];
  M.schritte = [M.preisCostPlus / M.p1 - 1];
  M.pG1 = M.preisCostPlus;
  M.ebitda = (p) => p * M.kanal - M.vollkosten;                  // pro Gerät beim Referenzvolumen
  M.dbGeraet = (p) => p * M.kanal - M.varKosten;
  M.kanalmarge = (p) => p * (1 - M.kanal);
  M.schritt1 = M.schritte[0] || 0;
  M.schritt2 = M.schritte.length > 1 ? Math.max(...M.schritte.slice(1)) : 0;
  M.penetrationsInvest = M.preisCostPlus - M.p1;                  // Hotelpreis-Differenz
  M.penetrationsInvestNetto = M.penetrationsInvest * M.kanal;     // Verzicht auf Geberit-Nettoerlös

  // ---------- Preisanker und Wettbewerb ----------
  const mw = v("mwst_ch");
  M.netto = (b) => netto(b, mw);
  M.anker = {
    hotelWC: M.netto(v("anker_hotel_wc")),
    laden: M.netto(v("alba_ladenpreis")),
    richt: M.netto(v("alba_richtpreis")),
  };
  M.peers = v("peers").map((p) => Object.assign({}, p, { netto: M.netto(p.brutto) })).sort((a, b) => a.netto - b.netto);
  M.peerMin = M.peers[0];
  const pn = M.peers.map((p) => p.netto);
  M.peerMedianNetto = pn.length % 2 ? pn[(pn.length - 1) / 2] : (pn[pn.length / 2 - 1] + pn[pn.length / 2]) / 2;

  // ---------- Pakete ----------
  M.fleetPaketPeer = schwelle(M.peerMin.netto);        // knapp unter dem günstigsten Peer
  M.fleetPaket = M.fleetPaketPeer;                     // wird nach Hotelnutzen ggf. gekappt (s. unten)
  M.preisFleet = M.fleetPaket - M.preisCostPlus;       // Wettbewerbsresidual
  M.preisPredict = 0; M.preisCare = 0; M.carePaket = 0;   // werden nach dem Hotelnutzen gesetzt (Wertabschöpfung)
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
  // Fleet-Aufpreis höchstens gleich dem Hotelnutzen: Paket = min(knapp unter Peer, Schwelle(Cost-Plus + Nutzen))
  // Feature-Preise = Wertabschöpfung × Hotelnutzen (Schwellenpreise); Fleet-Paket höchstens knapp unter dem günstigsten Peer
  M.wertanteil = v("wertabschoepfung_features");
  M.fleetPaket = Math.min(M.fleetPaketPeer, schwelle(M.preisCostPlus + M.wertanteil * M.nutzen.fleet));
  M.preisPredict = schwelle(M.wertanteil * M.nutzen.predict);
  M.preisCare = schwelle(M.wertanteil * M.nutzen.care);
  M.preisFleet = M.fleetPaket - M.preisCostPlus;
  M.vollFleet = M.fleetPaket + M.preisPredict + M.preisCare;
  M.carePaket = schwelle(M.vollFleet * (1 - v("buendelrabatt_care")));
  M.vollCare = M.carePaket;
  M.vorteilFleet = M.vollFleet / M.vollEinzel - 1;
  M.vorteilCare = M.vollCare / M.vollEinzel - 1;
  M.careImPaket = M.carePaket - M.fleetPaket - M.preisPredict;
  M.projektRabatt = 1 - M.preisCostPlus / M.liste;

  // ---------- Value Message ----------
  M.mehrinvestition = M.p1 + v("kosten_elektroanschluss") - M.anker.hotelWC;   // Referenz: Hotel-Standard-WC Geberit iCon, netto
  M.naechte = v("nutzungsdauer_jahre") * 365 * v("auslastung");
  M.rappenProNacht = (M.mehrinvestition / M.naechte) * 100;
  M.rappenGerundet = Math.round(M.rappenProNacht);

  // ---------- Markt und Gates ----------
  // Evidenz DACH-Hotelpipeline (TOPHOTELPROJECTS): Anteil 4/5-Sterne an den Projekten
  M.pipeline = { projekte: v("thp_projekte_dach"), anteil45: v("thp_projekte_4_5_sterne") / v("thp_projekte_dach"), planung: v("thp_projekte_planung"), eroeffnungen: v("thp_eroeffnungen_2027") };
  // Zielsegment-Bäder pro Jahr = Renovation (Bestand) + Neubau (Pipeline)
  M.zimmerDACH = v("hotel_zimmer_de") + v("hotel_zimmer_at") + v("hotel_zimmer_ch");
  M.renovationen = M.zimmerDACH * v("anteil_zielsegment") / v("renovationszyklus");
  M.zimmerProProjekt = v("costar_pipeline_zimmer") / v("costar_pipeline_projekte");
  M.neubau = M.pipeline.eroeffnungen * M.pipeline.anteil45 * M.zimmerProProjekt;
  M.zielsegment = M.renovationen + M.neubau;
  // ---------- International ----------
  const de = v("strassenpreis_de_eur");
  M.deStrasseNetto = netto((de[0] + de[1]) / 2, v("mwst_de"));
  // DE/AT: gleicher Abstand zum lokalen Strassenpreis wie der Schweizer Einführungspreis
  M.faktorStrasse = M.p1 / netto(v("alba_ladenpreis"), v("mwst_ch"));
  M.preisDE = schwelle(M.deStrasseNetto * M.faktorStrasse);
  M.atStrasseNetto = netto(v("strassenpreis_at_eur"), v("mwst_at"));
  M.preisAT = schwelle(M.atStrasseNetto * M.faktorStrasse);
  M.chStrasseNetto = M.anker.laden;
  // Ländermix DACH: Volumen nach Zimmerbestand, Preise lokal (DE/AT in EUR, umgerechnet in CHF)
  M.fx = v("wechselkurs_eur_chf");
  M.laenderAnteil = { de: v("hotel_zimmer_de") / M.zimmerDACH, at: v("hotel_zimmer_at") / M.zimmerDACH, ch: v("hotel_zimmer_ch") / M.zimmerDACH };
  // Preisniveau DE/AT relativ zur Schweiz aus den Strassenpreisen (unabhängig vom gewählten Einführungspreis)
  M.laenderFaktor = { ch: 1, de: (M.deStrasseNetto * M.fx) / M.chStrasseNetto, at: (M.atStrasseNetto * M.fx) / M.chStrasseNetto };
  M.preisfaktorDACH = ["ch", "de", "at"].reduce((a, k) => a + M.laenderAnteil[k] * M.laenderFaktor[k], 0);
  M.dbGeraetDACH = (p) => p * M.preisfaktorDACH * M.kanal - M.varKosten;
  const ga = v("gate_anteile");
  M.gateGeraete = ga.map((a) => a * M.zielsegment);
  // Programmkosten = nur zusätzliche Kosten (Relevanzprinzip): Zeitanteil der bestehenden B2B-PMs + Programmpositionen
  M.pmKosten = v("b2b_pm_anzahl") * v("b2b_pm_kosten_fte") * v("b2b_pm_zeitanteil");
  M.progPos = { referenz: v("prog_referenzprogramm"), schulungen: v("prog_schulungen"), marktforschung: v("prog_marktforschung"), fleetCare: v("prog_fleet_care") };
  Object.entries(M.progPos).forEach(([k, a]) => { if (a.length !== jahre.length) throw new Error("prog_" + k + " braucht " + jahre.length + " Werte"); });
  const prog = jahre.map((_, t) => M.pmKosten + M.progPos.referenz[t] + M.progPos.schulungen[t] + M.progPos.marktforschung[t] + M.progPos.fleetCare[t]);
  M.programmkosten = prog;

  // ---------- Diffusion nach Bass mit Wettbewerb (zwei Anbieter, ein Marktpotenzial) ----------
  // Jedes Preisszenario wird eigenständig gerechnet (Entweder-oder: Geberit fährt genau eine Strategie).
  // a = Alba-Anteil, w = Anteil Konkurrenz an den jährlich renovierten/neu gebauten Bädern im Zielsegment.
  //   frei_t = s_max − a − w                                   (noch nicht besetztes Kategoriepotenzial)
  //   Δa = (p + q · a/s_max) · frei_Alba · min(1, (Preis/ZB)^(−ε))   (Alba: Innovatoren + eigene Referenzen)
  //   frei_Alba = s_max · min(1, (ZB/Preis)^ε) − a − w            (preisabhängiges Potenzial, Kalish 1985)
  //   Δw = (p_W + q · (w + θ·a)/s_max) · frei                    (Konkurrenz: profitiert zu θ von Albas Kategorieaufbau)
  //   ZB = Referenzpreis · (1 + δ · (a + θ·w)/s_max)             (Zahlungsbereitschaft wächst v. a. mit Albas Referenzen)
  // Wer schneller Referenzen aufbaut, besetzt das Potenzial, bevor die Konkurrenz es holt (First-Mover).
  const B = { p: v("bass_p"), q: v("bass_q"), smax: v("bass_smax"), eps: v("bass_eps"), delta: v("bass_delta"), ref: v("bass_referenzpreis"), pW: v("wettbewerb_p"), theta: v("wettbewerb_spillover"), zMax: v("bass_preiseffekt_max") };
  M.bass = B;
  M.dbOptimalKurzfristig = B.eps > 1 ? (M.varKosten / M.kanal * B.eps) / (B.eps - 1) : Infinity; // Amoroso-Robinson ohne Diffusion, als Hotelpreis
  const featDB = {
    fleet: v("takerate_fleet") * (M.preisFleet * M.preisfaktorDACH * M.kanalF - fk.fleet),
    wert: v("takerate_predict") * (M.preisPredict * M.preisfaktorDACH * M.kanalF - fk.predict) + v("takerate_care") * (M.preisCare * M.preisfaktorDACH * M.kanalF - fk.care),
  };
  M.kannibalisierungJeGeraet = v("kannibalisierung_anteil") * v("db_geberit_keramik");
  const featErl = {
    fleet: v("takerate_fleet") * M.preisFleet * M.preisfaktorDACH,
    wert: (v("takerate_predict") * M.preisPredict + v("takerate_care") * M.preisCare) * M.preisfaktorDACH,
  };
  // preisRegel(t, sVorjahr, stufe) → { preis, stufe }
  function diffusion(preisRegel, qFaktor) {
    const q = B.q * (qFaktor || 1);
    let s = 0, w = 0, stufe = 0, fleet = false, wert = false;
    const r = { preise: [], vol: [], anteil: [], wettbewerb: [], stufe: [], fleet: [], wert: [], zb: [], db: [], erloes: [], paket: [], absatzFleet: [], absatzPredict: [], absatzCare: [] };
    jahre.forEach((jahr, t) => {
      const x = preisRegel(t, s, stufe); stufe = x.stufe;
      // Features erst, wenn technisch verfügbar UND die Kategorie reif ist (Gate G3/G4) – höchstens ein Schritt pro Jahr
      if (!fleet && jahr >= v("fleet_ab_jahr") && s >= ga[1]) fleet = true;
      else if (fleet && !wert && jahr >= v("wert_ab_jahr") && s >= ga[2]) wert = true;
      const frei = Math.max(0, B.smax - s - w);
      // (C) Zahlungsbereitschaft für Alba wächst mit Albas eigenen Referenzen; Konkurrenz-Installationen zählen nur zu θ
      const zb = B.ref * (1 + B.delta * (s + B.theta * w) / B.smax);
      // (A) Preis bremst, wenn er über der Zahlungsbereitschaft liegt – ein tiefer Preis beschleunigt aber nicht unbegrenzt
      const z = Math.min(B.zMax, Math.pow(x.preis / zb, -B.eps));   // Preis unter ZB beschleunigt (begrenzt), darüber bremst
      // (B) Preisabhängiges Marktpotenzial (Kalish 1985): Bei Preis > ZB kommt nur ein Teil der Hotels überhaupt in Frage
      const potenzial = B.smax * Math.min(1, Math.pow(zb / x.preis, B.eps));
      const freiAlba = Math.max(0, potenzial - s - w);
      const dA = (B.p + q * s / B.smax) * freiAlba * z;
      const dW = (B.pW + q * (w + B.theta * s) / B.smax) * frei;
      const k = dA + dW > frei ? frei / (dA + dW) : 1;          // nicht mehr verteilen, als frei ist
      s += dA * k; w += dW * k;
      r.preise.push(x.preis); r.anteil.push(s); r.wettbewerb.push(w); r.vol.push(s * M.zielsegment); r.stufe.push(stufe);
      r.fleet.push(fleet); r.wert.push(wert); r.zb.push(zb);
      // Geberit-DB pro Gerät: Nettoerlös nach Kanal − variable Kosten + Feature-DB − entgangener DB Geberit-Keramik
      r.db.push(x.preis * M.preisfaktorDACH * M.kanal - M.varKosten + (fleet ? featDB.fleet : 0) + (wert ? featDB.wert : 0) - M.kannibalisierungJeGeraet);
      // Ø Netto-Erlös pro Gerät inkl. Features (Grundgerät + Take-Rate × Featurepreis) = Basis der DB-Rechnung
      r.erloes.push(x.preis * M.preisfaktorDACH + (fleet ? featErl.fleet : 0) + (wert ? featErl.wert : 0));
      // Listenpreis des höchsten verfügbaren Pakets (Grundgerät → Fleet-Paket → Care-Paket)
      r.paket.push(wert ? M.carePaket : fleet ? M.fleetPaket : x.preis);
      // verkaufte Features (Stück) = Geräte × Take-Rate, sobald das Feature verfügbar ist
      r.absatzFleet.push(fleet ? s * M.zielsegment * v("takerate_fleet") : 0);
      r.absatzPredict.push(wert ? s * M.zielsegment * v("takerate_predict") : 0);
      r.absatzCare.push(wert ? s * M.zielsegment * v("takerate_care") : 0);
    });
    return r;
  }
  function ergebnis(r) {
    const dbTotal = r.vol.map((x, k) => x * r.db[k]);
    const erg = dbTotal.map((x, k) => x - prog[k]);
    const kum = []; erg.reduce((a, x, k) => (kum[k] = a + x), 0);
    const be = kum.findIndex((x) => x >= 0);
    const zins = v("kalkulationszins_bc");
    const barwert = erg.reduce((a, x, t) => a + x / Math.pow(1 + zins, t + 1), 0);
    const nettoUmsatz = r.vol.map((x, t) => x * (r.preise[t] * M.preisfaktorDACH * M.kanal + (r.fleet[t] ? featErl.fleet * M.kanalF : 0) + (r.wert[t] ? featErl.wert * M.kanalF : 0)));
    const ebitdaMarge = erg.map((x, t) => (nettoUmsatz[t] > 0 ? x / nettoUmsatz[t] : 0));
    const zielJ = ebitdaMarge.findIndex((x) => x >= M.marge);
    return Object.assign(r, { dbTotal, programm: prog, ergebnis: erg, kum, barwert, nettoUmsatz, ebitdaMarge, zielMargeJahr: zielJ >= 0 ? jahre[zielJ] : null, breakEvenJahr: be >= 0 ? jahre[be] : null, maxInvest: -Math.min(0, ...kum), endwert: kum[kum.length - 1] });
  }
  // Penetration: Preisstufe steigt, sobald der Anteil des Vorjahres das nächste Gate erreicht (max. ein Schritt pro Jahr)
  // Einführungsangebot läuft einfuehrung_jahre (Kalender), danach Cost-Plus; Features über Gates G2/G3
  const SP = M.stufenPreise;
  const penetrationsRegel = (t, s, stufe) => {
    stufe = t < M.einfuehrungJahre ? 0 : 1;
    return { preis: SP[stufe], stufe };
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
    g1: M.plan.stufe.indexOf(1), g2: M.plan.stufe.indexOf(1),
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


  // ---------- Pay-per-Flush ----------
  M.ppfKostenJahr = (M.hk + v("ppf_installation")) / v("ppf_abschreibung_jahre") + v("ppf_service_jahr") + v("ppf_connectivity_jahr");
  M.ppfBreakEven = M.ppfKostenJahr / v("ppf_gebuehr");
  M.ppfProNacht = M.ppfBreakEven / (365 * v("auslastung"));

  // ---------- Konsistenzprüfungen ----------
  M.checks = [];
  const chk = (ok, msg) => M.checks.push({ ok, msg });
  chk(v("anteil_zielsegment") >= 0.3 && v("anteil_zielsegment") <= M.pipeline.anteil45, `4/5★-Anteil Bestand ${Math.round(v("anteil_zielsegment") * 100)} % zwischen 30 % und Neubau-Pipeline ${Math.round(M.pipeline.anteil45 * 100)} %`);
  chk(M.dbGeraetDACH(M.p1) > 0, `Phase 1 im DACH-Mix: DB ${Math.round(M.dbGeraetDACH(M.p1))} pro Gerät (Ø ${Math.round(M.preisfaktorDACH * 100)} % des CH-Preises)`);
  chk(M.dbGeraet(M.p1) > 0, `Phase 1: Geberit-Nettoerlös ${Math.round(M.netto_(M.p1))} über variablen Kosten ${M.varKosten} (DB ${Math.round(M.dbGeraet(M.p1))})`);
  chk(M.preisCostPlus < M.peerMin.netto, `Cost-Plus-Hotelpreis ${M.preisCostPlus} unter günstigstem Peer ${Math.round(M.peerMin.netto)}`);
  chk(M.p1 < M.chStrasseNetto, `Phase-1-Preis unter Ladenpreis netto ${M.chStrasseNetto.toFixed(0)}`);
  chk(M.einfuehrungJahre >= 1 && M.einfuehrungJahre <= 2, `Einführungsangebot ${M.einfuehrungJahre} Jahre (max. 2, sonst Dauerrabatt)`);
  chk(M.preisCostPlus < v("alba_listenpreis_privat_netto"), `Hotel-Cost-Plus ${M.preisCostPlus} unter Privat-Listenpreis ${v("alba_listenpreis_privat_netto")} (Hotelpreis ab 5 Geräten)`);
  chk(M.preisFleet >= M.mindest.fleet, `Fleet ${M.preisFleet} ≥ Mindestpreis ${M.mindest.fleet.toFixed(0)}`);
  chk(M.preisPredict >= M.mindest.predict, `Predict ${M.preisPredict} ≥ Mindestpreis ${M.mindest.predict.toFixed(0)}`);
  chk(M.preisCare >= M.mindest.care, `Care ${M.preisCare} ≥ Mindestpreis ${M.mindest.care.toFixed(0)}`);
  chk(M.careImPaket >= M.mindest.careBundle, `Care-Anteil im Care-Paket ${M.careImPaket} ≥ Mindestpreis bei Bündelung ${M.mindest.careBundle.toFixed(0)}`);
  chk(M.preisFleet <= M.nutzen.fleet && M.preisPredict <= M.nutzen.predict && M.preisCare <= M.nutzen.care, "Alle Featurepreise unter dem Hotelnutzen");
  chk(M.vollEinzel > M.vollFleet && M.vollFleet > M.vollCare, `Staffel fallend: ${M.vollEinzel} > ${M.vollFleet} > ${M.vollCare}`);
  chk(B.eps > 1, `Preisreaktion elastisch (ε = ${B.eps} > 1) – Voraussetzung für Penetration Pricing`);
  chk(M.phasen.g1 >= 0, `Cost-Plus ab ${M.phasen.g1 >= 0 ? jahre[M.phasen.g1] : "–"} (Ende Einführungsangebot)`);
  chk(M.phasen.g3 >= 0 && M.phasen.g4 >= 0, `Features starten im Horizont (Fleet ${M.phasen.g3 >= 0 ? jahre[M.phasen.g3] : "–"}, Care ${M.phasen.g4 >= 0 ? jahre[M.phasen.g4] : "–"})`);
  chk(M.preisCostPlus < M.dbOptimalKurzfristig, `Endpreis ${M.preisCostPlus} unter dem kurzfristig DB-optimalen Preis ${Math.round(M.dbOptimalKurzfristig)} (bewusster Verzicht zugunsten der Diffusion)`);
  M.szenarien.slice(1).forEach((s) => chk(M.plan.barwert > s.barwert, `Penetration schlägt ${s.kurz} im Barwert (${Math.round(M.plan.barwert / 1000)} vs. ${Math.round(s.barwert / 1000)} TCHF)`));
  chk(M.plan.barwert > 0, `Barwert der Penetration positiv (${Math.round(M.plan.barwert / 1000)} TCHF bei ${v("kalkulationszins_bc") * 100} %)`);
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
    console.log("Value Message:", M.rappenProNacht.toFixed(1), "Rp. pro Nacht | Zielsegment", f(M.zielsegment), "Bäder/Jahr = Renovation", f(M.renovationen), "+ Neubau", f(M.neubau), "| DE", M.preisDE, "AT", M.preisAT);
    console.log("Anteil Plan:", M.anteil.map((x) => (x * 100).toFixed(1) + "%").join(" / "));
    M.szenarien.forEach((z) => console.log("  Endanteil", z.kurz.padEnd(12), "Alba", (z.anteil[M.jahre.length - 1] * 100).toFixed(1) + "%", "Konkurrenz", (z.wettbewerb[M.jahre.length - 1] * 100).toFixed(1) + "%"));
    console.log("Bass: p", M.bass.p, "q", M.bass.q, "s_max", M.bass.smax, "ε", M.bass.eps, "δ", M.bass.delta, "| Cost-Plus / G2 Fleet / G3 Care:", ["g1", "g3", "g4"].map((g) => (M.phasen[g] >= 0 ? M.jahre[M.phasen[g]] : "–")).join(" / "), "| kurzfr. DB-opt.", Math.round(M.dbOptimalKurzfristig));
    M.szenarien.forEach((s) => console.log(s.kurz.padEnd(12), "Barwert", f(s.barwert / 1000), "TCHF | Ziel-EBITDA ab", s.zielMargeJahr, "|"));
    M.szenarien.forEach((s) => console.log(s.kurz.padEnd(12), "Preis", s.preise.map((x) => f(x)).join(" / "), "| Absatz", s.vol.map((x) => f(x)).join(" / "), "| kum. TCHF", s.kum.map((x) => f(x / 1000)).join(" / "), "| BE", s.breakEvenJahr));
    console.log("\nPrüfungen:");
    M.checks.forEach((c) => console.log((c.ok ? "  OK    " : "  WARN  ") + c.msg));
  }
} else {
  root.AlbaModell = { berechne };
}
})(this);
