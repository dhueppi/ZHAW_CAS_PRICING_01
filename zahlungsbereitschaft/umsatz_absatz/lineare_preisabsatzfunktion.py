"""Lineare Preis-Absatz-Funktion und Umsatzmaximierung.

Die Nachfragefunktion lautet:
    x(p) = 400 - 0.5 * p

Dabei gilt:
- p: Preis in Geldeinheiten
- x(p): nachgefragte Menge

Ziel:
- Darstellung der Nachfragefunktion
- Berechnung des maximalen Umsatzes U(p) = x(p) * p
- Ableitung der Umsatzfunktion
- Bestimmung der optimalen Preisstrategie mit U'(p) = 0

Die Lösung ist:
    U(p) = (400 - 0.5p) * p = 400p - 0.5p^2
    U'(p) = 400 - p
    U'(p) = 0  =>  p* = 400
    x(400) = 200
    U(400) = 80'000
"""

from __future__ import annotations

import matplotlib

# Use a non-interactive backend so plots can be generated in headless environments.
matplotlib.use("Agg")

import numpy as np
import matplotlib.pyplot as plt


def demand(price: np.ndarray | float) -> np.ndarray | float:
    """Berechnet die lineare Nachfragefunktion x(p) = 400 - 0.5p."""
    return 400 - 0.5 * price


def revenue(price: np.ndarray | float) -> np.ndarray | float:
    """Berechnet den Umsatz U(p) = x(p) * p."""
    return demand(price) * price


def revenue_derivative(price: np.ndarray | float) -> np.ndarray | float:
    """Ableitung der Umsatzfunktion: U'(p) = 400 - p."""
    return 400 - price


def solve_optimum() -> tuple[float, float, float]:
    """Löst das Optimierungsproblem und liefert (Preis, Menge, Umsatz)."""
    p_star = 400.0
    x_star = demand(p_star)
    u_star = revenue(p_star)
    return p_star, x_star, u_star


def create_plots() -> None:
    """Erzeugt saubere Grafiken für Nachfrage und Umsatz."""
    p = np.linspace(0, 800, 1000)
    x = demand(p)
    u = revenue(p)
    du = revenue_derivative(p)

    p_star, x_star, u_star = solve_optimum()

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # 1. Nachfragefunktion x(p)
    axes[0].plot(p, x, color="tab:blue", linewidth=2.5, label=r"$x(p)=400-0.5p$")
    axes[0].scatter(p_star, x_star, color="red", zorder=5, label=f"Optimum: p*={p_star}")
    axes[0].axvline(p_star, color="red", linestyle="--", linewidth=1.2, alpha=0.8)
    axes[0].axhline(x_star, color="red", linestyle="--", linewidth=1.2, alpha=0.8)
    axes[0].set_title("Preis-Absatz-Funktion")
    axes[0].set_xlabel("Preis p")
    axes[0].set_ylabel("Nachfrage x(p)")
    axes[0].grid(True, linestyle="--", alpha=0.4)
    axes[0].legend()

    # 2. Umsatzfunktion U(p)
    axes[1].plot(p, u, color="tab:green", linewidth=2.5, label=r"$U(p)=x(p)\cdot p$")
    axes[1].scatter(p_star, u_star, color="red", zorder=5, label=f"Maximaler Umsatz: {u_star:.0f}")
    axes[1].axvline(p_star, color="red", linestyle="--", linewidth=1.2, alpha=0.8)
    axes[1].axhline(u_star, color="red", linestyle="--", linewidth=1.2, alpha=0.8)
    axes[1].set_title("Umsatzfunktion")
    axes[1].set_xlabel("Preis p")
    axes[1].set_ylabel("Umsatz U(p)")
    axes[1].grid(True, linestyle="--", alpha=0.4)
    axes[1].legend()

    # 3. Ableitung U'(p)
    axes[2].plot(p, du, color="tab:orange", linewidth=2.5, label=r"$U'(p)=400-p$")
    axes[2].axhline(0, color="black", linewidth=1, linestyle="-.")
    axes[2].scatter(p_star, 0, color="red", zorder=5, label=f"Nullstelle: p*={p_star}")
    axes[2].set_title("Ableitung der Umsatzfunktion")
    axes[2].set_xlabel("Preis p")
    axes[2].set_ylabel("U'(p)")
    axes[2].grid(True, linestyle="--", alpha=0.4)
    axes[2].legend()

    fig.suptitle("Lineare Preis-Absatz-Funktion und Umsatzmaximierung", fontsize=16)
    plt.tight_layout()
    plt.savefig("zahlungsbereitschaft/lineare_preisabsatzfunktion_und_umsatz.png", dpi=300)
    plt.close(fig)


def main() -> None:
    """Hauptfunktion: berechnet die Kennzahlen und erzeugt die Plots."""
    p_star, x_star, u_star = solve_optimum()

    print("=== Lineare Preis-Absatz-Funktion ===")
    print("x(p) = 400 - 0.5 * p")
    print()
    print("=== Umsatzfunktion ===")
    print("U(p) = x(p) * p = (400 - 0.5p) * p = 400p - 0.5p^2")
    print()
    print("=== Ableitung ===")
    print("U'(p) = 400 - p")
    print()
    print("=== Optimale Preisstrategie ===")
    print("U'(p) = 0 => 400 - p = 0 => p* = 400")
    print(f"x(p*) = 400 - 0.5 * {p_star} = {x_star}")
    print(f"U(p*) = {p_star} * {x_star} = {u_star:.0f}")
    print()
    print("Der maximale Umsatz liegt bei einem Preis von 400 und einer Menge von 200.")
    print("Der maximale Umsatz beträgt 80'000.")

    create_plots()
    print("\nPlots wurden als PNG-Datei gespeichert: zahlungsbereitschaft/lineare_preisabsatzfunktion_und_umsatz.png")


if __name__ == "__main__":
    main()
