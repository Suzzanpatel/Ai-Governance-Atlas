
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent

TABLES = ROOT / "results" / "tables"
CHARTS = ROOT / "results" / "charts"

CHARTS.mkdir(parents=True, exist_ok=True)

INPUT_FILE = TABLES / "provision_specific_enforcement_long.csv"

print("\nAI GOVERNANCE ATLAS — ENFORCEMENT ARCHITECTURE")
print("=" * 60)


# --------------------------------------------------
# 2. SYSTEM-LEVEL ARCHITECTURE
# One row per jurisdiction / benchmark.
# These descriptions are based on the existing
# research coding and must be legally verified.
# --------------------------------------------------

architecture = [
    {
        "country": "EU",
        "instrument_type": "Binding legislation",
        "system_level_architecture": (
            "Provider and deployer compliance duties; "
            "conformity assessment; market surveillance; "
            "administrative fines."
        ),
        "enforcement_character": (
            "Statutory enforcement framework"
        ),
        "evidence_basis": (
            "EU AI Act Articles 16, 43, 74, 79 and 99 "
            "as referenced in the research dataset."
        ),
        "verification_status": "Requires provision-level verification"
    },
    {
        "country": "India",
        "instrument_type": "Non-binding guidance",
        "system_level_architecture": (
            "Existing sectoral regulators; MeitY coordination; "
            "AI Safety Institute testing and advice; "
            "transparency reporting and proposed future measures."
        ),
        "enforcement_character": (
            "Existing sectoral powers and soft accountability"
        ),
        "evidence_basis": (
            "India AI Governance Guidelines, including the "
            "institutional and accountability provisions coded."
        ),
        "verification_status": "Requires institutional implementation verification"
    },
    {
        "country": "UK",
        "instrument_type": "Government policy (non-statutory)",
        "system_level_architecture": (
            "Existing sectoral regulators apply their statutory "
            "powers; central government monitoring and evaluation; "
            "possible future regulatory duties."
        ),
        "enforcement_character": (
            "Existing regulator powers; no new general AI-specific "
            "sanctions created by the examined White Paper."
        ),
        "evidence_basis": (
            "UK AI Regulation White Paper, including paragraphs "
            "55-59, 64 and 68 as referenced in the research dataset."
        ),
        "verification_status": "Requires regulator-specific verification"
    },
    {
        "country": "OECD (international benchmark)",
        "instrument_type": "International recommendation (non-binding)",
        "system_level_architecture": (
            "Implementation monitoring, reporting to Council, "
            "peer exchange and OECD.AI Policy Observatory."
        ),
        "enforcement_character": (
            "International monitoring; no legal sanctions "
            "under the examined Recommendation."
        ),
        "evidence_basis": (
            "OECD Recommendation on AI, OECD/LEGAL/0449, "
            "including Section VIII(d) as referenced in the dataset."
        ),
        "verification_status": "Non-binding instrument; monitoring is not legal enforcement"
    }
]

architecture_df = pd.DataFrame(architecture)

architecture_df.to_csv(
    TABLES / "system_level_enforcement_architecture.csv",
    index=False
)

print("\nSYSTEM-LEVEL ARCHITECTURE")
print("-" * 60)
print(
    architecture_df[
        ["country", "enforcement_character"]
    ].to_string(index=False)
)


# --------------------------------------------------
# 3. LOAD PROVISION-LEVEL ENFORCEMENT DATA
# --------------------------------------------------

long_df = pd.read_csv(INPUT_FILE)

# Keep only direct and cross-referenced classifications.
provision_df = long_df[
    long_df["enforcement_level"].isin(
        ["direct", "cross_referenced"]
    )
].copy()

# Remove absence / non-applicability labels.
# These are findings, not enforcement mechanisms.
excluded_labels = [
    "No specific enforcement mechanism identified",
    "No new enforcement mechanism",
    "No new AI-specific enforcement power",
    "No coercive enforcement power identified",
    "No legal enforcement or sanctions",
    "Not applicable"
]

provision_df = provision_df[
    ~provision_df["mechanism"].isin(excluded_labels)
].copy()

# "Provider compliance obligation" describes a duty,
# not an enforcement mechanism. Keep it in the audit
# dataset, but exclude it from the mechanism chart.
provision_df = provision_df[
    provision_df["mechanism"] != "Provider compliance obligation"
].copy()

# Remove duplicate provision/category/level combinations.
provision_df = provision_df.drop_duplicates(
    subset=["id", "country", "enforcement_level", "mechanism"]
)

# Save the filtered mechanism data.
provision_df.to_csv(
    TABLES / "enforcement_mechanisms_for_visualisation.csv",
    index=False
)


# --------------------------------------------------
# 4. BUILD PROVISION-LEVEL MATRIX
# --------------------------------------------------

if not provision_df.empty:

    matrix = pd.crosstab(
        [provision_df["country"], provision_df["enforcement_level"]],
        provision_df["mechanism"]
    )

    matrix.to_csv(
        TABLES / "provision_level_enforcement_matrix.csv"
    )

    print("\nPROVISION-LEVEL MECHANISM COUNTS")
    print("-" * 60)
    print(matrix.to_string())

else:
    print("\nNo direct or cross-referenced mechanisms to plot.")


# --------------------------------------------------
# 5. CREATE PROVISION-LEVEL ENFORCEMENT CHART
# --------------------------------------------------

if not provision_df.empty:

    plot_data = (
        provision_df.groupby(
            ["country", "mechanism"]
        )["id"]
        .nunique()
        .unstack(fill_value=0)
    )

    ax = plot_data.plot(
        kind="barh",
        figsize=(13, 8),
        width=0.75
    )

    ax.set_title(
        "Provision-Level Enforcement Mechanisms"
    )
    ax.set_xlabel(
        "Number of distinct coded provisions"
    )
    ax.set_ylabel(
        "Jurisdiction / International Benchmark"
    )

    ax.legend(
        title="Mechanism",
        bbox_to_anchor=(1.02, 1),
        loc="upper left"
    )

    plt.tight_layout()

    plt.savefig(
        CHARTS / "06_provision_level_enforcement.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()


# --------------------------------------------------
# 6. COMPLETION REPORT
# --------------------------------------------------

print("\nFILES CREATED")
print("-" * 60)

print("1. system_level_enforcement_architecture.csv")
print("2. enforcement_mechanisms_for_visualisation.csv")
print("3. provision_level_enforcement_matrix.csv")
print("4. 06_provision_level_enforcement.png")

print("\nSystem-level architecture records:", len(architecture_df))
print("Provision-level mechanism records:", len(provision_df))

print("\nIMPORTANT:")
print("System-level architecture is stored separately.")
print("Absence of a mechanism is not counted as enforcement.")
print("Category counts may overlap across provisions.")

print("\nStage 8.2 completed.")
