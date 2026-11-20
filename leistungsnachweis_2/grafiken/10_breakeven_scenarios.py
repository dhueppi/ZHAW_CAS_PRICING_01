from chart_theme import GOLD, INK, NAVY, RED, TEAL, finish, new_figure


scenarios = [
    ("Niedrig", 240, 5000, 21, "#78929E"),
    ("Basis", 340, 3500, 11, TEAL),
    ("Hoch", 600, 3000, 5, NAVY),
]
units = list(range(0, 31))

fig, ax = new_figure((13.1, 4.75))
for name, unit_db, fixed, breakeven, color in scenarios:
    profit = [unit_db * n - fixed for n in units]
    fixed_text = f"{fixed:,}".replace(",", "’")
    ax.plot(units, profit, label=f"{name}: DB CHF {unit_db}/Gerät, Fix CHF {fixed_text}",
            color=color, linewidth=2.6)
    ax.scatter([breakeven], [unit_db * breakeven - fixed],
               s=90, color=color, edgecolor="white", zorder=4)
    ax.annotate(f"{breakeven} Geräte", (breakeven, 0),
                xytext=(0, 10), textcoords="offset points",
                ha="center", fontsize=9, color=color, fontweight="bold")
ax.axhline(0, color=RED, linewidth=1.8)
ax.text(29.5, 350, "Break-even", color=RED, fontsize=9.5,
        ha="right", fontweight="bold")
ax.set_xlim(0, 30)
ax.set_ylim(-6000, 15000)
ax.set_xticks(range(0, 31, 5))
ax.set_xlabel("Verkaufte Geräte im Pilotprojekt",
              fontsize=10.5, color=INK)
ax.set_ylabel("Projektbeitrag nach Fixkosten, CHF",
              fontsize=10.5, color=INK)
ax.set_title("Break-even-Szenarien: erforderliche Gerätemenge hängt am DB",
             loc="left", color=NAVY, fontsize=15, fontweight="bold", pad=12)
ax.grid(color="#E8EEF1", linewidth=0.8)
ax.legend(loc="upper left", frameon=False, fontsize=8.6)
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)
ax.spines["left"].set_color("#D8E1E7")
ax.spines["bottom"].set_color("#D8E1E7")
ax.tick_params(colors="#657685")
fig.text(0.015, 0.01,
         "Illustration ohne Ist-Kosten: niedrig DB CHF 240/Fix CHF 5’000; Basis DB CHF 340/Fix CHF 3’500; hoch DB CHF 600/Fix CHF 3’000. Weitere Modellannahmen im Anhang.",
         color="#657685", fontsize=8.8)
fig.tight_layout(rect=(0, 0.08, 1, 0.98))
finish(fig, "10_breakeven_scenarios.png")
