"""
Usage:
  1) python doughnut.py prepare input.xlsx manipulated.xlsx
     -> creates the file for manipulating values (columns: Status | Value | Adjusted Value | Label)
  2) Edit "Adjusted Value" in manipulated.xlsx if needed
  3) python doughnut.py chart manipulated.xlsx output_dir
"""
import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Patch

SHEETS = ["AMEA", "EUAM", "AUNZ"]
STATUS_COLORS = {
    "Backlog": "#808080",
    "Open": "#3c96bc",
    "Fix In Progress": "#e7af00",
    "Ready in UAT": "#27488b",
    "Passed in UAT": "#6cc080",
    "Failed in UAT": "#ffa396",
    "For Client Review": "#e4eafc",
    "Client Test": "#9ae2ca",
    "Close": "#6cc080",
    "Closed": "#6cc080",
}
FIXED_STATUSES = {"Close", "Closed"}


def read_raw(path, sheet):
    df = pd.read_excel(path, sheet_name=sheet, header=None, usecols=[0, 1], names=["Status", "Value"])
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
    df = df.dropna(subset=["Value"])  # drops header row / blanks
    df["Status"] = df["Status"].astype(str).str.strip()
    return df.reset_index(drop=True)


def make_labels(df):
    total = df["Adjusted Value"].sum()
    pct = df["Adjusted Value"] / total * 100 if total else 0 * df["Adjusted Value"]
    return df["Adjusted Value"].astype(int).astype(str) + " " + df["Status"] + " (" + pct.round(0).astype(int).astype(str) + "%)"


def prepare(src, dst):
    with pd.ExcelWriter(dst, engine="openpyxl") as writer:
        for sheet in SHEETS:
            df = read_raw(src, sheet)
            df["Adjusted Value"] = df["Value"]
            df["Label"] = make_labels(df)
            df.to_excel(writer, sheet_name=sheet, index=False)

            ws = writer.sheets[sheet]
            last = len(df) + 1
            # Live formula so the label updates when Adjusted Value is edited in Excel
            for r in range(2, last + 1):
                ws[f"D{r}"] = f'=TEXT(C{r},"0")&" "&A{r}&" ("&TEXT(IFERROR(C{r}/SUM($C$2:$C${last}),0),"0%")&")"'
            for col, width in zip("ABCD", (25, 10, 16, 30)):
                ws.column_dimensions[col].width = width
    print(f"Saved: {dst}")


def chart(src, outdir):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    data = {s: pd.read_excel(src, sheet_name=s) for s in SHEETS}

    # Status is dropped only if Value is 0 in ALL sheets
    matrix = pd.concat(
        [d.groupby("Status")["Value"].sum().rename(s) for s, d in data.items()], axis=1
    ).fillna(0)
    keep = [st for st in matrix.index if (matrix.loc[st] != 0).any()]
    order = [st for d in data.values() for st in d["Status"] if st in keep]
    keep = list(dict.fromkeys(order))

    palette = plt.cm.tab20.colors
    colors = {st: STATUS_COLORS.get(st, palette[i % len(palette)]) for i, st in enumerate(keep)}

    fig_all, axes = plt.subplots(1, len(SHEETS), figsize=(6 * len(SHEETS), 6))
    for ax_all, sheet in zip(axes, SHEETS):
        df = data[sheet]
        df = df[df["Status"].isin(keep)].copy()
        df["Label"] = make_labels(df)

        fig, ax = plt.subplots(figsize=(7, 6))
        for target in (ax, ax_all):
            draw_doughnut(target, df, colors, sheet)
        fig.tight_layout()
        fig.savefig(outdir / f"{sheet}.png", dpi=200, bbox_inches="tight")
        plt.close(fig)

    fig_all.tight_layout()
    fig_all.savefig(outdir / "ALL.png", dpi=200, bbox_inches="tight")
    plt.close(fig_all)
    print(f"Charts saved to: {outdir.resolve()}")


def draw_doughnut(ax, df, colors, title):
    shown = df[df["Adjusted Value"] > 0]
    if shown.empty:
        ax.text(0, 0, "No data", ha="center", va="center")
    else:
        ax.pie(
            shown["Adjusted Value"],
            colors=[colors[s] for s in shown["Status"]],
            startangle=90,
            counterclock=False,
            wedgeprops={"width": 0.4, "edgecolor": "white"},
        )
    total = df["Adjusted Value"].sum()
    fixed = df.loc[df["Status"].isin(FIXED_STATUSES), "Adjusted Value"].sum()
    percentage = round(fixed / total * 100) if total else 0
    ax.text(0, 0.1, f"{percentage}%", ha="center", va="center", fontsize=24, weight="bold", color="green")
    ax.text(0, -0.2, "FIXED", ha="center", va="center", fontsize=11, weight="bold", color="green")
    ax.axis("equal")
    handles = [Patch(color=colors[s], label=l) for s, l in zip(df["Status"], df["Label"])]
    ax.legend(handles=handles, loc="center left", bbox_to_anchor=(1.02, 0.5), frameon=False, fontsize=9)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("prepare")
    a.add_argument("src")
    a.add_argument("dst", nargs="?", default="manipulated.xlsx")
    b = sub.add_parser("chart")
    b.add_argument("src", nargs="?", default="manipulated.xlsx")
    b.add_argument("outdir", nargs="?", default="charts")
    args = p.parse_args()

    if args.cmd == "prepare":
        prepare(args.src, args.dst)
    else:
        chart(args.src, args.outdir)
