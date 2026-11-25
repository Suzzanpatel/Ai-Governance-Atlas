"""
Phase 13.4 — Institutional and Actor Responsibility Comparison
AI Governance Atlas

Compares the responsible_party and applicability fields in the annotated
provision dataset across represented jurisdictions.

Run from project root:
    python src/analysis/phase13/phase13_4_institutional_responsibility.py

This is descriptive coding analysis. It does not independently establish
the legal identity, powers, duties, or accountability of any actor.
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
        "Could not find data/annotated/governance_dataset.csv."
    )


def clean(series: pd.Series) -> pd.Series:
    return (
        series.fillna("").astype(str).str.strip()
        .replace("", "Not recorded")
    )


def save_crosstab(df, row, col, path):
    table = pd.crosstab(df[row], df[col])
    table.to_csv(path)
    return table


def main():
    root = locate_root()
    source = root / "data/annotated/governance_dataset.csv"
    output = root / "results/phase13/comparative_analysis"
    reports = root / "results/phase13/reports"
    output.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(source, dtype=str).fillna("")
    required = ["id", "country", "responsible_party", "applicability"]
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    if df.empty:
        raise ValueError("The annotated dataset is empty.")
    if df["id"].duplicated().any():
        raise ValueError("Duplicate provision IDs detected.")

    for column in required[1:]:
        df[column] = clean(df[column])

    # Count actor/responsible-party labels by jurisdiction.
    actor_counts = pd.crosstab(df["country"], df["responsible_party"])
    actor_counts.to_csv(
        output / "phase13_4_responsible_party_by_jurisdiction_counts.csv"
    )

    actor_percentages = actor_counts.div(
        actor_counts.sum(axis=1).replace(0, pd.NA), axis=0
    ).mul(100).round(1)
    actor_percentages.to_csv(
        output / "phase13_4_responsible_party_by_jurisdiction_percentages.csv"
    )

    # Actor labels by applicability labels.
    actor_applicability = save_crosstab(
        df,
        "responsible_party",
        "applicability",
        output / "phase13_4_responsible_party_by_applicability.csv",
    )

    # Actor labels by governance dimension, if present.
    if "governance_dimension" in df.columns:
        df["governance_dimension"] = clean(df["governance_dimension"])
        save_crosstab(
            df,
            "responsible_party",
            "governance_dimension",
            output / "phase13_4_responsible_party_by_governance_dimension.csv",
        )

    # Actor labels by obligation type, if present.
    if "obligation_type" in df.columns:
        df["obligation_type"] = clean(df["obligation_type"])
        save_crosstab(
            df,
            "responsible_party",
            "obligation_type",
            output / "phase13_4_responsible_party_by_obligation_type.csv",
        )

    # Record-level inventory for traceability.
    inventory_columns = [
        "id", "country", "document", "document_type", "article_or_section",
        "governance_dimension", "obligation_type", "responsible_party",
        "applicability", "enforcement_mechanism", "exact_text",
        "verification_notes",
    ]
    inventory_columns = [c for c in inventory_columns if c in df.columns]
    df[inventory_columns].to_csv(
        output / "phase13_4_responsibility_provision_inventory.csv",
        index=False,
    )

    overall = (
        df["responsible_party"].value_counts()
        .rename_axis("responsible_party")
        .reset_index(name="provision_count")
    )
    overall["sample_share_pct"] = (
        overall["provision_count"] / len(df) * 100
    ).round(1)
    overall.to_csv(
        output / "phase13_4_overall_responsible_party_distribution.csv",
        index=False,
    )

    jurisdiction_count = df["country"].nunique()
    actor_count = df["responsible_party"].nunique()

    lines = [
        "# Phase 13.4 — Institutional and Actor Responsibility Comparison",
        "",
        "## Purpose",
        "",
        "This phase examines how responsibility is assigned in the selected "
        "provisions, using the dataset's `responsible_party` and `applicability` "
        "coding. It identifies patterns in the coded sample for subsequent "
        "legal interpretation.",
        "",
        "## Dataset scope",
        "",
        f"- Provisions analysed: **{len(df)}**",
        f"- Jurisdictions represented: **{jurisdiction_count}**",
        f"- Distinct responsible-party labels: **{actor_count}**",
        "- Source: `data/annotated/governance_dataset.csv`",
        "- Original dataset modified: **No**",
        "",
        "## 1. Overall responsible-party distribution",
        "",
    ]

    for _, row in overall.iterrows():
        lines.append(
            f"- **{row['responsible_party']}**: {int(row['provision_count'])} "
            f"provision(s) ({row['sample_share_pct']:.1f}%)"
        )

    lines.extend([
        "",
        "## 2. Responsibility patterns by jurisdiction",
        "",
        "The accompanying count and percentage matrices show how the recorded "
        "responsible-party labels are distributed within each jurisdiction's "
        "selected sample.",
        "",
    ])

    for jurisdiction in actor_counts.index:
        lines.append(f"### {jurisdiction}")
        total = int(actor_counts.loc[jurisdiction].sum())
        for actor, count in actor_counts.loc[jurisdiction].items():
            if count:
                pct = (count / total * 100) if total else 0
                lines.append(f"- {actor}: {int(count)} provision(s), {pct:.1f}%")
        lines.append("")

    lines.extend([
        "## 3. Responsibility and applicability",
        "",
        "The file `phase13_4_responsible_party_by_applicability.csv` cross-tabulates "
        "the coded actor labels against the recorded applicability categories. "
        "It can help identify whether provisions are directed at providers, "
        "deployers, public authorities, or other categories as represented in "
        "the dataset. The underlying wording must be checked before drawing "
        "legal conclusions.",
        "",
        "## 4. Questions for comparative legal interpretation",
        "",
        "1. Which actors are assigned direct duties by the selected provisions?",
        "2. Are duties allocated to developers/providers, deployers/users, "
        "regulators, public authorities, or multiple actors?",
        "3. Are responsibilities clearly allocated, shared, conditional, or "
        "dependent on implementing measures?",
        "4. Does the instrument distinguish the actor who must comply from the "
        "institution that supervises or enforces compliance?",
        "5. Are there accountability or coordination gaps apparent from the "
        "primary legal texts?",
        "",
        "## 5. Limitations",
        "",
        "- Responsible-party labels reproduce the dataset's coding and may "
        "combine actors with legally distinct roles.",
        "- A coded actor label does not by itself establish the exact scope of "
        "that actor's legal duty.",
        "- The analysis does not infer institutional capacity, independence, "
        "coordination quality, or actual compliance.",
        "- The selected provisions are not a complete inventory of each "
        "jurisdiction's allocation of responsibility.",
        "- Pending Phase 12 corrections have not been automatically applied.",
        "",
        "## 6. Output files",
        "",
        "Detailed tables are saved in `results/phase13/comparative_analysis/` "
        "with the prefix `phase13_4_`.",
        "",
        "## Next phase",
        "",
        "Phase 13.5 will examine implementation evidence and distinguish formal "
        "legal requirements from documented implementation activity and "
        "unresolved evidence gaps.",
        "",
    ])

    report = reports / "Phase13_4_Institutional_Responsibility_Comparison.md"
    report.write_text("\n".join(lines), encoding="utf-8")

    print("\nPHASE 13.4 COMPLETED")
    print(f"Records analysed: {len(df)}")
    print(f"Jurisdictions: {jurisdiction_count}")
    print(f"Responsible-party labels: {actor_count}")
    print(f"Applicability categories: {df['applicability'].nunique()}")
    print(f"Tables saved to: {output}")
    print(f"Report saved to: {report}")
    print("Original annotated dataset was not modified.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\nPHASE 13.4 FAILED: {exc}", file=sys.stderr)
        raise
