
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent

TABLES = ROOT / "results" / "tables"
CHARTS = ROOT / "results" / "charts"

CHARTS.mkdir(parents=True, exist_ok=True)

print("\nAI GOVERNANCE ATLAS — STAGE 8")
print("=" * 55)


# --------------------------------------------------
# 2. LOAD DATA
# --------------------------------------------------

governance = pd.read_csv(
    TABLES / "comparative_governance_matrix.csv"
).set_index("country")

responsibility = pd.read_csv(
    TABLES / "comparative_responsibility_matrix.csv"
).set_index("country")

enforcement = pd.read_csv(
    TABLES / "comparative_enforcement_matrix.csv"
).set_index("country")

obligations = pd.read_csv(
    TABLES / "comparative_obligation_matrix.csv"
).set_index("country")

implementation = pd.read_csv(
    TABLES / "implementation_by_country.csv"
).set_index("country")


# --------------------------------------------------
# 3. CHART 1 — GOVERNANCE HEATMAP
# --------------------------------------------------

plt.figure(figsize=(11, 6))

sns.heatmap(
    governance,
    annot=True,
    fmt="g",
    cmap="Blues",
    linewidths=0.5
)

plt.title("Comparative AI Governance Dimensions")
plt.xlabel("Governance Dimension")
plt.ylabel("Jurisdiction / Benchmark")
plt.tight_layout()

plt.savefig(
    CHARTS / "01_governance_heatmap.png",
    dpi=300
)
plt.close()


# --------------------------------------------------
# 4. CHART 2 — RESPONSIBILITY ALLOCATION
# --------------------------------------------------

ax = responsibility.plot(
    kind="bar",
    figsize=(13, 7),
    width=0.8
)

ax.set_title("AI Governance Responsibility Allocation")
ax.set_xlabel("Jurisdiction / Benchmark")
ax.set_ylabel("Number of coded provisions")
ax.legend(
    title="Responsibility Category",
    bbox_to_anchor=(1.02, 1),
    loc="upper left"
)

plt.xticks(rotation=0)
plt.tight_layout()

plt.savefig(
    CHARTS / "02_responsibility_allocation.png",
    dpi=300
)
plt.close()


# --------------------------------------------------
# 5. CHART 3 — ENFORCEMENT MECHANISMS
# --------------------------------------------------

ax = enforcement.plot(
    kind="bar",
    figsize=(14, 7),
    width=0.8
)

ax.set_title("AI Governance Enforcement Mechanisms")
ax.set_xlabel("Jurisdiction / Benchmark")
ax.set_ylabel("Number of coded provisions")
ax.legend(
    title="Enforcement Category",
    bbox_to_anchor=(1.02, 1),
    loc="upper left"
)

plt.xticks(rotation=0)
plt.tight_layout()

plt.savefig(
    CHARTS / "03_enforcement_mechanisms.png",
    dpi=300
)
plt.close()


# --------------------------------------------------
# 6. CHART 4 — OBLIGATION TYPES
# --------------------------------------------------

ax = obligations.plot(
    kind="bar",
    figsize=(10, 6),
    width=0.75
)

ax.set_title("Mandatory, Recommended and Institutional Provisions")
ax.set_xlabel("Jurisdiction / Benchmark")
ax.set_ylabel("Number of coded provisions")
ax.legend(title="Obligation Type")

plt.xticks(rotation=0)
plt.tight_layout()

plt.savefig(
    CHARTS / "04_obligation_types.png",
    dpi=300
)
plt.close()


# --------------------------------------------------
# 7. CHART 5 — IMPLEMENTATION STATUS
# --------------------------------------------------

ax = implementation.plot(
    kind="bar",
    figsize=(12, 7),
    width=0.8
)

ax.set_title("Recorded Implementation Status")
ax.set_xlabel("Jurisdiction / Benchmark")
ax.set_ylabel("Number of coded provisions")
ax.legend(
    title="Implementation Status",
    bbox_to_anchor=(1.02, 1),
    loc="upper left"
)

plt.xticks(rotation=0)
plt.tight_layout()

plt.savefig(
    CHARTS / "05_implementation_status.png",
    dpi=300
)
plt.close()


# --------------------------------------------------
# 8. COMPLETION
# --------------------------------------------------

print("\nFIVE CHARTS GENERATED SUCCESSFULLY")

for file in sorted(CHARTS.glob("0*.png")):
    print(file.name)

print("\nCharts saved in:", CHARTS)
print("\nStage 8 completed.")
