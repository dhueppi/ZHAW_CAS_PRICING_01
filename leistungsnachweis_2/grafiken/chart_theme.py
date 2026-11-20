from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "output"
OUTPUT.mkdir(parents=True, exist_ok=True)

NAVY = "#14283B"
INK = "#263B4C"
TEAL = "#007C78"
MINT = "#B9DED8"
PALE = "#E8EEF1"
MID = "#657685"
GOLD = "#D7A13A"
RED = "#B84D48"
WHITE = "#FFFFFF"


def new_figure(figsize=(13.2, 4.65)):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(WHITE)
    ax.set_facecolor(WHITE)
    return fig, ax


def finish(fig, filename, tight=True):
    fig.savefig(OUTPUT / filename, dpi=220, bbox_inches="tight" if tight else None,
                facecolor=WHITE)
    plt.close(fig)
    print(OUTPUT / filename)


def note(ax, text, y=-0.19):
    ax.text(0.01, y, text, transform=ax.transAxes, ha="left", va="top",
            color=MID, fontsize=9.5, wrap=True)


def style_axes(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(PALE)
    ax.spines["bottom"].set_color(PALE)
    ax.tick_params(colors=MID, labelsize=10)
    ax.grid(axis="x", color=PALE, linewidth=0.8, zorder=0)


def rounded_label(ax, x, y, width, height, title, body, facecolor=PALE,
                  edgecolor=PALE, title_color=NAVY, fontsize=10):
    patch = FancyBboxPatch((x, y), width, height,
                           boxstyle="round,pad=0.015,rounding_size=0.025",
                           transform=ax.transAxes, facecolor=facecolor,
                           edgecolor=edgecolor, linewidth=0.8)
    ax.add_patch(patch)
    ax.text(x + 0.015, y + height - 0.04, title, transform=ax.transAxes,
            ha="left", va="top", fontsize=fontsize, fontweight="bold",
            color=title_color)
    ax.text(x + 0.015, y + height - 0.105, body, transform=ax.transAxes,
            ha="left", va="top", fontsize=fontsize - 1, color=INK,
            wrap=True)
