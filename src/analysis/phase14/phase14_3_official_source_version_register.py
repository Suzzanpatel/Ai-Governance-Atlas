"""
Phase 14.3 — Official Source and Version Validation Register
AI Governance Atlas

Builds a structured validation register from the Phase 14.2 source-context
queue and the original annotated dataset. It extracts source URLs where they
are already recorded, captures local PDF metadata/hash information, and
creates fields for checking official status, version, amendments, commencement,
and legal citation accuracy.

It does NOT access the internet, authenticate URLs, or mark sources verified.
No source files or annotated dataset rows are modified.

Run from project root:
    python src/analysis/phase14/phase14_3_official_source_version_register.py
"""

from pathlib import Path
import re
import sys
import pandas as pd


def locate_root() -> Path:
    here = Path(__file__).resolve()
    for candidate in [here.parent, *here.parents]:
        if (candidate / "data/annotated/governance_dataset.csv").is_file():
            return candidate
    raise FileNotFoundError(
        "Cannot locate data/annotated/governance_dataset.csv."
    )


def first_url(value: str) -> str:
    if not value:
        return ""
    match = re.search(r"https?://[^\s<>\])}\"']+", str(value), flags=re.I)
    return match.group(0).rstrip(".,;") if match else ""


def read_csv(path: Path, required=None):
    if not path.is_file():
        raise FileNotFoundError(f"Required Phase 14.2 output not found: {path}")
    frame = pd.read_csv(path, dtype=str).fillna("")
    if required:
        missing = [column for column in required if column not in frame.columns]
        if missing:
            raise ValueError(f"{path.name} is missing columns: {missing}")
    return frame


