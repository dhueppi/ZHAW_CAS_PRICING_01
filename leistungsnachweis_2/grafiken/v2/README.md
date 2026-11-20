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
Vollkosten (750), Cost-Plus-Preis (CHF 1'070), Fleet-Aufpreis, Deckungsbeiträge, alle Szenarien, Break-even und das Annahmenregister.
`node model.js` meldet dann zusätzlich `WARN Preisschritte 12.7 % / 20.2 % ≤ 13 %` – also: Zwischenstufe (`preis_stufe_g1`) anpassen oder einen dritten Schritt einplanen.

## Absatzmodell: Bass-Diffusion («Create the Category», Folie 9)

Der Absatz ist kein Eingabewert mehr, sondern wird aus einem **Bass-Diffusionsmodell mit Wettbewerb** berechnet (Bass 1969; Generalized Bass Model; zwei Anbieter teilen ein Potenzial):

```
frei_t        = s_max − Alba_t−1 − Konkurrenz_t−1
ΔAlba         = (p   + q · Alba/s_max)                 · frei · (Preis_t / ZB_t)^(−ε)
ΔKonkurrenz   = (p_W + q · (Konkurrenz + θ·Alba)/s_max) · frei
ZB_t          = Referenzpreis · (1 + δ · (Alba + Konkurrenz)/s_max)
Absatz_t      = Alba_t × Zielsegment-Bäder pro Jahr (~30'000)
```

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
| Penetration (unsere Strategie) | 790 → 890 → Cost-Plus, über Gates | `preis_phase1`, `preis_stufe_g1`, `gate_anteile` |
| Skimming | hoch einsteigen, dann senken | `szenario_skimming_preise` (ein Preis pro Jahr) |
| Konstant | heutiger Privatkunden-Listenpreis netto (CHF 1'000), gehalten | `szenario_konstant_preis` (0 = automatisch `alba_listenpreis_privat_netto`) |

Programmkosten und Feature-Regeln sind in allen Szenarien gleich. Warum die Penetration gewinnt: Ein tiefer Einstieg beschleunigt die Referenzen (q), Alba besetzt mehr vom Markt, bevor die Konkurrenz ihn holt (Endanteil 17.5 % statt 13–15 %), und danach erntet die Penetration über den höheren Preis. Theorie: Bei starkem Imitationseffekt ist ein steigender Preispfad optimal (Dolan & Jeuland 1981).

## Was bewusst Eingabe ist und was gerechnet wird

- **Eingabe (Entscheide/Annahmen):** Einführungspreis 790, Zwischenstufe 890, Predict 99, Care 249, Care-Paket 1'499, Einzelpreise, Take-Rates, Programmkosten, Bass-Parameter, Gate-Schwellen.
- **Gerechnet:** Absatz je Szenario (Bass-Diffusion), Zeitpunkte der Gates, Cost-Plus-Preis (gerundet auf 10), Fleet-Paket (Schwellenpreis unter dem günstigsten Peer netto), DE/AT-Preise (Schwellenpreis aus 95 % des Strassenpreises netto), alle Nutzen-, Margen- und Business-Case-Werte.

## Hinweise

- Texte und Layout stehen in `build_v2.js`; Zahlen dort nie direkt eintippen, sondern über `params.json` / `model.js`.
- Die v1-Skripte im Ordner `grafiken/` (matplotlib + `insert_charts.py`) gehören zur v1 und sind unabhängig davon. `insert_charts.py` nicht auf die v2 anwenden.
