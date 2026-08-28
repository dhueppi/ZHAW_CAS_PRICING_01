"""Analyse der Korrelation zwischen Number of promotions und Money spent.

Das Skript liest die Excel-Datei "Beispiel Preis-Absatz-Funktion.xlsx" aus dem
Projektordner, identifiziert das Sheet "Case 1" und analysiert die beiden
Spalten:
- Number of promotions
- $ spent

Es berechnet den Pearson-Korrelationskoeffizienten und erstellt ein
Scatter-Diagramm mit linearer Trendlinie und Regressionsgleichung.
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
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def resolve_column_index(header_map: dict[str, int], aliases: list[str]) -> int | None:
    """Sucht eine passende Spalte in den Headern anhand von Alias-Liste."""
    for alias in aliases:
        if alias in header_map:
            return header_map[alias]

    for key, index in header_map.items():
        if any(alias in key for alias in aliases):
            return index

    return None


def _read_sheet_data(file_path: Path, sheet_name: str, x_aliases: list[str], y_aliases: list[str]) -> tuple[list[float], list[float], str, str]:
    """Liest ein bestimmtes Sheet und liefert numerische X/Y-Werte sowie Spaltennamen."""
    workbook = load_workbook(file_path, data_only=True)
    if sheet_name not in workbook.sheetnames:
        raise ValueError(f"Das Sheet '{sheet_name}' wurde in der Excel-Datei nicht gefunden.")

    sheet = workbook[sheet_name]
    rows = list(sheet.iter_rows(values_only=True))
    if not rows:
        raise ValueError(f"Das Excel-Sheet '{sheet_name}' ist leer.")

    header_row = rows[0]
    header_map = {normalize_header(cell): i for i, cell in enumerate(header_row)}

    x_col = resolve_column_index(header_map, x_aliases)
    y_col = resolve_column_index(header_map, y_aliases)

    if x_col is None or y_col is None:
        raise ValueError(
            f"Die relevanten Spalten fuer '{sheet_name}' wurden nicht gefunden. "
            f"Erwartet x={x_aliases}, y={y_aliases}."
        )

    x_values: list[float] = []
    y_values: list[float] = []

    for row in rows[1:]:
        if row is None:
            continue

        x_value = row[x_col]
        y_value = row[y_col]

        try:
            x = float(x_value)
            y = float(y_value)
        except (TypeError, ValueError):
            continue

        x_values.append(x)
        y_values.append(y)

    if len(x_values) < 2:
        raise ValueError(f"In '{sheet_name}' wurden zu wenige gültige Datenpunkte gefunden.")

    x_header = header_row[x_col] if x_col < len(header_row) else "X"
    y_header = header_row[y_col] if y_col < len(header_row) else "Y"
    return x_values, y_values, str(x_header), str(y_header)


def pearson_correlation(x: list[float], y: list[float]) -> float:
    """Berechnet den Pearson-Korrelationskoeffizienten."""
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)
    corr = np.corrcoef(x_arr, y_arr)[0, 1]
    if np.isnan(corr):
        raise ValueError("Korrelation konnte nicht berechnet werden; vermutlich sind die Daten konstant.")
    return float(corr)


def fit_linear_trend(x: list[float], y: list[float]) -> tuple[float, float, np.ndarray]:
    """Fit einer linearen Trendlinie y = a*x + b nach Least Squares."""
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)
    slope, intercept = np.polyfit(x_arr, y_arr, 1)
    trend = slope * x_arr + intercept
    return float(slope), float(intercept), trend


def r_squared(x: list[float], y: list[float], slope: float, intercept: float) -> float:
    """Berechnet R^2 fuer die lineare Regression."""
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)
    y_hat = slope * x_arr + intercept
    ss_res = np.sum((y_arr - y_hat) ** 2)
    ss_tot = np.sum((y_arr - np.mean(y_arr)) ** 2)
    if ss_tot == 0:
        return 1.0
    return float(1 - ss_res / ss_tot)


def create_scatter_plot(
    x: list[float],
    y: list[float],
    corr: float,
    slope: float,
    intercept: float,
    x_label: str,
    y_label: str,
    output_path: Path,
    title: str,
) -> None:
    """Erzeugt einen Scatter-Plot mit Least-Squares-Trendlinie, Residuen-Quadraten und Textbox."""
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)

    fit_x = np.linspace(x_arr.min(), x_arr.max(), 200)
    fit_y = slope * fit_x + intercept
    y_hat = slope * x_arr + intercept
    residuals = y_arr - y_hat
    ss_res = np.sum(residuals ** 2)
    ss_tot = np.sum((y_arr - np.mean(y_arr)) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot != 0 else 1.0

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.scatter(x_arr, y_arr, color="royalblue", s=60, alpha=0.8, label="Datenpunkte")
    ax.plot(fit_x, fit_y, color="darkorange", linewidth=2.5, label="Least-Squares-Trendlinie")

    for xi, yi, yi_hat in zip(x_arr, y_arr, y_hat):
        ax.vlines(xi, ymin=min(yi, yi_hat), ymax=max(yi, yi_hat), color="gray", linestyle="--", linewidth=0.7, alpha=0.5)
        ax.scatter(xi, yi_hat, color="darkorange", s=12, alpha=0.7, zorder=2)

    equation = f"y = {slope:.3f}x + {intercept:.3f}"
    info_text = (
        f"Least Squares\n"
        f"r = {corr:.3f}\n"
        f"R^2 = {r2:.3f}\n"
        f"{equation}\n\n"
        f"Interpretation:\n"
        f"- r > 0: positiver Zusammenhang\n"
        f"- 0 < R^2 < 1: Anteil der erklärten Varianz\n"
        f"- R^2 nahe 1: starke Anpassung\n"
        f"- R^2 nahe 0: schwache Anpassung"
    )
    ax.text(
        0.05,
        0.95,
        info_text,
        transform=ax.transAxes,
        fontsize=10,
        va="top",
        bbox={"boxstyle": "round,pad=0.45", "facecolor": "white", "alpha": 0.94},
    )

    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend(frameon=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close(fig)


def export_cleaned_csv(x_values: list[float], y_values: list[float], x_label: str, y_label: str, output_path: Path) -> None:
    """Exportiert die bereinigten Daten als CSV-Datei für die tabellarische Anzeige im VS Code."""
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([x_label, y_label])
        for x, y in zip(x_values, y_values):
            writer.writerow([x, y])


def main() -> None:
    """Hauptfunktion der Analyse fuer mehrere Register einer Excel-Datei."""
    base_dir = Path(__file__).resolve().parent
    excel_candidates = [
        base_dir / "Beispiel Preis-Absatz-Funktion.xlsx",
        base_dir.parent / "Beispiel Preis-Absatz-Funktion.xlsx",
    ]
    excel_file = next((path for path in excel_candidates if path.exists()), excel_candidates[0])

    if not excel_file.exists():
        raise FileNotFoundError(
            "Die Excel-Datei 'Beispiel Preis-Absatz-Funktion.xlsx' wurde weder im "
            "aktuellen Ordner noch im übergeordneten Ordner gefunden."
        )

    workbook = load_workbook(excel_file, data_only=True)
    sheet_configs = [
        ("Case 1", ["numberofpromotions", "promotions"], ["spent", "moneyspent"]),
        ("Case 2", ["price"], ["unitspurchased", "units"]),
    ]

    print("=== Excel-Analyse fuer mehrere Register ===")
    print(f"Datei: {excel_file}")

    for sheet_name, x_aliases, y_aliases in sheet_configs:
        if sheet_name not in workbook.sheetnames:
            print(f"- Sheet '{sheet_name}' nicht gefunden, übersprungen.")
            continue

        try:
            x_values, y_values, x_label, y_label = _read_sheet_data(excel_file, sheet_name, x_aliases, y_aliases)
        except ValueError as exc:
            print(f"- {sheet_name}: {exc}")
            continue

        corr = pearson_correlation(x_values, y_values)
        slope, intercept, _ = fit_linear_trend(x_values, y_values)
        r2 = r_squared(x_values, y_values, slope, intercept)

        safe_name = sheet_name.lower().replace(" ", "_")
        output_file = base_dir / f"{safe_name}_scatter.png"
        csv_file = base_dir / f"{safe_name}_clean.csv"

        export_cleaned_csv(x_values, y_values, x_label, y_label, csv_file)
        create_scatter_plot(
            x_values,
            y_values,
            corr,
            slope,
            intercept,
            x_label,
            y_label,
            output_file,
            f"{sheet_name}: {x_label} vs. {y_label}",
        )

        print(f"\n=== {sheet_name} ===")
        print(f"Anzahl gültiger Beobachtungen: {len(x_values)}")
        print(f"Pearson-Korrelation r = {corr:.4f}")
        print(f"R^2 = {r2:.4f}")
        print(f"Trendlinie: y = {slope:.4f} * x + {intercept:.4f}")
        print(f"Scatter-Plot: {output_file}")
        print(f"CSV: {csv_file}")


if __name__ == "__main__":
    main()
