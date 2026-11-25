
from pathlib import Path
import pandas as pd

# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "results" / "phase12"

DATA_FILE = ROOT / "data" / "annotated" / "governance_dataset.csv"
REGISTER_FILE = (
    OUTPUT_DIR / "AI_Governance_Atlas_Phase12_Correction_Register.csv"
)

REVISED_DATA_FILE = (
    OUTPUT_DIR / "governance_dataset_phase12_revised.csv"
)
CHANGE_LOG_FILE = (
    OUTPUT_DIR / "phase12_approved_corrections_change_log.csv"
)

# --------------------------------------------------
# LOAD AND VALIDATE FILES
# --------------------------------------------------

for file_path in [DATA_FILE, REGISTER_FILE]:
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

original_df = pd.read_csv(DATA_FILE).fillna("")
register = pd.read_csv(REGISTER_FILE).fillna("")

required_columns = [
    "id",
    "field_to_review",
    "review_decision",
    "approved_revised_value",
    "reviewer_comments",
]

missing_columns = [
    column for column in required_columns
    if column not in register.columns
]

if missing_columns:
    raise ValueError(f"Missing register columns: {missing_columns}")

if original_df["id"].duplicated().any():
    raise ValueError("Duplicate provision IDs in original dataset.")

if register.duplicated(["id", "field_to_review"]).any():
    raise ValueError("Duplicate provision and field combinations found.")

allowed_decisions = {"Pending", "Approve", "Reject", "Needs evidence"}

register["review_decision"] = (
    register["review_decision"].astype(str).str.strip()
)

unexpected = set(register["review_decision"]) - allowed_decisions

if unexpected:
    raise ValueError(f"Invalid review decisions: {unexpected}")

# --------------------------------------------------
# APPLY ONLY EXPLICITLY APPROVED CORRECTIONS
# --------------------------------------------------

revised_df = original_df.copy()
change_log = []

for _, row in register.iterrows():

    if row["review_decision"] != "Approve":
        continue

    provision_id = row["id"]
    field_name = row["field_to_review"]
    new_value = row["approved_revised_value"]

    if field_name not in revised_df.columns:
        raise ValueError(
            f"Field '{field_name}' does not exist in the dataset."
        )

    if provision_id not in set(revised_df["id"]):
        raise ValueError(
            f"Provision ID '{provision_id}' not found in dataset."
        )

    if str(new_value).strip() == "":
        raise ValueError(
            f"Approved correction for {provision_id} / {field_name} "
            "has no approved revised value."
        )

    record_index = revised_df.index[
        revised_df["id"] == provision_id
    ][0]

    old_value = revised_df.at[record_index, field_name]

    revised_df.at[record_index, field_name] = new_value

    change_log.append({
        "id": provision_id,
        "field": field_name,
        "original_value": old_value,
        "approved_revised_value": new_value,
        "review_decision": "Approve",
        "reviewer_comments": row["reviewer_comments"],
    })

# --------------------------------------------------
# EXPORT REVISED DATASET AND CHANGE LOG
# --------------------------------------------------

revised_df.to_csv(
    REVISED_DATA_FILE,
    index=False,
    encoding="utf-8-sig"
)

change_log_df = pd.DataFrame(
    change_log,
    columns=[
        "id",
        "field",
        "original_value",
        "approved_revised_value",
        "review_decision",
        "reviewer_comments",
    ],
)

change_log_df.to_csv(
    CHANGE_LOG_FILE,
    index=False,
    encoding="utf-8-sig"
)

# --------------------------------------------------
# COMPLETION SUMMARY
# --------------------------------------------------

decision_counts = register["review_decision"].value_counts()

print("\nAI GOVERNANCE ATLAS")
print("PHASE 12: APPROVED CORRECTION WORKFLOW")
print("-" * 50)

print("Total correction findings:", len(register))
print("Approved:", decision_counts.get("Approve", 0))
print("Rejected:", decision_counts.get("Reject", 0))
print("Needs evidence:", decision_counts.get("Needs evidence", 0))
print("Pending:", decision_counts.get("Pending", 0))

print("Corrections applied:", len(change_log_df))

print("\nFiles generated:")
print(REVISED_DATA_FILE)
print(CHANGE_LOG_FILE)

print("\nOriginal annotated dataset was not modified.")
print("Approval workflow completed.")
