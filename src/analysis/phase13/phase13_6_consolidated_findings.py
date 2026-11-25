"""
Phase 13.6 — Consolidated Comparative Findings Report
AI Governance Atlas

Synthesises outputs produced by Phases 13.1–13.5 into one structured report.
It reads existing CSV/report outputs and does not modify source data or prior
phase outputs. Missing phase outputs are disclosed rather than guessed.

Run from project root:
    python src/analysis/phase13/phase13_6_consolidated_findings.py
"""

from pathlib import Path
import sys
import pandas as pd


PHASE_REPORTS = [
    ("13.1", "Comparative jurisdictional analysis",
     "Phase13_1_Comparative_Jurisdictional_Analysis.md"),
    ("13.2", "Governance dimension comparison",
     "Phase13_2_Governance_Dimension_Comparison.md"),
    ("13.3", "Legal force and enforceability",
     "Phase13_3_Legal_Force_and_Enforceability.md"),
    ("13.4", "Institutional responsibility",
     "Phase13_4_Institutional_Responsibility_Comparison.md"),
    ("13.5", "Implementation evidence and governance gaps",
     "Phase13_5_Implementation_Evidence_and_Gaps.md"),
]


def locate_root() -> Path:
    here = Path(__file__).resolve()
    for candidate in [here.parent, *here.parents]:
        if (candidate / "data/annotated/governance_dataset.csv").is_file():
            return candidate
    raise FileNotFoundError(
        "Cannot locate data/annotated/governance_dataset.csv."
    )


def read_csv_if_exists(path: Path):
    if not path.is_file():
        return None
    try:
        return pd.read_csv(path, dtype=str).fillna("")
    except Exception as exc:
        print(f"WARNING: Could not read {path.name}: {exc}")
        return None


def top_distribution(path: Path, label_column: str, count_column: str,
                     max_rows: int = 10):
    table = read_csv_if_exists(path)
    if table is None or label_column not in table or count_column not in table:
        return None
    return table[[label_column, count_column]].head(max_rows)


def format_distribution(table, label_column, count_column):
    if table is None or table.empty:
        return "- No corresponding Phase 13 output was available."
    return "\n".join(
        f"- **{row[label_column]}:** {row[count_column]}"
        for _, row in table.iterrows()
    )


