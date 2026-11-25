
import pandas as pd
from pathlib import Path

# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = ROOT / "results" / "tables" / "normalised_governance_dataset.csv"
OUTPUT_DIR = ROOT / "results" / "tables"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INPUT_FILE)

print("\nAI GOVERNANCE ATLAS — STAGE 7.2")
print("=" * 60)


# --------------------------------------------------
# 2. GOVERNANCE DIMENSION MATRIX
# --------------------------------------------------

dimension_matrix = pd.crosstab(
    df["country"],
    df["governance_dimension"]
)

dimension_matrix.to_csv(
    OUTPUT_DIR / "comparative_governance_matrix.csv"
)

print("\n1. GOVERNANCE DIMENSION MATRIX")
print("-" * 50)
print(dimension_matrix.to_string())


# --------------------------------------------------
# 3. OBLIGATION TYPE MATRIX
# --------------------------------------------------

obligation_matrix = pd.crosstab(
    df["country"],
    df["obligation_type"]
)

obligation_matrix.to_csv(
    OUTPUT_DIR / "comparative_obligation_matrix.csv"
)

print("\n2. OBLIGATION TYPE MATRIX")
print("-" * 50)
print(obligation_matrix.to_string())


# --------------------------------------------------
# 4. RESPONSIBILITY CATEGORY MATRIX
# Multiple categories per provision are allowed.
# --------------------------------------------------

responsibility_long = df[
    ["id", "country", "responsibility_categories"]
].copy()

responsibility_long["responsibility_category"] = (
    responsibility_long["responsibility_categories"]
    .fillna("")
   .str.split(" | ", regex=False)
)

responsibility_long = responsibility_long.explode(
    "responsibility_category"
)

responsibility_matrix = pd.crosstab(
    responsibility_long["country"],
    responsibility_long["responsibility_category"]
)

responsibility_matrix.to_csv(
    OUTPUT_DIR / "comparative_responsibility_matrix.csv"
)

print("\n3. RESPONSIBILITY CATEGORY MATRIX")
print("-" * 50)
print(responsibility_matrix.to_string())


# --------------------------------------------------
# 5. ENFORCEMENT CATEGORY MATRIX
# Multiple categories per provision are allowed.
# --------------------------------------------------

enforcement_long = df[
    ["id", "country", "enforcement_categories"]
].copy()

enforcement_long["enforcement_category"] = (
    enforcement_long["enforcement_categories"]
    .fillna("")
   .str.split(" | ", regex=False)
)

enforcement_long = enforcement_long.explode(
    "enforcement_category"
)

enforcement_matrix = pd.crosstab(
    enforcement_long["country"],
    enforcement_long["enforcement_category"]
)

enforcement_matrix.to_csv(
    OUTPUT_DIR / "comparative_enforcement_matrix.csv"
)

print("\n4. ENFORCEMENT CATEGORY MATRIX")
print("-" * 50)
print(enforcement_matrix.to_string())


# --------------------------------------------------
# 6. COMBINED GOVERNANCE SUMMARY
# --------------------------------------------------

combined_summary = (
    df.groupby(
        ["country", "governance_dimension", "obligation_type"],
        dropna=False
    )
    .size()
    .reset_index(name="provision_count")
)

combined_summary.to_csv(
    OUTPUT_DIR / "combined_governance_summary.csv",
    index=False
)


# --------------------------------------------------
# 7. PROVISION-LEVEL COMPARATIVE DATA
# --------------------------------------------------

selected_columns = [
    "id",
    "country",
    "document",
    "governance_dimension",
    "secondary_dimension",
    "legal_status",
    "obligation_type",
    "responsible_party",
    "responsibility_categories",
    "enforcement_mechanism",
    "enforcement_categories",
    "applicability_status",
    "implementation_status",
    "implementation_notes"
]

provision_audit = df[selected_columns].copy()

provision_audit.to_csv(
    OUTPUT_DIR / "comparative_provision_audit.csv",
    index=False
)


# --------------------------------------------------
# 8. RECORD COUNT CHECK
# --------------------------------------------------

print("\n5. DATASET CHECK")
print("-" * 50)
print("Total provisions:", len(df))
print("\nRecords by group:")
print(df["country"].value_counts().to_string())

print("\nOECD remains a separate international benchmark.")
print("Responsibility and enforcement categories may overlap.")

print("\nOUTPUT FILES CREATED")
print("-" * 50)

files = [
    "comparative_governance_matrix.csv",
    "comparative_obligation_matrix.csv",
    "comparative_responsibility_matrix.csv",
    "comparative_enforcement_matrix.csv",
    "combined_governance_summary.csv",
    "comparative_provision_audit.csv"
]

for file in files:
    print(file)

print("\nStage 7.2 completed successfully.")
