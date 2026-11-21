# LN2 v2 – Slidedoc aus zentralen Parametern

Alle Zahlen im Deck `LN2_AquaClean_Alba_Hotel_Preiskonzept_2026_v2.pptx` kommen aus **einer** Datei: `params.json`.

| Datei | Aufgabe |
|---|---|
| `params.json` | **Einzige Stelle für Eingabewerte** (Kosten, Preise, Volumen, Annahmen). Jeder Wert hat `wert`, `label` und `typ` (Fakt / Teaminput / Annahme). |
| `model.js` | Rechnet alles Abgeleitete: Vollkosten, Cost-Plus-Preis, Fleet-Preis (knapp unter dem günstigsten Peer), Mindestpreise, Hotelnutzen, Value Message, Business Case, DE/AT-Preise, Pay-per-Flush. Enthält Konsistenzprüfungen. |
| `tool.html` | **Parameter-Tool im Browser**: alle Parameter mit Schiebereglern, alle Grafiken des Decks live, Konsistenzprüfungen, Änderungsliste, Export als SVG/PNG. Rechnet mit demselben `model.js`. |
| `gui_server.js` | Kleiner lokaler Server für das Tool (ohne Zusatzpakete). Ermöglicht «Speichern» (mit Backup `params.backup.json`) und «Speichern + Deck bauen». |
| `build_v2.js` | Baut das Deck (10 Hauptfolien + 5 Anhänge). Alle Diagramme sind native PowerPoint-Diagramme. Das Annahmenregister (Anhang A3) wird direkt aus `params.json` erzeugt. |

## Ablauf

```bash
cd grafiken/v2
npm install          # einmalig, installiert pptxgenjs
node model.js        # Kennzahlen anzeigen und Prüfungen laufen lassen
node build_v2.js     # schreibt das Deck in den Ordner leistungsnachweis_2
```

Optional mit eigenem Ausgabepfad: `node build_v2.js /pfad/zum/deck.pptx`

## Parameter-Tool (GUI)

```bash
cd grafiken/v2
node gui_server.js        # oder: npm run gui
```

Dann **http://localhost:8080** im Browser öffnen.

- Ganz oben: **★ Favoriten** – die wichtigsten Stellschrauben (Start: Einführungspreis, Referenzeffekt q, Preisreaktion ε, Konkurrenz p_W, Herstellkosten). Mit ☆/★ neben jedem Parameter hinzufügen oder entfernen; «Speichern» schreibt die Auswahl als `_favoriten` in `params.json`.
- Darunter: alle übrigen Parameter nach Gruppen, mit Suche. Geänderte Werte sind gelb markiert; die Badges zeigen Fakt / Teaminput / Annahme.
- Rechts: Kennzahlen mit Veränderung zum gespeicherten Stand, Konsistenzprüfungen, alle Grafiken der Folien 2, 4–9 und Anhang A4.
- **Speichern** schreibt `params.json` (das alte File landet in `params.backup.json`). **Speichern + Deck bauen** erzeugt danach sofort das PowerPoint neu.
- Ohne Server (tool.html per Doppelklick): params.json über «params.json laden» wählen; Änderungen dann mit «params.json herunterladen» sichern und die Datei in `grafiken/v2` ersetzen.

**Erweitern:** Ein neuer Parameter in `params.json` (Format `{ "wert": …, "label": …, "typ": … }`) erscheint automatisch im Tool unter «Weitere Parameter». In `model.js` verwenden, dann ist er im Deck und im Tool wirksam. Für einen Schieberegler mit passendem Bereich den Eintrag in `GROUPS` oben in `tool.html` ergänzen; neue Grafiken analog zu den bestehenden Karten in `render()`.

## Beispiel: Herstellkosten ändern

