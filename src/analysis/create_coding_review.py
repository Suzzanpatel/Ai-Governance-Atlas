
import pandas as pd
from pathlib import Path

# Project paths
ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = ROOT / "data" / "annotated" / "governance_dataset.csv"
OUTPUT_DIR = ROOT / "results" / "phase12"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load original dataset
df = pd.read_csv(DATA_FILE)

print("\nAI GOVERNANCE ATLAS")
print("PHASE 12D: MANUAL RECODING REVIEW")

# Required source columns
required_columns = [
    "id",
    "country",
    "exact_text",
    "provision_summary",
    "legal_status",
    "obligation_type",
    "responsible_party",
    "enforcement_mechanism",
    "implementation_status",
    "source_reference"
]

missing_columns = [
    col for col in required_columns if col not in df.columns
]

if missing_columns:
    raise ValueError(f"Missing columns: {missing_columns}")

# Preserve original classifications
review = df[required_columns].copy()

# Add separate review fields
review["obligation_force_review"] = ""
review["obligation_nature_review"] = ""
review["responsible_actor_review"] = ""
review["enforcement_mechanism_review"] = ""
review["implementation_evidence_review"] = ""
review["coding_rationale"] = ""
review["reviewer_source"] = ""
review["reviewer_decision"] = "Pending"

# Save review template
output_file = OUTPUT_DIR / "coding_review_template.csv"

review.to_csv(output_file, index=False)

print("\nRecords prepared:", len(review))
print("Original classifications preserved.")
print("New review fields created.")
print("Output:", output_file)
print("\nPhase 12D template created successfully.")
