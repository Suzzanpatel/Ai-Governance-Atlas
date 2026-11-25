#!/usr/bin/env python3
"""
Phase 14.5 — Comparative Legal Argument Matrix

Purpose
-------
Builds a provision-level research matrix to help develop the comparative legal
argument across the jurisdictions in the AI Governance Atlas.

This script DOES NOT make legal findings, verify legislation, or invent
comparative conclusions. It organises existing project data and creates
transparent prompts for human legal analysis.

Run from the project root:
    python src/analysis/phase14/phase14_5_comparative_legal_argument_matrix.py
"""

from pathlib import Path
import csv
import re
from datetime import datetime

ROOT = Path(__file__).resolve().parents[3]
DATASET = ROOT / "data/annotated/governance_dataset.csv"
P14_2 = ROOT / "results/phase14/source_validation/phase14_2_source_context_validation_queue.csv"
P14_3 = ROOT / "results/phase14/source_validation/phase14_3_official_source_version_validation_register.csv"
P14_4 = ROOT / "results/phase14/legal_analysis/phase14_4_provision_level_legal_analysis_worksheet.csv"

OUT_DIR = ROOT / "results/phase14/comparative_argument"
REPORT_DIR = ROOT / "results/phase14/reports"

def read_csv(path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def first(row, *keys):
    for key in keys:
        value = row.get(key, "")
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""

def normalise(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()

def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

def main():
    if not DATASET.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET}\nRun this script from the project repository."
        )

    dataset = read_csv(DATASET)
    p14_2 = read_csv(P14_2)
    p14_3 = read_csv(P14_3)
    p14_4 = read_csv(P14_4)

    # Index supporting Phase 14 records by provision ID.
    q_by_id = {first(r, "id", "provision_id"): r for r in p14_2 if first(r, "id", "provision_id")}
    v_by_id = {first(r, "id", "provision_id"): r for r in p14_3 if first(r, "id", "provision_id")}
    a_by_id = {first(r, "id", "provision_id"): r for r in p14_4 if first(r, "id", "provision_id")}

    argument_rows = []
    evidence_rows = []

    for source in dataset:
        pid = first(source, "id", "provision_id")
        q = q_by_id.get(pid, {})
        v = v_by_id.get(pid, {})
        a = a_by_id.get(pid, {})

        jurisdiction = first(source, "country", "jurisdiction")
        document = first(source, "document")
        article = first(source, "article_or_section")
        dimension = first(source, "governance_dimension")
        secondary = first(source, "secondary_dimension")
        legal_status = first(source, "legal_status")
        obligation = first(source, "obligation_type")
        responsible = first(source, "responsible_party")
        applicability = first(source, "applicability")
        enforcement = first(source, "enforcement_mechanism")
        summary = first(source, "provision_summary")
        exact_text = first(source, "exact_text")
        source_ref = first(source, "source_reference")

        source_validation = first(v, "source_validation_status", "validation_status", "status") or "NOT_CONFIRMED_IN_REGISTER"
        version_status = first(v, "version_status", "version_validation_status") or "NOT_ASSESSED"
        candidate_page = first(q, "candidate_page", "matched_page", "page_number")
        context_excerpt = first(q, "context_excerpt", "source_context", "matched_excerpt")
        legal_review_status = first(a, "legal_review_status", "review_status") or "PENDING_HUMAN_ANALYSIS"

        argument_rows.append({
            "id": pid,
            "jurisdiction": jurisdiction,
            "document": document,
            "article_or_section": article,
            "primary_governance_dimension": dimension,
            "secondary_governance_dimension": secondary,
            "recorded_legal_status": legal_status,
            "recorded_obligation_type": obligation,
            "recorded_responsible_party": responsible,
            "recorded_applicability": applicability,
            "recorded_enforcement_mechanism": enforcement,
            "provision_summary_from_dataset": summary,
            "comparative_question_1_legal_force": "Is this instrument legally binding, and on whom? Distinguish legal status from practical influence.",
            "comparative_question_2_duty_holder": "Who bears the duty, and is the duty direct, shared, delegated, or conditional?",
            "comparative_question_3_scope": "Which systems, actors, risks, sectors, or circumstances fall within scope? Identify exclusions and thresholds.",
            "comparative_question_4_implementation": "What institutional, procedural, technical, or documentary steps are required for implementation?",
            "comparative_question_5_enforcement": "What supervision, complaint, audit, sanction, remedy, or accountability route is available?",
            "comparative_question_6_outcomes": "What evidence demonstrates implementation or outcomes? Do not infer effectiveness from the existence of a rule.",
            "comparative_question_7_comparability": "Is the provision functionally comparable to provisions in other jurisdictions, or does it address a different regulatory function?",
            "potential_comparison_group": dimension,
            "proposed_argument": "",
            "supporting_evidence_ids": "",
            "counter_evidence_or_limitation": "",
            "researcher_legal_assessment": "",
            "confidence": "NOT_ASSESSED",
            "human_review_status": "REQUIRES_RESEARCHER_COMPLETION",
            "source_validation_status_from_register": source_validation,
            "source_version_status_from_register": version_status,
            "candidate_source_page_from_phase14_2": candidate_page,
            "phase14_4_review_status": legal_review_status,
            "source_reference_from_dataset": source_ref,
        })

        evidence_rows.append({
            "claim_id": f"DESC-{pid}",
            "provision_id": pid,
            "jurisdiction": jurisdiction,
            "descriptive_claim": (
                f"The dataset records {document}, {article}, under the governance dimension "
                f"'{dimension}'."
            ),
            "claim_type": "DESCRIPTIVE_DATASET_RECORD",
            "dataset_support": "PRESENT" if any([document, article, dimension]) else "INCOMPLETE",
            "exact_text_available": "YES" if exact_text else "NO",
            "source_reference_available": "YES" if source_ref else "NO",
            "source_context_available": "YES" if context_excerpt else "NO",
            "source_validation_status": source_validation,
            "source_version_status": version_status,
            "candidate_source_page": candidate_page,
            "evidence_excerpt": normalise(context_excerpt)[:1200],
            "interpretive_claim": "",
            "outcome_evidence": "",
            "limitations": "This is a description of how the project dataset records the provision, not an independently verified legal conclusion or evidence of effectiveness.",
            "next_action": "Verify the official source and version; complete the Phase 14.4 legal analysis worksheet; then add a supported interpretive claim if justified.",
        })

    argument_fields = list(argument_rows[0].keys()) if argument_rows else []
    evidence_fields = list(evidence_rows[0].keys()) if evidence_rows else []
    write_csv(OUT_DIR / "phase14_5_comparative_legal_argument_matrix.csv", argument_rows, argument_fields)
    write_csv(OUT_DIR / "phase14_5_claim_evidence_register.csv", evidence_rows, evidence_fields)

    # Counts are workflow diagnostics only, not research findings.
    jurisdiction_count = len({r["jurisdiction"] for r in argument_rows if r["jurisdiction"]})
    dimensions = sorted({r["primary_governance_dimension"] for r in argument_rows if r["primary_governance_dimension"]})
    source_confirmed = sum(
        1 for r in argument_rows
        if r["source_validation_status_from_register"].upper() in {"VERIFIED", "CONFIRMED", "VALIDATED"}
    )

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report = f"""# Phase 14.5 — Comparative Legal Argument Matrix

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Purpose

This phase converts the existing provision dataset and Phase 14 source-review
records into a structured matrix for developing a comparative legal argument.
It does not decide which jurisdiction is stronger, more effective, or more
compliant. Those conclusions require source-verified legal analysis and
implementation evidence.

## Files created

1. `results/phase14/comparative_argument/phase14_5_comparative_legal_argument_matrix.csv`
2. `results/phase14/comparative_argument/phase14_5_claim_evidence_register.csv`

## Input availability

- Dataset provisions processed: {len(argument_rows)}
- Jurisdictions represented in dataset: {jurisdiction_count}
- Primary governance dimensions represented: {len(dimensions)}
- Phase 14.2 source-context rows available: {len(p14_2)}
- Phase 14.3 source/version register rows available: {len(p14_3)}
- Phase 14.4 legal-analysis worksheet rows available: {len(p14_4)}
- Rows with a source status explicitly labelled Verified/Confirmed/Validated: {source_confirmed}

## How to use the argument matrix

For each provision:

1. Confirm the official legal text and the version applicable to the research period.
2. Complete the legal questions using the provision and its surrounding context.
3. Compare only provisions with a genuinely similar regulatory function.
4. Record the argument and cite the supporting provision IDs.
5. Record counter-evidence, limitations, and unresolved interpretive questions.
6. Do not treat a statutory obligation as proof that it has been implemented.
7. Do not treat enforcement powers as proof that enforcement has occurred.

## Important distinction

The `recorded_*` fields are copied from the project's annotated dataset.
The `comparative_question_*` fields are prompts, not answers.
The claim register contains only cautious descriptions of dataset records.
Blank interpretive and outcome fields are intentional.

## Governance dimensions present

{chr(10).join('- ' + d for d in dimensions) if dimensions else '- Not available'}

## Limitations

- Missing Phase 14 input files are not treated as evidence that a provision is invalid.
- A candidate PDF page or extracted excerpt is not, by itself, source verification.
- This script does not access the internet or independently check official legislation.
- No legal conclusion or effectiveness ranking is generated.
"""
    (REPORT_DIR / "Phase14_5_Comparative_Legal_Argument_Matrix.md").write_text(report, encoding="utf-8")

    print("PHASE 14.5 COMPLETED")
    print(f"Dataset provisions processed: {len(argument_rows)}")
    print(f"Jurisdictions represented: {jurisdiction_count}")
    print(f"Primary governance dimensions: {len(dimensions)}")
    print(f"Phase 14.2 rows found: {len(p14_2)}")
    print(f"Phase 14.3 rows found: {len(p14_3)}")
    print(f"Phase 14.4 rows found: {len(p14_4)}")
    print("\nCreated:")
    print(" - results/phase14/comparative_argument/phase14_5_comparative_legal_argument_matrix.csv")
    print(" - results/phase14/comparative_argument/phase14_5_claim_evidence_register.csv")
    print(" - results/phase14/reports/Phase14_5_Comparative_Legal_Argument_Matrix.md")
    print("\nOriginal dataset was not modified.")

if __name__ == "__main__":
    main()
