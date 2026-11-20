from chart_theme import GOLD, INK, NAVY, TEAL, finish, new_figure


names = [
    "AquaClean Alba",
    "VitrA V-Care Comfort",
    "Duravit ME by Starck",
    "Grohe Sensia Arena",
    "Laufen Cleanet Navia",
]
values = [899, 1299, 1390, 1999, 1999]
colors = [TEAL, "#78929E", "#78929E", NAVY, NAVY]

fig, ax = new_figure((13.0, 4.7))
bars = ax.barh(names, values, color=colors, height=0.56, zorder=3)
ax.invert_yaxis()
ax.set_xlim(0, 2350)
ax.set_xlabel("Beobachteter CH-Händlerpreis, CHF (Preise / Sets zu verifizieren)",
              fontsize=10.5, color=INK, labelpad=10)
ax.set_title("Schweizer Preisvergleich: Alba unter den ausgewählten integrierten Peers",
             loc="left", color=NAVY, fontsize=15, fontweight="bold", pad=12)
ax.grid(axis="x", color="#E8EEF1", linewidth=0.8, zorder=0)
for bar, value in zip(bars, values):
    ax.text(value + 42, bar.get_y() + bar.get_height() / 2,
            f"CHF {value:,}".replace(",", "’"), va="center",
            color=NAVY, fontsize=11, fontweight="bold")
ax.axvline(1299, color=GOLD, linestyle="--", linewidth=1.5, alpha=0.9)
ax.text(1308, 4.72, "günstigster direkter Peer: CHF 1’299",
        fontsize=9.2, color="#8C6519", va="bottom")
for spine in ["top", "right", "left"]:
    ax.spines[spine].set_visible(False)
ax.spines["bottom"].set_color("#D8E1E7")
ax.tick_params(axis="y", length=0, colors=INK, labelsize=10)
ax.tick_params(axis="x", colors="#657685")
fig.text(0.015, 0.01,
         "CH Shop-Momentaufnahmen aus Projekt-Marktanalyse. Ausstattung, Preisstatus, MwSt. und Setumfang nicht vollständig harmonisiert; kein Hotelprojektpreis.",
         color="#657685", fontsize=9)
fig.tight_layout(rect=(0, 0.06, 1, 0.98))
finish(fig, "05_peer_prices.png")
