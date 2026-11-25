"""
Phase 13.1 — Comparative Jurisdictional Analysis
AI Governance Atlas

Reads the original annotated dataset and produces reproducible descriptive
comparisons. It does not independently verify legal claims or infer real-world
implementation effectiveness.

Run from the project root:
    python src/analysis/phase13/phase13_1_comparative_analysis.py
"""

from pathlib import Path
import sys
import pandas as pd

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None


def find_project_root() -> Path:
    """Find the project root by locating the expected dataset."""
    current = Path(__file__).resolve()
    for candidate in [current.parent, *current.parents]:
        expected = candidate / "data" / "annotated" / "governance_dataset.csv"
        if expected.exists():
            return candidate
    raise FileNotFoundError(
        "Could not locate data/annotated/governance_dataset.csv. "
        "Run this script from inside the AI Governance Atlas project."
    )


def clean_text(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.strip().replace("", "Not recorded")


def save_bar_chart(data: pd.Series, title: str, filename: Path, xlabel: str):
    if plt is None or data.empty:
        return False

    plot_data = data.sort_values(ascending=True)
    height = max(4, 0.45 * len(plot_data))
    fig, ax = plt.subplots(figsize=(10, height))
    plot_data.plot(kind="barh", ax=ax)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("")
    fig.tight_layout()
    fig.savefig(filename, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return True


def main():
    root = find_project_root()
    source = root / "data" / "annotated" / "governance_dataset.csv"
    output = root / "results" / "phase13" / "comparative_analysis"
    charts = root / "results" / "phase13" / "charts"
    reports = root / "results" / "phase13" / "reports"

    for folder in (output, charts, reports):
        folder.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(source, dtype=str).fillna("")

    required = [
        "id", "country", "document", "document_type", "legal_status",
        "governance_dimension", "obligation_type", "responsible_party",
        "applicability", "enforcement_mechanism",
        "implementation_status"
    ]
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")

    if df.empty:
        raise ValueError("The annotated dataset contains no records.")
    if df["id"].duplicated().any():
        duplicates = df.loc[df["id"].duplicated(), "id"].tolist()
        raise ValueError(f"Duplicate provision IDs found: {duplicates}")

    # Keep jurisdiction labels exactly as recorded in the dataset.
    fields = [
        "country", "document_type", "legal_status", "governance_dimension",
        "obligation_type", "responsible_party", "applicability",
        "enforcement_mechanism", "implementation_status"
    ]
    for field in fields:
        df[field] = clean_text(df[field])

    # Core frequency tables.
    summary_specs = {
        "provisions_by_jurisdiction": "country",
        "provisions_by_document_type": "document_type",
        "provisions_by_legal_status": "legal_status",
        "provisions_by_governance_dimension": "governance_dimension",
        "provisions_by_obligation_type": "obligation_type",
        "provisions_by_responsible_party": "responsible_party",
        "provisions_by_applicability": "applicability",
        "provisions_by_enforcement_mechanism": "enforcement_mechanism",
        "provisions_by_implementation_status": "implementation_status",
    }

    tables = {}
    for filename, field in summary_specs.items():
        table = (
            df[field].value_counts(dropna=False)
            .rename_axis(field)
            .reset_index(name="provision_count")
        )
        table["share_of_dataset_pct"] = (
            table["provision_count"] / len(df) * 100
        ).round(1)
        table.to_csv(output / f"{filename}.csv", index=False)
        tables[field] = table

    # Jurisdiction-by-dimension count and row-percentage matrices.
    jurisdiction_dimension = pd.crosstab(
        df["country"], df["governance_dimension"], margins=False
    )
    jurisdiction_dimension.to_csv(
        output / "jurisdiction_by_governance_dimension_counts.csv"
    )

    row_pct = jurisdiction_dimension.div(
        jurisdiction_dimension.sum(axis=1).replace(0, pd.NA), axis=0
    ).mul(100).round(1)
    row_pct.to_csv(
        output / "jurisdiction_by_governance_dimension_row_percentages.csv"
    )

    # Jurisdiction-by-legal-status comparison.
    legal_status_matrix = pd.crosstab(df["country"], df["legal_status"])
    legal_status_matrix.to_csv(
        output / "jurisdiction_by_legal_status_counts.csv"
    )

    # Jurisdiction-by-enforcement comparison.
    enforcement_matrix = pd.crosstab(
        df["country"], df["enforcement_mechanism"]
    )
    enforcement_matrix.to_csv(
        output / "jurisdiction_by_enforcement_mechanism_counts.csv"
    )

    # Record-level inventory and data completeness.
    inventory_columns = [
        "id", "country", "document", "document_type", "legal_status",
        "article_or_section", "governance_dimension", "secondary_dimension",
        "obligation_type", "responsible_party", "applicability",
        "enforcement_mechanism", "implementation_status"
    ]
    available_inventory = [c for c in inventory_columns if c in df.columns]
    df[available_inventory].to_csv(
        output / "provision_comparison_inventory.csv", index=False
    )

    completeness = pd.DataFrame({
        "column": df.columns,
        "non_empty_records": [
            int(df[c].astype(str).str.strip().ne("").sum()) for c in df.columns
        ],
    })
    completeness["empty_records"] = len(df) - completeness["non_empty_records"]
    completeness["completeness_pct"] = (
        completeness["non_empty_records"] / len(df) * 100
    ).round(1)
    completeness.to_csv(output / "dataset_completeness.csv", index=False)

    charts_created = []
    if plt is not None:
        chart_specs = [
            ("country", "Provisions by jurisdiction", "provisions_by_jurisdiction.png"),
            ("governance_dimension", "Provisions by governance dimension", "provisions_by_governance_dimension.png"),
            ("legal_status", "Provisions by recorded legal status", "provisions_by_legal_status.png"),
            ("obligation_type", "Provisions by obligation type", "provisions_by_obligation_type.png"),
        ]
        for field, title, filename in chart_specs:
            counts = df[field].value_counts()
            if save_bar_chart(counts, title, charts / filename, "Number of provisions"):
                charts_created.append(filename)

    # Report uses descriptive language only; no unsupported effectiveness claims.
    jurisdiction_counts = df["country"].value_counts()
    dimension_counts = df["governance_dimension"].value_counts()
    legal_counts = df["legal_status"].value_counts()
    enforcement_counts = df["enforcement_mechanism"].value_counts()

    def bullet_lines(series, limit=12):
        if series.empty:
            return "- No values recorded."
        return "\n".join(
            f"- **{label}:** {count} ({count / len(df) * 100:.1f}%)"
            for label, count in series.head(limit).items()
        )

    report = f"""# Phase 13.1 — Comparative Jurisdictional Analysis

## Purpose

This report describes the distribution and recorded characteristics of the
provisions in the AI Governance Atlas dataset. It is a descriptive analysis of
the coded sample, not a complete census of each jurisdiction's AI regulation.

## Dataset scope

- Source: `data/annotated/governance_dataset.csv`
- Records analysed: **{len(df)}**
- Unique provision IDs: **{df['id'].nunique()}**
- Jurisdictions / benchmark groups represented: **{df['country'].nunique()}**
- Duplicate IDs: **0**
- Original dataset modified: **No**

## 1. Provisions by jurisdiction

{bullet_lines(jurisdiction_counts)}

## 2. Governance dimensions

{bullet_lines(dimension_counts)}

## 3. Recorded legal status

{bullet_lines(legal_counts)}

## 4. Recorded enforcement mechanisms

{bullet_lines(enforcement_counts)}

## 5. Comparative matrices

The following files support cross-jurisdictional comparison:

- `jurisdiction_by_governance_dimension_counts.csv`
- `jurisdiction_by_governance_dimension_row_percentages.csv`
- `jurisdiction_by_legal_status_counts.csv`
- `jurisdiction_by_enforcement_mechanism_counts.csv`

Counts show how the selected provisions are distributed in this dataset.
Row percentages show the composition of each jurisdiction's selected sample.
Neither measure, by itself, establishes regulatory strength or effectiveness.

## 6. Methodological cautions

1. The dataset contains a selected set of coded provisions, not every relevant
   legal or policy instrument in each jurisdiction.
2. Differences in record counts may reflect sampling and coding choices rather
   than differences in the overall regulatory systems.
3. Governance dimensions and other categories reflect the dataset's coding.
4. A recorded enforcement mechanism indicates what the provision or instrument
   specifies; it does not prove that enforcement has occurred.
5. An implementation-status entry is not independent proof of implementation.
6. The Phase 12 audit and review outputs include unresolved items. This report
   uses the original annotated dataset as its baseline and does not silently
   apply pending corrections.
7. This script performs descriptive computation only. It does not retrieve
   primary sources, resolve legal interpretation, or independently verify
   legal status or implementation claims.

## 7. Output files

The CSV tables are saved in `results/phase13/comparative_analysis/`.
Charts, when Matplotlib is installed, are saved in `results/phase13/charts/`.
This report is saved in `results/phase13/reports/`.

## Next analytical step

Phase 13.2 will examine the distribution of governance dimensions across
jurisdictions, identify areas represented unevenly in the coded sample, and
prepare cautious comparative observations for legal interpretation.
"""
    report_path = reports / "Phase13_1_Comparative_Jurisdictional_Analysis.md"
    report_path.write_text(report, encoding="utf-8")

    print("\nPHASE 13.1 COMPLETED")
    print(f"Project root: {root}")
    print(f"Source dataset: {source}")
    print(f"Records analysed: {len(df)}")
    print(f"Jurisdictions represented: {df['country'].nunique()}")
    print(f"Output tables: {output}")
    print(f"Charts created: {len(charts_created)}")
    if plt is None:
        print("Charts skipped: matplotlib is not installed.")
    print(f"Report: {report_path}")
    print("\nNo source dataset rows were changed.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\nPHASE 13.1 FAILED: {exc}", file=sys.stderr)
        raise
