from chart_theme import GOLD, INK, NAVY, RED, TEAL, finish, new_figure


features = ["Fleet-Benachrichtigung", "Prädiktive Diagnose", "3J-Servicepaket"]
wts = [100.00, 64.29, 228.57]
wtp_proxy = [201.67, 100 / 1.081, 200 / 1.081]

fig, ax = new_figure((13.2, 4.7))
positions = [0, 1, 2]
width = 0.32
ax.bar([p - width / 2 for p in positions], wts, width,
       color=NAVY, label="WTS: angenommener Kostenfloor / (1−30%)")
ax.bar([p + width / 2 for p in positions], wtp_proxy, width,
       color=TEAL, label="WTP-Proxy: Team-/Wettbewerbspreis")
for p, val in zip([p - width / 2 for p in positions], wts):
    ax.text(p, val + 5, f"{val:.0f}", ha="center", color=NAVY,
            fontsize=10, fontweight="bold")
for p, val in zip([p + width / 2 for p in positions], wtp_proxy):
    ax.text(p, val + 5, f"{val:.0f}", ha="center", color=TEAL,
            fontsize=10, fontweight="bold")
ax.annotate("Lücke ca. CHF 44 netto",
            xy=(2 + width / 2, wtp_proxy[2]), xytext=(1.35, 295),
            color=RED, fontsize=10, fontweight="bold",
            arrowprops={"arrowstyle": "->", "color": RED})
ax.set_xticks(positions, features)
ax.set_ylabel("Einmaliger CHF pro Gerät, netto (Hypothesen)",
              fontsize=10.5, color=INK)
ax.set_ylim(0, 330)
ax.set_title("Willingness to Sell vs. WTP-Proxy – Feature für Feature",
             loc="left", color=NAVY, fontsize=15, fontweight="bold", pad=12)
ax.grid(axis="y", color="#E8EEF1", linewidth=0.8)
ax.legend(loc="upper left", frameon=False, fontsize=9.2)
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)
ax.spines["left"].set_color("#D8E1E7")
ax.spines["bottom"].set_color("#D8E1E7")
ax.tick_params(colors="#657685", labelsize=9.5)
fig.text(0.015, 0.01,
         "WTS ist hier eine modellierte Mindestpreis-Hürde: angenommene Featurekosten CHF 70/45/160 netto ÷ (1−30% Zielmarge). WTP ist kein gemessener Kundenwert: CHF 201.67 Wettbewerbsresidual, CHF 100/200 brutto Teamhypothesen, auf netto umgerechnet.",
         color="#657685", fontsize=8.6)
fig.tight_layout(rect=(0, 0.08, 1, 0.98))
finish(fig, "06_wts_wtp.png")
