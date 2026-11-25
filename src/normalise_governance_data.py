
import pandas as pd
from pathlib import Path

# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = ROOT / "data" / "annotated" / "governance_dataset.csv"
OUTPUT_DIR = ROOT / "results" / "tables"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INPUT_FILE)

print("\nAI GOVERNANCE ATLAS — STAGE 7.1")
print("=" * 55)


# --------------------------------------------------
# 2. RESPONSIBILITY CATEGORY CODING
# Multiple categories are allowed per provision.
# These are analytical codes, not new legal duties.
# --------------------------------------------------

responsibility_map = {

    "EU001": ["AI Provider"],
    "EU002": ["AI Provider"],
    "EU003": ["AI Provider"],
    "EU004": ["AI Provider", "AI Deployer"],
    "EU005": ["AI Provider"],

    "IND001": ["Developer", "AI Deployer"],
    "IND002": [
        "Government",
        "Regulator",
        "Developer",
        "AI Deployer",
        "End User"
    ],
    "IND003": ["Government", "Institution"],
    "IND004": ["Institution", "Regulator"],
    "IND005": ["Regulator", "Government", "Institution"],

    "UK001": ["Regulator", "AI Lifecycle Actors"],
    "UK002": ["Regulator", "AI Lifecycle Actors"],
    "UK003": ["Government", "Regulator"],
    "UK004": [
        "Regulator",
        "Developer",
        "AI Lifecycle Actors"
    ],
    "UK005": ["Regulator", "Government"],

    "OECD001": ["AI Lifecycle Actors", "Government"],
    "OECD002": ["AI Lifecycle Actors"],
    "OECD003": ["AI Lifecycle Actors", "Multiple Stakeholders"],
    "OECD004": ["AI Lifecycle Actors", "Government", "Multiple Stakeholders"],
    "OECD005": ["Institution"]
}


# --------------------------------------------------
# 3. ENFORCEMENT CATEGORY CODING
# Categories can overlap.
# --------------------------------------------------

enforcement_map = {

    "EU001": [
        "Financial Penalties",
        "Conformity Assessment",
        "Market Surveillance"
    ],
    "EU002": [
        "Financial Penalties",
        "Conformity Assessment",
        "Market Surveillance"
    ],
    "EU003": [
        "Financial Penalties",
        "Conformity Assessment",
        "Market Surveillance"
    ],
    "EU004": [
        "Financial Penalties",
        "Conformity Assessment",
        "Market Surveillance"
    ],
    "EU005": [
        "Financial Penalties",
        "Conformity Assessment",
        "Market Surveillance"
    ],

    "IND001": [
        "Voluntary or Soft Accountability",
        "Monitoring and Reporting"
    ],
    "IND002": [
        "No Specific Mechanism Identified",
        "Proposed or Future Mechanism"
    ],
    "IND003": ["Not Applicable"],
    "IND004": ["Monitoring and Reporting"],
    "IND005": ["Existing Regulatory Powers"],

    "UK001": [
        "Existing Regulatory Powers",
        "Monitoring and Evaluation"
    ],
    "UK002": [
        "Existing Regulatory Powers",
        "Monitoring and Evaluation"
    ],
    "UK003": ["Monitoring and Evaluation"],
    "UK004": [
        "Existing Regulatory Powers",
        "Monitoring and Evaluation"
    ],
    "UK005": [
        "Existing Regulatory Powers",
        "Monitoring and Evaluation",
        "Proposed or Future Mechanism"
    ],

    "OECD001": ["Monitoring and Reporting"],
    "OECD002": ["Monitoring and Reporting"],
    "OECD003": ["Monitoring and Reporting"],
    "OECD004": ["Monitoring and Reporting"],
    "OECD005": ["Monitoring and Reporting"]
}


# --------------------------------------------------
# 4. CHECK THAT EVERY RECORD HAS BEEN CODED
# --------------------------------------------------

ids = set(df["id"])

missing_responsibility = ids - set(responsibility_map)
missing_enforcement = ids - set(enforcement_map)

if missing_responsibility or missing_enforcement:
    raise ValueError(
        f"Uncoded records found.\n"
        f"Responsibility: {missing_responsibility}\n"
        f"Enforcement: {missing_enforcement}"
    )

# Check for unexpected IDs in the coding dictionaries
extra_responsibility = set(responsibility_map) - ids
extra_enforcement = set(enforcement_map) - ids

if extra_responsibility or extra_enforcement:
    raise ValueError(
        f"Unexpected IDs in coding maps.\n"
        f"Responsibility: {extra_responsibility}\n"
        f"Enforcement: {extra_enforcement}"
    )


# --------------------------------------------------
# 5. ADD STANDARDISED CATEGORIES
# --------------------------------------------------

df["responsibility_categories"] = df["id"].map(
    lambda x: " | ".join(responsibility_map[x])
)

df["enforcement_categories"] = df["id"].map(
    lambda x: " | ".join(enforcement_map[x])
)


# --------------------------------------------------
# 6. SAVE NORMALISED DATASET
# --------------------------------------------------

normalised_file = OUTPUT_DIR / "normalised_governance_dataset.csv"

df.to_csv(normalised_file, index=False)


# --------------------------------------------------
# 7. CREATE RESPONSIBILITY MATRIX
# Each provision can count in multiple categories.
# --------------------------------------------------

responsibility_long = df[
    ["id", "country", "responsibility_categories"]
].copy()

responsibility_long["responsibility_category"] = (
    responsibility_long["responsibility_categories"].str.split(" | ", regex=False)
)

responsibility_long = responsibility_long.explode(
    "responsibility_category"
)

responsibility_matrix = pd.crosstab(
    responsibility_long["country"],
    responsibility_long["responsibility_category"]
)

responsibility_matrix.to_csv(
    OUTPUT_DIR / "normalised_responsibility_matrix.csv"
)

responsibility_long.drop(
    columns=["responsibility_categories"]
).to_csv(
    OUTPUT_DIR / "responsibility_categories_long.csv",
    index=False
)


# --------------------------------------------------
# 8. CREATE ENFORCEMENT MATRIX
# --------------------------------------------------

enforcement_long = df[
    ["id", "country", "enforcement_categories"]
].copy()

enforcement_long["enforcement_category"] = (
    enforcement_long["enforcement_categories"].str.split(" | ")
)

enforcement_long = enforcement_long.explode(
    "enforcement_category"
)

enforcement_matrix = pd.crosstab(
    enforcement_long["country"],
    enforcement_long["enforcement_category"]
)

enforcement_matrix.to_csv(
    OUTPUT_DIR / "normalised_enforcement_matrix.csv"
)

enforcement_long.drop(
    columns=["enforcement_categories"]
).to_csv(
    OUTPUT_DIR / "enforcement_categories_long.csv",
    index=False
)


# --------------------------------------------------
# 9. PRINT RESULTS
# --------------------------------------------------

print("\nRESPONSIBILITY MATRIX")
print("-" * 55)
print(responsibility_matrix.to_string())

print("\nENFORCEMENT MATRIX")
print("-" * 55)
print(enforcement_matrix.to_string())

print("\nOUTPUT FILES CREATED")
print("-" * 55)

print("1. normalised_governance_dataset.csv")
print("2. normalised_responsibility_matrix.csv")
print("3. responsibility_categories_long.csv")
print("4. normalised_enforcement_matrix.csv")
print("5. enforcement_categories_long.csv")

print("\nTotal provisions processed:", len(df))
print("\nStage 7.1 completed successfully.")