def main():
    root = locate_root()
    dataset_path = root / "data/annotated/governance_dataset.csv"
    queue_path = (
        root / "results/phase14/source_validation/"
        "phase14_2_source_context_validation_queue.csv"
    )
    inventory_path = (
        root / "results/phase14/source_validation/"
        "phase14_1_local_pdf_source_inventory.csv"
    )
    output_dir = root / "results/phase14/source_validation"
    report_dir = root / "results/phase14/reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    dataset = read_csv(dataset_path, ["id", "country", "document"])
    queue = read_csv(
        queue_path,
        ["id", "locator_status", "source_relative_path", "pdf_page_number",
         "source_pdf_sha256", "human_validation_status"]
    )

    inventory = None
    if inventory_path.is_file():
        inventory = pd.read_csv(inventory_path, dtype=str).fillna("")

    # One register row per candidate source match. Keep unmatched provisions
    # too, so no provision silently disappears from the validation workflow.
    rows = []
    for _, q in queue.iterrows():
        dataset_rows = dataset.loc[dataset["id"] == q["id"]]
        d = dataset_rows.iloc[0] if not dataset_rows.empty else pd.Series(dtype=str)

        source_ref = str(d.get("source_reference", ""))
        candidate_path = str(q.get("source_relative_path", ""))
        local_meta = {}
        if inventory is not None and candidate_path and "relative_path" in inventory.columns:
            hits = inventory.loc[inventory["relative_path"] == candidate_path]
            if not hits.empty:
                local_meta = hits.iloc[0].to_dict()

        rows.append({
            "id": q.get("id", ""),
            "country": q.get("country", ""),
            "dataset_document": q.get("dataset_document", ""),
            "dataset_article_or_section": q.get("dataset_article_or_section", ""),
            "dataset_page_number": q.get("dataset_page_number", ""),
            "dataset_source_reference": source_ref,
            "source_url_extracted_from_existing_reference": first_url(source_ref),
            "dataset_version_used": q.get("dataset_version_used", ""),
            "candidate_pdf": q.get("source_pdf", ""),
            "candidate_pdf_path": candidate_path,
            "candidate_pdf_page": q.get("pdf_page_number", ""),
            "candidate_pdf_sha256": q.get("source_pdf_sha256", ""),
            "pdf_metadata_title": q.get("pdf_metadata_title", ""),
            "pdf_inventory_page_count": local_meta.get("page_count", ""),
            "pdf_inventory_readable": local_meta.get("pdf_readable", ""),
            "locator_status": q.get("locator_status", ""),
            "match_type": q.get("match_type", ""),
            "candidate_source_excerpt": q.get("source_excerpt", ""),
            "source_context": q.get("context_before_and_after", ""),
            "official_publisher_identified": "NOT_ASSESSED",
            "official_source_url_confirmed": "NOT_ASSESSED",
            "instrument_title_confirmed": "NOT_ASSESSED",
            "version_or_consolidation_date_confirmed": "NOT_ASSESSED",
            "amendments_checked": "NOT_ASSESSED",
            "commencement_and_in_force_status_checked": "NOT_ASSESSED",
            "article_paragraph_and_page_confirmed": "NOT_ASSESSED",
            "quotation_verbatim_and_context_checked": "NOT_ASSESSED",
            "definitions_exceptions_cross_references_checked": "NOT_ASSESSED",
            "overall_validation_decision": "PENDING_SOURCE_REVIEW",
            "reviewer_name_or_initials": "",
            "review_date": "",
            "reviewer_evidence_reference": "",
            "reviewer_notes": "",
        })

    register = pd.DataFrame(rows)
    register_path = output_dir / "phase14_3_official_source_version_validation_register.csv"
    register.to_csv(register_path, index=False)

    # Coverage summary at provision level.
    if not register.empty:
        provision_summary = (
            register.groupby(["id", "country", "dataset_document"], dropna=False)
            .agg(
                candidate_rows=("locator_status", "size"),
                local_candidate_paths=("candidate_pdf_path",
                    lambda s: int(s.astype(str).str.strip().ne("").sum())),
                source_review_state=("overall_validation_decision",
                    lambda s: "; ".join(sorted(set(s)))),
            )
            .reset_index()
        )
    else:
        provision_summary = pd.DataFrame(
            columns=["id", "country", "dataset_document", "candidate_rows",
                     "local_candidate_paths", "source_review_state"]
        )
    summary_path = output_dir / "phase14_3_source_validation_coverage.csv"
    provision_summary.to_csv(summary_path, index=False)

    no_candidate = (
        int(register["candidate_pdf_path"].astype(str).str.strip().eq("").sum())
        if not register.empty else 0
    )
    total_provisions = dataset["id"].nunique()
    provisions_with_candidate = (
        register.loc[
            register["candidate_pdf_path"].astype(str).str.strip().ne(""), "id"
        ].nunique()
        if not register.empty else 0
    )

    report = f"""# Phase 14.3 — Official Source and Version Validation Register

## Purpose

This phase converts the Phase 14.2 source locator results into a structured
register for validating source authority, document identity, version, legal
status, citation accuracy, and quotation context.

## Coverage

- Unique provisions in the annotated dataset: **{total_provisions}**
- Provision IDs with at least one local PDF candidate: **{provisions_with_candidate}**
- Candidate source rows in the register: **{len(register)}**
- Register rows without a candidate PDF path: **{no_candidate}**
- Automatically authenticated official sources: **0**
- Automatically verified legal provisions: **0**

## Main outputs

- `phase14_3_official_source_version_validation_register.csv`
- `phase14_3_source_validation_coverage.csv`

## Validation checklist

For each candidate source, the reviewer should establish:

1. **Official publisher:** identify the legislature, regulator, government,
   international organisation, or other competent issuing body.
2. **Official source location:** confirm the source through the publisher's
   official repository or website.
3. **Instrument identity:** confirm the complete title and instrument number.
4. **Version:** confirm whether the PDF is an original, amended, or consolidated
   version and record its date.
5. **Amendments:** check later amendments, corrigenda, delegated/implementing
   acts, and relevant transitional provisions.
6. **Commencement:** establish whether the provision was in force at the
   relevant date, including phased application where applicable.
7. **Pinpoint citation:** confirm article, paragraph, page, schedule or annex.
8. **Quotation and context:** check exact wording, surrounding text, definitions,
   exceptions, qualifications and cross-references.

## Decision discipline

The register begins with `PENDING_SOURCE_REVIEW`. Do not change this to a
verified outcome solely because a text locator match exists. A candidate PDF
hash identifies the local file reviewed; it does not establish authenticity.

Recommended decision values for a later reviewed register:
- `VERIFIED`: all material source and pinpoint checks are supported by official
  evidence and reviewer notes.
- `DISCREPANCY_FOUND`: a source, version, pinpoint citation or quotation differs.
- `UNRESOLVED`: evidence is insufficient or contradictory.
- `NOT_APPLICABLE`: a specific check genuinely does not apply, with explanation.

## Limitations

This script does not access the internet, resolve URLs, verify official domains,
or determine legal status. URL values are extracted only when already present
in the dataset's source_reference field. Human review and authoritative source
evidence remain necessary.

## Next step

Phase 14.4 should use the completed register and authoritative source material
to document provision-level legal analysis, including legal force, scope,
conditions, responsible actor, enforcement cross-references, and interpretive
uncertainties.
"""
    report_path = report_dir / "Phase14_3_Official_Source_and_Version_Validation.md"
    report_path.write_text(report, encoding="utf-8")

    print("\nPHASE 14.3 COMPLETED")
    print(f"Dataset provisions: {total_provisions}")
    print(f"Provision IDs with local PDF candidates: {provisions_with_candidate}")
    print(f"Validation register rows: {len(register)}")
    print(f"Rows without candidate PDF path: {no_candidate}")
    print(f"Validation register: {register_path}")
    print(f"Coverage summary: {summary_path}")
    print(f"Report: {report_path}")
    print("No source or provision was automatically marked verified.")
    print("Original dataset and source PDFs were not modified.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\nPHASE 14.3 FAILED: {exc}", file=sys.stderr)
        raise
