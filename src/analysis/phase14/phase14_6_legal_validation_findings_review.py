#!/usr/bin/env python3
"""
Phase 14.6 — Legal Validation and Findings Review

Creates a quality-control register for the Phase 14 legal research workflow.
It checks whether source validation and legal-analysis fields have been
completed, identifies missing evidence and unsupported conclusions, and
produces a review report.

It does NOT verify law, fetch official sources, decide legal questions, or
change the original dataset or earlier research files.

Run from the project root:
    python src/analysis/phase14/phase14_6_legal_validation_findings_review.py
"""

from pathlib import Path
import csv
import re
from datetime import datetime

ROOT = Path(__file__).resolve().parents[3]

DATASET = ROOT / "data/annotated/governance_dataset.csv"
P14_3 = ROOT / "results/phase14/source_validation/phase14_3_official_source_version_validation_register.csv"
P14_4 = ROOT / "results/phase14/legal_analysis/phase14_4_provision_level_legal_analysis_worksheet.csv"
P14_5_MATRIX = ROOT / "results/phase14/comparative_argument/phase14_5_comparative_legal_argument_matrix.csv"
P14_5_CLAIMS = ROOT / "results/phase14/comparative_argument/phase14_5_claim_evidence_register.csv"

OUT_DIR = ROOT / "results/phase14/legal_validation"
REPORT_DIR = ROOT / "results/phase14/reports"

