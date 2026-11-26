
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ==================================================
# 1. PROJECT PATHS
# ==================================================

ROOT = Path(__file__).resolve().parent.parent

TABLES = ROOT / "results" / "tables"
CHARTS = ROOT / "results" / "charts"

TABLES.mkdir(parents=True, exist_ok=True)
CHARTS.mkdir(parents=True, exist_ok=True)

INPUT_FILE = TABLES / "provision_specific_enforcement_long.csv"

print("\nAI GOVERNANCE ATLAS")
print("STAGE 8.3 — FINAL ENFORCEMENT ANALYSIS")
print("=" * 60)


# ==================================================
# 2. LOAD EXISTING ENFORCEMENT DATA
# ==================================================

source = pd.read_csv(INPUT_FILE)

# We use the existing provision-level coding as the
# starting point. We do not use system-level mechanisms
# in this final provision-level comparison.

# ==================================================
# 3. DEFINE FINAL PROVISION-LEVEL CLASSIFICATIONS
# ==================================================

final_coding = {

    # EU: provider administrative fines
    "EU001": {
        "mechanisms": ["Provider administrative fines"],
        "level": "Cross-referenced",
        "character": "Statutory enforcement"
    },

    "EU002": {
        "mechanisms": ["Provider administrative fines"],
        "level": "Cross-referenced",
        "character": "Statutory enforcement"
    },

    "EU003": {
        "mechanisms": ["Provider administrative fines"],
        "level": "Cross-referenced",
        "character": "Statutory enforcement"
    },

    # EU004: provider and deployer penalty routes
    "EU004": {
        "mechanisms": [
            "Provider administrative fines",
            "Deployer administrative fines"
        ],
        "level": "Cross-referenced",
        "character": "Statutory enforcement"
    },

    "EU005": {
        "mechanisms": ["Provider administrative fines"],
        "level": "Cross-referenced",
        "character": "Statutory enforcement"
    },

    # India: soft accountability mechanisms
    "IND001": {
        "mechanisms": [
            "Voluntary transparency reporting",
            "Peer scrutiny"
        ],
        "level": "Direct",
        "character": "Soft accountability"
    },

    # India: no specific mechanism in the examined provision
    "IND002": {
        "mechanisms": [],
        "level": "None identified",
        "character": "No specific mechanism identified"
    },

    "IND003": {
        "mechanisms": [],
        "level": "Not applicable",
        "character": "Not applicable"
    },

    "IND004": {
        "mechanisms": [],
        "level": "None identified",
        "character": "No coercive enforcement power identified"
    },

    "IND005": {
        "mechanisms": [],
        "level": "System-level only",
        "character": "Existing sectoral powers"
    },

    # UK: existing regulator powers
    "UK001": {
        "mechanisms": [],
        "level": "System-level only",
        "character": "Existing regulator powers"
    },

    "UK002": {
        "mechanisms": [],
        "level": "System-level only",
        "character": "Existing regulator powers"
    },

    "UK003": {
        "mechanisms": [],
        "level": "Not applicable",
        "character": "Government institutional function"
    },

    "UK004": {
        "mechanisms": [],
        "level": "System-level only",
        "character": "Existing regulator powers"
    },

    "IND006": {
        "mechanisms": [
            "Loss of section 79 safe harbour (rule 7)"
        ],
        "level": "Cross-referenced",
        "character": "Statutory enforcement"
    },

    "IND007": {
        "mechanisms": [
            "Loss of section 79 safe harbour"
        ],
        "level": "Direct",
        "character": "Statutory enforcement"
    },

    "UK006": {
        "mechanisms": [],
        "level": "System-level only",
        "character": "Existing regulator powers"
    },

    "UK007": {
        "mechanisms": [],
        "level": "None identified",
        "character": "No specific mechanism identified"
    },

    "UK005": {
        "mechanisms": [
            "Existing statutory regulator powers"
        ],
        "level": "Direct",
        "character": "Existing statutory powers"
    },

    # OECD: non-binding international recommendation
    "OECD001": {
        "mechanisms": [],
        "level": "None identified",
        "character": "Monitoring is not legal enforcement"
    },

    "OECD002": {
        "mechanisms": [],
        "level": "None identified",
        "character": "Monitoring is not legal enforcement"
    },

    "OECD003": {
        "mechanisms": [],
        "level": "None identified",
        "character": "Monitoring is not legal enforcement"
    },

    "OECD004": {
        "mechanisms": [],
        "level": "None identified",
        "character": "Monitoring is not legal enforcement"
    },

    "OECD005": {
        "mechanisms": [],
        "level": "System-level only",
        "character": "Monitoring and reporting"
    }
}


