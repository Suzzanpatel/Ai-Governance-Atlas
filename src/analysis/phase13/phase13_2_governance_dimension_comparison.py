"""
Phase 13.2 — Governance Dimension Comparison
AI Governance Atlas

Analyses how the coded governance dimensions are distributed across the
jurisdictions represented in the annotated dataset.

Run from the project root:
    python src/analysis/phase13/phase13_2_governance_dimension_comparison.py

This is descriptive analysis of the selected coded sample. It does not
measure regulatory effectiveness or establish that a jurisdiction lacks
a governance mechanism merely because it is absent from this dataset.
"""

from pathlib import Path
import sys
import pandas as pd


def locate_root() -> Path:
    here = Path(__file__).resolve()
    for candidate in [here.parent, *here.parents]:
        if (candidate / "data/annotated/governance_dataset.csv").exists():
            return candidate
    raise FileNotFoundError(
        "Cannot find data/annotated/governance_dataset.csv. "
        "Run this script from inside the project."
    )


def normalise(series: pd.Series) -> pd.Series:
    return (
        series.fillna("")
        .astype(str)
        .str.strip()
        .replace("", "Not recorded")
    )


def main():
    root = locate_root()
    source = root / "data/annotated/governance_dataset.csv"
    out = root / "results/phase13/comparative_analysis"
    reports = root / "results/phase13/reports"
    out.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(source, dtype=str).fillna("")
    required = {"id", "country", "governance_dimension"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    if df.empty:
        raise ValueError("The annotated dataset is empty.")
    if df["id"].duplicated().any():
        raise ValueError("Duplicate provision IDs detected; resolve these first.")

    df["country"] = normalise(df["country"])
    df["governance_dimension"] = normalise(df["governance_dimension"])

    # Count provisions per jurisdiction and dimension.
    counts = pd.crosstab(df["country"], df["governance_dimension"])
    counts.index.name = "jurisdiction"
    counts.columns.name = "governance_dimension"
    counts.to_csv(out / "phase13_2_dimension_counts_by_jurisdiction.csv")

    # Within-jurisdiction percentages support comparisons despite unequal
    # numbers of sampled provisions per jurisdiction.
    totals = counts.sum(axis=1).replace(0, pd.NA)
    percentages = counts.div(totals, axis=0).mul(100).round(1)
    percentages.to_csv(
        out / "phase13_2_dimension_percentages_by_jurisdiction.csv"
    )

    # Overall share of each dimension in the coded sample.
    overall = (
        df["governance_dimension"].value_counts()
        .rename_axis("governance_dimension")
        .reset_index(name="provision_count")
    )
    overall["sample_share_pct"] = (
        overall["provision_count"] / len(df) * 100
    ).round(1)
    overall.to_csv(out / "phase13_2_overall_dimension_distribution.csv", index=False)

    # Explicit presence table: 1 means at least one provision is coded in that
    # dimension for that jurisdiction; 0 means none in this selected dataset.
    presence = (counts > 0).astype(int)
    presence.to_csv(out / "phase13_2_dimension_presence_matrix.csv")

    # Dimension coverage: number of represented jurisdictions in which each
    # dimension appears. This describes dataset coverage, not legal coverage.
    coverage = pd.DataFrame({
        "governance_dimension": counts.columns,
        "jurisdictions_with_at_least_one_coded_provision": [
            int(presence[col].sum()) for col in counts.columns
        ],
        "jurisdictions_in_dataset": len(counts.index),
    })
    coverage["jurisdiction_sample_coverage_pct"] = (
        coverage["jurisdictions_with_at_least_one_coded_provision"]
        / len(counts.index) * 100
    ).round(1)
    coverage = coverage.sort_values(
        ["jurisdictions_with_at_least_one_coded_provision", "governance_dimension"],
        ascending=[False, True],
    )
    coverage.to_csv(out / "phase13_2_dimension_sample_coverage.csv", index=False)

    # Concentration of coded provisions across dimensions within each
    # jurisdiction (Herfindahl-style index). Higher values indicate a more
    # concentrated distribution in this sample; not a measure of regulation.
    concentration_rows = []
    for jurisdiction, row in percentages.iterrows():
        shares = row.dropna() / 100
        concentration_rows.append({
            "jurisdiction": jurisdiction,
            "coded_provisions": int(counts.loc[jurisdiction].sum()),
            "dimensions_with_coded_provisions": int((counts.loc[jurisdiction] > 0).sum()),
            "dimension_distribution_concentration_index": round(
                float((shares ** 2).sum()), 4
            ),
        })
    concentration = pd.DataFrame(concentration_rows)
    concentration.to_csv(
        out / "phase13_2_within_jurisdiction_dimension_concentration.csv",
        index=False,
    )

    # Machine-generated observations are deliberately framed as sample
    # descriptions and avoid causal or effectiveness conclusions.
    lines = [
        "# Phase 13.2 — Governance Dimension Comparison",
        "",
        "## Purpose",
        "",
        "This analysis compares the distribution of coded governance dimensions "
        "across the jurisdictions represented in the AI Governance Atlas sample.",
        "",
        "## Dataset scope",
        "",
        f"- Provisions analysed: **{len(df)}**",
        f"- Jurisdictions represented: **{len(counts.index)}**",
        f"- Distinct recorded governance-dimension labels: **{len(counts.columns)}**",
        "- Source: `data/annotated/governance_dataset.csv`",
        "- Original dataset modified: **No**",
        "",
        "## 1. Overall dimension distribution",
        "",
    ]
    for _, row in overall.iterrows():
        lines.append(
            f"- **{row['governance_dimension']}**: {int(row['provision_count'])} "
            f"provisions ({row['sample_share_pct']:.1f}% of the coded sample)"
        )

    lines.extend([
        "",
        "## 2. Dimension distribution within each jurisdiction",
        "",
        "The percentages below use each jurisdiction's own number of coded "
        "provisions as the denominator. This helps describe the composition "
        "of each jurisdiction's sample when sample sizes differ.",
        "",
    ])
    for jurisdiction in percentages.index:
        lines.append(f"### {jurisdiction}")
        for dimension, value in percentages.loc[jurisdiction].dropna().items():
            count = int(counts.loc[jurisdiction, dimension])
            lines.append(f"- {dimension}: {count} provision(s), {value:.1f}%")
        lines.append("")

    lines.extend([
        "## 3. Sample coverage across jurisdictions",
        "",
        "A dimension's coverage count is the number of represented jurisdictions "
        "with at least one provision coded under that label in this dataset.",
        "",
    ])
    for _, row in coverage.iterrows():
        lines.append(
            f"- **{row['governance_dimension']}**: present in "
            f"{int(row['jurisdictions_with_at_least_one_coded_provision'])} "
            f"of {int(row['jurisdictions_in_dataset'])} represented jurisdictions"
        )

    lines.extend([
        "",
        "## 4. Interpretation limits",
        "",
        "1. These results describe the selected provisions and their current coding; "
        "they are not a complete inventory of each jurisdiction's AI governance.",
        "2. A dimension with no coded provision for a jurisdiction is a gap in this "
        "dataset's coverage, not proof that the jurisdiction has no relevant rule.",
        "3. A higher share for a dimension does not show that the jurisdiction "
        "regulates that issue more strongly or effectively.",
        "4. Differences may reflect the selection of instruments, provision-level "
        "sampling, classification choices, or differences in document structure.",
        "5. The concentration index describes the distribution of this sample only. "
        "It is not a regulatory quality score.",
        "6. Phase 12 pending corrections have not been applied automatically.",
        "",
        "## 5. Output files",
        "",
        "All detailed tables are in `results/phase13/comparative_analysis/` "
        "and have the prefix `phase13_2_`.",
        "",
        "## 6. Next step",
        "",
        "Phase 13.3 will compare the recorded legal force and enforceability of "
        "the selected provisions, keeping binding duties distinct from voluntary "
        "or recommendatory instruments.",
        "",
    ])

    report_path = reports / "Phase13_2_Governance_Dimension_Comparison.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")

    print("\nPHASE 13.2 COMPLETED")
    print(f"Records analysed: {len(df)}")
    print(f"Jurisdictions: {len(counts.index)}")
    print(f"Governance-dimension labels: {len(counts.columns)}")
    print(f"Tables saved to: {out}")
    print(f"Report saved to: {report_path}")
    print("Original annotated dataset was not modified.")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"\nPHASE 13.2 FAILED: {error}", file=sys.stderr)
        raise
