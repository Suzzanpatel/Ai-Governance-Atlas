
import pandas as pd
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = PROJECT_ROOT / "data" / "annotated" / "governance_dataset.csv"
OUTPUT_DIR = PROJECT_ROOT / "results" / "tables"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load dataset
df = pd.read_csv(INPUT_FILE)

print("\nAI GOVERNANCE ATLAS")
print("STAGE 6.2 — COMPARATIVE LEGAL ANALYSIS")
print("=" * 55)

# Columns to compare
analyses = {
    "governance_dimension": "governance_dimensions_by_country.csv",
    "obligation_type": "obligation_types_by_country.csv",
    "responsible_party": "responsible_parties_by_country.csv",
    "applicability_status": "applicability_by_country.csv",
    "implementation_status": "implementation_by_country.csv",
    "enforcement_mechanism": "enforcement_by_country.csv"
}

# Generate comparative tables
for column, filename in analyses.items():

    table = pd.crosstab(
        df["country"],
        df[column],
        dropna=False
    )

    output_path = OUTPUT_DIR / filename
    table.to_csv(output_path)

    print(f"\n{column.upper().replace('_', ' ')}")
    print("-" * 45)
    print(table.to_string())
    print(f"Saved: {filename}")

# Create a provision-level analysis table
selected_columns = [
    "id",
    "country",
    "document",
    "governance_dimension",
    "secondary_dimension",
    "legal_status",
    "obligation_type",
    "responsible_party",
    "applicability_status",
    "enforcement_mechanism",
    "implementation_status"
]

provision_summary = df[selected_columns].copy()

provision_summary.to_csv(
    OUTPUT_DIR / "comparative_provision_summary.csv",
    index=False
)

# Create an overall descriptive summary
overall_summary = (
    df.groupby(
        ["country", "governance_dimension"],
        dropna=False
    )
    .size()
    .reset_index(name="provision_count")
)

overall_summary.to_csv(
    OUTPUT_DIR / "overall_governance_summary.csv",
    index=False
)

print("\n" + "=" * 55)
print("COMPARATIVE ANALYSIS COMPLETED")
print(f"Tables saved in: {OUTPUT_DIR}")
print("Total provisions analysed:", len(df))
