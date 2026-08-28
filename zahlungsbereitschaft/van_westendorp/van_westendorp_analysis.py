"""Van-Westendorp-Analyse für das Excel-Workbook mit mehreren Registerkarten.

Das Skript:
1. exportiert jede Registerkarte als CSV in denselben Ordner,
2. liest das Datenblatt der Van-Westendorp-Analyse,
3. berechnet die relevanten Schnittpunkte,
4. erzeugt ein übersichtliches Diagramm mit Markierungen für die Preise und deren Bedeutung.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from openpyxl import load_workbook


def normalize_header(value: object) -> str:
    """Normalisiert Spaltennamen für einen robusten Vergleich."""
    if value is None:
        return ""
    text = str(value).lower().replace("\n", " ")
    return re.sub(r"[^a-z0-9]", "", text)


def export_all_tabs_to_csv(workbook_path: Path, out_dir: Path) -> None:
    """Exportiert jede Registerkarte als CSV-Datei."""
    out_dir.mkdir(parents=True, exist_ok=True)
    workbook = load_workbook(workbook_path, data_only=True)

    for ws in workbook.worksheets:
        safe_name = re.sub(r"[^a-z0-9]+", "_", ws.title.lower()).strip("_")
        csv_path = out_dir / f"{safe_name}.csv"
        rows = list(ws.iter_rows(values_only=True))
        with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            for row in rows:
                writer.writerow(["" if cell is None else cell for cell in row])
        print(f"CSV exportiert: {csv_path.name}")


def find_index_for_alias(header_row: list[object], aliases: list[str], prefer_percent: bool = False) -> int | None:
    """Finde eine Spaltenposition anhand exakter Aliasnamen; explizite Suffixe wie 'percent' oder 'cumulative' sind erlaubt, kein Teilstring-Match."""
    suffix_aliases = {"percent", "percentage", "cumulative", "cumulated", "count", "counts"}

    for idx, cell in enumerate(header_row):
        if cell is None:
            continue

        text = str(cell).lower()
        if prefer_percent and "%" not in text and "percent" not in text:
            continue
        if (not prefer_percent) and ("%" in text or "percent" in text):
            continue

        normalized_cell = normalize_header(cell)
        for alias in aliases:
            normalized_alias = normalize_header(alias)
            if normalized_cell == normalized_alias:
                return idx

            if normalized_cell.startswith(normalized_alias):
                remainder = normalized_cell[len(normalized_alias):]
                if remainder in suffix_aliases or remainder.startswith("percent") or remainder.startswith("cumulative"):
                    return idx
    return None


def read_van_westendorp_data(workbook_path: Path) -> dict[str, list[float]] | None:
    """Liest das Van-Westendorp-Datenblatt aus und liefert die relevanten Preis-/Prozentwerte."""
    workbook = load_workbook(workbook_path, data_only=True)
    if "2-Data" not in workbook.sheetnames:
        return None

    ws = workbook["2-Data"]
    rows = list(ws.iter_rows(values_only=True))
    if len(rows) < 3:
        return None

    header_row = rows[1]
    data_rows = rows[2:]

    price_idx = find_index_for_alias(header_row, ["price"]) 
    too_cheap_idx = find_index_for_alias(header_row, ["too cheap", "toocheap"], prefer_percent=True)
    cheap_idx = find_index_for_alias(header_row, ["cheap"], prefer_percent=True)
    expensive_idx = find_index_for_alias(header_row, ["expensive"], prefer_percent=True)
    too_expensive_idx = find_index_for_alias(header_row, ["too expensive", "tooexpensive"], prefer_percent=True)
    not_cheap_idx = find_index_for_alias(header_row, ["not cheap", "notcheap"], prefer_percent=True)
    not_expensive_idx = find_index_for_alias(header_row, ["not expensive", "notexpensive"], prefer_percent=True)
    price_ok_idx = find_index_for_alias(header_row, ["price ok", "priceok", "acceptable"]) 

    if any(idx is None for idx in [price_idx, too_cheap_idx, cheap_idx, expensive_idx, too_expensive_idx]):
        return None

    prices: list[float] = []
    too_cheap: list[float] = []
    cheap: list[float] = []
    expensive: list[float] = []
    too_expensive: list[float] = []
    not_cheap: list[float] = []
    not_expensive: list[float] = []
    price_ok: list[float] = []

    for row in data_rows:
        if row is None or not row:
            continue
        try:
            p = float(row[price_idx])
        except (TypeError, ValueError):
            continue

        def safe_float(column_index: int | None, fallback: float = 0.0) -> float:
            if column_index is None or column_index >= len(row):
                return fallback
            try:
                return float(row[column_index])
            except (TypeError, ValueError):
                return fallback

        prices.append(p)
        too_cheap.append(safe_float(too_cheap_idx))
        cheap.append(safe_float(cheap_idx))
        expensive.append(safe_float(expensive_idx))
        too_expensive.append(safe_float(too_expensive_idx))
        not_cheap.append(safe_float(not_cheap_idx))
        not_expensive.append(safe_float(not_expensive_idx))
        price_ok.append(safe_float(price_ok_idx))

    if len(prices) < 2:
        return None

    return {
        "price": prices,
        "too_cheap": too_cheap,
        "cheap": cheap,
        "expensive": expensive,
        "too_expensive": too_expensive,
        "not_cheap": not_cheap,
        "not_expensive": not_expensive,
        "price_ok": price_ok,
    }


def interpolate_intersection(x: np.ndarray, y1: np.ndarray, y2: np.ndarray) -> float | None:
    """Interpoliert den Schnittpunkt zwischen zwei Kurven."""
    delta = y1 - y2
    if np.all(delta == 0):
        return float(np.mean(x))

    for i in range(len(x) - 1):
        d1 = delta[i]
        d2 = delta[i + 1]
        if d1 == 0:
            return float(x[i])
        if d1 * d2 <= 0:
            if d2 == d1:
                return float(x[i])
            frac = abs(d1) / abs(d2 - d1)
            return float(x[i] + frac * (x[i + 1] - x[i]))
    return None


def find_threshold_price(x: np.ndarray, y: np.ndarray, target: float = 50.0) -> float | None:
    """Finde den Preis, an dem eine Kurve den Zielwert in % erreicht."""
    y_pct = np.asarray(y, dtype=float) * 100.0
    delta = y_pct - target
    if np.allclose(delta, 0):
        return float(np.mean(x))

    for i in range(len(x) - 1):
        d1 = delta[i]
        d2 = delta[i + 1]
        if d1 == 0:
            return float(x[i])
        if d1 * d2 <= 0:
            if d2 == d1:
                return float(x[i])
            frac = abs(d1) / abs(d2 - d1)
            return float(x[i] + frac * (x[i + 1] - x[i]))

    return float(x[np.argmin(np.abs(delta))])


def compute_van_westendorp_points(data: dict[str, list[float]]) -> dict[str, float | str]:
    """Berechnet die relevanten Van-Westendorp-Schnittpunkte mit den üblichen Marginalpunkten bei 50 %."""
    price = np.asarray(data["price"], dtype=float)
    too_cheap = np.asarray(data["too_cheap"], dtype=float)
    cheap = np.asarray(data["cheap"], dtype=float)
    expensive = np.asarray(data["expensive"], dtype=float)
    too_expensive = np.asarray(data["too_expensive"], dtype=float)
    not_cheap = np.asarray(data["not_cheap"], dtype=float)
    not_expensive = np.asarray(data["not_expensive"], dtype=float)
    price_ok = np.asarray(data["price_ok"], dtype=float)

    points: dict[str, float | str] = {}

    p_marginal_cheapness = find_threshold_price(price, too_cheap, target=50.0)
    p_optimal = interpolate_intersection(price, 100 * cheap, 100 * expensive)
    p_marginal_expensiveness = find_threshold_price(price, too_expensive, target=50.0)
    p_accept = interpolate_intersection(price, 100 * not_cheap, 100 * not_expensive)
    if p_accept is None and len(price_ok) > 0:
        p_accept = float(price[np.argmax(price_ok)])

    if p_marginal_cheapness is not None:
        points["marginal_cheapness"] = float(p_marginal_cheapness)
    if p_optimal is not None:
        points["optimal"] = float(p_optimal)
    if p_marginal_expensiveness is not None:
        points["marginal_expensiveness"] = float(p_marginal_expensiveness)
    if p_accept is not None:
        points["acceptable"] = float(p_accept)

    if "marginal_cheapness" in points:
        points["marginal_cheapness_meaning"] = "Point of marginal cheapness: Preis, bei dem die Kurve 'too cheap' 50 % erreicht; ab hier wird der Preis als marginal eher noch akzeptabel empfunden."
    if "optimal" in points:
        points["optimal_meaning"] = "Optimaler Preis: Schnittpunkt von 'cheap' und 'expensive'; hier ist der Preis für die meisten Kunden am ehesten passend."
    if "marginal_expensiveness" in points:
        points["marginal_expensiveness_meaning"] = "Point of marginal expensiveness: Preis, bei dem die Kurve 'too expensive' 50 % erreicht; ab hier wird der Preis als marginal zu teuer empfunden."
    if "acceptable" in points:
        points["acceptable_meaning"] = "Acceptable price: Schnittpunkt der 'not cheap' und 'not expensive'-Kurven; der Preisbereich, in dem die meisten Kunden den Preis als vertretbar ansehen."

    return points


def plot_van_westendorp(data: dict[str, list[float]], points: dict[str, float | str], output_path: Path) -> None:
    """Erzeugt die typische Van-Westendorp-Darstellung mit x=Preis und y=Anteil in %."""
    price = np.asarray(data["price"], dtype=float)
    too_cheap = np.asarray(data["too_cheap"], dtype=float) * 100
    cheap = np.asarray(data["cheap"], dtype=float) * 100
    expensive = np.asarray(data["expensive"], dtype=float) * 100
    too_expensive = np.asarray(data["too_expensive"], dtype=float) * 100

    order = np.argsort(price)
    price = price[order]
    too_cheap = too_cheap[order]
    cheap = cheap[order]
    expensive = expensive[order]
    too_expensive = too_expensive[order]

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(price, too_cheap, label='Too cheap', color='tab:blue', linewidth=3.0, zorder=6)
    ax.plot(price, cheap, label='Cheap', color='tab:green', linewidth=2.5, zorder=4)
    ax.plot(price, expensive, label='Expensive', color='tab:orange', linewidth=2.5, zorder=3)
    ax.plot(price, too_expensive, label='Too expensive', color='tab:red', linewidth=2.5, zorder=2)

    labels = {
        "marginal_cheapness": "Point of marginal cheapness",
        "optimal": "Optimal price",
        "marginal_expensiveness": "Point of marginal expensiveness",
        "acceptable": "Acceptable price"
    }

    for key, label in labels.items():
        if key in points:
            value = float(points[key])
            ax.axvline(value, linestyle='--', color='black', linewidth=1.0, alpha=0.7)
            ax.text(value, 8, f"{label}\n{value:.2f}", rotation=90, va='bottom', fontsize=8.5, color='black')

    ax.set_title("Van Westendorp: price sensitivity curve")
    ax.set_xlabel("Preis")
    ax.set_ylabel("Anteil der Befragten (%)")
    ax.set_xlim(price.min() * 0.8, price.max() * 1.05)
    ax.set_ylim(-5, 105)
    ax.grid(True, linestyle='--', alpha=0.4)
    ax.legend(loc='lower right', frameon=True)

    summary_text = (
        "Van Westendorp Interpretation\n"
        f"Marginal cheapness: {points.get('marginal_cheapness', 'n/a')}\n"
        f"Optimal price: {points.get('optimal', 'n/a')}\n"
        f"Marginal expensiveness: {points.get('marginal_expensiveness', 'n/a')}\n"
        f"Acceptable price: {points.get('acceptable', 'n/a')}\n\n"
        f"{points.get('marginal_cheapness_meaning', '')}\n"
        f"{points.get('optimal_meaning', '')}\n"
        f"{points.get('marginal_expensiveness_meaning', '')}\n"
        f"{points.get('acceptable_meaning', '')}"
    )
    ax.text(
        0.02,
        0.98,
        summary_text,
        transform=ax.transAxes,
        fontsize=9,
        va='top',
        bbox={"boxstyle": "round,pad=0.4", "facecolor": "white", "alpha": 0.9},
    )

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close(fig)


def write_summary_csv(points: dict[str, float | str], output_path: Path) -> None:
    """Schreibt eine kompakte Zusammenfassung der Van-Westendorp-Schnittpunkte als CSV."""
    rows = [
        ["metric", "price", "meaning"],
    ]
    for key, label in [
        ("marginal_cheapness", "Point of marginal cheapness"),
        ("optimal", "Optimal price"),
        ("marginal_expensiveness", "Point of marginal expensiveness"),
        ("acceptable", "Acceptable price"),
    ]:
        value = points.get(key)
        if value is None:
            continue
        meaning = points.get(f"{key}_meaning", "")
        rows.append([label, str(value), meaning])

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(rows)


def main() -> None:
    """Hauptroutine: Export der Registerkarten und Van-Westendorp-Analyse."""
    base_dir = Path(__file__).resolve().parent
    workbook_path = base_dir / "Beispiel Van Westendorp Navigationsgerät.xlsx"

    if not workbook_path.exists():
        raise FileNotFoundError(f"Excel-Datei nicht gefunden: {workbook_path}")

    export_all_tabs_to_csv(workbook_path, base_dir)

    data = read_van_westendorp_data(workbook_path)
    if data is None:
        print("Van-Westendorp-Datenblatt '2-Data' konnte nicht gelesen werden.")
        return

    points = compute_van_westendorp_points(data)
    plot_path = base_dir / "van_westendorp_analysis.png"
    summary_path = base_dir / "van_westendorp_summary.csv"

    plot_van_westendorp(data, points, plot_path)
    write_summary_csv(points, summary_path)

    print("\n=== Van Westendorp Ergebnisse ===")
    for key in ("marginal_cheapness", "optimal", "marginal_expensiveness", "acceptable"):
        if key in points:
            print(f"{key}: {points[key]}")

    print(f"Diagramm gespeichert: {plot_path}")
    print(f"Zusammenfassung gespeichert: {summary_path}")


if __name__ == "__main__":
    main()
