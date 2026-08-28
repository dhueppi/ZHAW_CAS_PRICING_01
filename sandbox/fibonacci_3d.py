"""
Fibonacci 3D Punktewolke
========================

Idee:
- X-Achse : Index n der Fibonacci-Folge (0 .. N-1)  -> "Höhe" der Punktewolke
- Y/Z     : Position auf einer Spirale um die X-Achse.
            Der Radius wächst mit sqrt(fib(n)) (sonst würde die
            Punktewolke wegen des exponentiellen Wachstums der
            Fibonacci-Zahlen sofort explodieren), der Winkel wächst
            pro Punkt um den "goldenen Winkel" (~137.5°), das ist
            derselbe Trick, der z.B. bei Sonnenblumenkernen /
            Fibonacci-Spiralen verwendet wird.

Ergebnis: eine 3D-Spirale, deren Form direkt aus der Fibonacci-Folge
und dem goldenen Schnitt abgeleitet ist.
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 (nötig für 3D-Projektion)

N = 20

# ---------------------------------------------------------
# 1) Fibonacci-Folge berechnen
# ---------------------------------------------------------
def fibonacci_sequence(n):
    fib = [0, 1]
    for _ in range(2, n):
        fib.append(fib[-1] + fib[-2])
    return np.array(fib[:n], dtype=float)

fib = fibonacci_sequence(N)

# ---------------------------------------------------------
# 2) 3D-Koordinaten aus der Fibonacci-Folge ableiten
# ---------------------------------------------------------
golden_angle = np.pi * (3 - np.sqrt(5))  # ~2.399963 rad = 137.5°

n = np.arange(N)
theta = n * golden_angle          # Winkel pro Punkt
radius = np.sqrt(fib)             # gedämpfter Radius (sonst Explosion)

x = n                             # Index als "Höhe" / Zeitachse
y = radius * np.cos(theta)
z = radius * np.sin(theta)

# ---------------------------------------------------------
# 3) Visualisierung
# ---------------------------------------------------------
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection="3d")

sc = ax.scatter(x, y, z, c=n, cmap="plasma", s=40, depthshade=True)

# Verbindungslinie, damit die Spiralform sichtbar wird
ax.plot(x, y, z, color="gray", alpha=0.3, linewidth=1)

ax.set_xlabel("Index n")
ax.set_ylabel("Y = √fib(n) · cos(n·φ)")
ax.set_zlabel("Z = √fib(n) · sin(n·φ)")
ax.set_title(f"Fibonacci-Punktewolke im 3D-Raum (N={N})")

cbar = fig.colorbar(sc, ax=ax, shrink=0.6, pad=0.1)
cbar.set_label("Index n")

ax.view_init(elev=22, azim=-60)

plt.tight_layout()
plt.savefig("fibonacci_3d.png", dpi=150)
print("Fertig. PNG gespeichert.")
print("Erste 10 Fibonacci-Werte:", fib[:10].astype(int).tolist())
print(f"fib({N-1}) = {int(fib[-1])}")
