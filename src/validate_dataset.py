
import pandas as pd
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = PROJECT_ROOT / "data" / "annotated" / "governance_dataset.csv"
OUTPUT_FILE = PROJECT_ROOT / "results" / "tables" / "dataset_validation_report.txt"

# Load dataset
df = pd.read_csv(INPUT_FILE)

print("\nAI GOVERNANCE ATLAS — DATA VALIDATION")
print("=" * 50)

# 1. Basic information
print("\n1. DATASET OVERVIEW")
print("-" * 30)
print(f"Total records: {len(df)}")
print(f"Total columns: {len(df.columns)}")

# 2. Missing values
print("\n2. MISSING VALUES")
print("-" * 30)

missing = df.isnull().sum()
missing = missing[missing > 0]

if missing.empty:
    print("No missing values found.")
else:
    print(missing)

# 3. Duplicate records
print("\n3. DUPLICATE CHECK")
print("-" * 30)

print(f"Duplicate IDs: {df['id'].duplicated().sum()}")
print(f"Duplicate complete rows: {df.duplicated().sum()}")

# 4. Country distribution
print("\n4. RECORDS BY JURISDICTION / BENCHMARK")
print("-" * 30)
print(df["country"].value_counts().to_string())

# 5. Governance dimension distribution
print("\n5. GOVERNANCE DIMENSIONS")
print("-" * 30)
print(df["governance_dimension"].value_counts().to_string())

# 6. Legal status distribution
print("\n6. LEGAL STATUS")
print("-" * 30)
print(df["legal_status"].value_counts().to_string())

# 7. Obligation type distribution
print("\n7. OBLIGATION TYPE")
print("-" * 30)
print(df["obligation_type"].value_counts().to_string())

# 8. Applicability status
print("\n8. APPLICABILITY STATUS")
print("-" * 30)
print(df["applicability_status"].value_counts().to_string())

# 9. Implementation status
print("\n9. IMPLEMENTATION STATUS")
print("-" * 30)
print(df["implementation_status"].value_counts().to_string())

# 10. Check expected columns
print("\n10. REQUIRED COLUMN CHECK")
print("-" * 30)

required_columns = [
    "id", "country", "document", "document_type",
    "legal_status", "article_or_section", "page_number",
    "governance_dimension", "exact_text",
    "provision_summary", "obligation_type",
    "responsible_party", "applicability",
    "enforcement_mechanism", "source_reference",
    "verification_notes", "version_used",
    "secondary_dimension", "applicability_status",
    "implementation_status", "implementation_notes"
]

missing_columns = [
    col for col in required_columns if col not in df.columns
]

if missing_columns:
    print("Missing columns:", missing_columns)
else:
    print("All required columns are present.")

# 11. Save report
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

report = [
    "AI GOVERNANCE ATLAS — DATA VALIDATION REPORT",
    "=" * 50,
    f"Total records: {len(df)}",
    f"Total columns: {len(df.columns)}",
    f"Duplicate IDs: {df['id'].duplicated().sum()}",
    f"Duplicate rows: {df.duplicated().sum()}",
    f"Missing columns: {missing_columns}",
    "",
    "Missing values:",
    missing.to_string() if not missing.empty else "None",
    "",
    "Records by jurisdiction / benchmark:",
    df["country"].value_counts().to_string(),
    "",
    "Governance dimensions:",
    df["governance_dimension"].value_counts().to_string(),
    "",
    "Obligation types:",
    df["obligation_type"].value_counts().to_string(),
    "",
    "Applicability status:",
    df["applicability_status"].value_counts().to_string(),
    "",
    "Implementation status:",
    df["implementation_status"].value_counts().to_string()
]

OUTPUT_FILE.write_text("\n".join(report), encoding="utf-8")

print("\n" + "=" * 50)
print("VALIDATION REPORT SAVED")
print(OUTPUT_FILE)
print("\nValidation script completed.")
