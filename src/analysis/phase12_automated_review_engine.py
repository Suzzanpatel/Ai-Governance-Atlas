"""
AI Governance Atlas — Phase 12 Automated Review Engine

Purpose
-------
Processes every row in verification_audit.csv and creates:
1. An automated review register with a row-by-row assessment.
2. A summary report with counts and unresolved items.
3. A proposed-change queue for human/legal review.

IMPORTANT METHODOLOGICAL LIMITATION
-----------------------------------
This is a deterministic triage and consistency engine. It does NOT use an
LLM, independently retrieve legal sources, or prove that a legal correction
is correct. The audit's finding_and_evidence text is treated as a review
instruction, not as a complete replacement value.

The engine deliberately does NOT overwrite governance_dataset.csv and does
NOT auto-approve legal changes. It identifies cases that appear mechanical,
cases needing evidence, and cases requiring substantive legal review.

Run from the repository root:
    python src/analysis/phase12_automated_review_engine.py
"""

from __future__ import annotations

from pathlib import Path
from datetime import date
import re
import sys

import pandas as pd


# ---------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = ROOT / "data" / "annotated" / "governance_dataset.csv"
AUDIT_FILE = ROOT / "research" / "evidence" / "verification_audit.csv"
EVIDENCE_FILE = ROOT / "research" / "evidence" / "stage_9_evidence_pack.json"

OUTPUT_DIR = ROOT / "results" / "phase12"
REGISTER_FILE = OUTPUT_DIR / "AI_Governance_Atlas_Phase12_Automated_Review.csv"
QUEUE_FILE = OUTPUT_DIR / "AI_Governance_Atlas_Phase12_Human_Review_Queue.csv"
REPORT_FILE = OUTPUT_DIR / "AI_Governance_Atlas_Phase12_Automated_Review_Report.md"


# ---------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------

def clean_text(value) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def classify_finding(field: str, finding: str) -> tuple[str, str, str]:
    """
    Return (automated_status, recommended_action, reason).

    This function classifies the nature of an audit finding. It does not
    decide the legal merits of the finding.
    """
    text = finding.lower()
    field = field.lower()

    # Evidence gaps and caveats take priority.
    evidence_terms = (
        "not verified", "not independently re-verified", "not verified",
        "check against", "check whether", "verify whether",
        "could not be confirmed", "page-count match",
        "taken only through", "eur-lex web view", "needs javascript",
        "confirm that", "further evidence",
    )
    if any(term in text for term in evidence_terms):
        return (
            "FURTHER_EVIDENCE_REQUIRED",
            "Obtain and record the specified primary-source evidence before changing the dataset.",
            "The audit finding explicitly identifies an unresolved source, page, date, or verification gap.",
        )

    # Changes that affect legal meaning, scope, duty-holders, enforcement,
    # obligations, or legal status require a human legal check.
    legal_terms = (
        "obligation", "obligations", "duty", "duty-holder", "binding",
        "non-binding", "fine", "fines", "sanction", "enforcement",
        "responsible", "responsibility", "applicability", "applies",
        "amended", "article 4a", "article 99", "article 113",
        "government", "regulator", "regulators", "undertaking",
        "sme", "smc", "legal", "permission", "permits",
    )
    if field in {
        "legal_status", "responsible_party", "applicability",
        "enforcement_mechanism", "obligation_type",
    } or any(term in text for term in legal_terms):
        return (
            "HUMAN_LEGAL_REVIEW_REQUIRED",
            "Prepare a revised value from the primary source and obtain human legal sign-off.",
            "The proposed change may affect legal interpretation, legal scope, responsibility, or enforcement.",
        )

    # Citation/heading/wording corrections are often mechanical, but still
    # require checking the cited source and confirming the replacement text.
    mechanical_terms = (
        "heading completed", "title added", "mis-cited", "citation split",
        "added the", "removed the attribution", "removed '",
        "reworded", "aligned", "added oj page", "page reference",
    )
    if any(term in text for term in mechanical_terms):
        return (
            "SOURCE_CHECKED_DRAFT_REQUIRED",
            "Prepare a draft edit and verify the exact wording/page against the cited source.",
            "The finding appears editorial or citation-focused, but the replacement text is not fully encoded in the audit row.",
        )

    return (
        "HUMAN_REVIEW_REQUIRED",
        "Compare the original field with the cited evidence and draft a replacement if justified.",
        "The audit finding does not contain enough structured information for a safe automatic replacement.",
    )


def get_original_value(dataset: pd.DataFrame, provision_id: str, field: str) -> str:
    if field not in dataset.columns:
        return ""
    matches = dataset.loc[dataset["id"].astype(str) == provision_id, field]
    if matches.empty:
        return ""
    return clean_text(matches.iloc[0])


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------

