#!/usr/bin/env python3
"""
Phase 14.7 — Research Synthesis and Evidence-Led Findings Framework

Synthesises the project's existing Phase 13 and Phase 14 outputs into:
1. A jurisdiction-level descriptive profile.
2. A governance-dimension comparison table.
3. A synthesis worksheet with prompts for evidence-led findings.
4. A report documenting what the available project files can and cannot support.

This script does not independently verify law, infer regulatory effectiveness,
rank jurisdictions, or write unsupported legal conclusions. It does not modify
the original annotated dataset or earlier phase outputs.

Run from the project root:
    python src/analysis/phase14/phase14_7_research_synthesis.py
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from review_record import apply_review_record, apply_review_record_rows  # noqa: E402
import csv
import re
from datetime import datetime

ROOT = Path(__file__).resolve().parents[3]
DATASET = ROOT / "data/annotated/governance_dataset.csv"

P13_DIR = ROOT / "results/phase13"
P14_DIR = ROOT / "results/phase14"
P14_3 = P14_DIR / "source_validation/phase14_3_official_source_version_validation_register.csv"
P14_4 = P14_DIR / "legal_analysis/phase14_4_provision_level_legal_analysis_worksheet.csv"
P14_5 = P14_DIR / "comparative_argument/phase14_5_comparative_legal_argument_matrix.csv"
# Read the corrected Phase 14.6 audit, whose checks match the 14.3-14.5 worksheet columns
P14_6 = P14_DIR / "legal_validation/phase14_6_corrected_legal_validation_audit.csv"

OUT_DIR = P14_DIR / "research_synthesis"
REPORT_DIR = ROOT / "results/phase14/reports"

def read_csv(path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def get(row, *keys):
    for key in keys:
        value = row.get(key, "")
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""

def clean(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()

def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

def pct(part, total):
    return round((part / total) * 100, 1) if total else 0.0

def main():
    if not DATASET.exists():
        raise FileNotFoundError(f"Dataset not found: {DATASET}")

    dataset = read_csv(DATASET)
    p14_3 = read_csv(P14_3)
    p14_4 = read_csv(P14_4)
    p14_5 = read_csv(P14_5)
    p14_6 = read_csv(P14_6)

    # Summarise only the records actually present in the annotated dataset.
    by_jurisdiction = {}
    by_dimension = {}
    for row in dataset:
        jurisdiction = get(row, "country", "jurisdiction") or "UNSPECIFIED"
        dimension = get(row, "governance_dimension") or "UNSPECIFIED"
        by_jurisdiction[jurisdiction] = by_jurisdiction.get(jurisdiction, 0) + 1
        by_dimension[dimension] = by_dimension.get(dimension, 0) + 1

    jurisdiction_rows = []
    for jurisdiction, count in sorted(by_jurisdiction.items()):
        subset = [
            r for r in dataset
            if (get(r, "country", "jurisdiction") or "UNSPECIFIED") == jurisdiction
        ]
        jurisdiction_rows.append({
            "jurisdiction": jurisdiction,
            "provision_records_in_dataset": count,
            "share_of_dataset_percent": pct(count, len(dataset)),
            "distinct_documents_in_dataset": len({get(r, "document") for r in subset if get(r, "document")}),
            "governance_dimensions_represented": "; ".join(sorted({
                get(r, "governance_dimension") for r in subset if get(r, "governance_dimension")
            })),
            "legal_status_categories_recorded": "; ".join(sorted({
                get(r, "legal_status") for r in subset if get(r, "legal_status")
            })),
            "interpretation": "Descriptive coverage of this dataset only; not a measure of jurisdiction-wide regulatory activity or quality.",
        })

    dimension_rows = []
    for dimension, count in sorted(by_dimension.items()):
        jurisdictions = sorted({
            get(r, "country", "jurisdiction") or "UNSPECIFIED"
            for r in dataset if (get(r, "governance_dimension") or "UNSPECIFIED") == dimension
        })
        dimension_rows.append({
            "governance_dimension": dimension,
            "provision_records_in_dataset": count,
            "share_of_dataset_percent": pct(count, len(dataset)),
            "jurisdictions_represented": "; ".join(jurisdictions),
            "jurisdiction_count": len(jurisdictions),
            "interpretation": "Presence in the coded sample only; absence may reflect sampling or coding choices rather than absence of regulation.",
        })

    # Map Phase 14.6 audit status to each provision where available.
    audit_by_id = {
        get(r, "id", "provision_id"): r
        for r in p14_6 if get(r, "id", "provision_id")
    }
    source_by_id = {
        get(r, "id", "provision_id"): r
        for r in p14_3 if get(r, "id", "provision_id")
    }
    legal_by_id = {
        get(r, "id", "provision_id"): r
        for r in p14_4 if get(r, "id", "provision_id")
    }
    argument_by_id = {
        get(r, "id", "provision_id"): r
        for r in p14_5 if get(r, "id", "provision_id")
    }

    synthesis_rows = []
    for row in dataset:
        pid = get(row, "id", "provision_id")
        source = source_by_id.get(pid, {})
        legal = legal_by_id.get(pid, {})
        argument = argument_by_id.get(pid, {})
        audit = audit_by_id.get(pid, {})
        synthesis_rows.append({
            "id": pid,
            "jurisdiction": get(row, "country", "jurisdiction"),
            "document": get(row, "document"),
            "article_or_section": get(row, "article_or_section"),
            "governance_dimension": get(row, "governance_dimension"),
            "dataset_provision_summary": get(row, "provision_summary"),
            "source_validation_status": get(audit, "source_validation_decisions", "source_validation_status") or get(source, "source_validation_status", "validation_status") or "NOT_AVAILABLE",
            "source_version_status": get(audit, "version_human_confirmed", "source_version_status") or get(source, "version_status", "version_validation_status") or "NOT_AVAILABLE",
            "legal_analysis_status": get(audit, "overall_review_status") or "NOT_AUDITED",
            "legal_interpretation_present": get(audit, "legal_analysis_completed", "legal_interpretation_completed") or "NOT_CHECKED",
            "comparative_argument_present": get(audit, "comparative_argument_drafted") or ("YES" if get(argument, "proposed_argument") else "NO"),
            "research_synthesis_claim": "",
            "supporting_provision_ids": "",
            "official_source_citation": "",
            "implementation_or_outcome_evidence": "",
            "counterargument_or_limitation": "",
            "researcher_conclusion": "",
            "reviewer_status": "PENDING_HUMAN_COMPLETION",
            "synthesis_prompt": "What does this provision show when compared with functionally similar provisions, and what verified evidence supports that interpretation?",
        })

    write_csv(OUT_DIR / "phase14_7_jurisdiction_descriptive_profiles.csv",
              jurisdiction_rows, list(jurisdiction_rows[0].keys()) if jurisdiction_rows else [])
    write_csv(OUT_DIR / "phase14_7_governance_dimension_comparison.csv",
              dimension_rows, list(dimension_rows[0].keys()) if dimension_rows else [])
    synthesis_rows = apply_review_record_rows(synthesis_rows)
    write_csv(OUT_DIR / "phase14_7_research_synthesis_worksheet.csv",
              synthesis_rows, list(synthesis_rows[0].keys()) if synthesis_rows else [])

    # Collect the Phase 13 report files that are actually present.
    p13_reports = sorted((P13_DIR / "reports").glob("*.md")) if (P13_DIR / "reports").exists() else []
    p13_csvs = sorted(P13_DIR.rglob("*.csv")) if P13_DIR.exists() else []
    dimensions_text = "\n".join(
        f"- {r['governance_dimension']}: {r['provision_records_in_dataset']} records "
        f"({r['share_of_dataset_percent']}% of this dataset)"
        for r in dimension_rows
    ) or "- No dimension records available."
    jurisdictions_text = "\n".join(
        f"- {r['jurisdiction']}: {r['provision_records_in_dataset']} records "
        f"({r['share_of_dataset_percent']}% of this dataset)"
        for r in jurisdiction_rows
    ) or "- No jurisdiction records available."

    # Statuses written by phase14_6_corrected_audit.py
    status_of = [get(r, "overall_review_status") for r in p14_6]
    ready_count = sum(s == "SOURCE_AND_LEGAL_REVIEW_COMPLETE" for s in status_of)
    draft_count = sum(s == "DRAFT_COMPLETE_AWAITING_RESEARCHER_REVIEW" for s in status_of)
    source_pending_count = sum(s in ("SOURCE_AND_LEGAL_REVIEW_PENDING", "SOURCE_REGISTER_ROW_MISSING") for s in status_of)
    analysis_pending_count = sum(s == "RESEARCH_WORKSHEET_ROW_MISSING" for s in status_of)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report = f"""# Phase 14.7 — Research Synthesis

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 1. Purpose and scope

