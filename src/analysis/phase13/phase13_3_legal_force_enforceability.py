"""
Phase 13.3 — Legal Force and Enforceability Comparison
AI Governance Atlas

Descriptive comparison of the legal_status, obligation_type and
enforcement_mechanism fields in the annotated dataset.

Run from project root:
    python src/analysis/phase13/phase13_3_legal_force_enforceability.py

This script does not independently determine legal force, interpret legislation,
or establish whether enforcement has occurred.
"""

from pathlib import Path
import sys
import pandas as pd


def locate_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in [current.parent, *current.parents]:
        if (candidate / "data/annotated/governance_dataset.csv").is_file():
            return candidate
    raise FileNotFoundError(
        "Could not locate data/annotated/governance_dataset.csv."
    )


def clean(series: pd.Series) -> pd.Series:
    return (
        series.fillna("").astype(str).str.strip()
        .replace("", "Not recorded")
    )


def cross_tab(df: pd.DataFrame, row: str, col: str, output: Path):
    result = pd.crosstab(df[row], df[col], dropna=False)
    result.to_csv(output)
    return result


def main():
    root = locate_root()
    source = root / "data/annotated/governance_dataset.csv"
    output = root / "results/phase13/comparative_analysis"
    reports = root / "results/phase13/reports"
    output.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(source, dtype=str).fillna("")
    required = [
        "id", "country", "legal_status", "obligation_type",
        "enforcement_mechanism"
    ]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")
    if df.empty:
        raise ValueError("The annotated dataset is empty.")
    if df["id"].duplicated().any():
        raise ValueError("Duplicate provision IDs detected.")

    for col in required:
        if col != "id":
            df[col] = clean(df[col])

    # Counts and within-jurisdiction percentages for each legal dimension.
    fields = ["legal_status", "obligation_type", "enforcement_mechanism"]
    for field in fields:
        counts = pd.crosstab(df["country"], df[field])
        counts.to_csv(output / f"phase13_3_{field}_by_jurisdiction_counts.csv")
        percentages = counts.div(
            counts.sum(axis=1).replace(0, pd.NA), axis=0
        ).mul(100).round(1)
        percentages.to_csv(
            output / f"phase13_3_{field}_by_jurisdiction_percentages.csv"
        )

        overall = (
            df[field].value_counts()
            .rename_axis(field)
            .reset_index(name="provision_count")
        )
        overall["sample_share_pct"] = (
            overall["provision_count"] / len(df) * 100
        ).round(1)
        overall.to_csv(
            output / f"phase13_3_overall_{field}_distribution.csv",
            index=False,
        )

    # Pairwise relationships: these are coding co-occurrences, not proof
    # that a particular enforcement route legally attaches to every duty.
    cross_tab(
        df, "legal_status", "enforcement_mechanism",
        output / "phase13_3_legal_status_by_enforcement_mechanism.csv"
    )
    cross_tab(
        df, "legal_status", "obligation_type",
        output / "phase13_3_legal_status_by_obligation_type.csv"
    )
    cross_tab(
        df, "obligation_type", "enforcement_mechanism",
        output / "phase13_3_obligation_type_by_enforcement_mechanism.csv"
    )

    selected = [
        "id", "country", "document", "document_type", "legal_status",
        "article_or_section", "obligation_type", "responsible_party",
        "enforcement_mechanism", "verification_notes"
    ]
    available = [c for c in selected if c in df.columns]
    df[available].to_csv(
        output / "phase13_3_provision_level_legal_force_inventory.csv",
        index=False,
    )

    def describe(field: str) -> str:
        counts = df[field].value_counts()
        return "\n".join(
            f"- **{label}:** {number} provision(s) "
            f"({number / len(df) * 100:.1f}%)"
            for label, number in counts.items()
        )

    jurisdictions = sorted(df["country"].unique())
    lines = [
        "# Phase 13.3 — Legal Force and Enforceability Comparison",
        "",
        "## Purpose",
        "",
        "This phase compares how the selected provisions are coded for legal "
        "status, obligation type and enforcement mechanism. The analysis is "
        "descriptive and limited to the annotated sample.",
        "",
        "## Dataset scope",
        "",
        f"- Provisions analysed: **{len(df)}**",
        f"- Jurisdictions represented: **{len(jurisdictions)}**",
        f"- Jurisdiction labels: {', '.join(jurisdictions)}",
        "- Source: `data/annotated/governance_dataset.csv`",
        "- Original annotated dataset modified: **No**",
        "",
        "## 1. Recorded legal status",
        "",
        describe("legal_status"),
        "",
        "## 2. Recorded obligation type",
        "",
        describe("obligation_type"),
        "",
        "## 3. Recorded enforcement mechanisms",
        "",
        describe("enforcement_mechanism"),
        "",
        "## 4. Comparative interpretation",
        "",
        "Use the jurisdiction-level percentage tables to compare the composition "
        "of each jurisdiction's selected sample. Use the pairwise cross-tabulations "
        "to identify which labels co-occur in the dataset. These are descriptive "
        "relationships, not legal conclusions.",
        "",
        "A binding instrument may contain provisions with different kinds of "
        "duties and different enforcement routes. Conversely, a non-binding "
        "instrument may influence governance without creating directly "
        "enforceable legal obligations. The dataset's labels must therefore be "
        "checked against the relevant source text before making instrument-wide "
        "claims.",
        "",
        "## 5. Questions for legal interpretation",
        "",
        "1. Is the recorded legal status accurate for the specific provision, "
        "rather than only for the instrument as a whole?",
        "2. Does the text create a mandatory duty, a conditional duty, a power, "
        "a recommendation, or a voluntary commitment?",
        "3. Who is legally bound, and under what conditions does the duty apply?",
        "4. Is the recorded enforcement mechanism directly attached to this "
        "provision, located elsewhere in the instrument, or supplied by another "
        "legal framework?",
        "5. Are there procedural, jurisdictional, or commencement conditions "
        "that affect enforceability?",
        "",
        "## 6. Limitations",
        "",
        "- The script does not read or interpret primary legal sources.",
        "- The script does not determine whether an instrument is legally binding "
        "as a matter of law.",
        "- A recorded enforcement mechanism does not demonstrate actual enforcement.",
        "- Co-occurrence in a dataset does not establish a legal relationship.",
        "- The 20 provisions are a selected sample and do not represent every "
        "relevant rule in each jurisdiction.",
        "- Pending Phase 12 corrections have not been applied.",
        "",
        "## 7. Output files",
        "",
        "Detailed CSV tables are saved in `results/phase13/comparative_analysis/` "
        "with the prefix `phase13_3_`.",
        "",
        "## Next phase",
        "",
        "Phase 13.4 will compare the allocation of institutional and actor "
        "responsibility across the selected provisions.",
        "",
    ]

    report = reports / "Phase13_3_Legal_Force_and_Enforceability.md"
    report.write_text("\n".join(lines), encoding="utf-8")

    print("\nPHASE 13.3 COMPLETED")
    print(f"Records analysed: {len(df)}")
    print(f"Jurisdictions: {len(jurisdictions)}")
    print(f"Legal-status categories: {df['legal_status'].nunique()}")
    print(f"Obligation-type categories: {df['obligation_type'].nunique()}")
    print(f"Enforcement-mechanism categories: {df['enforcement_mechanism'].nunique()}")
    print(f"Tables saved to: {output}")
    print(f"Report saved to: {report}")
    print("Original annotated dataset was not modified.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\nPHASE 13.3 FAILED: {exc}", file=sys.stderr)
        raise
