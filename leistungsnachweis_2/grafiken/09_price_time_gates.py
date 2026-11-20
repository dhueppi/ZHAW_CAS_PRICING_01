from chart_theme import GOLD, INK, NAVY, RED, TEAL, finish, new_figure


stages = [0, 1, 2, 3, 4]
price_levels = [854, 1081, 1299, 1399, 1599]
labels = [
    "Pilot\nAlba-Grundgerät",
    "Rollout\nGrundgerät",
    "Fleet\n+ Benachrichtigung",
    "Predict\n+ Prädiktion",
    "Care\n+ Service",
]
gate_x = [1.5, 2.5, 3.5]
gate_names = [
    "G1 · Referenz + positiver DB",
    "G2 · Fleet-WTP + Betrieb",
    "G3 · Kosten + Service-Risiko",
]

fig, ax = new_figure((13.2, 4.65))
ax.step(stages, price_levels, where="post", color=TEAL, linewidth=3)
ax.scatter(stages, price_levels, color=TEAL, s=85, zorder=3)
for x, y, label in zip(stages, price_levels, labels):
    ax.annotate(label, (x, y), xytext=(0, 16 if x % 2 == 0 else -35),
                textcoords="offset points", ha="center", fontsize=9.4,
                color=NAVY, fontweight="bold")
for x, gate in zip(gate_x, gate_names):
    ax.axvline(x, color=GOLD, linestyle="--", linewidth=1.6)
    ax.text(x + 0.035, 710, gate, rotation=90, va="bottom",
            fontsize=8.5, color="#8B651E")
ax.set_xticks(stages, ["Pilot", "Rollout", "Kategorie etabliert",
                       "Feature-Launch", "Service-Launch"])
ax.set_xlim(-0.2, 4.35)
ax.set_ylim(700, 1770)
ax.set_ylabel("CHF · CH-Bruttopreis-Äquivalent, Montage exkl.",
              fontsize=10.5, color=INK)
ax.set_title("Preis-Zeit-Kurve: Featurepreise nur nach Gates freigeben",
             loc="left", color=NAVY, fontsize=15, fontweight="bold", pad=12)
ax.grid(axis="y", color="#E8EEF1", linewidth=0.8)
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)
ax.spines["left"].set_color("#D8E1E7")
ax.spines["bottom"].set_color("#D8E1E7")
ax.tick_params(colors="#657685", labelsize=9)
fig.text(0.015, 0.01,
         "CHF 790 Hotelpreis netto → CHF 854 brutto äquivalent; CHF 1’000 netto → CHF 1’081 brutto. Danach Preis-Hypothesen: Fleet CHF 1’299, Predict CHF 1’399, Care CHF 1’599 brutto. Angebotspakete ändern sich; kein automatischer Preisaufschlag für alle Kunden.",
         color="#657685", fontsize=8.5)
fig.tight_layout(rect=(0, 0.08, 1, 0.98))
finish(fig, "09_price_time_gates.png")
