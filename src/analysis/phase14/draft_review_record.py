"""Draft the persistent Phase 14 review record from completed project evidence.

ONE-OFF DRAFTING SCRIPT: not part of the pipeline. It creates
research/evidence/phase14_review_record.csv, which the Phase 14 scripts then
merge into their worksheets (see review_record.py). It refuses to overwrite an
existing record, because the record is where the researcher's own review lives.

What it draws on
- Source checks for EU001-OECD005 come from the 180-check source verification
  audit (research/evidence/verification_audit.csv, 2026-11-25), whose 37
  corrections were approved on 2026-11-26.
- Source checks for records added later (IND006, IND007, UK006, UK007) record
  the checks made when those records were coded, with their caveats.
- Legal-analysis, argument and synthesis fields are DRAFTED from the coded
  dataset. They are marked DRAFT_FROM_CODED_DATA so that Phase 14.6 reports
  them as awaiting researcher review, not as completed legal analysis.

Usage:
    python src/analysis/phase14/draft_review_record.py          # create the record
    python src/analysis/phase14/draft_review_record.py --force  # overwrite it
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
DATASET = ROOT / "data" / "annotated" / "governance_dataset.csv"
AUDIT = ROOT / "research" / "evidence" / "verification_audit.csv"
ENFORCEMENT = ROOT / "results" / "tables" / "final_enforcement_provision_audit.csv"
OUT = ROOT / "research" / "evidence" / "phase14_review_record.csv"

REVIEW_DATE = "2026-11-26"
AUDIT_REVIEWER = "Source verification audit 2026-11-25; corrections approved by Suzzan Patel 2026-11-26"
NEW_RECORD_REVIEWER = "Coded and source-checked 2026-11-26 with AI assistance (Claude); requires researcher confirmation"
DRAFT_STATUS = "DRAFT_FROM_CODED_DATA_AWAITING_RESEARCHER_REVIEW"

NAME = {"EU": "the EU", "India": "India", "UK": "the UK", "OECD (international benchmark)": "the OECD benchmark"}

# Source-check outcome for records added after the verification audit
NEW_RECORD_CHECKS = {
    "IND006": dict(
        official_publisher_identified="CONFIRMED: Ministry of Electronics and Information Technology (MeitY), Government of India",
        official_source_url_confirmed="CONFIRMED: consolidated Rules and FAQs on meity.gov.in",
        instrument_title_confirmed="CONFIRMED",
        version_or_consolidation_date_confirmed="CONFIRMED_WITH_CAVEAT: consolidated text 'updated as on 10.02.2026'; a Second Amendment Rules 2026 text (April 2026) had no G.S.R. number or date and is not treated as in force",
        amendments_checked="CONFIRMED_WITH_CAVEAT: G.S.R. 120(E) of 10.02.2026 and corrigenda of 26.02.2026 identified; Second Amendment status unconfirmed",
        commencement_and_in_force_status_checked="CONFIRMED: in force from 20 February 2026",
        article_paragraph_and_page_confirmed="CONFIRMED_WITH_CAVEAT: rule-level pinpoint confirmed; PDF page not yet checked against a downloaded copy",
        quotation_verbatim_and_context_checked="CONFIRMED_WITH_CAVEAT: operative words checked against the official text read online; to be re-checked against a downloaded PDF",
        definitions_exceptions_cross_references_checked="CONFIRMED: rule 2(1)(wa) definition of SGI; rule 4(1A); rule 7",
        overall_validation_decision="VERIFIED_WITH_CAVEATS",
    ),
    "IND007": dict(
        official_publisher_identified="CONFIRMED: MeitY, Government of India",
        official_source_url_confirmed="CONFIRMED: consolidated Rules on meity.gov.in",
        instrument_title_confirmed="CONFIRMED",
        version_or_consolidation_date_confirmed="CONFIRMED_WITH_CAVEAT: consolidated text 'updated as on 10.02.2026'",
        amendments_checked="CONFIRMED_WITH_CAVEAT: rule 7 unchanged by G.S.R. 120(E); Second Amendment status unconfirmed",
        commencement_and_in_force_status_checked="CONFIRMED: IT Rules 2021 in force; SGI duties from 20 February 2026",
        article_paragraph_and_page_confirmed="CONFIRMED_WITH_CAVEAT: rule-level pinpoint; PDF page not yet checked",
        quotation_verbatim_and_context_checked="CONFIRMED_WITH_CAVEAT: operative clause checked against the official text read online",
        definitions_exceptions_cross_references_checked="CONFIRMED: section 79(1) IT Act, 2000",
        overall_validation_decision="VERIFIED_WITH_CAVEATS",
    ),
    "UK006": dict(
        official_publisher_identified="CONFIRMED: Department for Science, Innovation and Technology (DSIT)",
        official_source_url_confirmed="CONFIRMED: assets.publishing.service.gov.uk and gov.uk",
        instrument_title_confirmed="CONFIRMED: CP 1019",
        version_or_consolidation_date_confirmed="CONFIRMED: February 2024 (amended web-ready PDF)",
        amendments_checked="NOT_APPLICABLE: policy document, not amended",
        commencement_and_in_force_status_checked="NOT_APPLICABLE: non-statutory policy",
        article_paragraph_and_page_confirmed="CONFIRMED_WITH_CAVEAT: paragraph 15, printed p. 14; PDF page not yet checked",
        quotation_verbatim_and_context_checked="CONFIRMED_WITH_CAVEAT: excerpts checked against the official text read online",
        definitions_exceptions_cross_references_checked="CONFIRMED: regulators listed in footnote 28; outcome published 1 May 2024",
        overall_validation_decision="VERIFIED_WITH_CAVEATS",
    ),
    "UK007": dict(
        official_publisher_identified="CONFIRMED: DSIT",
        official_source_url_confirmed="CONFIRMED: assets.publishing.service.gov.uk and gov.uk",
        instrument_title_confirmed="CONFIRMED: CP 1019",
        version_or_consolidation_date_confirmed="CONFIRMED: February 2024 (amended web-ready PDF)",
        amendments_checked="NOT_APPLICABLE: policy document, not amended",
        commencement_and_in_force_status_checked="NOT_APPLICABLE: non-statutory policy",
        article_paragraph_and_page_confirmed="CONFIRMED_WITH_CAVEAT: paragraph 72, printed p. 31; PDF page not yet checked",
        quotation_verbatim_and_context_checked="CONFIRMED_WITH_CAVEAT: excerpt checked against the official text read online",
        definitions_exceptions_cross_references_checked="CONFIRMED: read with paragraph 60",
        overall_validation_decision="VERIFIED_WITH_CAVEATS",
    ),
}


def audit_checks(rid: str, audit: dict, row: dict) -> dict:
    """Map the verification-audit verdicts for one record onto the Phase 14.3 fields."""
    v = audit.get(rid, {})

    def verdict(column, label):
        outcome = v.get(column)
        if outcome == "Verified":
            return f"CONFIRMED: {label} verified against the primary source"
        if outcome == "Corrected":
            return f"CONFIRMED: {label} corrected against the primary source (correction approved 2026-11-26)"
        if outcome == "Verified with caveat":
            return f"CONFIRMED_WITH_CAVEAT: {label} verified with a caveat (see verification_audit.csv)"
        return f"NOT_ASSESSED: {label} not covered by the verification audit"

    binding = row["legal_status"].startswith("Binding")
    return dict(
        official_publisher_identified=verdict("source_reference", "issuing body and official source"),
        official_source_url_confirmed=verdict("source_reference", "official URL"),
        instrument_title_confirmed=verdict("legal_status", "instrument and its legal status"),
        version_or_consolidation_date_confirmed=f"CONFIRMED_WITH_CAVEAT: version recorded as '{row['version_used'][:120]}'; version was not a separate audit field",
        amendments_checked=("CONFIRMED: amendment by Regulation (EU) 2026/1744 identified and the consolidated text of 27 July 2026 used"
                            if row["country"] == "EU" else
                            "CONFIRMED: 2023 and 2024 revisions identified and the May 2024 text used"
                            if row["country"].startswith("OECD") else
                            "CONFIRMED_WITH_CAVEAT: instrument not amended; later instruments (UK CP 1019; India IT Rules 2026) are coded as separate records"),
        commencement_and_in_force_status_checked=(f"CONFIRMED: {row['applicability_status']}" if binding else
                                                  "NOT_APPLICABLE: non-binding instrument"),
        article_paragraph_and_page_confirmed=verdict("article_or_section", "article/section and page reference"),
        quotation_verbatim_and_context_checked=verdict("exact_text", "verbatim quotation"),
        definitions_exceptions_cross_references_checked=verdict("enforcement_mechanism", "enforcement cross-references"),
        overall_validation_decision="VERIFIED_WITH_CAVEATS" if "Verified with caveat" in v.values() else "VERIFIED",
    )


def main() -> None:
    if OUT.exists() and "--force" not in sys.argv:
        raise SystemExit(f"Refusing to overwrite {OUT.relative_to(ROOT)}: it may contain researcher edits. Use --force.")

    df = pd.read_csv(DATASET, dtype=str, keep_default_na=False)
    enf = pd.read_csv(ENFORCEMENT, dtype=str, keep_default_na=False).set_index("id")
    audit_df = pd.read_csv(AUDIT, dtype=str, keep_default_na=False)
    audit = defaultdict(dict)
    for _, a in audit_df.iterrows():
        audit[a["id"]][a["column"]] = a["verdict"]

    by_dim = defaultdict(list)
    for _, r in df.iterrows():
        by_dim[r["governance_dimension"]].append(r["id"])

    rows = []
    for _, r in df.iterrows():
        rid = r["id"]
        e = enf.loc[rid] if rid in enf.index else {}
        level = e.get("enforcement_level", "") if len(e) else ""
        character = e.get("mechanism_character", "") if len(e) else ""
        if rid in audit:
            checks, reviewer, basis = audit_checks(rid, audit, r), AUDIT_REVIEWER, "research/evidence/verification_audit.csv"
        else:
            checks, reviewer, basis = NEW_RECORD_CHECKS[rid], NEW_RECORD_REVIEWER, "verification_notes and source_reference in governance_dataset.csv"

        name = NAME[r["country"]]
        force = r["obligation_type"].lower()
        peers = [x for x in by_dim[r["governance_dimension"]] if x != rid]
        citation = f"{r['document']}, {r['article_or_section']} ({r['page_number']})"
        conclusion = (f"In {name}, this {r['governance_dimension'].lower()} provision is {force} "
                      f"({r['obligation_nature'].lower()}) within an instrument coded as {r['legal_status'].lower()}; "
                      f"its enforcement linkage is {level.lower() or 'not coded'}"
                      f"{f' ({character.lower()})' if character else ''}, and implementation is coded as "
                      f"{r['implementation_status'].lower()}.")

        rows.append({
            "id": rid,
            **checks,
            "reviewer_name_or_initials": reviewer,
            "review_date": REVIEW_DATE,
            "reviewer_evidence_reference": basis,
            "reviewer_notes": "Source checks recorded from completed verification; legal-analysis fields are drafts from the coded dataset.",
            # Phase 14.4 legal analysis (drafted from coded data)
            "legal_question_or_issue": f"How far does {r['article_or_section']} translate the {r['governance_dimension'].lower()} principle into an enforceable obligation?",
            "instrument_level_legal_force": r["legal_status"],
            "provision_level_legal_effect": f"{r['obligation_type']} ({r['obligation_nature']})",
            "mandatory_or_discretionary_language": f"Coded {force}; see exact_text and verification_notes for the operative wording.",
            "scope_and_addressees": r["applicability"],
            "commencement_and_temporal_application": r["applicability_status"],
            "responsible_actor_analysis": r["responsible_party"],
            "enforcement_route_and_remedies": r["enforcement_mechanism"],
            "researcher_legal_analysis": r["provision_summary"],
            "provisional_conclusion": conclusion,
            "primary_source_evidence_reference": citation,
            "analysis_status": DRAFT_STATUS,
            # Phase 14.5 comparative argument (drafted)
            "proposed_argument": conclusion,
            "supporting_evidence_ids": " | ".join(peers),
            "counter_evidence_or_limitation": ("Purposive sample; the provision does not represent the whole framework. "
                                               + (r["implementation_notes"][:300] if r["implementation_notes"] else "")),
            "researcher_legal_assessment": "Draft generated from coded data; awaiting researcher assessment.",
            "confidence": "MEDIUM (draft)",
            "human_review_status": DRAFT_STATUS,
            # Phase 14.7 synthesis (drafted)
            "research_synthesis_claim": conclusion,
            "supporting_provision_ids": " | ".join(peers),
            "official_source_citation": citation,
            "implementation_or_outcome_evidence": f"{r['implementation_status']}: {r['implementation_notes']}",
            "counterargument_or_limitation": "Single-provision evidence from a purposive sample; effectiveness is outside the study's scope.",
            "researcher_conclusion": "DRAFT: to be confirmed or revised by the researcher.",
            "reviewer_status": DRAFT_STATUS,
        })

    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"Wrote {OUT.relative_to(ROOT)} ({len(rows)} provisions)")


if __name__ == "__main__":
    main()