In `params.json` `"herstellkosten": { "wert": 250 … }` auf 300 setzen. Danach ändern sich automatisch:
Vollkosten (650), Cost-Plus-Preis (CHF 1'080), Fleet-Aufpreis, Deckungsbeiträge, alle Szenarien, Break-even und das Annahmenregister.
Preispfad Penetration: Einführungsangebot = Listenpreis × (1 − `einfuehrung_rabatt`) während `einfuehrung_jahre` (Kalender), danach Cost-Plus = Projektpreis ab 5 Geräten (`costplus_zuschlag`); Fleet ab Gate G2, Care ab Gate G3. Feature-Preise = `wertabschoepfung_features` × Hotelnutzen (Schwellenpreise), Fleet-Paket höchstens knapp unter dem günstigsten Peer; Care-Paket = Summe × (1 − `buendelrabatt_care`).

## Absatzmodell: Bass-Diffusion («Create the Category», Folie 9)

Der Absatz ist kein Eingabewert mehr, sondern wird aus einem **Bass-Diffusionsmodell mit Wettbewerb** berechnet (Bass 1969; Generalized Bass Model; zwei Anbieter teilen ein Potenzial):

```
frei_t        = s_max − Alba_t−1 − Konkurrenz_t−1
ZB_t          = Referenzpreis · (1 + δ · (Alba + θ·Konkurrenz)/s_max)     (v. a. Albas eigene Referenzen)
frei_Alba     = s_max · min(1, (ZB_t / Preis_t)^ε) − Alba − Konkurrenz     (preisabhängiges Potenzial, Kalish 1985)
ΔAlba         = (p   + q · Alba/s_max)                 · frei_Alba · min(z_max, (Preis_t / ZB_t)^(−ε))
ΔKonkurrenz   = (p_W + q · (Konkurrenz + θ·Alba)/s_max) · frei
Absatz_t      = Alba_t × Zielsegment-Bäder pro Jahr (~30'000)
```

Jedes Preisszenario wird **eigenständig** gerechnet (Entweder-oder: Geberit fährt genau eine Strategie). Ein Preis über der Zahlungsbereitschaft bremst das Tempo **und** verkleinert das erreichbare Potenzial; ein Preis unter der Zahlungsbereitschaft beschleunigt, begrenzt auf `bass_preiseffekt_max` (×1.5).

Wer schneller Referenzen aufbaut, besetzt das Potenzial, bevor die Konkurrenz es holt (First-Mover). Ein hoher Einstiegspreis bremst Alba und überlässt der Konkurrenz den Markt – dauerhaft.

| Parameter | Bedeutung |
|---|---|
| `bass_p` | Innovatoren: Hotels, die ohne Vorbild kaufen (kalibriert auf ~100 Geräte im Pilotjahr) |
| `bass_q` | Imitatoren: Kauf wegen Referenzen – der eigentliche «Create the Category»-Effekt |
| `bass_smax` | Sättigung: maximaler Alba-Anteil (30 % = Hotelstars-Schwelle) |
| `bass_eps` | Preisreaktion der Diffusion (ε > 1 = elastisch) |
| `bass_delta` | Zahlungsbereitschaft wächst mit der Durchdringung, nicht mit dem Kalender |
| `bass_referenzpreis` | Preis, bei dem p und q unverändert wirken |
| `wettbewerb_p` | Konkurrenz gewinnt Hotels auch ohne Alba (TOTO, VitrA, Duravit …) |
| `wettbewerb_spillover` | θ: Anteil von Albas Kategorieaufbau, der der Konkurrenz zugutekommt |
| `risiko_faktor_imitation` | Risiko-Szenario: Referenzeffekt q × Faktor |

**Penetration = Preisstufen über Gates:** Die Penetration erhöht den Preis, sobald der Anteil des Vorjahres das nächste Gate erreicht (`gate_anteile`: G1 → CHF 890, G2 → Cost-Plus). Fleet startet bei G3, Predict/Care bei G4 (frühestens `fleet_ab_jahr` / `wert_ab_jahr`). Höchstens ein Schritt pro Jahr.

**Drei Preisszenarien** (Grafiken «Preis über Zeit» und «Absatz über Zeit»):

| Szenario | Preis Grundgerät | Parameter |
|---|---|---|
| Penetration (unsere Strategie) | 700 (Liste −30 %, 2 Jahre) → 900 (Projektpreis) → + Fleet (G2) → + Care (G3) | `einfuehrung_rabatt`, `einfuehrung_jahre`, `costplus_zuschlag`, `wertabschoepfung_features`, `gate_anteile` |
| Skimming | hoch einsteigen, dann senken | `szenario_skimming_preise` (ein Preis pro Jahr) |
| Konstant | heutiger Privatkunden-Listenpreis netto (CHF 1'000), gehalten | `szenario_konstant_preis` (0 = automatisch `alba_listenpreis_privat_netto`) |

Programmkosten und Feature-Regeln sind in allen Szenarien gleich. Programmkosten enthalten nur **zusätzliche** Kosten (Relevanzprinzip): `b2b_pm_anzahl` (1 B2B-PM pro Land) × `b2b_pm_kosten_fte` × `b2b_pm_zeitanteil` (20 %) plus die Positionen `prog_*` (Referenzprogramm, Schulungen, Marktforschung, Fleet/Care). Cost-Plus rechnet dagegen bewusst mit Vollkosten inkl. geteiltem Vertrieb (`gemeinkosten_pro_geraet`).

**Kanal, Kannibalisierung, Barwert:** Geberit erhält beim Grundgerät nur `kanal_nettoanteil` (70 %) des Hotelpreises; Features laufen direkt (`kanal_nettoanteil_features` = 100 %). Cost-Plus = Vollkosten × (1 + `costplus_zuschlag`) ÷ Kanalanteil (klassisches Cost-Plus mit Gewinnzuschlag). Pro verkauftem Alba fällt `kannibalisierung_anteil` × `db_geberit_keramik` an entgangenem Geberit-Keramik-DB weg. Szenarien werden über den Barwert (`kalkulationszins_bc`, 8 %) verglichen. Warum die Penetration gewinnt: Ein tiefer Einstieg beschleunigt die Referenzen (q), Alba besetzt mehr vom Markt, bevor die Konkurrenz ihn holt (Endanteil 17.5 % statt 13–15 %), und danach erntet die Penetration über den höheren Preis. Theorie: Bei starkem Imitationseffekt ist ein steigender Preispfad optimal (Dolan & Jeuland 1981).

## DACH-Ausrichtung (Markt und Ländermix)

- **Marktvolumen:** Zielsegment-Bäder pro Jahr = Renovation (Hotelzimmer DE + AT + CH × 4/5★-Anteil ÷ Renovationszyklus) + Neubau (Eröffnungen × 4/5★-Anteil × Ø Zimmer pro Projekt). Quellen in `params.json`.
- **Ländermix im Business Case:** Volumen nach Zimmerbestand gewichtet; DE/AT zu lokalen Preisen (`preisDE`/`preisAT` in EUR × `wechselkurs_eur_chf`). Daraus `preisfaktorDACH` (Ø Erlös in % des CH-Preises), der auf Gerät und Features wirkt. Der Preispfad selbst ist als CH-Listenpreis angegeben; DE/AT folgen ihm proportional.

## Was bewusst Eingabe ist und was gerechnet wird

- **Eingabe (Entscheide/Annahmen):** Einführungsrabatt 30 % und Dauer 2 Jahre, Cost-Plus-Zuschlag, Wertabschöpfung Features 60 %, Bündelrabatt, Einzelpreise, Take-Rates, Programmkosten, Bass-Parameter, Gate-Schwellen.
- **Gerechnet:** Absatz je Szenario (Bass-Diffusion), Zeitpunkte der Gates, Cost-Plus-Preis (gerundet auf 10), Fleet-Paket (Schwellenpreis unter dem günstigsten Peer netto), DE/AT-Preise (Schwellenpreis aus 95 % des Strassenpreises netto), alle Nutzen-, Margen- und Business-Case-Werte.

## Hinweise

- Texte und Layout stehen in `build_v2.js`; Zahlen dort nie direkt eintippen, sondern über `params.json` / `model.js`.
- Die v1-Skripte im Ordner `grafiken/` (matplotlib + `insert_charts.py`) gehören zur v1 und sind unabhängig davon. `insert_charts.py` nicht auf die v2 anwenden.
