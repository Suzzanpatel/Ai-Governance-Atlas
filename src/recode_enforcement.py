
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

INPUT = ROOT / "results" / "tables" / "normalised_governance_dataset.csv"
OUTPUT = ROOT / "results" / "tables"

df = pd.read_csv(INPUT)

# --------------------------------------------------
# PROVISION-SPECIFIC ENFORCEMENT CODING
# --------------------------------------------------
# These are provisional analytical classifications.
# Each category is assigned only where supported by
# the provision description and verification notes.
#
# Direct = mechanism attached to the specific duty.
# Cross-referenced = mechanism linked through another
# identified provision.
# System-level = wider regulatory architecture.
# --------------------------------------------------

coding = {

    # EUROPEAN UNION
    "EU001": {
        "direct": [],
        "cross_referenced": [
            "Provider compliance obligation",
            "Administrative fines"
        ],
        "system_level": [
            "Conformity assessment",
            "Market surveillance"
        ],
        "rationale": (
            "Article 9 provider duty is linked to Article 16(a); "
            "Article 99(4)(a) provides fines for provider obligations "
            "under Article 16. Conformity assessment and market "
            "surveillance are wider system mechanisms."
        )
    },

    "EU002": {
        "direct": [],
        "cross_referenced": [
            "Provider compliance obligation",
            "Administrative fines"
        ],
        "system_level": [
            "Conformity assessment",
            "Market surveillance"
        ],
        "rationale": (
            "Article 10 is linked to provider compliance under "
            "Article 16(a) and the Article 99(4)(a) penalty framework. "
            "Assessment and surveillance operate at system level."
        )
    },

    "EU003": {
        "direct": [],
        "cross_referenced": [
            "Provider compliance obligation",
            "Administrative fines"
        ],
        "system_level": [
            "Conformity assessment",
            "Market surveillance"
        ],
        "rationale": (
            "Article 13 provider transparency duty is within the "
            "Articles 9-15 requirements linked by Article 16(a). "
            "Article 99(4)(a) applies to provider obligations under "
            "Article 16. Wider assessment and surveillance are "
            "recorded separately."
        )
    },

    "EU004": {
        "direct": [],
        "cross_referenced": [
            "Provider administrative fines",
            "Deployer administrative fines"
        ],
        "system_level": [
            "Conformity assessment",
            "Market surveillance"
        ],
        "rationale": (
            "Article 14 provider design obligations connect to "
            "Article 16(a) and Article 99(4)(a). The deployer duty "
            "under Article 26(2) is subject to Article 99(4)(e). "
            "These are cross-referenced penalty routes."
        )
    },

    "EU005": {
        "direct": [],
        "cross_referenced": [
            "Provider compliance obligation",
            "Administrative fines"
        ],
        "system_level": [
            "Conformity assessment",
            "Market surveillance"
        ],
        "rationale": (
            "Article 15 provider requirements connect to Article "
            "16(a) and Article 99(4)(a). Conformity assessment and "
            "market surveillance are wider system mechanisms."
        )
    },

    # INDIA
    "IND001": {
        "direct": [
            "Voluntary transparency reporting",
            "Peer scrutiny"
        ],
        "cross_referenced": [],
        "system_level": [
            "Soft accountability"
        ],
        "rationale": (
            "The examined guidance describes transparency reporting "
            "and public or peer scrutiny. These are soft accountability "
            "mechanisms, not statutory sanctions."
        )
    },

    "IND002": {
        "direct": [
            "No specific enforcement mechanism identified"
        ],
        "cross_referenced": [],
        "system_level": [
            "Proposed future liability framework"
        ],
        "rationale": (
            "The provision recommends that government create future "
            "obligations. Those obligations do not yet exist in this "
            "examined provision."
        )
    },

    "IND003": {
        "direct": [
            "Not applicable"
        ],
        "cross_referenced": [],
        "system_level": [
            "Proposed risk framework development"
        ],
        "rationale": (
            "This is a framework-development task, not a compliance "
            "duty. The proposed incidents database is not a sanction."
        )
    },

    "IND004": {
        "direct": [
            "No coercive enforcement power identified"
        ],
        "cross_referenced": [],
        "system_level": [
            "Institutional testing and advice",
            "Compliance monitoring"
        ],
        "rationale": (
            "The AI Safety Institute has research, testing and advisory "
            "functions in the examined guidance, but no power to compel "
            "testing or impose sanctions."
        )
    },

    "IND005": {
        "direct": [
            "No new AI-specific enforcement power"
        ],
        "cross_referenced": [],
        "system_level": [
            "Existing sectoral regulatory powers"
        ],
        "rationale": (
            "Existing regulators may enforce applicable laws under "
            "their own statutory powers. The guidelines do not create "
            "new AI-specific sanctions."
        )
    },

    # UNITED KINGDOM
    "UK001": {
        "direct": [
            "No new enforcement mechanism"
        ],
        "cross_referenced": [],
        "system_level": [
            "Existing regulator powers",
            "Regulatory information requests"
        ],
        "rationale": (
            "The non-statutory transparency principle relies on "
            "existing regulator powers. Information may be requested "
            "by regulators, but the principle itself creates no "
            "new general sanction."
        )
    },

    "UK002": {
        "direct": [
            "No new enforcement mechanism"
        ],
        "cross_referenced": [],
        "system_level": [
            "Existing regulator powers"
        ],
        "rationale": (
            "The accountability principle is non-statutory. Existing "
            "regulators apply their powers under their respective laws."
        )
    },

    "UK003": {
        "direct": [
            "Not applicable"
        ],
        "cross_referenced": [],
        "system_level": [
            "Central government risk assessment",
            "Central monitoring and evaluation"
        ],
        "rationale": (
            "This is an internal government function, not an "
            "enforceable business compliance obligation."
        )
    },

    "UK004": {
        "direct": [
            "No new enforcement mechanism"
        ],
        "cross_referenced": [],
        "system_level": [
            "Existing regulator powers",
            "Regulatory monitoring"
        ],
        "rationale": (
            "The safety principle is non-statutory. Testing may be "
            "required through regulator implementation using existing "
            "powers, rather than through a new general statutory duty."
        )
    },

    "UK005": {
        "direct": [
            "Existing statutory regulator powers"
        ],
        "cross_referenced": [],
        "system_level": [
            "Central monitoring and evaluation",
            "Proposed future due-regard duty"
        ],
        "rationale": (
            "Existing regulators use powers under their own laws. "
            "The proposed due-regard duty was conditional and "
            "not a binding new power in the examined White Paper."
        )
    },

    # OECD INTERNATIONAL BENCHMARK
    "OECD001": {
        "direct": [
            "No legal enforcement or sanctions"
        ],
        "cross_referenced": [],
        "system_level": [
            "OECD implementation monitoring",
            "Reporting to Council"
        ],
        "rationale": (
            "The transparency principle is non-binding. Monitoring "
            "and reporting operate at instrument level."
        )
    },

    "OECD002": {
        "direct": [
            "No legal enforcement or sanctions"
        ],
        "cross_referenced": [],
        "system_level": [
            "OECD implementation monitoring",
            "Reporting to Council"
        ],
        "rationale": (
            "The accountability principle is non-binding. Reporting "
            "and peer monitoring do not constitute legal sanctions."
        )
    },

    "OECD003": {
        "direct": [
            "No legal enforcement or sanctions"
        ],
        "cross_referenced": [],
        "system_level": [
            "OECD implementation monitoring",
            "Reporting to Council"
        ],
        "rationale": (
            "The risk-management element is part of the non-binding "
            "OECD accountability principle. Monitoring is recorded "
            "at instrument level."
        )
    },

    "OECD004": {
        "direct": [
            "No legal enforcement or sanctions"
        ],
        "cross_referenced": [],
        "system_level": [
            "OECD implementation monitoring",
            "Reporting to Council"
        ],
        "rationale": (
            "The robustness, security and safety principle is "
            "non-binding. OECD monitoring does not create sanctions."
        )
    },

    "OECD005": {
        "direct": [
            "No legal enforcement or sanctions"
        ],
        "cross_referenced": [],
        "system_level": [
            "Digital Policy Committee reporting",
            "Peer exchange"
        ],
        "rationale": (
            "The provision concerns institutional monitoring and "
            "reporting to Council. It is not legal enforcement."
        )
    }
}

