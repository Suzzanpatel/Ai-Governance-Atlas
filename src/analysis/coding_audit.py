
import pandas as pd
from pathlib import Path

# Project paths
ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = ROOT / "data" / "annotated" / "governance_dataset.csv"
OUTPUT_DIR = ROOT / "results" / "phase12"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load dataset
df = pd.read_csv(DATA_FILE)

print("\nAI GOVERNANCE ATLAS")
print("PHASE 12: CODING CONSISTENCY AUDIT")

# 1. Basic dataset checks
print("\n--- DATASET OVERVIEW ---")
print("Rows:", len(df))
print("Columns:", len(df.columns))
print("Duplicate IDs:", df["id"].duplicated().sum())
print("Duplicate rows:", df.duplicated().sum())

# 2. Missing values
print("\n--- MISSING VALUES ---")
missing = df.isnull().sum()
print(missing[missing > 0])

# 3. Jurisdiction distribution
print("\n--- JURISDICTION DISTRIBUTION ---")
print(df["country"].value_counts())

# 4. Governance dimension distribution
print("\n--- GOVERNANCE DIMENSIONS ---")
print(df["governance_dimension"].value_counts())

# 5. Jurisdiction vs governance dimension
print("\n--- JURISDICTION x DIMENSION ---")
dimension_matrix = pd.crosstab(
    df["country"],
    df["governance_dimension"]
)
print(dimension_matrix.to_string())
print("\n--- JURISDICTION x OBLIGATION TYPE ---")

obligation_matrix = pd.crosstab(
    df["country"],
    df["obligation_type"]
)

print(obligation_matrix.to_string())


print("\n--- JURISDICTION x IMPLEMENTATION STATUS ---")

implementation_matrix = pd.crosstab(
    df["country"],
    df["implementation_status"]
)

print(implementation_matrix.to_string())


# Save additional audit outputs

obligation_matrix.to_csv(
    OUTPUT_DIR / "jurisdiction_obligation_matrix.csv"
)

implementation_matrix.to_csv(
    OUTPUT_DIR / "jurisdiction_implementation_matrix.csv"
)
# 6. Legal status distribution
print("\n--- LEGAL STATUS ---")
print(df["legal_status"].value_counts())

# 7. Obligation classification
print("\n--- OBLIGATION TYPES ---")
print(df["obligation_type"].value_counts())

# 8. Implementation status
print("\n--- IMPLEMENTATION STATUS ---")
print(df["implementation_status"].value_counts())

# 10. Detailed record-level classification review

print("\n--- RECORD LEVEL CODING REVIEW ---")

review_columns = [
    "id",
    "country",
    "governance_dimension",
    "legal_status",
    "obligation_type",
    "implementation_status"
]

print(df[review_columns].to_string(index=False))

# Export detailed review
df[review_columns].to_csv(
    OUTPUT_DIR / "record_level_coding_review.csv",
    index=False
)

print("\nRecord-level coding review exported.")

# 9. Save audit outputs
dimension_matrix.to_csv(
    OUTPUT_DIR / "jurisdiction_dimension_matrix.csv"
)

df.groupby(
    ["country", "legal_status"]
).size().to_csv(
    OUTPUT_DIR / "legal_status_distribution.csv"
)

df.groupby(
    ["country", "obligation_type"]
).size().to_csv(
    OUTPUT_DIR / "obligation_distribution.csv"
)

print("\nPhase 12 initial audit completed.")
print("Results saved in:", OUTPUT_DIR)
