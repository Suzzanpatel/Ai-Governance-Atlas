
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Locate project directory
PROJECT_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_DIR / "results" / "tables"
    / "keyword_summary_by_country.csv"
)

OUTPUT_DIR = PROJECT_DIR / "results" / "charts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load keyword analysis results
df = pd.read_csv(INPUT_FILE)

# Keep the three jurisdictions separate from OECD
jurisdictions = df[
    df["country"].isin(["india", "eu", "uk"])
].copy()

# Prepare a country-by-dimension table
pivot = jurisdictions.pivot(
    index="dimension",
    columns="country",
    values="frequency_per_1000_words"
)

pivot = pivot.reindex(columns=["india", "eu", "uk"])

# Consistent labels
pivot.columns = ["India", "EU", "UK"]

# -------------------------------
# GRAPH 1: Comparative bar chart
# -------------------------------

plt.figure(figsize=(11, 6))

pivot.plot(
    kind="bar",
    figsize=(11, 6),
    width=0.8
)

plt.title(
    "AI Governance: Keyword Frequency by Jurisdiction",
    fontsize=14
)
plt.xlabel("Governance Dimension")
plt.ylabel("Occurrences per 1,000 words")
plt.xticks(rotation=20, ha="right")
plt.legend(title="Jurisdiction")
plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "comparative_bar_chart.png",
    dpi=300
)
plt.close()

# -------------------------------
# GRAPH 2: Governance heatmap
# -------------------------------

plt.figure(figsize=(9, 5))

sns.heatmap(
    pivot,
    annot=True,
    fmt=".2f",
    cmap="YlGnBu",
    linewidths=0.5
)

plt.title("AI Governance Keyword Frequency Heatmap")
plt.xlabel("Jurisdiction")
plt.ylabel("Governance Dimension")
plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "governance_heatmap.png",
    dpi=300
)
plt.close()

# -------------------------------
# GRAPH 3: Stacked bar chart
# -------------------------------

pivot.plot(
    kind="bar",
    stacked=True,
    figsize=(10, 6)
)

plt.title("Distribution of Governance Keyword Frequencies")
plt.xlabel("Governance Dimension")
plt.ylabel("Occurrences per 1,000 words")
plt.xticks(rotation=20, ha="right")
plt.legend(title="Jurisdiction")
plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "stacked_bar_chart.png",
    dpi=300
)
plt.close()

print("VISUALISATION COMPLETED!")
print("Charts saved in:", OUTPUT_DIR)
