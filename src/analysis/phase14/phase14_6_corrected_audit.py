#!/usr/bin/env python3
"""Schema-aware replacement for Phase 14.6.

Reads the original dataset plus actual Phase 14.3, 14.4 and 14.5 CSV schemas.
Writes a corrected audit and priority queue without modifying source files.
Run from the repository root:
    python src/analysis/phase14/phase14_6_corrected_audit.py
"""
from pathlib import Path
import csv
import re
from collections import defaultdict, Counter

ROOT = Path(__file__).resolve().parents[3]
DATASET = ROOT / "data/annotated/governance_dataset.csv"
P14_3 = ROOT / "results/phase14/source_validation/phase14_3_official_source_version_validation_register.csv"
P14_4 = ROOT / "results/phase14/legal_analysis/phase14_4_provision_level_legal_analysis_worksheet.csv"
P14_5 = ROOT / "results/phase14/comparative_argument/phase14_5_comparative_legal_argument_matrix.csv"
OUT = ROOT / "results/phase14/legal_validation"

def read_csv(path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def clean(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()

def filled(value):
    return clean(value).lower() not in {
        "", "none", "n/a", "na", "unknown", "not assessed", "not_assessed",
        "pending", "pending source review", "pending_source_review",
        "not yet reviewed", "not_yet_reviewed"
    }

def group(rows):
    result = defaultdict(list)
    for row in rows:
        if clean(row.get("id")):
            result[clean(row["id"])].append(row)
    return result

def write(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0].keys()) if rows else []
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

def main():
    if not DATASET.exists():
        raise FileNotFoundError(f"Dataset not found: {DATASET}")
    dataset = read_csv(DATASET)
    sources = group(read_csv(P14_3))
    legal = group(read_csv(P14_4))
    arguments = group(read_csv(P14_5))
    output = []

    for d in dataset:
        pid = clean(d.get("id"))
        ss, ls, ars = sources.get(pid, []), legal.get(pid, []), arguments.get(pid, [])
        issues, actions = [], []

        if not ss:
            issues.append("No Phase 14.3 source-locator/register row found")
            actions.append("Restore or create the source locator record")
        else:
            source_checks = [
                ("official_publisher_identified", "Official publisher has not been human-assessed", "Confirm the issuing body against the official source"),
                ("official_source_url_confirmed", "Official source URL has not been human-confirmed", "Open and confirm the official source URL"),
                ("instrument_title_confirmed", "Instrument title has not been human-confirmed", "Confirm the exact instrument title and issuing body"),
                ("version_or_consolidation_date_confirmed", "Applicable version/consolidation date remains unassessed", "Confirm version, amendment history and research cut-off date"),
                ("amendments_checked", "Amendment history has not been checked", "Check amendments and identify the applicable text"),
                ("commencement_and_in_force_status_checked", "Commencement/in-force status has not been checked", "Check commencement, application and transitional provisions"),
                ("article_paragraph_and_page_confirmed", "Pinpoint article/paragraph/page has not been confirmed", "Verify provision boundaries and pinpoint citation"),
                ("quotation_verbatim_and_context_checked", "Quotation and surrounding context have not been human-checked", "Compare quotation with official text and surrounding context"),
                ("definitions_exceptions_cross_references_checked", "Definitions, exceptions and cross-references remain unchecked", "Review relevant definitions, exceptions and cross-references"),
            ]
            for field, message, action in source_checks:
                if not any(filled(r.get(field)) and clean(r.get(field)).upper() not in {"NOT_ASSESSED", "PENDING"} for r in ss):
                    issues.append(message)
                    actions.append(action)

        if not ls:
            issues.append("No Phase 14.4 legal-analysis row found")
            actions.append("Restore or create the provision-level legal-analysis row")
        else:
            for field, message in [
                ("researcher_legal_analysis", "Substantive legal analysis is blank"),
                ("scope_and_addressees", "Scope and addressees analysis is blank"),
                ("responsible_actor_analysis", "Responsible-actor analysis is blank"),
                ("enforcement_route_and_remedies", "Enforcement route/remedies analysis is blank"),
                ("primary_source_evidence_reference", "Primary-source evidence reference is blank"),
                ("provisional_conclusion", "Provisional legal conclusion is blank"),
            ]:
                if not any(filled(r.get(field)) for r in ls):
                    issues.append(message)
            if not any(filled(r.get("analysis_status")) and clean(r.get("analysis_status")).upper() not in {"NOT_YET_REVIEWED", "PENDING"} for r in ls):
                actions.append("Complete and record human legal analysis in the Phase 14.4 worksheet")

        if not ars:
            issues.append("No Phase 14.5 comparative argument row found")
            actions.append("Restore or create the comparative argument row")
        else:
            for field, message in [
                ("proposed_argument", "Comparative argument has not been drafted"),
                ("supporting_evidence_ids", "Supporting evidence IDs have not been linked"),
                ("counter_evidence_or_limitation", "Counter-evidence/limitations have not been recorded"),
                ("researcher_legal_assessment", "Researcher legal assessment is blank"),
            ]:
                if not any(filled(r.get(field)) for r in ars):
                    issues.append(message)
            if not all(any(filled(r.get(f)) for r in ars) for f in ("proposed_argument", "researcher_legal_assessment")):
                actions.append("Draft a qualified comparative argument after completing source and legal review")

        analysis_states = {clean(r.get("analysis_status")).upper() for r in ls}
        if not ss:
            status = "SOURCE_REGISTER_ROW_MISSING"
        elif not ls or not ars:
            status = "RESEARCH_WORKSHEET_ROW_MISSING"
        elif issues:
            status = "SOURCE_AND_LEGAL_REVIEW_PENDING"
        elif any(state.startswith("DRAFT") for state in analysis_states):
            # Every field is filled, but the legal analysis is a draft that the
            # researcher still has to review (see phase14_review_record.csv)
            status = "DRAFT_COMPLETE_AWAITING_RESEARCHER_REVIEW"
        else:
            status = "SOURCE_AND_LEGAL_REVIEW_COMPLETE"

        candidates = sorted({clean(r.get("candidate_pdf")) for r in ss if clean(r.get("candidate_pdf"))})
        pages = sorted({clean(r.get("candidate_pdf_page")) for r in ss if clean(r.get("candidate_pdf_page"))})
        decisions = sorted({clean(r.get("overall_validation_decision")) or "NOT_RECORDED" for r in ss})

        output.append({
            "id": pid,
            "jurisdiction_or_benchmark": clean(d.get("country")),
            "document": clean(d.get("document")),
            "article_or_section": clean(d.get("article_or_section")),
            "primary_governance_dimension": clean(d.get("governance_dimension")),
            "source_candidate_rows": len(ss),
            "candidate_pdf_files": " | ".join(candidates),
            "candidate_pdf_pages": " | ".join(pages),
            "source_validation_decisions": " | ".join(decisions),
            "official_publisher_human_confirmed": "YES" if any(filled(r.get("official_publisher_identified")) and clean(r.get("official_publisher_identified")).upper() != "NOT_ASSESSED" for r in ss) else "NO",
            "official_url_human_confirmed": "YES" if any(filled(r.get("official_source_url_confirmed")) and clean(r.get("official_source_url_confirmed")).upper() != "NOT_ASSESSED" for r in ss) else "NO",
            "version_human_confirmed": "YES" if any(filled(r.get("version_or_consolidation_date_confirmed")) and clean(r.get("version_or_consolidation_date_confirmed")).upper() != "NOT_ASSESSED" for r in ss) else "NO",
            "legal_analysis_completed": "YES" if any(filled(r.get("researcher_legal_analysis")) for r in ls) else "NO",
            "scope_analysis_completed": "YES" if any(filled(r.get("scope_and_addressees")) for r in ls) else "NO",
            "responsible_actor_analysis_completed": "YES" if any(filled(r.get("responsible_actor_analysis")) for r in ls) else "NO",
            "enforcement_analysis_completed": "YES" if any(filled(r.get("enforcement_route_and_remedies")) for r in ls) else "NO",
            "comparative_argument_drafted": "YES" if any(filled(r.get("proposed_argument")) for r in ars) else "NO",
            "supporting_evidence_linked": "YES" if any(filled(r.get("supporting_evidence_ids")) for r in ars) else "NO",
            "counter_evidence_recorded": "YES" if any(filled(r.get("counter_evidence_or_limitation")) for r in ars) else "NO",
            "issue_count": len(issues),
            "issues": " | ".join(issues),
            "recommended_next_actions": " | ".join(dict.fromkeys(actions)),
            "overall_review_status": status,
            "audit_note": "Workflow completeness check only; candidate PDF matches are not source verification and no legal conclusion is made."
        })

    write(OUT / "phase14_6_corrected_legal_validation_audit.csv", output)
    write(OUT / "phase14_6_corrected_priority_review_queue.csv",
          [r for r in output if r["overall_review_status"] != "READY_FOR_HUMAN_REVIEW"])
    print("CORRECTED PHASE 14.6 AUDIT COMPLETED")
    print(f"Provisions audited: {len(output)}")
    print(f"Phase 14.3 source candidate rows: {sum(len(v) for v in sources.values())}")
    print(f"Provisions with source/legal review pending: {sum(r['overall_review_status']=='SOURCE_AND_LEGAL_REVIEW_PENDING' for r in output)}")
    print(f"Checklist issues: {sum(r['issue_count'] for r in output)}")
    print("Original dataset and Phase 14 source files were not modified.")

if __name__ == "__main__":
    main()