def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for path in (DATA_FILE, AUDIT_FILE, EVIDENCE_FILE):
        if not path.exists():
            print(f"ERROR: Required input file not found: {path}")
            return 1

    dataset = pd.read_csv(DATA_FILE, dtype=str).fillna("")
    audit = pd.read_csv(AUDIT_FILE, dtype=str).fillna("")

    required_dataset_cols = {"id", "country"}
    required_audit_cols = {
        "id", "column", "verdict", "finding_and_evidence", "audit_date"
    }

    if not required_dataset_cols.issubset(dataset.columns):
        print(f"ERROR: Dataset must contain {sorted(required_dataset_cols)}")
        return 1

    if not required_audit_cols.issubset(audit.columns):
        print(f"ERROR: Audit must contain {sorted(required_audit_cols)}")
        return 1

    if dataset["id"].duplicated().any():
        print("ERROR: Duplicate IDs found in the annotated dataset.")
        return 1

    if audit[["id", "column", "verdict"]].eq("").any().any():
        print("ERROR: Blank ID, column, or verdict found in the audit.")
        return 1

    allowed_verdicts = {"Verified", "Corrected", "Verified with caveat"}
    unexpected = set(audit["verdict"]) - allowed_verdicts
    if unexpected:
        print(f"ERROR: Unexpected audit verdicts: {sorted(unexpected)}")
        return 1

    dataset_ids = set(dataset["id"].astype(str))
    audit_ids = set(audit["id"].astype(str))
    if not audit_ids.issubset(dataset_ids):
        print("ERROR: Audit contains provision IDs absent from the dataset.")
        return 1

    # Only findings requiring a correction or caveat need an action queue.
    actionable = audit[audit["verdict"].isin(
        ["Corrected", "Verified with caveat"]
    )].copy()

    rows = []
    for _, audit_row in actionable.iterrows():
        provision_id = clean_text(audit_row["id"])
        field = clean_text(audit_row["column"])
        finding = clean_text(audit_row["finding_and_evidence"])
        verdict = clean_text(audit_row["verdict"])
        original = get_original_value(dataset, provision_id, field)

        if verdict == "Verified with caveat":
            status = "FURTHER_EVIDENCE_REQUIRED"
            action = "Resolve the caveat and record primary-source evidence; do not change the dataset yet."
            reason = "The source audit explicitly marked this item as verified with a caveat."
        else:
            status, action, reason = classify_finding(field, finding)

        rows.append({
            "id": provision_id,
            "country": get_original_value(dataset, provision_id, "country"),
            "field_to_review": field,
            "audit_verdict": verdict,
            "original_value": original,
            "audit_finding_and_evidence": finding,
            "automated_status": status,
            "recommended_action": action,
            "classification_reason": reason,
            "draft_revised_value": "",
            "reviewer_decision": "Pending",
            "reviewer_comments": "",
            "review_date": date.today().isoformat(),
        })

    review = pd.DataFrame(rows)

    if review.empty:
        print("No correction findings or caveats found. Nothing to process.")
        return 0

    # Human queue contains only unresolved / non-verified findings.
    queue = review[[
        "id", "country", "field_to_review", "audit_verdict",
        "original_value", "audit_finding_and_evidence",
        "automated_status", "recommended_action", "classification_reason"
    ]].copy()

    review.to_csv(REGISTER_FILE, index=False, encoding="utf-8-sig")
    queue.to_csv(QUEUE_FILE, index=False, encoding="utf-8-sig")

    status_counts = review["automated_status"].value_counts().to_dict()
    verdict_counts = review["audit_verdict"].value_counts().to_dict()

    report_lines = [
        "# AI Governance Atlas",
        "## Phase 12: Automated Review Engine",
        "",
        "### Scope",
        "",
        f"- Annotated dataset records: {len(dataset)}",
        f"- Total audit checks: {len(audit)}",
        f"- Correction/caveat findings processed: {len(review)}",
        f"- Correction findings: {verdict_counts.get('Corrected', 0)}",
        f"- Caveats: {verdict_counts.get('Verified with caveat', 0)}",
        "",
        "### Automated triage results",
        "",
        "| Automated status | Findings |",
        "|---|---:|",
    ]

    for status, count in sorted(status_counts.items()):
        report_lines.append(f"| {status} | {count} |")

    report_lines += [
        "",
        "### Methodological safeguards",
        "",
        "- This is deterministic triage, not independent legal verification.",
        "- Audit findings are not treated as complete replacement wording.",
        "- No legal correction is automatically approved.",
        "- The original annotated dataset is not modified.",
        "- Draft revised values remain blank until prepared from and checked against primary sources.",
        "- Evidence caveats remain unresolved until supporting evidence is recorded.",
        "",
        "### Output files",
        "",
        f"- `{REGISTER_FILE.name}`",
        f"- `{QUEUE_FILE.name}`",
        f"- `{REPORT_FILE.name}`",
        "",
    ]

    REPORT_FILE.write_text("\n".join(report_lines), encoding="utf-8")

    print("\nAI GOVERNANCE ATLAS")
    print("PHASE 12: AUTOMATED REVIEW ENGINE")
    print("-" * 55)
    print("Dataset records:", len(dataset))
    print("Audit checks:", len(audit))
    print("Findings processed:", len(review))
    print("Correction findings:", verdict_counts.get("Corrected", 0))
    print("Caveats:", verdict_counts.get("Verified with caveat", 0))
    print("\nAUTOMATED CLASSIFICATION")
    for status, count in sorted(status_counts.items()):
        print(f"{status}: {count}")

    print("\nFiles generated:")
    print(REGISTER_FILE)
    print(QUEUE_FILE)
    print(REPORT_FILE)
    print("\nOriginal annotated dataset was not modified.")
    print("No legal corrections were automatically applied.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
