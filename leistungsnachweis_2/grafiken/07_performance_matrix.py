from matplotlib.colors import ListedColormap
import matplotlib.pyplot as plt

from chart_theme import GOLD, INK, NAVY, PALE, TEAL, WHITE, finish, new_figure


fig, ax = new_figure((13.0, 4.5))
data = [[1, 1, 1],
        [0, 1, 1],
        [0, 0, 1],
        [0, 0, 1]]
cmap = ListedColormap(["#F3F6F8", "#DDF0EC"])
ax.imshow(data, cmap=cmap, vmin=0, vmax=1, aspect="auto")
ax.set_xticks(range(3), ["1–4 Geräte\nEinzelabruf", "ab 5 Geräte\nFleet-Bundle*",
                         "ab 10 Geräte\nCare-Bundle*"])
ax.set_yticks(range(4), ["Alba-Grundgerät", "Benachrichtigung / Fleet",
                         "Prädiktive Diagnose", "3J Service inkl. Teile"])
ax.tick_params(top=True, bottom=False, labeltop=True, labelbottom=False,
               length=0, pad=12, labelsize=11, colors=INK)
for spine in ax.spines.values():
    spine.set_visible(False)
for i, row in enumerate(data):
    for j, value in enumerate(row):
        if i == 0 or value:
            label = "ENTHALTEN"
            color = TEAL
        else:
            label = "OPTIONAL · HÖHERER EINZELPREIS"
            color = "#8B6B2E"
        ax.text(j, i, label, ha="center", va="center", fontsize=8.4,
                fontweight="bold", color=color)
ax.set_xticks([x - 0.5 for x in range(1, 3)], minor=True)
ax.set_yticks([y - 0.5 for y in range(1, 4)], minor=True)
ax.grid(which="minor", color=WHITE, linestyle="-", linewidth=3)
ax.tick_params(which="minor", bottom=False, left=False)
ax.set_title("Leistungsmatrix: mehr Menge schaltet Bundleumfang frei",
             loc="left", color=NAVY, fontsize=15, fontweight="bold", pad=24)
fig.text(0.02, 0.02,
         "*5er-/10er-Schwellen und enthaltene Leistung sind Prüfannahmen. Features sollen bei kleineren Mengen kaufbar bleiben, aber separat zu höherem Stückpreis. Care-Deckung ist noch zu kalkulieren.",
         color="#657685", fontsize=9)
fig.tight_layout(rect=(0, 0.08, 1, 0.95))
finish(fig, "07_performance_matrix.png")
