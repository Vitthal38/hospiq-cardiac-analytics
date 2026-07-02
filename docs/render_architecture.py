"""
render_architecture.py — Render the HOSPIQ pipeline architecture diagram.

Produces docs/architecture_diagram.png using only matplotlib (no external
diagram libraries). Run: python docs/render_architecture.py
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = os.path.join(os.path.dirname(__file__), "architecture_diagram.png")


def _node(ax, x, y, w, h, text, face, textcolor):
    ax.add_patch(FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        facecolor=face, edgecolor="#333333", linewidth=1.4))
    ax.text(x, y, text, ha="center", va="center",
            color=textcolor, fontsize=11, fontweight="bold", linespacing=1.4)


def _arrow(ax, x1, y1, x2, y2, label, rad=0.0):
    ax.add_patch(FancyArrowPatch(
        (x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=16,
        color="#555555", linewidth=1.4,
        connectionstyle=f"arc3,rad={rad}"))
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    ax.text(mx, my + 0.16, label, ha="center", va="bottom",
            color="#555555", fontsize=8.5, style="italic")


def render():
    fig, ax = plt.subplots(figsize=(14, 7), dpi=100)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 7)
    ax.axis("off")

    ax.text(7, 6.5, "HOSPIQ — End-to-End Analytics Pipeline",
            ha="center", va="center", fontsize=16, fontweight="bold", color="#333333")

    y = 4.4
    w, h = 2.2, 1.2
    xs = [1.4, 4.3, 7.0, 9.7, 12.6]
    nodes = [
        ("Hero DMC\nSource Data", "#E8E8E8", "#333333"),
        ("AWS S3\nRaw Zone", "#FF9900", "white"),
        ("Python ETL\npandas · boto3", "#3B82F6", "white"),
        ("PostgreSQL\nStar Schema", "#336791", "white"),
        ("Power BI\nDashboard", "#F2C811", "#333333"),
    ]
    for x, (t, face, tc) in zip(xs, nodes):
        _node(ax, x, y, w, h, t, face, tc)

    labels = ["Upload raw CSV", "Extract", "Load star schema", "DirectQuery / Import"]
    for i, lab in enumerate(labels):
        _arrow(ax, xs[i] + w / 2, y, xs[i + 1] - w / 2, y, lab)

    # Secondary dbt node below node 4 (PostgreSQL), fed from Python ETL (node 3)
    dbt_x, dbt_y = 9.7, 1.9
    _node(ax, dbt_x, dbt_y, 2.6, 1.1, "dbt Project\nstaging · marts · tests",
          "#00A35C", "white")
    _arrow(ax, xs[2], y - h / 2, dbt_x - 0.6, dbt_y + 0.55, "dbt run", rad=-0.15)
    _arrow(ax, dbt_x, dbt_y + 0.55, xs[3], y - h / 2, "materialise", rad=-0.15)

    ax.text(7, 0.5,
            "15,757 admissions · 12,244 patients · "
            "Hero DMC Heart Institute, Ludhiana · April 2017 – March 2019",
            ha="center", va="center", fontsize=9, color="#888888")

    fig.savefig(OUT, dpi=100, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved {OUT}")


if __name__ == "__main__":
    render()
