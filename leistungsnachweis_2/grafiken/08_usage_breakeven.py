from chart_theme import GOLD, INK, NAVY, RED, TEAL, WHITE, finish, new_figure


device_and_installation = 400
life_years = 5
service_reserve_per_year = 45
connectivity_admin_per_year = 25
price_per_flush = 0.20
annualized_total_cost = (
    device_and_installation / life_years
    + service_reserve_per_year
    + connectivity_admin_per_year
)
break_even_uses = annualized_total_cost / price_per_flush

fig, ax = new_figure((13.0, 4.65))
uses = list(range(0, 2001, 50))
revenue = [u * price_per_flush for u in uses]
cost = [annualized_total_cost for _ in uses]
ax.plot(uses, revenue, color=TEAL, linewidth=3,
        label=f"Pay-per-Flush-Erlös · CHF {price_per_flush:.2f} je Nutzung")
ax.plot(uses, cost, color=NAVY, linewidth=2.6,
        label=f"Annualisierte Gesamtkosten · CHF {annualized_total_cost:.0f}/Jahr")
ax.fill_between(uses, revenue, cost, where=[r < c for r, c in zip(revenue, cost)],
                color="#FBEAE8", alpha=0.7, label="Unter Break-even")
ax.scatter([break_even_uses], [annualized_total_cost], color=GOLD, s=120,
           edgecolor=WHITE, zorder=4)
ax.axvline(break_even_uses, color=GOLD, linestyle="--", linewidth=1.5)
ax.annotate(f"Break-even ≈ {break_even_uses:.0f} Nutzungen/Jahr",
            xy=(break_even_uses, annualized_total_cost),
            xytext=(break_even_uses + 260, annualized_total_cost + 65),
            color="#8B651E", fontsize=10, fontweight="bold",
            arrowprops={"arrowstyle": "->", "color": GOLD})
ax.set_xlim(0, 2000)
ax.set_ylim(0, 460)
ax.set_xlabel("Tatsächliche Nutzungen je Gerät und Jahr",
              fontsize=10.5, color=INK)
ax.set_ylabel("CHF je Gerät/Jahr, annualisiert",
              fontsize=10.5, color=INK)
ax.set_title("Pay-per-Flush: Nutzungs- und Geberit-Break-even-Kurve",
             loc="left", color=NAVY, fontsize=15, fontweight="bold", pad=12)
ax.grid(color="#E8EEF1", linewidth=0.8)
ax.legend(loc="upper left", frameon=False, fontsize=9)
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)
ax.spines["left"].set_color("#D8E1E7")
ax.spines["bottom"].set_color("#D8E1E7")
ax.tick_params(colors="#657685")
fig.text(0.015, 0.01,
         "Illustration nur für Geberit: (CHF 250 Herstellung + CHF 150 Installation)/5 Jahre + CHF 45 Service/Jahr + CHF 25 Connectivity/Admin/Jahr; Gebühr CHF 0.20/Nutzung. Keine bestätigten Kosten oder Tarife.",
         color="#657685", fontsize=8.8)
fig.tight_layout(rect=(0, 0.08, 1, 0.98))
finish(fig, "08_usage_breakeven.png")
