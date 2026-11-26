"""Inter-coder agreement between the primary coding and a second coding.

Inputs
    data/annotated/governance_dataset.csv                 primary coding
    results/tables/final_enforcement_provision_audit.csv  primary enforcement linkage
    data/reliability/second_coder_ai.csv                  second coding (blind)

The second coding currently on file was produced by an AI agent working blind:
it saw only each provision's text, location and instrument, plus the coding
framework, and never the primary codes. It is reported as AI-ASSISTED and is
not a substitute for an independent human second coder. To use a human second
coder, give them data/reliability/blind_coding_template.csv and the coding
framework, save their file as data/reliability/second_coder_human.csv, and
re-run: the human coding is then used instead.

Outputs (results/reliability/)
    agreement_summary.csv   per variable: n, % agreement, Cohen's kappa
    disagreements.csv       every provision/variable where the coders differ
    Reliability_Report.md
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATASET = ROOT / "data" / "annotated" / "governance_dataset.csv"
ENFORCEMENT = ROOT / "results" / "tables" / "final_enforcement_provision_audit.csv"
REL_DIR = ROOT / "data" / "reliability"
HUMAN = REL_DIR / "second_coder_human.csv"
AI = REL_DIR / "second_coder_ai.csv"
TEMPLATE = REL_DIR / "blind_coding_template.csv"
OUT = ROOT / "results" / "reliability"

# Dataset legal-status labels -> coding framework section 2 labels
LEGAL_STATUS = {
    "Binding legislation": "Binding",
    "Non-binding guidance": "Non-binding",
    "Government policy (non-statutory)": "Government policy",
    "International recommendation (non-binding)": "International recommendation",
}

SINGLE = [
    ("legal_status", "Legal force of instrument"),
    ("governance_dimension", "Primary governance dimension"),
    ("obligation_force", "Obligation force"),
    ("enforcement_linkage", "Enforcement linkage"),
]


def cohen_kappa(a: list[str], b: list[str]) -> float | None:
    n = len(a)
    if n == 0:
        return None
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    if pe == 1:
        return 1.0 if po == 1 else 0.0
    return (po - pe) / (1 - pe)


def interpret(k: float | None) -> str:
    # Landis and Koch (1977) benchmarks
    if k is None:
        return "n/a"
    if k < 0:
        return "poor"
    for limit, label in [(0.20, "slight"), (0.40, "fair"), (0.60, "moderate"), (0.80, "substantial")]:
        if k <= limit:
            return label
    return "almost perfect"


def as_set(value: str) -> frozenset:
    return frozenset(p.strip() for p in str(value).split("|") if p.strip())


def write_template(primary: pd.DataFrame) -> None:
    """A blank coding sheet a human second coder can fill without seeing the primary codes."""
    REL_DIR.mkdir(parents=True, exist_ok=True)
    cols = ["id", "framework", "instrument", "location", "provision_text",
            "legal_status", "governance_dimension", "obligation_force", "obligation_nature",
            "enforcement_linkage", "confidence", "rationale"]
    t = pd.DataFrame({
        "id": primary["id"], "framework": primary["country"], "instrument": primary["document"],
        "location": primary["article_or_section"], "provision_text": primary["exact_text"],
    })
    for c in cols[5:]:
        t[c] = ""
    t[cols].to_csv(TEMPLATE, index=False)


def main() -> None:
    primary = pd.read_csv(DATASET, dtype=str, keep_default_na=False)
    write_template(primary)

    source, label = (HUMAN, "human") if HUMAN.is_file() else (AI, "AI-assisted") if AI.is_file() else (None, None)
    if source is None:
        print("No second coding found in data/reliability/; skipping reliability analysis.")
        return

    enf = pd.read_csv(ENFORCEMENT, dtype=str, keep_default_na=False).set_index("id")["enforcement_level"]
    p = primary.set_index("id")
    p = pd.DataFrame({
        "legal_status": p["legal_status"].map(LEGAL_STATUS).fillna(p["legal_status"]),
        "governance_dimension": p["governance_dimension"],
        "obligation_force": p["obligation_type"],
        "obligation_nature": p["obligation_nature"],
        "enforcement_linkage": enf.reindex(p.index).fillna(""),
        "country": p["country"],
    })
    s = pd.read_csv(source, dtype=str, keep_default_na=False).set_index("id")
    ids = [i for i in p.index if i in s.index]
    missing = sorted(set(p.index) - set(s.index))

    rows, disagreements = [], []
    for col, name in SINGLE:
        a = [p.at[i, col].strip() for i in ids]
        b = [s.at[i, col].strip() for i in ids]
        k = cohen_kappa(a, b)
        agree = sum(x == y for x, y in zip(a, b))
        rows.append({"variable": name, "field": col, "n": len(ids), "agreements": agree,
                     "percent_agreement": round(100 * agree / len(ids), 1) if ids else None,
                     "cohens_kappa": round(k, 3) if k is not None else None,
                     "interpretation": interpret(k), "measure": "Cohen's kappa"})
        disagreements += [{"id": i, "framework": p.at[i, "country"], "variable": name,
                           "primary": x, "second": y, "second_rationale": s.at[i, "rationale"]}
                          for i, x, y in zip(ids, a, b) if x != y]

    # Obligation nature is multi-label: exact-set agreement and mean Jaccard overlap
    pa = [as_set(p.at[i, "obligation_nature"]) for i in ids]
    sb = [as_set(s.at[i, "obligation_nature"]) for i in ids]
    exact = sum(x == y for x, y in zip(pa, sb))
    jacc = [len(x & y) / len(x | y) if (x | y) else 1.0 for x, y in zip(pa, sb)]
    rows.append({"variable": "Obligation nature (multi-label)", "field": "obligation_nature", "n": len(ids),
                 "agreements": exact, "percent_agreement": round(100 * exact / len(ids), 1) if ids else None,
                 "cohens_kappa": None, "interpretation": f"mean Jaccard overlap {sum(jacc) / len(jacc):.2f}" if jacc else "n/a",
                 "measure": "exact-set agreement; mean Jaccard"})
    disagreements += [{"id": i, "framework": p.at[i, "country"], "variable": "Obligation nature (multi-label)",
                       "primary": " | ".join(sorted(x)), "second": " | ".join(sorted(y)),
                       "second_rationale": s.at[i, "rationale"]}
                      for i, x, y in zip(ids, pa, sb) if x != y]

    OUT.mkdir(parents=True, exist_ok=True)
    summary = pd.DataFrame(rows)
    summary.insert(0, "second_coder", label)
    summary.to_csv(OUT / "agreement_summary.csv", index=False)
    pd.DataFrame(disagreements).to_csv(OUT / "disagreements.csv", index=False)

    table = "\n".join(
        f"| {r['variable']} | {r['n']} | {r['percent_agreement']}% | "
        f"{'' if r['cohens_kappa'] is None else r['cohens_kappa']} | {r['interpretation']} |"
        for r in rows)
    caveat = ("" if label == "human" else
              "\n> **AI-assisted second coding.** The second coder was an AI agent working blind: it saw each "
              "provision's text, location and instrument and the coding framework, never the primary codes. "
              "Agreement with an AI coder is not equivalent to agreement between two trained human coders "
              "and should be reported as AI-assisted.\n")
    (OUT / "Reliability_Report.md").write_text(f"""# Inter-coder reliability

Second coder: **{label}** (`{source.relative_to(ROOT)}`), {len(ids)} provisions compared{f'; missing from second coding: {", ".join(missing)}' if missing else ''}.
{caveat}
| Variable | n | Agreement | Cohen's κ | Interpretation |
|---|---|---|---|---|
{table}

Kappa benchmarks follow Landis and Koch (1977). With small n, kappa is unstable and sensitive to
category prevalence; read it together with percentage agreement and the disagreement list in
`results/reliability/disagreements.csv`.
""", encoding="utf-8")
    print(f"RELIABILITY ({label} second coder, n={len(ids)})")
    print(summary[["variable", "percent_agreement", "cohens_kappa", "interpretation"]].to_string(index=False))


if __name__ == "__main__":
    main()
