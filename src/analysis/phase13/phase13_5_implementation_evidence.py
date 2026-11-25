"""
Phase 13.5 — Implementation Evidence and Governance Gaps
AI Governance Atlas

Describes the implementation-status coding and the presence/absence of
implementation-related evidence fields in the annotated dataset. If the
Phase 12 verification audit exists, it also summarises implementation-related
audit entries separately.

Run from project root:
    python src/analysis/phase13/phase13_5_implementation_evidence.py

IMPORTANT:
- Missing evidence in this dataset is not proof that implementation has not
  occurred.
- A status label is not independent proof of implementation.
- This script does not browse the web or verify implementation claims.
- The original annotated dataset is never modified.
"""

from pathlib import Path
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


def clean(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.strip()


def nonempty_count(series: pd.Series) -> int:
    return int(clean(series).ne("").sum())


def write_distribution(df, field, path):
    values = clean(df[field]).replace("", "Not recorded")
    table = (
        values.value_counts()
        .rename_axis(field)
        .reset_index(name="provision_count")
    )
    table["sample_share_pct"] = (
        table["provision_count"] / len(df) * 100
    ).round(1)
    table.to_csv(path, index=False)
    return table


def main():
    root = locate_root()
    source = root / "data/annotated/governance_dataset.csv"
    audit_source = root / "research/evidence/verification_audit.csv"
    output = root / "results/phase13/comparative_analysis"
    reports = root / "results/phase13/reports"
    output.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(source, dtype=str).fillna("")
    required = ["id", "country", "implementation_status"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")
    if df.empty:
        raise ValueError("The annotated dataset is empty.")
    if df["id"].duplicated().any():
        raise ValueError("Duplicate provision IDs detected.")

    for field in ["country", "implementation_status"]:
        df[field] = clean(df[field]).replace("", "Not recorded")

    status_table = write_distribution(
        df, "implementation_status",
        output / "phase13_5_implementation_status_distribution.csv"
    )

    # Cross-jurisdiction implementation-status table.
    status_by_jurisdiction = pd.crosstab(
        df["country"], df["implementation_status"]
    )
    status_by_jurisdiction.to_csv(
        output / "phase13_5_implementation_status_by_jurisdiction_counts.csv"
    )
    status_pct = status_by_jurisdiction.div(
        status_by_jurisdiction.sum(axis=1).replace(0, pd.NA), axis=0
    ).mul(100).round(1)
    status_pct.to_csv(
        output / "phase13_5_implementation_status_by_jurisdiction_percentages.csv"
    )

    # Assess whether evidence-related fields contain text. Presence is not
    # equivalent to quality, independence, or proof.
    evidence_fields = [
        "implementation_notes",
        "verification_notes",
        "source_reference",
        "exact_text",
        "provision_summary",
    ]
    evidence_rows = []
    for field in evidence_fields:
        if field in df.columns:
            present = clean(df[field]).ne("")
            evidence_rows.append({
                "field": field,
                "records_with_content": int(present.sum()),
                "records_without_content": int((~present).sum()),
                "records_total": len(df),
                "content_presence_pct": round(float(present.mean() * 100), 1),
                "interpretation": (
                    "Text is present; its evidential quality must be assessed."
                    if present.any()
                    else "No text recorded in this field."
                ),
            })
    evidence_completeness = pd.DataFrame(evidence_rows)
    evidence_completeness.to_csv(
        output / "phase13_5_evidence_field_completeness.csv", index=False
    )

    # Provision-level queue to support later source review.
    inventory_fields = [
        "id", "country", "document", "article_or_section",
        "implementation_status", "implementation_notes",
        "verification_notes", "source_reference", "exact_text",
    ]
    available_inventory = [c for c in inventory_fields if c in df.columns]
    inventory = df[available_inventory].copy()
    inventory.to_csv(
        output / "phase13_5_implementation_evidence_inventory.csv",
        index=False,
    )

    # Optional: summarise audit rows that explicitly concern implementation.
    audit_summary_text = (
        "The Phase 12 verification audit was not found; no audit summary "
        "was generated."
    )
    audit_output = output / "phase13_5_implementation_related_audit_entries.csv"
    if audit_source.is_file():
        audit = pd.read_csv(audit_source, dtype=str).fillna("")
        expected = {"id", "column", "verdict", "finding_and_evidence"}
        if expected.issubset(audit.columns):
            mask = (
                audit["column"].astype(str).str.contains(
                    "implementation", case=False, na=False
                )
                | audit["finding_and_evidence"].astype(str).str.contains(
                    "implementation|implemented|deployment|deployed|operational",
                    case=False, na=False, regex=True
                )
            )
            implementation_audit = audit.loc[mask].copy()
            implementation_audit.to_csv(audit_output, index=False)
            audit_summary_text = (
                f"Found {len(implementation_audit)} audit row(s) whose field "
                "or finding text refers to implementation-related matters. "
                "These are audit notes, not proof of implementation."
            )
        else:
            audit_summary_text = (
                "The verification audit exists but does not contain all expected "
                "columns; it was not analysed."
            )

    def distribution_text(table, field):
        return "\n".join(
            f"- **{row[field]}:** {int(row['provision_count'])} provision(s) "
            f"({row['sample_share_pct']:.1f}%)"
            for _, row in table.iterrows()
        )

    lines = [
        "# Phase 13.5 — Implementation Evidence and Governance Gaps",
        "",
        "## Purpose",
        "",
        "This phase examines the implementation-status labels and the presence "
        "of implementation-related text recorded in the annotated dataset. "
        "It distinguishes recorded evidence from demonstrated implementation.",
        "",
        "## Dataset scope",
        "",
        f"- Provisions analysed: **{len(df)}**",
        f"- Jurisdictions represented: **{df['country'].nunique()}**",
        "- Source: `data/annotated/governance_dataset.csv`",
        "- Original annotated dataset modified: **No**",
        "",
        "## 1. Recorded implementation-status distribution",
        "",
        distribution_text(status_table, "implementation_status"),
        "",
        "## 2. Implementation status by jurisdiction",
        "",
        "See the accompanying count and within-jurisdiction percentage matrices. "
        "They describe only the coded records in this sample.",
        "",
        "## 3. Evidence-field completeness",
        "",
        "The completeness table records whether selected fields contain text. "
        "It does not assess the reliability, independence, date, or sufficiency "
        "of that text.",
        "",
    ]

    for _, row in evidence_completeness.iterrows():
        lines.append(
            f"- **{row['field']}**: {row['records_with_content']}/"
            f"{row['records_total']} records contain text "
            f"({row['content_presence_pct']:.1f}%)."
        )

    lines.extend([
        "",
        "## 4. Phase 12 audit cross-reference",
        "",
        audit_summary_text,
        "",
        "## 5. How to interpret apparent gaps",
        "",
        "- A blank implementation field is an evidence-recording gap in this "
        "dataset; it does not prove that implementation has not occurred.",
        "- A populated implementation note may describe an announcement, plan, "
        "institution, consultation, or activity; the underlying source and "
        "specific passage must be checked before classifying it as implementation.",
        "- Formal legal duties and evidence of operational implementation are "
        "different analytical categories.",
        "- An implementation status should ideally be supported by an identifiable "
        "issuing organisation, publication date, source, and specific passage.",
        "- The selected 20 provisions are not a comprehensive implementation "
        "survey of any jurisdiction.",
        "",
        "## 6. Recommended evidence standard for subsequent source review",
        "",
        "For each implementation claim, record where available:",
        "1. Issuing organisation or responsible institution.",
        "2. Document or source title and stable reference.",
        "3. Publication date (and relevant event date, if different).",
        "4. Page, paragraph, article, or section.",
        "5. A short specific passage supporting the claim.",
        "6. What the evidence demonstrates and what it does not demonstrate.",
        "7. Whether the source is primary, official secondary, or other material.",
        "",
        "## 7. Limitations",
        "",
        "This script performs structured descriptive analysis only. It does not "
        "retrieve external sources, validate implementation claims, determine "
        "causation, or measure governance effectiveness. Pending Phase 12 "
        "corrections have not been automatically applied.",
        "",
        "## 8. Output files",
        "",
        "Detailed CSV files are saved in `results/phase13/comparative_analysis/` "
        "with the prefix `phase13_5_`.",
        "",
        "## Next phase",
        "",
        "Phase 13.6 will synthesise the comparative findings into a structured "
        "research report, clearly separating dataset observations, legal "
        "interpretation, implementation evidence, and limitations.",
        "",
    ])

    report = reports / "Phase13_5_Implementation_Evidence_and_Gaps.md"
    report.write_text("\n".join(lines), encoding="utf-8")

    print("\nPHASE 13.5 COMPLETED")
    print(f"Records analysed: {len(df)}")
    print(f"Jurisdictions: {df['country'].nunique()}")
    print(f"Implementation-status categories: {df['implementation_status'].nunique()}")
    print(f"Evidence fields assessed: {len(evidence_completeness)}")
    print(f"Tables saved to: {output}")
    print(f"Report saved to: {report}")
    print("Original annotated dataset was not modified.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\nPHASE 13.5 FAILED: {exc}", file=sys.stderr)
        raise
