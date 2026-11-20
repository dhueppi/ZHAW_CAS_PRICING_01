from chart_theme import GOLD, INK, NAVY, PALE, TEAL, finish, new_figure


fig, ax = new_figure((13.2, 4.6))
rows = [
    ("Hotelbasis", 790, 250, 540),
    ("Referenzpreis", 1000, 250, 750),
]
for yi, (name, revenue, cogs, residual) in enumerate(rows):
    ax.barh(yi, revenue, color="white", edgecolor="#D8E1E7", height=0.48,
            linewidth=1.1, label="Gesamtpreis" if yi == 0 else None)
    ax.barh(yi, cogs, color=GOLD, height=0.48,
            label="Herstellkosten" if yi == 0 else None)
    ax.barh(yi, residual, left=cogs, color=TEAL if yi == 0 else NAVY,
            height=0.48, label="Rohertrag vor sonstigen Kosten" if yi == 0 else None)
    ax.text(cogs / 2, yi, f"−{cogs}",
            ha="center", va="center", color=NAVY, fontsize=10, fontweight="bold")
    ax.text(cogs + residual / 2, yi,
            f"CHF {residual:,}".replace(",", "’"),
            ha="center", va="center", color="white", fontsize=11, fontweight="bold")
    ax.text(revenue + 28, yi,
            f"Total CHF {revenue:,}".replace(",", "’"),
            ha="left", va="center", color=NAVY, fontsize=10, fontweight="bold")
ax.set_yticks([0, 1], [r[0] for r in rows])
ax.invert_yaxis()
ax.set_xlim(0, 1250)
ax.set_xlabel("CHF je Gerät · netto (Teaminput / Rechenwerte)",
              fontsize=10.5, color=INK)
ax.set_title("Kosten-Wasserfall: der Rest ist noch kein EBITDA",
             loc="left", color=NAVY, fontsize=15, fontweight="bold", pad=12)
ax.grid(axis="x", color=PALE, linewidth=0.8)
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.20),
          frameon=False, ncol=3, fontsize=9)
for spine in ["top", "right", "left"]:
    ax.spines[spine].set_visible(False)
ax.spines["bottom"].set_color("#D8E1E7")
ax.tick_params(axis="y", length=0, colors=INK)
ax.tick_params(axis="x", colors="#657685")
fig.tight_layout()
fig.subplots_adjust(bottom=0.25)
fig.text(0.015, 0.015,
         "Nach dem Rohertrag noch zu decken: Logistik · Garantie · Vertrieb · Installation · Support · Service · Fixkosten (nicht beziffert).",
         color="#B84D48", fontsize=9)
finish(fig, "04_cost_waterfall.png")
