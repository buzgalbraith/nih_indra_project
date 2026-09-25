import csv
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib_venn import venn3, venn3_circles

BASE_PATH = Path("./outputs/")
MEMBERSHIP_TSV = BASE_PATH / "stmt_membership.tsv"
VENN_PNG = BASE_PATH / "stmt_venn.png"
# colorblind-safe (Okabe-Ito) blue, orange, green
COLORS = ("#0072B2", "#E69F00", "#009E73")


def main():
    with open(MEMBERSHIP_TSV, newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        sources = reader.fieldnames[3:]
        # region key like "101" = in first and third source only
        regions = Counter(
            "".join(row[src] for src in sources) for row in reader
        )

    # venn3 subset order: 100, 010, 110, 001, 101, 011, 111
    order = ["100", "010", "110", "001", "101", "011", "111"]
    subsets = [regions.get(key, 0) for key in order]

    fig, ax = plt.subplots(figsize=(7, 6))
    venn3(subsets=subsets, set_labels=sources, set_colors=COLORS,
          alpha=0.45, ax=ax)
    venn3_circles(subsets=subsets, linewidth=1, color="#444444", ax=ax)
    ax.set_title("INDRA statement overlap by source")
    fig.savefig(VENN_PNG, dpi=200, bbox_inches="tight")
    print(f"wrote {VENN_PNG}")


if __name__ == "__main__":
    main()
