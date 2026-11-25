
import json
from pathlib import Path

import pandas as pd


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = ROOT / "data" / "annotated" / "governance_dataset.csv"
EVIDENCE_FILE = ROOT / "research" / "evidence" / "stage_9_evidence_pack.json"
AUDIT_FILE = ROOT / "research" / "evidence" / "verification_audit.csv"
TEMPLATE_FILE = ROOT / "results" / "phase12" / "coding_review_template.csv"

OUTPUT_DIR = ROOT / "results" / "phase12"

REVIEW_CSV = OUTPUT_DIR / "AI_Governance_Atlas_Phase12_Consolidated_Review.csv"
REVIEW_REPORT = OUTPUT_DIR / "AI_Governance_Atlas_Phase12_Consolidated_Review_Report.md"


# --------------------------------------------------
# VALIDATE INPUT FILES
# --------------------------------------------------

required_files = [
    DATA_FILE,
    EVIDENCE_FILE,
    AUDIT_FILE,
    TEMPLATE_FILE,
]

for file in required_files:
    if not file.exists():
        raise FileNotFoundError(f"Required file not found: {file}")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# LOAD PROJECT DATA
# --------------------------------------------------

df = pd.read_csv(DATA_FILE).fillna("")
audit = pd.read_csv(AUDIT_FILE).fillna("")
template = pd.read_csv(TEMPLATE_FILE).fillna("")

with open(EVIDENCE_FILE, "r", encoding="utf-8") as file:
    evidence_pack = json.load(file)

print("\nAI GOVERNANCE ATLAS")
print("PHASE 12: CONSOLIDATED REVIEW GENERATOR")
print("-" * 55)


# --------------------------------------------------
# CHECK DATA INTEGRITY
# --------------------------------------------------

if df["id"].duplicated().any():
    raise ValueError("Duplicate IDs found in the annotated dataset.")

if audit[["id", "column", "verdict"]].isnull().any().any():
    raise ValueError("Missing ID, column or verdict in verification audit.")

if set(df["id"]) != set(audit["id"]):
    raise ValueError("Dataset and verification audit contain different IDs.")

if len(df) != 20:
    print(f"WARNING: Expected 20 provisions, found {len(df)}.")

if not isinstance(evidence_pack.get("provisions"), list):
    raise ValueError("Evidence pack does not contain a provisions list.")

evidence_ids = {
    item.get("id")
    for item in evidence_pack["provisions"]
    if isinstance(item, dict)
}

if set(df["id"]) != evidence_ids:
    raise ValueError("Dataset and evidence pack IDs do not match.")

print("Dataset records:", len(df))
print("Audit checks:", len(audit))
print("Evidence pack records:", len(evidence_ids))


# --------------------------------------------------
# CHECK AUDIT VERDICTS
# --------------------------------------------------

allowed_verdicts = {
    "Verified",
    "Corrected",
    "Verified with caveat",
}

unexpected = set(audit["verdict"]) - allowed_verdicts

if unexpected:
    raise ValueError(f"Unexpected audit verdicts: {unexpected}")

verdict_counts = audit["verdict"].value_counts().to_dict()

print("\nAUDIT VERDICTS")

for verdict in sorted(allowed_verdicts):
    print(f"{verdict}: {verdict_counts.get(verdict, 0)}")


# --------------------------------------------------
# PREPARE REVIEW TEMPLATE
# --------------------------------------------------

review = template.copy()

if review["id"].duplicated().any():
    raise ValueError("Duplicate IDs found in the review template.")

if set(review["id"]) != set(df["id"]):
    raise ValueError("Review template and dataset IDs do not match.")

# Keep the template's original column structure.
review = review.set_index("id")
dataset = df.set_index("id")


# --------------------------------------------------
# MAP ORIGINAL DATA INTO REVIEW TEMPLATE
# --------------------------------------------------

field_mapping = {
    "country": "country",
    "exact_text": "exact_text",
    "provision_summary": "provision_summary",
    "legal_status": "legal_status",
    "obligation_type": "obligation_type",
    "responsible_party": "responsible_party",
    "enforcement_mechanism": "enforcement_mechanism",
    "implementation_status": "implementation_status",
    "source_reference": "source_reference",
}

for review_column, dataset_column in field_mapping.items():
    if review_column in review.columns:
        review[review_column] = dataset[dataset_column]


