"""
Phase 14.4 — Provision-Level Legal Analysis Worksheet
AI Governance Atlas

Creates a structured legal-analysis worksheet for every coded provision,
incorporating available Phase 14.2 source-context and Phase 14.3 validation
register information.

This script prepares a research worksheet; it does not interpret the law,
complete legal conclusions, or mark provisions verified. It preserves source
and dataset values as supplied and leaves analytical decisions for review.

Run from project root:
    python src/analysis/phase14/phase14_4_provision_legal_analysis_worksheet.py
"""

from pathlib import Path
import sys
import pandas as pd


def locate_root() -> Path:
    here = Path(__file__).resolve()
    for candidate in [here.parent, *here.parents]:
        if (candidate / "data/annotated/governance_dataset.csv").is_file():
            return candidate
    raise FileNotFoundError("Cannot locate data/annotated/governance_dataset.csv.")


def read_optional(path: Path):
    if not path.is_file():
        return pd.DataFrame()
    return pd.read_csv(path, dtype=str).fillna("")


def first_nonempty(series):
    for value in series:
        if str(value).strip():
            return str(value).strip()
    return ""


def main():
    root = locate_root()
    dataset_path = root / "data/annotated/governance_dataset.csv"
    source_queue_path = (
        root / "results/phase14/source_validation/"
        "phase14_2_source_context_validation_queue.csv"
    )
    validation_register_path = (
        root / "results/phase14/source_validation/"
        "phase14_3_official_source_version_validation_register.csv"
    )
    output_dir = root / "results/phase14/legal_analysis"
    report_dir = root / "results/phase14/reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(dataset_path, dtype=str).fillna("")
    if df.empty:
        raise ValueError("Annotated dataset is empty.")
    if "id" not in df.columns or df["id"].duplicated().any():
        raise ValueError("Dataset must contain unique provision IDs.")

    queue = read_optional(source_queue_path)
    register = read_optional(validation_register_path)

    # Create one analysis worksheet row per provision. Candidate source
    # information is included only where an exact matching provision ID exists.
    worksheet_rows = []
    for _, row in df.iterrows():
        provision_id = str(row["id"])
        q_matches = (
            queue.loc[queue["id"].astype(str) == provision_id]
            if not queue.empty and "id" in queue.columns else pd.DataFrame()
        )
        r_matches = (
            register.loc[register["id"].astype(str) == provision_id]
            if not register.empty and "id" in register.columns else pd.DataFrame()
        )

        source_candidates = []
        if not q_matches.empty:
            for _, candidate in q_matches.iterrows():
                path = str(candidate.get("source_relative_path", "")).strip()
                page = str(candidate.get("pdf_page_number", "")).strip()
                if path or page:
                    source_candidates.append(f"{path} (PDF page {page})")

        validation_state = (
            "; ".join(sorted(set(r_matches.get(
                "overall_validation_decision",
                pd.Series(dtype=str)
            ).astype(str))))
            if not r_matches.empty else "PHASE_14_3_REGISTER_NOT_AVAILABLE"
        )

        worksheet_rows.append({
            "id": provision_id,
            "country": row.get("country", ""),
            "document": row.get("document", ""),
            "document_type": row.get("document_type", ""),
            "legal_status_as_coded": row.get("legal_status", ""),
            "article_or_section_as_coded": row.get("article_or_section", ""),
            "page_number_as_coded": row.get("page_number", ""),
            "exact_text_as_coded": row.get("exact_text", ""),
            "provision_summary_as_coded": row.get("provision_summary", ""),
            "primary_governance_dimension": row.get("governance_dimension", ""),
            "secondary_governance_dimension": row.get("secondary_dimension", ""),
            "obligation_type_as_coded": row.get("obligation_type", ""),
            "responsible_party_as_coded": row.get("responsible_party", ""),
            "applicability_as_coded": row.get("applicability", ""),
            "enforcement_mechanism_as_coded": row.get("enforcement_mechanism", ""),
            "source_reference_as_coded": row.get("source_reference", ""),
            "version_used_as_coded": row.get("version_used", ""),
            "candidate_local_source_pages": " | ".join(source_candidates),
            "source_validation_register_state": validation_state,
            "legal_question_or_issue": "",
            "legal_basis_and_interpretive_method": "",
            "instrument_level_legal_force": "",
            "provision_level_legal_effect": "",
            "mandatory_or_discretionary_language": "",
            "scope_and_addressees": "",
            "conditions_and_thresholds": "",
            "exceptions_and_qualifications": "",
            "definitions_and_cross_references": "",
            "territorial_and_material_scope": "",
            "commencement_and_temporal_application": "",
            "responsible_actor_analysis": "",
            "supervisory_or_enforcement_authority": "",
            "enforcement_route_and_remedies": "",
            "relationship_to_other_legal_instruments": "",
            "interpretive_uncertainties_or_counterarguments": "",
            "researcher_legal_analysis": "",
            "provisional_conclusion": "",
            "primary_source_evidence_reference": "",
            "reviewer_name_or_initials": "",
            "review_date": "",
            "analysis_status": "NOT_YET_REVIEWED",
        })

    worksheet = pd.DataFrame(worksheet_rows)
    worksheet_path = output_dir / "phase14_4_provision_level_legal_analysis_worksheet.csv"
    worksheet.to_csv(worksheet_path, index=False)

    # A compact methodology guide accompanies the spreadsheet.
    guide = """# Phase 14.4 — Provision-Level Legal Analysis Worksheet

## Purpose

This phase creates one structured legal-analysis worksheet row for each
provision in `data/annotated/governance_dataset.csv`. It carries forward the
dataset's existing coding and any available local source-locator information,
while leaving legal analysis fields blank for evidence-led research.

## Main output

`results/phase14/legal_analysis/phase14_4_provision_level_legal_analysis_worksheet.csv`

Each row corresponds to one unique provision ID. Existing dataset values are
labelled `as_coded` to distinguish them from the researcher's legal conclusions.

## Recommended analysis sequence

1. **Identify the legal issue.** State the narrow legal question raised by
   the provision.
2. **Establish the legal basis.** Cite the official instrument and relevant
   interpretive method; distinguish text, context, purpose and authoritative
   interpretation.
3. **Separate instrument-level and provision-level effect.** Do not assume
   that every provision in a binding instrument creates an independently
   enforceable duty.
4. **Analyse operative language.** Identify mandatory, conditional,
   discretionary, permissive or recommendatory wording.
5. **Define scope.** Identify addressees, regulated activities, thresholds,
   territorial reach and material scope.
6. **Check qualifications.** Record exceptions, definitions, derogations,
   transitional rules and cross-references.
7. **Analyse institutional roles.** Distinguish the regulated actor from
   supervisory, notifying, coordinating and enforcement authorities.
8. **Trace enforcement.** Identify the legal basis for supervision, remedies,
   sanctions, procedural routes and any cross-instrument dependencies.
9. **Consider counterarguments.** Record ambiguities, competing readings and
   unresolved issues.
10. **State a proportionate provisional conclusion.** Tie it to the cited
    source evidence and disclose uncertainty.

## Important distinctions

- Legal status of an instrument is not identical to the legal effect of each
  provision within it.
- A duty-holder is not necessarily the supervisory or enforcement authority.
- A sanction elsewhere in an instrument should not be attributed to a specific
  duty without checking the legal cross-reference and scope.
- Policy commitments, voluntary standards and recommendations should not be
  described as statutory obligations unless the legal source supports that.
- The existence of a legal duty does not establish implementation or compliance.

## Evidence standard

For each material legal proposition, record an authoritative source reference
and a pinpoint citation (article, paragraph, page or section). Where possible,
retain the exact operative wording and relevant surrounding context. Distinguish
primary legal text from official guidance, explanatory material and academic
commentary.

## Status discipline

All rows begin as `NOT_YET_REVIEWED`. Do not mark a row complete merely because
a PDF text match exists or because the dataset already contains a summary.
The Phase 14.3 source-validation register is a separate source-authentication
workflow.

## Limitations

This script prepares a worksheet; it does not perform legal interpretation,
retrieve current law, authenticate documents, or complete the blank analysis
fields. It does not modify the original dataset, PDFs, or previous phase files.
"""
    guide_path = report_dir / "Phase14_4_Provision_Level_Legal_Analysis_Guide.md"
    guide_path.write_text(guide, encoding="utf-8")

    print("\nPHASE 14.4 COMPLETED")
    print(f"Provision rows created: {len(worksheet)}")
    print(f"Source-context queue available: {'Yes' if not queue.empty else 'No'}")
    print(f"Source-validation register available: {'Yes' if not register.empty else 'No'}")
    print(f"Legal analysis worksheet: {worksheet_path}")
    print(f"Methodology guide: {guide_path}")
    print("All legal analysis fields remain blank for evidence-led review.")
    print("Original dataset and source PDFs were not modified.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\nPHASE 14.4 FAILED: {exc}", file=sys.stderr)
        raise
