from chart_theme import GOLD, INK, NAVY, TEAL, finish, new_figure


labels = [
    "Geberit Renova\nWC-Set",
    "Designkeramik\nRichtpreis",
    "Alba\nShoppreis",
    "Hotel-Einstieg\nCHF 790 netto*",
    "Alba\nRichtpreis",
    "VitrA V-Care\nComfort",
    "Peer-Median\n4 Modelle",
    "Premium-Peers\nGrohe/Laufen",
]
prices = [279, 790, 899, 854, 1143, 1299, 1694.5, 1999]
colors = [NAVY, NAVY, TEAL, GOLD, TEAL, "#579892", "#859AA6", "#859AA6"]
order = sorted(range(len(prices)), key=lambda idx: prices[idx])
labels = [labels[i] for i in order]
prices = [prices[i] for i in order]
colors = [colors[i] for i in order]

fig, ax = new_figure((13.2, 4.55))
y = range(len(prices))
ax.hlines(y, 0, prices, color=colors, linewidth=3, alpha=0.7)
ax.scatter(prices, y, s=90, color=colors, zorder=3)
for yi, price in zip(y, prices):
    ax.text(price + 35, yi, f"CHF {price:,.0f}".replace(",", "’"),
            va="center", color=NAVY, fontsize=10.5, fontweight="bold")
ax.set_yticks(list(y), labels)
ax.invert_yaxis()
ax.set_xlim(0, 2350)
ax.set_xlabel("Beobachteter / vorgeschlagener Preis, CHF",
              fontsize=11, color=INK, labelpad=10)
ax.set_title("Preisanker-Leiter: vom Standard-WC in die Dusch-WC-Kategorie",
             loc="left", color=NAVY, fontsize=15, fontweight="bold", pad=12)
ax.grid(axis="x", color="#E8EEF1", linewidth=0.8)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)
ax.spines["bottom"].set_color("#D8E1E7")
ax.tick_params(axis="x", colors="#657685")
ax.tick_params(axis="y", length=0, labelsize=10, colors=INK)
fig.text(0.015, 0.015,
         "*Hotelpreis CHF 790 exkl. MwSt. zur Vergleichbarkeit mit 8.1% auf ca. CHF 854 brutto umgerechnet. Andere Punkte sind CH Shop-/Richtpreise; unterschiedliche Preisarten/Ausstattung, kein Hotelangebot.",
         color="#657685", fontsize=8.5)
fig.tight_layout(rect=(0, 0.08, 1, 0.98))
finish(fig, "03_price_ladder.png")