# --------------------------------------------------
# GROUP AUDIT FINDINGS BY PROVISION
# --------------------------------------------------

audit_groups = {
    provision_id: group.copy()
    for provision_id, group in audit.groupby("id")
}


def findings_for(provision_id, verdict=None):
    group = audit_groups[provision_id]

    if verdict:
        group = group[group["verdict"] == verdict]

    return group


def findings_text(group):
    if group.empty:
        return ""

    return "\n".join(
        f"[{row['column']}] {row['verdict']}: "
        f"{row['finding_and_evidence']}"
        for _, row in group.iterrows()
    )


# --------------------------------------------------
# GENERATE ONE REVIEW RECORD PER PROVISION
# --------------------------------------------------

for provision_id in review.index:

    original = dataset.loc[provision_id]
    group = audit_groups[provision_id]

    corrections = findings_for(provision_id, "Corrected")
    caveats = findings_for(provision_id, "Verified with caveat")
    verified = findings_for(provision_id, "Verified")

    all_findings = findings_text(group)
    correction_text = findings_text(corrections)

    # Source and audit information
    review.loc[provision_id, "reviewer_source"] = (
        "Annotated dataset; Stage 9 evidence pack; "
        "verification_audit.csv; source references recorded in dataset."
    )

    review.loc[provision_id, "source_verification_notes"] = all_findings

    review.loc[provision_id, "primary_source_reference"] = (
        original["source_reference"]
    )

    review.loc[provision_id, "review_date"] = (
        group["audit_date"].dropna().astype(str).max()
        if not group["audit_date"].empty else ""
    )

    # Link findings to relevant review fields
    for audit_column, review_column in [
        ("legal_status", "legal_force_review"),
        ("legal_status", "obligation_force_review"),
        ("responsible_party", "responsible_actor_review"),
        ("enforcement_mechanism", "enforcement_mechanism_review"),
    ]:
        relevant = group[group["column"] == audit_column]

        if not relevant.empty:
            review.loc[provision_id, review_column] = findings_text(
                relevant
            )

    # Retain original dimension coding as a reference.
    # It is not independently verified by the nine-field audit.
    review.loc[provision_id, "primary_governance_dimension_review"] = (
        original["governance_dimension"]
    )

    review.loc[provision_id, "secondary_governance_dimension_review"] = (
        original["secondary_dimension"]
    )

    review.loc[provision_id, "coding_rationale"] = (
        "Original coding retained for review. "
        "The verification audit does not independently assess "
        "governance-dimension classification."
    )

    # Implementation evidence is not covered by the nine audited fields.
    review.loc[provision_id, "implementation_evidence_review"] = (
        "Not independently assessed by the current verification audit. "
        "Additional implementation evidence and human review are required."
    )

    review.loc[
        provision_id, "implementation_evidence_summary_review"
    ] = original["implementation_notes"]

    # Record corrections as findings, not automatic dataset changes.
    review.loc[provision_id, "change_rationale"] = correction_text

    # Determine review status.
    if not caveats.empty:
        decision = "Further evidence required"
    elif not corrections.empty:
        decision = "Correction review required"
    else:
        decision = "Source audit passed - human sign-off required"

    review.loc[provision_id, "reviewer_decision"] = decision

    # The original dataset is never modified by this script.


# --------------------------------------------------
# EXPORT CONSOLIDATED REVIEW CSV
# --------------------------------------------------

review = review.reset_index()

review.to_csv(
    REVIEW_CSV,
    index=False,
    encoding="utf-8-sig"
)

print("\nConsolidated review CSV generated.")


# --------------------------------------------------
# GENERATE MARKDOWN REPORT
# --------------------------------------------------

correction_rows = audit[audit["verdict"] == "Corrected"]
caveat_rows = audit[audit["verdict"] == "Verified with caveat"]

report = []

report.append("# AI Governance Atlas")
report.append("## Phase 12: Consolidated Coding and Evidence Review")
report.append("")
report.append("### 1. Review overview")
report.append("")
report.append(f"- Dataset provisions: {len(df)}")
report.append(f"- Audit checks: {len(audit)}")
report.append(f"- Evidence-pack provisions: {len(evidence_ids)}")
report.append("")

report.append("### 2. Verification audit results")
report.append("")
report.append("| Verdict | Checks |")
report.append("|---|---:|")