def main():
    root = locate_root()
    dataset_path = root / "data/annotated/governance_dataset.csv"
    output_dir = root / "results/phase13/comparative_analysis"
    report_dir = root / "results/phase13/reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(dataset_path, dtype=str).fillna("")
    if df.empty:
        raise ValueError("The annotated dataset is empty.")
    if "id" not in df.columns:
        raise ValueError("The dataset does not contain an 'id' column.")
    if df["id"].duplicated().any():
        raise ValueError("Duplicate provision IDs detected.")

    # Check prior phase reports. The script does not fabricate missing results.
    phase_status = []
    report_contents = {}
    for number, title, filename in PHASE_REPORTS:
        path = report_dir / filename
        exists = path.is_file()
        phase_status.append({
            "phase": number,
            "analysis": title,
            "report_found": "Yes" if exists else "No",
            # Project-relative, so outputs are identical on every machine
            "report_path": path.relative_to(root).as_posix() if exists else "",
        })
        if exists:
            report_contents[number] = path.read_text(encoding="utf-8")

    pd.DataFrame(phase_status).to_csv(
        output_dir / "phase13_6_phase_output_check.csv", index=False
    )

    # Read key descriptive tables if they exist.
    tables = {
        "jurisdiction": top_distribution(
            output_dir / "provisions_by_jurisdiction.csv",
            "country", "provision_count"
        ),
        "dimension": top_distribution(
            output_dir / "provisions_by_governance_dimension.csv",
            "governance_dimension", "provision_count"
        ),
        "legal_status": top_distribution(
            output_dir / "phase13_3_overall_legal_status_distribution.csv",
            "legal_status", "provision_count"
        ),
        "obligation": top_distribution(
            output_dir / "phase13_3_overall_obligation_type_distribution.csv",
            "obligation_type", "provision_count"
        ),
        "enforcement": top_distribution(
            output_dir / "phase13_3_overall_enforcement_mechanism_distribution.csv",
            "enforcement_mechanism", "provision_count"
        ),
        "responsibility": top_distribution(
            output_dir / "phase13_4_overall_responsible_party_distribution.csv",
            "responsible_party", "provision_count"
        ),
        "implementation": top_distribution(
            output_dir / "phase13_5_implementation_status_distribution.csv",
            "implementation_status", "provision_count"
        ),
    }

    # A machine-readable synthesis inventory of available distributions.
    inventory_rows = []
    for key, table in tables.items():
        if table is None:
            inventory_rows.append({
                "analysis_area": key,
                "category": "",
                "provision_count": "",
                "availability": "Missing prior-phase table",
            })
        else:
            for _, row in table.iterrows():
                inventory_rows.append({
                    "analysis_area": key,
                    "category": row.iloc[0],
                    "provision_count": row.iloc[1],
                    "availability": "Available",
                })
    pd.DataFrame(inventory_rows).to_csv(
        output_dir / "phase13_6_findings_data_inventory.csv", index=False
    )

    phase_table = pd.DataFrame(phase_status)
    completed = phase_table[phase_table["report_found"] == "Yes"]["phase"].tolist()
    missing = phase_table[phase_table["report_found"] == "No"]["phase"].tolist()

    lines = [
        "# Phase 13.6 — Consolidated Comparative Findings",
        "",
        "## Executive overview",
        "",
        "This report consolidates the descriptive outputs of the AI Governance "
        "Atlas comparative analysis. It is a structured synthesis of the "
        "annotated sample, not a definitive ranking of national AI governance "
        "systems and not an independent legal opinion.",
        "",
        "## 1. Dataset and analytical scope",
        "",
        f"- Provisions in the current annotated dataset: **{len(df)}**",
        f"- Unique provision IDs: **{df['id'].nunique()}**",
        f"- Jurisdiction labels represented: **{df['country'].nunique() if 'country' in df.columns else 'Not available'}**",
        "- Baseline: `data/annotated/governance_dataset.csv`",
        "- Original annotated dataset modified: **No**",
        "",
        "## 2. Phase output availability",
        "",
    ]

    for _, row in phase_table.iterrows():
        status = "Available" if row["report_found"] == "Yes" else "Not found"
        lines.append(f"- **Phase {row['phase']} — {row['analysis']}:** {status}")

    lines.extend([
        "",
        f"Reports available for phases: {', '.join(completed) if completed else 'None'}.",
        f"Reports missing for phases: {', '.join(missing) if missing else 'None'}.",
        "",
        "## 3. Descriptive findings from available tables",
        "",
        "### 3.1 Jurisdictional distribution",
        "",
        format_distribution(tables["jurisdiction"], "country", "provision_count"),
        "",
        "### 3.2 Governance dimension distribution",
        "",
        format_distribution(
            tables["dimension"], "governance_dimension", "provision_count"
        ),
        "",
        "### 3.3 Recorded legal status",
        "",
        format_distribution(
            tables["legal_status"], "legal_status", "provision_count"
        ),
        "",
        "### 3.4 Recorded obligation types",
        "",
        format_distribution(
            tables["obligation"], "obligation_type", "provision_count"
        ),
        "",
        "### 3.5 Recorded enforcement mechanisms",
        "",
        format_distribution(
            tables["enforcement"], "enforcement_mechanism", "provision_count"
        ),
        "",
        "### 3.6 Recorded responsible parties",
        "",
        format_distribution(
            tables["responsibility"], "responsible_party", "provision_count"
        ),
        "",
        "### 3.7 Recorded implementation status",
        "",
        format_distribution(
            tables["implementation"], "implementation_status", "provision_count"
        ),
        "",
        "## 4. Comparative interpretation framework",
        "",
        "The results should be interpreted through four separate analytical "
        "layers:",
        "",
        "1. **Formal legal framework:** whether the relevant instrument or "
        "provision is binding, and the legal status applicable to the specific "
        "duty.",
        "2. **Substantive obligation:** what conduct is required, permitted, "
        "restricted, or recommended, and which actor is addressed.",
        "3. **Institutional and enforcement design:** which bodies supervise, "
        "administer, investigate, or enforce the relevant requirements, and "
        "what remedies or sanctions are available.",
        "4. **Implementation evidence:** whether reliable, dated and attributable "
        "sources demonstrate operational steps, institutional activity, or "
        "observed implementation.",
        "",
        "These layers must not be collapsed into a single measure of regulatory "
        "strength or effectiveness.",
        "",
        "## 5. Research questions for the final discussion",
        "",
        "- Which governance dimensions are represented across all jurisdictions "
        "in the selected sample, and which are unevenly represented?",
        "- How do binding obligations differ from voluntary, policy-based, or "
        "recommendatory approaches?",
        "- Are duties and supervisory functions clearly allocated among providers, "
        "deployers, regulators, and public authorities?",
        "- Do the selected provisions provide identifiable enforcement routes, "
        "and are those routes directly linked to the duties analysed?",
        "- What implementation evidence is available, and where does the evidence "
        "base remain incomplete?",
        "- What additional provisions or primary sources are required before "
        "making broader jurisdiction-level conclusions?",
        "",
        "## 6. Limitations and safeguards",
        "",
        "- The dataset contains a selected sample of 20 provisions; it is not a "
        "comprehensive inventory of the four jurisdictions or benchmark groups.",
        "- Counts and percentages are affected by the selection and coding of "
        "provisions.",
        "- A category absent from the sample is not necessarily absent from the "
        "jurisdiction's legal or policy framework.",
        "- Recorded enforcement mechanisms do not demonstrate that enforcement "
        "has occurred.",
        "- Recorded implementation status and notes are not independent proof "
        "of implementation.",
        "- Phase 12 pending corrections have not been automatically applied.",
        "- This script does not conduct source retrieval, legal interpretation, "
        "or independent verification.",
        "",
        "## 7. What is needed before drawing the final research conclusions",
        "",
        "1. Review each jurisdiction's primary legal sources for the provisions "
        "that support the comparative claims.",
        "2. Check whether legal status and commencement dates are current.",
        "3. Verify the relationship between substantive duties and enforcement "
        "provisions, including cross-references elsewhere in the instrument.",
        "4. Support implementation claims with dated official sources and "
        "specific passages.",
        "5. Expand the provision sample where a jurisdiction or governance "
        "dimension is underrepresented.",
        "6. Record unresolved or contradictory evidence transparently.",
        "",
        "## 8. Conclusion status",
        "",
        "This phase produces a consolidated descriptive findings document. "
        "It does not automatically generate a definitive conclusion about which "
        "jurisdiction has the strongest, weakest, or most effective AI governance "
        "system. Such conclusions require a defensible comparison framework, "
        "verified primary-source analysis, and evidence of implementation.",
        "",
        "## 9. Source phase reports",
        "",
    ])

    for number, title, filename in PHASE_REPORTS:
        if number in report_contents:
            lines.append(f"- **Phase {number}: {title}** — `{filename}`")

    report_path = report_dir / "Phase13_6_Consolidated_Comparative_Findings.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")

    print("\nPHASE 13.6 COMPLETED")
    print(f"Dataset records: {len(df)}")
    print(f"Phase reports found: {len(completed)}/5")
    print(f"Missing phase reports: {', '.join(missing) if missing else 'None'}")
    print(f"Findings inventory: {output_dir / 'phase13_6_findings_data_inventory.csv'}")
    print(f"Consolidated report: {report_path}")
    print("Original annotated dataset and prior phase outputs were not modified.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\nPHASE 13.6 FAILED: {exc}", file=sys.stderr)
        raise
