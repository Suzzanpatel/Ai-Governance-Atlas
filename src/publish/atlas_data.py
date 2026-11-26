"""Shared data layer for the paper and dashboard generators.

Both publication outputs read the coded evidence and the analysis tables
through this module, so the paper and the dashboard always report the same
figures. Nothing here writes files.

Inputs (all produced or maintained elsewhere in the pipeline):
    data/annotated/governance_dataset.csv                  coded provisions (master)
    results/tables/normalised_governance_dataset.csv       responsibility/enforcement categories
    results/tables/final_enforcement_provision_audit.csv   enforcement linkage per provision
    results/tables/system_level_enforcement_architecture.csv
    results/tables/keyword_summary_by_country.csv          computational indicators
"""

from __future__ import annotations

from collections import Counter, OrderedDict
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

DATASET = ROOT / "data" / "annotated" / "governance_dataset.csv"
NORMALISED = ROOT / "results" / "tables" / "normalised_governance_dataset.csv"
ENFORCEMENT_AUDIT = ROOT / "results" / "tables" / "final_enforcement_provision_audit.csv"
ARCHITECTURE = ROOT / "results" / "tables" / "system_level_enforcement_architecture.csv"
KEYWORDS = ROOT / "results" / "tables" / "keyword_summary_by_country.csv"
VERIFICATION_AUDIT = ROOT / "research" / "evidence" / "verification_audit.csv"
CORRECTION_REGISTER = ROOT / "results" / "phase12" / "AI_Governance_Atlas_Phase12_Correction_Register.csv"
RELIABILITY = ROOT / "results" / "reliability" / "agreement_summary.csv"

# Framework order used everywhere (tables, charts, prose). The OECD is the
# international benchmark and is always listed last.
FRAMEWORKS = ["EU", "India", "UK", "OECD (international benchmark)"]
SHORT = {
    "EU": "EU",
    "India": "India",
    "UK": "UK",
    "OECD (international benchmark)": "OECD",
}
KEYWORD_LABEL = {"eu": "EU", "india": "India", "uk": "UK", "oecd": "OECD (international benchmark)"}

DIMENSIONS = ["Transparency", "Accountability", "Risk Assessment", "Safety and Testing", "Enforcement"]

# Enforcement linkage: how a provision connects to an enforcement route.
ENFORCEMENT_LEVELS = [
    "Cross-referenced",
    "System-level only",
    "Direct",
    "None identified",
    "Not applicable",
]
ENFORCEMENT_LEVEL_DESC = {
    "Cross-referenced": "duty linked by cross-reference to statutory sanctions elsewhere in the instrument",
    "System-level only": "no provision-specific route; relies on the general powers of existing regulators or bodies",
    "Direct": "the provision itself names a compliance or accountability mechanism",
    "None identified": "no enforcement or compliance route identified",
    "Not applicable": "framework-building or institutional function rather than a compliance duty",
}

IMPLEMENTATION_LEVELS = [
    "Implemented",
    "Partially implemented",
    "Not yet implemented",
    "No evidence of implementation found",
    "Not assessed",
]

OBLIGATION_TYPES = ["Mandatory", "Recommended", "Voluntary", "Not specified"]


@dataclass
class Atlas:
    records: list[dict]
    keywords: pd.DataFrame
    architecture: dict[str, dict]
    sources: "OrderedDict[str, dict]"
    meta: dict = field(default_factory=dict)

    # ---- helpers -------------------------------------------------------
    def by_framework(self, framework: str) -> list[dict]:
        return [r for r in self.records if r["country"] == framework]

    def count(self, column: str, framework: str | None = None) -> Counter:
        rows = self.by_framework(framework) if framework else self.records
        return Counter(r[column] for r in rows)

    def crosstab(self, column: str, levels: list[str]) -> "OrderedDict[str, OrderedDict[str, int]]":
        out = OrderedDict()
        for fw in FRAMEWORKS:
            c = self.count(column, fw)
            out[fw] = OrderedDict((lvl, c.get(lvl, 0)) for lvl in levels)
        return out

    def multi_crosstab(self, column: str) -> tuple[list[str], "OrderedDict[str, Counter]"]:
        """Crosstab for ' | '-separated multi-category columns."""
        out = OrderedDict((fw, Counter()) for fw in FRAMEWORKS)
        for r in self.records:
            for cat in r[column]:
                out[r["country"]][cat] += 1
        cats = sorted({c for counter in out.values() for c in counter})
        return cats, out

    @property
    def n(self) -> int:
        return len(self.records)


def _split(value: str) -> list[str]:
    value = (value or "").strip()
    if not value or value.lower() == "none":
        return []
    return [part.strip() for part in value.split(" | ") if part.strip()]


def _require(path: Path) -> Path:
    if not path.is_file():
        raise FileNotFoundError(
            f"Required input not found: {path.relative_to(ROOT)}\n"
            "Run the earlier pipeline stages first: python run_pipeline.py --stage text --stage coding"
        )
    return path