This phase brings together the descriptive dataset and the research workflow
outputs from Phases 13 and 14. It prepares a transparent framework for writing
the final comparative analysis. It does not independently verify legislation,
determine legal meaning, measure real-world effectiveness, or rank jurisdictions.

## 2. Dataset coverage

- Provision records: **{len(dataset)}**
- Jurisdictions represented: **{len(by_jurisdiction)}**
- Primary governance dimensions represented: **{len(by_dimension)}**

### Records by jurisdiction

{jurisdictions_text}

### Records by primary governance dimension

{dimensions_text}

These figures describe the current coded sample. They must not be presented as
a complete inventory of each jurisdiction's AI governance framework.

## 3. Phase 13 and Phase 14 materials detected

- Phase 13 report files detected: {len(p13_reports)}
- Phase 13 CSV outputs detected: {len(p13_csvs)}
- Phase 14.3 source/version register rows: {len(p14_3)}
- Phase 14.4 legal-analysis worksheet rows: {len(p14_4)}
- Phase 14.5 comparative argument rows: {len(p14_5)}
- Phase 14.6 validation audit rows: {len(p14_6)}

### Phase 14.6 workflow flags

- Source and legal review complete: {ready_count}
- Draft complete, awaiting researcher review: {draft_count}
- Source or legal review pending: {source_pending_count}
- Worksheet rows missing: {analysis_pending_count}

