"""Build the headline figure: attack success rate (ASR), no-defense vs. defense,
overall and broken down by attack family.

Reads results.csv (written by run_experiment.py) so the chart always reflects the
latest run. Saves asr_chart.png.

Design note: colors carry only series identity (blue = no defense, aqua = defense
on); every other piece of text uses neutral ink. Each bar is directly labeled with
its value, which is also why aqua is safe here despite its lighter tone.
"""

import csv
from collections import defaultdict

import matplotlib

matplotlib.use("Agg")  # render to file, no display needed
import matplotlib.pyplot as plt

# --- palette (from the design system's validated categorical slots) ---
BLUE = "#2a78d6"   # series: no defense
AQUA = "#1baf7a"   # series: defense on
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRID = "#e1e0d9"
SURFACE = "#fcfcfb"


def load_asr():
    """Return (overall, per_family) ASR dicts keyed by condition."""
    rows = list(csv.DictReader(open("results.csv")))
    # counts[condition][family] = [successes, total]
    counts = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    overall = defaultdict(lambda: [0, 0])
    for r in rows:
        success = r["success"] == "True"
        c = r["condition"]
        counts[c][r["family"]][0] += success
        counts[c][r["family"]][1] += 1
        overall[c][0] += success
        overall[c][1] += 1

    def rate(pair):
        return 100.0 * pair[0] / pair[1] if pair[1] else 0.0

    families = sorted({r["family"] for r in rows})
    return overall, counts, families, {f: counts["defense_off"][f][1] for f in families}


def main():
    overall, counts, families, family_n = load_asr()

    def rate(pair):
        return 100.0 * pair[0] / pair[1] if pair[1] else 0.0

    # Order groups: Overall first, then families by no-defense ASR (descending).
    families_sorted = sorted(families, key=lambda f: rate(counts["defense_off"][f]), reverse=True)
    labels = ["Overall"] + [f.capitalize() for f in families_sorted]
    off_vals = [rate(overall["defense_off"])] + [rate(counts["defense_off"][f]) for f in families_sorted]
    on_vals = [rate(overall["defense_on"])] + [rate(counts["defense_on"][f]) for f in families_sorted]
    group_n = [sum(family_n.values())] + [family_n[f] for f in families_sorted]

    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=150)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)

    x = range(len(labels))
    width = 0.38
    gap = 0.02  # 2px-ish surface gap between the paired bars
    off_x = [i - width / 2 - gap / 2 for i in x]
    on_x = [i + width / 2 + gap / 2 for i in x]

    bars_off = ax.bar(off_x, off_vals, width, label="No defense", color=BLUE)
    bars_on = ax.bar(on_x, on_vals, width, label="Data-marking defense", color=AQUA)

    # Direct value labels on every bar (also satisfies the contrast relief rule).
    for bars, vals in ((bars_off, off_vals), (bars_on, on_vals)):
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v + 1.5, f"{v:.0f}%",
                    ha="center", va="bottom", fontsize=9, color=INK_SECONDARY)

    # Axes / chrome: recessive.
    ax.set_ylim(0, 100)
    ax.set_ylabel("Attack success rate", color=INK_SECONDARY, fontsize=10)
    ax.set_yticks(range(0, 101, 25))
    ax.set_yticklabels([f"{t}%" for t in range(0, 101, 25)], color=INK_MUTED, fontsize=9)
    ax.set_xticks(list(x))
    ax.set_xticklabels([f"{lab}\n(n={n})" for lab, n in zip(labels, group_n)],
                       color=INK_SECONDARY, fontsize=9)
    ax.grid(axis="y", color=GRID, linewidth=1)
    ax.set_axisbelow(True)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color("#c3c2b7")
    ax.tick_params(length=0)

    ax.set_title("Prompt-injection attack success rate on llama3.2:3b",
                 color=INK_PRIMARY, fontsize=13, fontweight="bold", loc="left", pad=24)
    ax.text(0, 1.03, "No defense vs. data-marking; overall (n=30) and by attack family. "
                     "Lower is better. Per-family n is small — read as directional.",
            transform=ax.transAxes, color=INK_MUTED, fontsize=9)

    ax.legend(loc="upper right", frameon=False, fontsize=9, labelcolor=INK_SECONDARY)

    fig.tight_layout()
    fig.savefig("asr_chart.png", facecolor=SURFACE, bbox_inches="tight")
    print("Saved asr_chart.png")


if __name__ == "__main__":
    main()