# --------------------------------------------------
# VALIDATE RECORD COVERAGE
# --------------------------------------------------

if set(df["id"]) != set(coding):
    raise ValueError(
        "Dataset IDs do not match the enforcement coding map.\n"
        f"Missing: {set(df['id']) - set(coding)}\n"
        f"Unexpected: {set(coding) - set(df['id'])}"
    )

# --------------------------------------------------
# ADD THREE DISTINCT ENFORCEMENT LEVELS
# --------------------------------------------------

df["direct_enforcement"] = df["id"].map(
    lambda x: " | ".join(coding[x]["direct"])
)

df["cross_referenced_enforcement"] = df["id"].map(
    lambda x: " | ".join(coding[x]["cross_referenced"])
)

df["system_level_mechanisms"] = df["id"].map(
    lambda x: " | ".join(coding[x]["system_level"])
)

df["enforcement_coding_rationale"] = df["id"].map(
    lambda x: coding[x]["rationale"]
)

# --------------------------------------------------
# SAVE PROVISION-LEVEL DATASET
# --------------------------------------------------

df.to_csv(
    OUTPUT / "provision_specific_enforcement_dataset.csv",
    index=False
)

# --------------------------------------------------
# CREATE LONG-FORM DATASET
# --------------------------------------------------

records = []

for _, row in df.iterrows():
    provision_id = row["id"]
    country = row["country"]

    for level in [
        "direct",
        "cross_referenced",
        "system_level"
    ]:
        for category in coding[provision_id][level]:
            records.append({
                "id": provision_id,
                "country": country,
                "enforcement_level": level,
                "mechanism": category,
                "rationale": coding[provision_id]["rationale"]
            })

long_df = pd.DataFrame(records)

long_df.to_csv(
    OUTPUT / "provision_specific_enforcement_long.csv",
    index=False
)

# --------------------------------------------------
# CREATE SEPARATE COMPARATIVE MATRICES
# --------------------------------------------------

for level in ["direct", "cross_referenced", "system_level"]:

    subset = long_df[
        long_df["enforcement_level"] == level
    ]

    matrix = pd.crosstab(
        subset["country"],
        subset["mechanism"]
    )

    matrix.to_csv(
        OUTPUT / f"{level}_enforcement_matrix.csv"
    )

# --------------------------------------------------
# COMPLETION REPORT
# --------------------------------------------------

print("\nPROVISION-SPECIFIC ENFORCEMENT RECODING")
print("=" * 55)

print("Total provisions:", len(df))

print("\nRecords by country:")
print(df["country"].value_counts().to_string())

print("\nMechanisms by enforcement level:")
print(long_df.groupby("enforcement_level").size().to_string())

print("\nFILES CREATED:")
print("1. provision_specific_enforcement_dataset.csv")
print("2. provision_specific_enforcement_long.csv")
print("3. direct_enforcement_matrix.csv")
print("4. cross_referenced_enforcement_matrix.csv")
print("5. system_level_enforcement_matrix.csv")

print("\nStage 8.1 recoding completed.")