These are administrative completeness flags only. They are not legal approval
or an assessment of the substantive quality of any rule.

## 4. Files created

1. `results/phase14/research_synthesis/phase14_7_jurisdiction_descriptive_profiles.csv`
2. `results/phase14/research_synthesis/phase14_7_governance_dimension_comparison.csv`
3. `results/phase14/research_synthesis/phase14_7_research_synthesis_worksheet.csv`
4. `results/phase14/reports/Phase14_7_Research_Synthesis.md`

## 5. Recommended structure for the final comparative argument

### A. Regulatory architecture
Compare the legal form, institutional setting, and regulatory instruments.
Distinguish binding legislation from non-binding standards, guidance, and
international policy instruments.

### B. Allocation of responsibilities
Compare who is responsible for risk assessment, data governance, transparency,
human oversight, monitoring, and incident response. Identify differences
between provider, deployer, regulator, and other actor duties.

### C. Enforcement and accountability
Compare supervisory powers, reporting duties, complaints, remedies, sanctions,
and institutional accountability. Distinguish powers available in law from
evidence that they have been exercised.

### D. Implementation and outcomes
Use empirical evidence such as enforcement decisions, audits, incident
reporting, institutional capacity, compliance studies, or documented
implementation. If such evidence is unavailable, state that effectiveness
cannot yet be assessed.

### E. Comparative evaluation
Explain functional similarities and differences, regulatory trade-offs,
limitations, and gaps. Avoid assuming that provisions with similar labels
perform the same legal function.

## 6. Essential research safeguards

1. Do not infer that a jurisdiction lacks a rule merely because it is absent
   from this 20-record sample.
2. Do not infer implementation from statutory text alone.
3. Do not infer effectiveness from the existence of enforcement powers.
4. Compare provisions only after checking scope, definitions, duty-holders,
   exceptions, and legal status.
5. Cite official primary sources for legal propositions and credible empirical
   sources for claims about implementation or outcomes.
6. State the research period and the version of each instrument examined.
7. Record counter-evidence and methodological limitations.

## 7. What remains for the researcher

Complete the blank synthesis fields in the worksheet only after checking the
primary sources and relevant empirical material. Each substantive claim should
have a traceable source citation, supporting provision IDs, a limitation or
counterargument, and a reasoned conclusion.

**Phase 14 is now structurally complete.** The substantive legal validation
and comparative conclusions remain dependent on human source review and
researcher analysis.
"""
    (REPORT_DIR / "Phase14_7_Research_Synthesis.md").write_text(report, encoding="utf-8")

    print("PHASE 14.7 COMPLETED")
    print(f"Dataset provisions synthesised: {len(dataset)}")
    print(f"Jurisdictions represented: {len(by_jurisdiction)}")
    print(f"Governance dimensions represented: {len(by_dimension)}")
    print(f"Phase 13 reports detected: {len(p13_reports)}")
    print(f"Phase 13 CSV files detected: {len(p13_csvs)}")
    print(f"Phase 14.3 rows: {len(p14_3)} | Phase 14.4 rows: {len(p14_4)}")
    print(f"Phase 14.5 rows: {len(p14_5)} | Phase 14.6 rows: {len(p14_6)}")
    print("\nCreated:")
    print(" - results/phase14/research_synthesis/phase14_7_jurisdiction_descriptive_profiles.csv")
    print(" - results/phase14/research_synthesis/phase14_7_governance_dimension_comparison.csv")
    print(" - results/phase14/research_synthesis/phase14_7_research_synthesis_worksheet.csv")
    print(" - results/phase14/reports/Phase14_7_Research_Synthesis.md")
    print("\nOriginal dataset and earlier phase outputs were not modified.")

if __name__ == "__main__":
    main()