# ==================================================
# 4. VALIDATE RECORDS
# ==================================================

dataset_ids = set(source["id"].unique())
coding_ids = set(final_coding.keys())

if dataset_ids != coding_ids:
    raise ValueError(
        "Record IDs do not match.\n"
        f"Missing coding: {dataset_ids - coding_ids}\n"
        f"Unexpected coding: {coding_ids - dataset_ids}"
    )

# ==================================================
# 5. CREATE PROVISION-LEVEL AUDIT TABLE
# ==================================================

audit_records = []

for provision_id, details in final_coding.items():

    country = source.loc[
        source["id"] == provision_id, "country"
    ].iloc[0]

    mechanisms = details["mechanisms"]

    if mechanisms:
        mechanism_text = " | ".join(mechanisms)
    else:
        mechanism_text = "None"

    audit_records.append({
        "id": provision_id,
        "country": country,
        "enforcement_mechanisms": mechanism_text,
        "enforcement_level": details["level"],
        "mechanism_character": details["character"],
        "number_of_mechanisms": len(mechanisms)
    })

audit_df = pd.DataFrame(audit_records)

audit_df.to_csv(
    TABLES / "final_enforcement_provision_audit.csv",
    index=False
)


# ==================================================
# 6. CREATE ONE ROW PER MECHANISM
# ==================================================

mechanism_records = []

for provision_id, details in final_coding.items():

    country = source.loc[
        source["id"] == provision_id, "country"
    ].iloc[0]

    for mechanism in details["mechanisms"]:

        mechanism_records.append({
            "id": provision_id,
            "country": country,
            "mechanism": mechanism,
            "enforcement_level": details["level"],
            "mechanism_character": details["character"]
        })

mechanism_df = pd.DataFrame(mechanism_records)

mechanism_df.to_csv(
    TABLES / "final_enforcement_mechanisms.csv",
    index=False
)


# ==================================================
# 7. CREATE FINAL COMPARATIVE MATRIX
# ==================================================

if not mechanism_df.empty:

    final_matrix = pd.crosstab(
        mechanism_df["country"],
        mechanism_df["mechanism"]
    )

    final_matrix.to_csv(
        TABLES / "final_enforcement_matrix.csv"
    )

    print("\nFINAL ENFORCEMENT MATRIX")
    print("-" * 60)
    print(final_matrix.to_string())


# ==================================================
# 8. CREATE ENFORCEMENT STATUS SUMMARY
# ==================================================

status_summary = (
    audit_df.groupby(
        ["country", "enforcement_level"]
    )
    .size()
    .reset_index(name="provision_count")
)

status_summary.to_csv(
    TABLES / "enforcement_status_summary.csv",
    index=False
)

print("\nENFORCEMENT STATUS SUMMARY")
print("-" * 60)
print(status_summary.to_string(index=False))



# ==================================================
# 9. CREATE FINAL CHART
# ==================================================

if not mechanism_df.empty:

    # Create provision-level counts
    plot_data = (
        mechanism_df.groupby(
            ["country", "mechanism"]
        )["id"]
        .nunique()
        .unstack(fill_value=0)
    )

    # Include all four groups, including OECD
    all_groups = [
        "EU",
        "India",
        "UK",
        "OECD (international benchmark)"
    ]

    # Add missing groups with zero values
    plot_data = plot_data.reindex(
        all_groups,
        fill_value=0
    )

    # Generate horizontal bar chart
    ax = plot_data.plot(
        kind="barh",
        figsize=(13, 7),
        width=0.7
    )

    ax.set_title(
        "Provision-Linked Compliance and Enforcement Mechanisms",
        fontsize=13
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

    # Save chart
    plt.savefig(
        CHARTS / "07_final_enforcement_comparison.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print("\nFinal enforcement chart generated successfully.")

else:
    print("\nNo enforcement mechanisms available for plotting.")


# ==================================================
# 10. COMPLETION REPORT
# ==================================================

print("\nFILES CREATED")
print("-" * 60)

print("1. final_enforcement_provision_audit.csv")
print("2. final_enforcement_mechanisms.csv")
print("3. final_enforcement_matrix.csv")
print("4. enforcement_status_summary.csv")
print("5. 07_final_enforcement_comparison.png")

print("\nTotal provisions:", len(audit_df))
print("Mechanism records:", len(mechanism_df))

print("\nStage 8.3 completed successfully.")
