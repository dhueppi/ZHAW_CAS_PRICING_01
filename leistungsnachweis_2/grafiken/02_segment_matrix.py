from chart_theme import GOLD, INK, NAVY, PALE, TEAL, WHITE, finish, new_figure


fig, ax = new_figure((12.6, 4.7))
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axvline(5, color=WHITE, linewidth=3)
ax.axhline(5, color=WHITE, linewidth=3)
ax.fill_between([0, 5], 0, 5, color="#F1F4F6")
ax.fill_between([5, 10], 0, 5, color="#E7EFF1")
ax.fill_between([0, 5], 5, 10, color="#F8F3E8")
ax.fill_between([5, 10], 5, 10, color="#DCEFEB")

ax.text(0.35, 9.55, "2 · Kleine Einzelhäuser", color=NAVY,
        fontsize=13, fontweight="bold", va="top")
ax.text(0.35, 8.85, "Gästeerlebnis hoch · Flottenhebel tief\nBoutique / einzelnes Wellnesshotel",
        color=INK, fontsize=10.5, va="top")
ax.text(5.35, 9.55, "1 · Zielsegment für den Pilot", color=TEAL,
        fontsize=13, fontweight="bold", va="top")
ax.text(5.35, 8.85,
        "Gästeerlebnis hoch · Flottenhebel hoch\nGehobene Business-/Wellnessketten,\nNeubau oder Renovation",
        color=INK, fontsize=10.5, va="top")
ax.text(0.35, 4.55, "4 · Preis-/Standardfokus", color=NAVY,
        fontsize=13, fontweight="bold", va="top")
ax.text(0.35, 3.90, "Gästeerlebnis tief · Flottenhebel tief\nBudgethotel / einzelnes Standardzimmer",
        color=INK, fontsize=10.5, va="top")
ax.text(5.35, 4.55, "3 · Ketten mit Betriebshebel", color=NAVY,
        fontsize=13, fontweight="bold", va="top")
ax.text(5.35, 3.90, "Gästeerlebnis moderat · Flottenhebel hoch\nStandardisierte Business-/Select-Service-Ketten",
        color=INK, fontsize=10.5, va="top")

ax.scatter([7.5], [7.0], s=210, color=TEAL, edgecolor=WHITE,
           linewidth=1.4, zorder=4)
ax.annotate("Priorität", (7.5, 7.0), xytext=(8.05, 6.65),
            color=TEAL, fontsize=11, fontweight="bold",
            arrowprops={"arrowstyle": "->", "color": TEAL, "lw": 1.5})
ax.set_xlabel("Potenzial für gebündelten Betrieb / Flottenservice  →",
              fontsize=11, color=INK, labelpad=10)
ax.set_ylabel("Potenzial für Gäste-Differenzierung  →",
              fontsize=11, color=INK, labelpad=8)
ax.set_xticks([])
ax.set_yticks([])
for spine in ax.spines.values():
    spine.set_visible(False)
ax.set_title("Hotel-Segmentierung nach Wertbeitrag und Bündelbarkeit",
             loc="left", color=NAVY, fontsize=15, fontweight="bold", pad=12)
fig.text(0.015, 0.02,
         "Strategische Segmenthypothesen aus Kickoff/Teaminput; keine quantitative Marktsegmentierung.",
         color="#657685", fontsize=9)
fig.tight_layout(rect=(0, 0.06, 1, 0.98))
finish(fig, "02_segment_matrix.png")