def load() -> Atlas:
    df = pd.read_csv(_require(DATASET), dtype=str).fillna("")
    norm = pd.read_csv(_require(NORMALISED), dtype=str).fillna("")
    enf = pd.read_csv(_require(ENFORCEMENT_AUDIT), dtype=str).fillna("")
    arch = pd.read_csv(_require(ARCHITECTURE), dtype=str).fillna("")
    kw = pd.read_csv(_require(KEYWORDS))

    unknown = set(df["country"]) - set(FRAMEWORKS)
    if unknown:
        raise ValueError(f"Unexpected framework labels in dataset: {sorted(unknown)}")

    norm_idx = norm.set_index("id")
    enf_idx = enf.set_index("id")

    records = []
    for _, row in df.iterrows():
        rec = row.to_dict()
        rid = rec["id"]
        n = norm_idx.loc[rid] if rid in norm_idx.index else None
        e = enf_idx.loc[rid] if rid in enf_idx.index else None
        rec["framework_short"] = SHORT[rec["country"]]
        rec["responsibility_categories"] = _split(n["responsibility_categories"]) if n is not None else []
        rec["enforcement_categories"] = _split(n["enforcement_categories"]) if n is not None else []
        rec["enforcement_level"] = (e["enforcement_level"] if e is not None else "") or "None identified"
        rec["enforcement_mechanisms"] = _split(e["enforcement_mechanisms"]) if e is not None else []
        rec["mechanism_character"] = e["mechanism_character"] if e is not None else ""
        if rec["enforcement_level"] not in ENFORCEMENT_LEVELS:
            raise ValueError(f"{rid}: unexpected enforcement level '{rec['enforcement_level']}'")
        records.append(rec)

    order = {fw: i for i, fw in enumerate(FRAMEWORKS)}
    records.sort(key=lambda r: (order[r["country"]], r["id"]))

    kw = kw.copy()
    kw["framework"] = kw["country"].map(KEYWORD_LABEL)

    architecture = {row["country"]: row.to_dict() for _, row in arch.iterrows()}

    # One entry per instrument (a framework can have several), in framework order.
    # The first instrument of each framework is its principal instrument.
    sources: "OrderedDict[str, dict]" = OrderedDict()
    for fw in FRAMEWORKS:
        for i, doc in enumerate(dict.fromkeys(df.loc[df["country"] == fw, "document"])):
            first = df[(df["country"] == fw) & (df["document"] == doc)].iloc[0]
            sources[doc] = {
            "framework": fw,
            "principal": i == 0,
            "n_provisions": int(((df["country"] == fw) & (df["document"] == doc)).sum()),
            "document": first["document"],
            "document_type": first["document_type"],
            "legal_status": first["legal_status"],
            "version_used": first["version_used"],
            "source_reference": first["source_reference"],
            "applicability_status": first["applicability_status"],
            }

    # Quality-assurance summary (optional inputs: reported only if present)
    meta = {"audit_checks": 0, "audit_verdicts": {}, "corrections": 0, "corrections_decided": 0, "audit_fields": 0,
            "corrections_in_dataset": 0, "corrections_by_field": {}}
    if VERIFICATION_AUDIT.is_file():
        audit = pd.read_csv(VERIFICATION_AUDIT, dtype=str).fillna("")
        meta["audit_checks"] = len(audit)
        meta["audit_verdicts"] = audit["verdict"].value_counts().to_dict()
        meta["audit_fields"] = audit["column"].nunique()
    if CORRECTION_REGISTER.is_file():
        reg = pd.read_csv(CORRECTION_REGISTER, dtype=str).fillna("")
        meta["corrections"] = len(reg)
        # "Needs evidence" keeps a correction open; only Approve/Reject close it
        meta["corrections_decided"] = int(reg["review_decision"].str.strip().isin(["Approve", "Reject"]).sum())
        meta["corrections_by_field"] = reg["field_to_review"].value_counts().to_dict()
        # The register records each field's value after the audit correction.
        # Count how many of those values are still in the dataset. A value that a
        # later, logged coding change extended (e.g. a note appended to
        # verification_notes) still counts, because the corrected text is kept.
        current = df.set_index("id")
        norm = lambda v: " ".join(str(v).split())  # noqa: E731
        meta["corrections_in_dataset"] = int(sum(
            row["id"] in current.index and row["field_to_review"] in current.columns
            and norm(current.at[row["id"], row["field_to_review"]]).startswith(norm(row["original_value"]))
            for _, row in reg.iterrows()))

    if RELIABILITY.is_file():
        rel = pd.read_csv(RELIABILITY, dtype=str, keep_default_na=False)
        meta["reliability"] = rel.to_dict("records")

    principal = {fw: next((d for d, s in sources.items() if s["framework"] == fw and s["principal"]), "")
                 for fw in FRAMEWORKS}
    for rec in records:
        rec["principal_instrument"] = rec["document"] == principal[rec["country"]]

    return Atlas(records=records, keywords=kw, architecture=architecture, sources=sources, meta=meta)