def read_csv(path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def val(row, *keys):
    for key in keys:
        x = row.get(key, "")
        if x is not None and str(x).strip():
            return str(x).strip()
    return ""

def norm(x):
    return re.sub(r"\s+", " ", str(x or "")).strip()

def yes(x):
    return bool(norm(x)) and norm(x).lower() not in {"none", "n/a", "na", "unknown", "not available"}

def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

def main():
    if not DATASET.exists():
        raise FileNotFoundError(f"Dataset not found: {DATASET}")

    dataset = read_csv(DATASET)
    p14_3 = read_csv(P14_3)
    p14_4 = read_csv(P14_4)
    p14_5 = read_csv(P14_5_MATRIX)
    claims = read_csv(P14_5_CLAIMS)

    def index(rows):
        return {
            val(r, "id", "provision_id"): r
            for r in rows if val(r, "id", "provision_id")
        }

    source_idx = index(p14_3)
    legal_idx = index(p14_4)
    argument_idx = index(p14_5)
    claim_idx = index(claims)

    audit = []
    for d in dataset:
        pid = val(d, "id", "provision_id")
        s = source_idx.get(pid, {})
        l = legal_idx.get(pid, {})
        a = argument_idx.get(pid, {})
        c = claim_idx.get(f"DESC-{pid}", {})

        issues = []
        actions = []

        official_url = val(s, "official_source_url", "source_url", "url")
        publisher = val(s, "official_publisher", "publisher")
        source_title = val(s, "official_source_title", "source_title", "title")
        version = val(s, "version_used", "source_version", "version")
        source_status = val(s, "source_validation_status", "validation_status", "status") or "MISSING_REGISTER_ROW"
        version_status = val(s, "version_status", "version_validation_status") or "NOT_ASSESSED"

        # Read common possible worksheet field names without assuming a schema.
        legal_question = val(l, "legal_question", "issue")
        interpretation = val(l, "legal_interpretation", "interpretation", "analysis")
        scope_analysis = val(l, "scope_analysis", "scope")
        duty_analysis = val(l, "duty_holder_analysis", "responsible_party_analysis")
        enforcement_analysis = val(l, "enforcement_analysis", "enforcement_assessment")
        limitation = val(l, "limitations", "caveats", "unresolved_questions")
        citation = val(l, "verified_citation", "legal_citation", "citation")
        review_status = val(l, "legal_review_status", "review_status") or "NOT_RECORDED"

        proposed_argument = val(a, "proposed_argument")
        supporting_ids = val(a, "supporting_evidence_ids")
        counter_evidence = val(a, "counter_evidence_or_limitation")
        researcher_assessment = val(a, "researcher_legal_assessment")
        confidence = val(a, "confidence") or "NOT_ASSESSED"

        if not s:
            issues.append("No Phase 14.3 source/version register row")
            actions.append("Complete the source/version register for this provision")
        if not official_url:
            issues.append("Official source URL not recorded")
            actions.append("Locate and record the official publisher URL")
        if not publisher:
            issues.append("Official publisher not recorded")
            actions.append("Record the issuing institution or official publisher")
        if not version:
            issues.append("Applicable source version not recorded")
            actions.append("Confirm the version and relevant amendment/commencement date")
        if source_status.upper() not in {"VERIFIED", "CONFIRMED", "VALIDATED"}:
            issues.append(f"Source status is {source_status}")
            actions.append("Human-check the official text, citation, and surrounding provision")
        if version_status.upper() not in {"VERIFIED", "CONFIRMED", "VALIDATED"}:
            issues.append(f"Version status is {version_status}")
            actions.append("Confirm that the selected version is appropriate for the research period")

        if not l:
            issues.append("No Phase 14.4 legal-analysis worksheet row")
            actions.append("Create or restore the provision-level legal-analysis row")
        if not interpretation:
            issues.append("Legal interpretation is blank")
            actions.append("Complete a reasoned interpretation with pinpoint legal support")
        if not scope_analysis:
            issues.append("Scope analysis is blank")
            actions.append("Analyse thresholds, covered actors/systems, exclusions, and conditions")
        if not duty_analysis:
            issues.append("Duty-holder analysis is blank")
            actions.append("Identify the precise duty-holder and the nature of the duty")
        if not enforcement_analysis:
            issues.append("Enforcement analysis is blank")
            actions.append("Distinguish available enforcement powers from evidence of their use")
        if not citation:
            issues.append("Verified legal citation is not recorded")
            actions.append("Add a verified pinpoint citation to the official source")

        if not proposed_argument:
            issues.append("Comparative argument has not been drafted")
            actions.append("Draft a qualified comparison only after source and legal review")
        if proposed_argument and not supporting_ids:
            issues.append("Proposed argument has no supporting evidence IDs")
            actions.append("Link each material claim to provision IDs and source citations")
        if proposed_argument and not counter_evidence:
            issues.append("Counter-evidence/limitations field is blank")
            actions.append("Record contrary evidence, differences in scope, and limitations")
        if proposed_argument and not researcher_assessment:
            issues.append("Researcher legal assessment is blank")
            actions.append("Record the researcher's reasoning and confidence basis")

        if not val(d, "exact_text"):
            issues.append("Dataset exact_text field is blank")
            actions.append("Retrieve and record the exact relevant text with page/paragraph reference")
        if not val(d, "source_reference"):
            issues.append("Dataset source_reference field is blank")
            actions.append("Add a traceable source reference to the dataset")

        if not issues:
            overall = "READY_FOR_SENIOR_HUMAN_REVIEW"
        elif any("source" in x.lower() or "version" in x.lower() or "citation" in x.lower() for x in issues):
            overall = "SOURCE_VALIDATION_REQUIRED"
        else:
            overall = "LEGAL_ANALYSIS_INCOMPLETE"

        audit.append({
            "id": pid,
            "jurisdiction": val(d, "country", "jurisdiction"),
            "document": val(d, "document"),
            "article_or_section": val(d, "article_or_section"),
            "governance_dimension": val(d, "governance_dimension"),
            "source_validation_status": source_status,
            "source_version_status": version_status,
            "official_publisher_recorded": "YES" if yes(publisher) else "NO",
            "official_url_recorded": "YES" if yes(official_url) else "NO",
            "version_recorded": "YES" if yes(version) else "NO",
            "verified_citation_recorded": "YES" if yes(citation) else "NO",
            "legal_interpretation_completed": "YES" if yes(interpretation) else "NO",
            "scope_analysis_completed": "YES" if yes(scope_analysis) else "NO",
            "duty_holder_analysis_completed": "YES" if yes(duty_analysis) else "NO",
            "enforcement_analysis_completed": "YES" if yes(enforcement_analysis) else "NO",
            "comparative_argument_drafted": "YES" if yes(proposed_argument) else "NO",
            "supporting_evidence_linked": "YES" if yes(supporting_ids) else "NO",
            "counter_evidence_recorded": "YES" if yes(counter_evidence) else "NO",
            "researcher_assessment_recorded": "YES" if yes(researcher_assessment) else "NO",
            "issue_count": len(issues),
            "issues": " | ".join(issues),
            "recommended_next_actions": " | ".join(dict.fromkeys(actions)),
            "overall_review_status": overall,
            "confidence_field_from_phase14_5": confidence,
            "automated_review_note": "Workflow completeness check only; not a legal opinion or source verification.",
        })

    fields = list(audit[0].keys()) if audit else []
    write_csv(OUT_DIR / "phase14_6_legal_validation_audit.csv", audit, fields)

    status_counts = {}
    for row in audit:
        status_counts[row["overall_review_status"]] = status_counts.get(row["overall_review_status"], 0) + 1
    total_issues = sum(row["issue_count"] for row in audit)
    ready = status_counts.get("READY_FOR_SENIOR_HUMAN_REVIEW", 0)
    source_required = status_counts.get("SOURCE_VALIDATION_REQUIRED", 0)
    analysis_incomplete = status_counts.get("LEGAL_ANALYSIS_INCOMPLETE", 0)

    # A separate concise list of records requiring attention.
    attention = [r for r in audit if r["overall_review_status"] != "READY_FOR_SENIOR_HUMAN_REVIEW"]
    attention_fields = [
        "id", "jurisdiction", "document", "article_or_section",
        "overall_review_status", "issue_count", "issues", "recommended_next_actions"
    ]
    write_csv(OUT_DIR / "phase14_6_priority_review_queue.csv", attention, attention_fields)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report = f"""# Phase 14.6 — Legal Validation and Findings Review

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Purpose

This is a quality-control pass over the research workflow. It checks whether
source/version records, provision-level legal analysis, and comparative
argument fields appear complete. It does not determine whether a legal
interpretation is correct.

## Input files found

| Input | Rows available |
|---|---:|
| Annotated dataset | {len(dataset)} |
| Phase 14.3 source/version register | {len(p14_3)} |
| Phase 14.4 legal-analysis worksheet | {len(p14_4)} |
| Phase 14.5 comparative argument matrix | {len(p14_5)} |
| Phase 14.5 claim-evidence register | {len(claims)} |

## Automated workflow status

| Status | Provisions |
|---|---:|
| Ready for senior human review | {ready} |
| Source validation required | {source_required} |
| Legal analysis incomplete | {analysis_incomplete} |
| Total provisions audited | {len(audit)} |
| Total checklist issues identified | {total_issues} |

These are workflow-completeness counts, not findings about the quality,
validity, or effectiveness of any jurisdiction's law.

## Files created

- `results/phase14/legal_validation/phase14_6_legal_validation_audit.csv`
- `results/phase14/legal_validation/phase14_6_priority_review_queue.csv`
- `results/phase14/reports/Phase14_6_Legal_Validation_and_Findings_Review.md`

## Human review protocol

For every provision, a researcher should:

1. Open the official legal source and confirm the exact text.
2. Confirm the applicable version, amendment history, and commencement date.
3. Check the surrounding paragraphs, definitions, exceptions, and cross-references.
4. Verify the pinpoint citation and record the source page/paragraph.
5. Explain the legal duty, its holder, scope, conditions, and limits.
6. Distinguish the existence of a legal power from evidence that it was exercised.
7. Support each comparative claim with traceable evidence and record counter-evidence.
8. Have material legal interpretations reviewed by a suitably qualified human reviewer.

## Important safeguards

- This script does not browse the web or independently verify official sources.
- A field marked YES means only that a value was present in an input file.
- A row marked READY_FOR_SENIOR_HUMAN_REVIEW is not legally approved.
- Blank fields are not filled with assumptions.
- The original annotated dataset and all earlier phase outputs are left unchanged.
"""
    (REPORT_DIR / "Phase14_6_Legal_Validation_and_Findings_Review.md").write_text(report, encoding="utf-8")

    print("PHASE 14.6 COMPLETED")
    print(f"Dataset provisions audited: {len(audit)}")
    print(f"Phase 14.3 register rows: {len(p14_3)}")
    print(f"Phase 14.4 worksheet rows: {len(p14_4)}")
    print(f"Phase 14.5 argument rows: {len(p14_5)}")
    print(f"Ready for senior human review: {ready}")
    print(f"Source validation required: {source_required}")
    print(f"Legal analysis incomplete: {analysis_incomplete}")
    print(f"Checklist issues identified: {total_issues}")
    print("\nCreated:")
    print(" - results/phase14/legal_validation/phase14_6_legal_validation_audit.csv")
    print(" - results/phase14/legal_validation/phase14_6_priority_review_queue.csv")
    print(" - results/phase14/reports/Phase14_6_Legal_Validation_and_Findings_Review.md")
    print("\nNo original dataset or prior phase file was modified.")

if __name__ == "__main__":
    main()