for verdict in [
    "Verified",
    "Corrected",
    "Verified with caveat",
]:
    report.append(
        f"| {verdict} | {verdict_counts.get(verdict, 0)} |"
    )

report.append("")
report.append(
    "**Important:** A `Corrected` audit verdict records a proposed "
    "correction or finding. It does not mean the original annotated "
    "dataset has been updated."
)
report.append("")

report.append("### 3. Record-level review")
report.append("")
report.append("| ID | Country | Corrections | Caveats | Review decision |")
report.append("|---|---|---:|---:|---|")

for _, row in review.iterrows():
    provision_id = row["id"]
    group = audit_groups[provision_id]

    correction_count = len(
        group[group["verdict"] == "Corrected"]
    )
    caveat_count = len(
        group[group["verdict"] == "Verified with caveat"]
    )

    report.append(
        f"| {provision_id} | {row['country']} | "
        f"{correction_count} | {caveat_count} | "
        f"{row['reviewer_decision']} |"
    )

report.append("")
report.append("### 4. Proposed corrections")
report.append("")

if correction_rows.empty:
    report.append("No correction findings recorded.")
else:
    for _, row in correction_rows.iterrows():
        report.append(
            f"#### {row['id']} - {row['column']}"
        )
        report.append("")
        report.append(str(row["finding_and_evidence"]))
        report.append("")

report.append("### 5. Findings requiring further evidence")
report.append("")

if caveat_rows.empty:
    report.append("No caveats recorded.")
else:
    for _, row in caveat_rows.iterrows():
        report.append(
            f"- **{row['id']} - {row['column']}:** "
            f"{row['finding_and_evidence']}"
        )

report.append("")
report.append("### 6. Methodological limitations")
report.append("")
report.append(
    "- The audit covers nine fields per provision."
)
report.append(
    "- Governance-dimension coding is retained as supplied; "
    "it is not independently verified by this audit."
)
report.append(
    "- Implementation status is not independently verified "
    "by the nine-field audit."
)
report.append(
    "- Legal interpretation and proposed changes require "
    "human review before adoption."
)
report.append(
    "- Automated generation does not constitute legal verification."
)
report.append(
    "- The original annotated dataset remains unchanged."
)

report.append("")
report.append("### 7. Output files")
report.append("")
report.append(
    "- `AI_Governance_Atlas_Phase12_Consolidated_Review.csv`"
)
report.append(
    "- `AI_Governance_Atlas_Phase12_Consolidated_Review_Report.md`"
)

REVIEW_REPORT.write_text(
    "\n".join(report),
    encoding="utf-8"
)

print("Consolidated review report generated.")

# --------------------------------------------------
# COMPLETION SUMMARY
# --------------------------------------------------

print("\n" + "-" * 55)
print("PHASE 12 REVIEW GENERATION COMPLETED")
print("-" * 55)

print("\nFiles created:")
print(REVIEW_CSV)
print(REVIEW_REPORT)

print("\nOriginal annotated dataset was not modified.")


# --------------------------------------------------
# GENERATE PHASE 12 CORRECTION REGISTER
# --------------------------------------------------

correction_register_rows = []

for _, audit_row in correction_rows.iterrows():
    provision_id = audit_row["id"]
    column_name = audit_row["column"]

    original_record = df.loc[df["id"] == provision_id].iloc[0]

    original_value = (
        original_record[column_name]
        if column_name in df.columns
        else ""
    )

    correction_register_rows.append({
        "id": provision_id,
        "country": original_record["country"],
        "field_to_review": column_name,
        "original_value": original_value,
        "audit_finding_and_proposed_change": audit_row[
            "finding_and_evidence"
        ],
        "audit_date": audit_row["audit_date"],
        "review_decision": "Pending",
        "approved_revised_value": "",
        "reviewer_comments": ""
    })

correction_register = pd.DataFrame(correction_register_rows)

CORRECTION_REGISTER_FILE = (
    OUTPUT_DIR / "AI_Governance_Atlas_Phase12_Correction_Register.csv"
)

correction_register.to_csv(
    CORRECTION_REGISTER_FILE,
    index=False,
    encoding="utf-8-sig"
)

print("\nPhase 12 correction register generated.")
print("Correction findings:", len(correction_register))
print("Output:", CORRECTION_REGISTER_FILE)
