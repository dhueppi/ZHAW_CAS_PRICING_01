"""Umsatzmaximierung bei linearer Preis-Absatz-Funktion.

Modell:
    x(p) = 400 - 0.5 * p

mit:
    p = Preis
    x(p) = nachgefragte Menge

Umsatz:
    U(p) = p * x(p) = p * (400 - 0.5p) = 400p - 0.5p^2

Zur Maximierung wird die Ableitung gebildet:
    U'(p) = 400 - p

Nullsetzen:
    400 - p = 0
    => p* = 400

Einsetzen in x(p):
    x(400) = 200

Maximaler Umsatz:
    U(400) = 400 * 200 = 80'000
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np


def demand(price: np.ndarray | float) -> np.ndarray | float:
    """Nachfragefunktion x(p) = 400 - 0.5p."""
    return 400 - 0.5 * price


def revenue(price: np.ndarray | float) -> np.ndarray | float:
    """Umsatzfunktion U(p) = p * x(p)."""
    return price * demand(price)


def revenue_derivative(price: np.ndarray | float) -> np.ndarray | float:
    """Ableitung des Umsatzes: U'(p) = 400 - p."""
    return 400 - price


def optimum_values() -> tuple[float, float, float]:
    """Gibt den optimalen Preis, die optimale Menge und den maximalen Umsatz zurück."""
    p_star = 400.0
    x_star = demand(p_star)
    u_star = revenue(p_star)
    return p_star, x_star, u_star


def create_plot() -> None:
    """Erzeugt die Visualisierung mit Nachfrage, Umsatz und Ableitung."""
    p = np.linspace(0, 800, 1000)
    x = demand(p)
    u = revenue(p)
    du = revenue_derivative(p)

    p_star, x_star, u_star = optimum_values()

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # Nachfragefunktion
    axes[0].plot(p, x, color="tab:blue", linewidth=2.5, label=r"$x(p)=400-0.5p$")
    axes[0].scatter(p_star, x_star, color="crimson", s=60, zorder=5, label=r"$p^*=400$")
    axes[0].axvline(p_star, color="crimson", linestyle="--", linewidth=1.2, alpha=0.8)
    axes[0].axhline(x_star, color="crimson", linestyle="--", linewidth=1.2, alpha=0.8)
    axes[0].set_title("Nachfragefunktion")
    axes[0].set_xlabel("Preis p")
    axes[0].set_ylabel("Nachfrage x(p)")
    axes[0].grid(True, linestyle="--", alpha=0.4)
    axes[0].legend()

    # Umsatzfunktion
    axes[1].plot(p, u, color="tab:green", linewidth=2.5, label=r"$U(p)=p\cdot x(p)$")
    axes[1].scatter(p_star, u_star, color="crimson", s=60, zorder=5, label=f"Umax = {u_star:.0f}")
    axes[1].axvline(p_star, color="crimson", linestyle="--", linewidth=1.2, alpha=0.8)
    axes[1].axhline(u_star, color="crimson", linestyle="--", linewidth=1.2, alpha=0.8)
    axes[1].set_title("Umsatzfunktion")
    axes[1].set_xlabel("Preis p")
    axes[1].set_ylabel("Umsatz U(p)")
    axes[1].grid(True, linestyle="--", alpha=0.4)
    axes[1].legend()

    # Ableitung
    axes[2].plot(p, du, color="tab:orange", linewidth=2.5, label=r"$U'(p)=400-p$")
    axes[2].axhline(0, color="black", linestyle="-.", linewidth=1)
    axes[2].scatter(p_star, 0, color="crimson", s=60, zorder=5, label=r"$U'(p)=0$")
    axes[2].set_title("Ableitung des Umsatzes")
    axes[2].set_xlabel("Preis p")
    axes[2].set_ylabel("U'(p)")
    axes[2].grid(True, linestyle="--", alpha=0.4)
    axes[2].legend()

    fig.suptitle("Umsatzmaximierung bei linearer Preis-Absatz-Funktion", fontsize=16)
    plt.tight_layout()
    plt.savefig("zahlungsbereitschaft/revenue_maximization.png", dpi=300)
    plt.close(fig)


def main() -> None:
    """Berechnet die optimale Preisstrategie und erzeugt die Diagramme."""
    p_star, x_star, u_star = optimum_values()

    print("=== Umsatzmaximierung ===")
    print("x(p) = 400 - 0.5p")
    print("U(p) = p * x(p) = 400p - 0.5p^2")
    print("U'(p) = 400 - p")
    print()
    print("Nullstelle der Ableitung:")
    print("400 - p = 0")
    print(f"=> p* = {p_star}")
    print(f"x(p*) = 400 - 0.5 * {p_star} = {x_star}")
    print(f"U(p*) = {p_star} * {x_star} = {u_star:.0f}")
    print()
    print("Ergebnis: Der maximale Umsatz liegt bei p* = 400 mit x* = 200 und Umax = 80'000.")

    create_plot()
    print("Diagramm gespeichert unter: zahlungsbereitschaft/revenue_maximization.png")


if __name__ == "__main__":
    main()
