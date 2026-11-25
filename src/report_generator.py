#!/usr/bin/env python3
"""
AI Governance Atlas — deterministic academic report generator.

This program does NOT call ChatGPT, an LLM, or any paid API.
It converts the project's coded evidence-pack JSON into a structured
academic-style Markdown report using transparent Python rules and templates.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = PROJECT_ROOT / "research" / "evidence" / "stage_9_evidence_pack.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "research" / "reports" / "AI_Governance_Atlas_Report.md"

GROUP_ORDER = [
    "EU",
    "India",
    "UK",
    "OECD (international benchmark)",
]

GROUP_NAMES = {
    "EU": "European Union",
    "India": "India",
    "UK": "United Kingdom",
    "OECD (international benchmark)": "OECD international benchmark",
}

DIMENSIONS = [
    "Transparency",
    "Accountability",
    "Risk Assessment",
    "Safety and Testing",
    "Enforcement",
]


def clean(value: Any, fallback: str = "Not specified") -> str:
    if value is None:
        return fallback
    text = re.sub(r"\s+", " ", str(value)).strip()
    return text if text else fallback


def md_cell(value: Any) -> str:
    return clean(value).replace("|", r"\|").replace("\n", " ")


def join_phrases(items: list[str]) -> str:
    """Join labels as a phrase without adding sentence-ending punctuation."""
    cleaned = []
    for item in items:
        value = clean(item)
        value = value.rstrip(" .;,:!?\t")
        if value and value != "Not specified":
            cleaned.append(value)
    if not cleaned:
        return "the evidence pack does not specify this point"
    if len(cleaned) == 1:
        return cleaned[0]
    if len(cleaned) == 2:
        return f"{cleaned[0]} and {cleaned[1]}"
    return ", ".join(cleaned[:-1]) + f", and {cleaned[-1]}"


def sentence_join(items: list[str]) -> str:
    """Join items into a complete sentence with exactly one final full stop."""
    return join_phrases(items).rstrip(" .;,:!?\t") + "."


def count_by(records: list[dict], field: str) -> Counter:
    return Counter(clean(r.get(field)) for r in records)


def table(headers: list[str], rows: list[list[Any]]) -> str:
    out = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        out.append("| " + " | ".join(md_cell(x) for x in row) + " |")
    return "\n".join(out)


def describe_obligation(records: list[dict]) -> str:
    counts = count_by(records, "obligation_type")
    total = len(records)
    labels = {
        "Mandatory": "mandatory obligations",
        "Recommended": "recommendations",
        "Institutional": "institutional provisions",
    }
    present = [(labels[k], counts[k]) for k in labels if counts.get(k)]
    if not present:
        return "No obligation-type classifications are recorded."
    if len(present) == 1:
        label, number = present[0]
        if number == total:
            return f"All {total} selected provisions are classified as {label}."
        return f"{number} of the {total} selected provisions are classified as {label}."
    details = [f"{number} as {label}" for label, number in present]
    return "The coding classifies " + join_phrases(details) + "."


def implementation_paragraph(records: list[dict]) -> str:
    counts = count_by(records, "implementation_status")
    if not counts:
        return "The evidence pack contains no implementation classifications for this group."
    labels = [
        ("Implemented", "implemented"),
        ("Partially implemented", "partially implemented"),
        ("Not yet implemented", "not yet implemented"),
        ("No evidence of implementation found", "recorded as having no evidence of implementation found"),
        ("Not assessed", "not assessed"),
    ]
    sentences = []
    for key, phrase in labels:
        if counts.get(key):
            n = counts[key]
            noun = "provision" if n == 1 else "provisions"
            sentences.append(f"{n} {noun} {phrase}")
    return (
        "Within this selected sample, implementation is recorded as follows: "
        + "; ".join(sentences)
        + ". These are provision-level research classifications, not a comprehensive "
          "measure of implementation across the jurisdiction."
    )


def enforcement_paragraph(group: str, records: list[dict]) -> str:
    """Describe only enforcement mechanisms affirmatively recorded for this group.

    This deliberately avoids keyword-only classification: words such as 'penalties'
    can appear in negative statements (for example, 'without the threat of penalties').
    """
    ids = {clean(r.get("id")) for r in records}
    texts = {clean(r.get("id")): clean(r.get("enforcement_mechanism"), "") for r in records}

    if group == "EU":
        provider_fines = any(
            re.search(r"fines? of up to|administrative fine|breach finable|subject to fines", t, re.I)
            for t in texts.values()
        )
        deployer_fines = any(
            re.search(r"deployer.{0,100}(?:finable|fine)|(?:finable|fine).{0,100}deployer", t, re.I)
            for t in texts.values()
        )
        parts = []
        if provider_fines:
            parts.append("cross-referenced administrative fines for provider non-compliance")
        if deployer_fines:
            parts.append("a deployer fine reference in the human-oversight record")
        if parts:
            return (
                "The selected EU provisions connect substantive Chapter III duties to "
                + join_phrases(parts)
                + ". The dataset also records conformity assessment and market-surveillance "
                  "arrangements as part of the wider statutory architecture. These are "
                  "cross-referenced mechanisms, not separate penalties created by each article."
            )
        return "The evidence pack does not identify a positive statutory penalty reference in these selected EU records."

    if group == "India":
        parts = []
        if "IND001" in ids:
            parts.append(
                "a transparency-reporting recommendation (IND001), which does not itself "
                "specify an enforcement mechanism; the wider Guidelines separately describe "
                "soft-accountability practices such as public and peer scrutiny"
            )
        if "IND005" in ids:
            parts.append("the use of existing sectoral regulators’ statutory powers, without new AI-specific sanctions (IND005)")
        if parts:
            return (
                "The selected Indian provisions indicate " + join_phrases(parts) +
                ". The other sampled recommendations either identify no specific enforcement "
                "mechanism or concern framework-building and institutional functions rather "
                "than an enforceable compliance duty."
            )
        return "The selected Indian provisions do not identify a specific enforcement mechanism."

    if group == "UK":
        return (
            "The selected UK provisions rely on existing regulators’ powers and processes; "
            "the White Paper does not create new AI-specific sanctions. The anticipated "
            "statutory ‘have due regard’ duty is recorded as a possible future measure, "
            "not an enacted duty. The central risk-assessment function is an internal "
            "government arrangement rather than a compliance sanction."
        )

    if group == "OECD (international benchmark)":
        return (
            "The selected OECD provisions rely on monitoring, periodic reporting and peer "
            "exchange. The Recommendation does not create legal sanctions or a coercive "
            "enforcement mechanism; these monitoring arrangements should not be described "
            "as statutory enforcement."
        )

    return (
        "The evidence pack records provision-level enforcement descriptions, but this "
        "group has no dedicated summary rule. Consult the individual provision records "
        "and distinguish direct, cross-referenced and system-level mechanisms."
    )


def dimension_profile(records: list[dict]) -> str:
    counts = count_by(records, "governance_dimension")
    present = [f"{d} ({counts[d]})" for d in DIMENSIONS if counts[d]]
    return (
        "The selected provisions cover "
        + join_phrases(present)
        + ". The distribution reflects the purposive sample and should not be read as "
          "a measure of the overall importance of each dimension in the framework."
    )


def provision_review(records: list[dict]) -> str:
    chunks = []
    for r in records:
        pid = clean(r.get("id"))
        heading = clean(r.get("article_or_section"))
        summary = clean(r.get("provision_summary"))
        dimension = clean(r.get("governance_dimension"))
        actor = clean(r.get("responsible_party"))
        status = clean(r.get("legal_status"))
        applicability = clean(r.get("applicability_status"))
        implementation = clean(r.get("implementation_status"))
        chunks.append(
            f"##### {pid}: {heading}\n\n"
            f"This provision is coded under **{dimension}** and is classified as "
            f"**{status.lower()}**. {summary} The recorded responsible party is "
            f"{actor}. Its applicability is coded as **{applicability}**, while "
            f"implementation is recorded as **{implementation}**.\n\n"
            f"**Enforcement recorded in the dataset:** "
            f"{clean(r.get('enforcement_mechanism'))} "
            f"**Source reference:** {clean(r.get('source_reference'))}"
        )
    return "\n\n".join(chunks)


def group_analysis(group: str, records: list[dict]) -> str:
    name = GROUP_NAMES.get(group, group)
    legal = count_by(records, "legal_status")
    legal_summary = sentence_join(
        [f"{n} of the {len(records)} selected provisions are classified as {status.lower()}"
         for status, n in legal.items()]
    )
    obligation_summary = describe_obligation(records)
    return (
        f"### {name}\n\n"
        f"The evidence pack contains **{len(records)} selected provisions** for {name}. "
        f"{legal_summary} {obligation_summary} "
        f"These classifications describe the selected records rather than the entire "
        f"legal or policy framework.\n\n"
        f"{dimension_profile(records)}\n\n"
        f"{implementation_paragraph(records)}\n\n"
        f"{enforcement_paragraph(group, records)}\n\n"
        f"#### Provision-level review\n\n"
        f"{provision_review(records)}"
    )



TABLE_SUMMARIES = {
    "EU001": "Requires providers to maintain a continuous risk-management process for high-risk AI systems.",
    "EU002": "Sets data-quality and governance requirements for datasets used to train, validate and test high-risk systems.",
    "EU003": "Requires providers to give deployers clear information and instructions for high-risk AI systems.",
    "EU004": "Requires high-risk AI systems to enable effective human oversight by providers and deployers.",
    "EU005": "Requires high-risk AI systems to meet accuracy, robustness and cybersecurity requirements.",
    "IND001": "Recommends transparency reports addressing harms to individuals and society in the Indian context.",
    "IND002": "Recommends graded responsibility across developers, deployers and end-users under existing law.",
    "IND003": "Recommends an India-specific risk-classification framework reflecting local context and evidence of harm.",
    "IND004": "Assigns the proposed AI Safety Institute testing, evaluation, standards-development and advisory functions.",
    "IND005": "Places AI-related enforcement with existing sectoral regulators acting under their own laws.",
    "UK001": "Promotes risk-proportionate transparency and explainability through existing regulators.",
    "UK002": "Calls for lifecycle-wide organisational governance, oversight and clear accountability.",
    "UK003": "Assigns central government a cross-sectoral risk register and horizon-scanning function.",
    "UK004": "Promotes lifecycle safety, security and robustness, with regulator-led testing or due diligence where appropriate.",
    "UK005": "Relies on existing regulators’ statutory powers; a possible future due-regard duty remains unenacted.",
    "OECD001": "Recommends meaningful transparency and disclosure that helps people understand and challenge AI outputs.",
    "OECD002": "Recommends accountability and traceability of data, processes and decisions across the AI lifecycle.",
    "OECD003": "Recommends ongoing lifecycle risk management and cooperation among AI actors and stakeholders.",
    "OECD004": "Recommends lifecycle robustness, security and safety, including override, repair and safe decommissioning.",
    "OECD005": "Provides for committee reporting and peer exchange to monitor implementation; it creates no sanctions.",
}


def compact_summary(record: dict) -> str:
    """Return a concise, manually reviewed summary for comparison tables.

    The complete source-derived provision summary remains in the jurisdictional review.
    """
    pid = clean(record.get("id"), "")
    return TABLE_SUMMARIES.get(
        pid,
        "See the full provision-level review for the recorded summary."
    )


def dimension_interpretation(dimension: str) -> str:
    """Carefully scoped comparative reading of the 20 coded pilot records."""
    interpretations = {
        "Transparency": (
            "In this sample, the EU provision is framed as a provider duty to supply "
            "information and instructions that enable deployers to use high-risk systems "
            "appropriately. India's selected guidance instead recommends transparency "
            "reports, with confidential regulator disclosure where publication would expose "
            "sensitive or proprietary material. The UK record links proportionate "
            "transparency and explainability to regulator implementation, while the OECD "
            "principle emphasises meaningful disclosure to affected people, including "
            "information that may help them challenge an output. The contrast is therefore "
            "not simply whether transparency is recognised, but who receives information, "
            "for what purpose, and whether the selected text frames disclosure as a binding "
            "provider duty or a recommendation/principle."
        ),
        "Accountability": (
            "The selected EU record focuses on human oversight, including provider design "
            "and deployer implementation responsibilities. India's recommendation proposes "
            "graded liability across developers, deployers and end-users, but the sampled "
            "text is guidance rather than an enacted AI-specific allocation of liability. "
            "The UK record calls for organisational governance and clear accountability "
            "across the AI lifecycle while expressly not changing legal liability at this "
            "stage. The OECD record emphasises accountability and traceability across the "
            "AI lifecycle. These approaches address related concerns but differ in their "
            "legal status and in whether they specify operational oversight, recommend "
            "future allocation, or articulate a general lifecycle principle."
        ),
        "Risk Assessment": (
            "The EU sample contains two records: a continuous provider risk-management "
            "process and data-governance requirements addressing representativeness, bias "
            "and data gaps. India's selected provision recommends an India-specific risk "
            "classification framework informed by local context and evidence of harm. The "
            "UK record assigns central government a cross-sectoral function to maintain a "
            "risk register, monitor emerging risks and identify gaps between regulators. "
            "The OECD record recommends systematic, ongoing risk management across the AI "
            "lifecycle. The sample thus captures different institutional locations for "
            "risk work: provider-level duties, proposed national framework-building, "
            "central-government coordination and lifecycle-wide international guidance."
        ),
        "Safety and Testing": (
            "The EU record imposes provider-facing requirements concerning accuracy, "
            "robustness and cybersecurity. India's selected provision assigns the AI Safety "
            "Institute testing, evaluation, standards-development and advisory functions, "
            "without recording coercive testing or sanction powers. The UK principle "
            "addresses safety, security and robustness and contemplates regulator-led "
            "testing or due diligence where appropriate. The OECD principle describes "
            "lifecycle robustness and safety, including the ability to override, repair or "
            "safely decommission systems. The distinction in this sample is between a "
            "binding technical duty, an institution-building and advisory model, a "
            "regulator-mediated principles approach, and a non-binding international "
            "lifecycle standard."
        ),
        "Enforcement": (
            "No EU provision in this pilot sample is assigned Enforcement as its primary "
            "dimension. However, the enforcement descriptions attached to the selected EU "
            "substantive provisions cross-reference statutory fine provisions and wider "
            "conformity-assessment and market-surveillance arrangements. India's selected "
            "enforcement record points to existing sectoral regulators acting under their "
            "own laws, rather than new AI-specific sanctions. The UK record likewise relies "
            "on existing regulators' statutory powers and describes a possible future "
            "‘have due regard’ duty on regulators as not yet enacted. The OECD record "
            "provides for periodic reporting and peer exchange, not legal sanctions. These "
            "are materially different mechanisms and should not be grouped together as "
            "equivalent forms of enforcement."
        ),
    }
    return interpretations.get(
        dimension,
        "The selected records should be interpreted in light of their source text and coding notes."
    )


def dimension_comparison(groups: dict[str, list[dict]]) -> str:
    """Compare the selected records dimension by dimension without inferring absence."""
    sections = []
    for dimension in DIMENSIONS:
        rows = []
        present_groups = []
        for group in GROUP_ORDER:
            group_records = [
                r for r in groups.get(group, [])
                if clean(r.get("governance_dimension")) == dimension
            ]
            label = GROUP_NAMES.get(group, group)
            if not group_records:
                rows.append([
                    label,
                    "No provision selected under this primary dimension",
                    "Not applicable to this sample row",
                    "No primary-dimension record in this pilot sample",
                ])
                continue

            present_groups.append(label)
            record_descriptions = []
            for record in group_records:
                pid = clean(record.get("id"))
                status = clean(record.get("legal_status"))
                actor = clean(record.get("responsible_party"))
                summary = compact_summary(record)
                record_descriptions.append(
                    f"**{pid}** ({status}): {summary} "
                    f"Responsible party recorded: {actor}."
                )
            rows.append([
                label,
                "; ".join(record_descriptions),
                "; ".join(sorted({clean(r.get("obligation_type")) for r in group_records})),
                "; ".join(sorted({clean(r.get("responsible_party")) for r in group_records})),
            ])

        if not present_groups:
            continue

        sections.append(
            f"### {dimension}\n\n"
            f"The table compares the provisions coded primarily under **{dimension}**. "
            "The table uses concise summaries for readability; full provision descriptions appear in the jurisdictional review above. "
            "An unselected dimension in this pilot sample is not proof that the framework lacks that type of rule.\n\n"
            + table(
                ["Group", "Selected provision and recorded approach", "Obligation coding", "Responsible party coding"],
                rows,
            )
            + "\n\n**Comparative interpretation.** "
            + dimension_interpretation(dimension)
        )


    return "\n\n".join(sections)


def comparative_findings(groups: dict[str, list[dict]]) -> str:
    all_records = [r for group in GROUP_ORDER for r in groups.get(group, [])]
    legal_counts = count_by(all_records, "legal_status")
    dimension_rows = []
    for group in GROUP_ORDER:
        recs = groups.get(group, [])
        counts = count_by(recs, "governance_dimension")
        dimension_rows.append([GROUP_NAMES.get(group, group)] + [counts.get(d, 0) for d in DIMENSIONS])

    legal_rows = [[k, v] for k, v in legal_counts.items()]
    return (
        "### 5.1 Legal form and normative force\n\n"
        "The selected records contain different forms of normative authority. "
        "The EU records are classified as binding legislation, whereas the Indian "
        "records are non-binding guidance, the UK records are non-statutory government "
        "policy, and the OECD records are an international recommendation. This "
        "distinction is fundamental: a shared governance principle does not necessarily "
        "create an equivalent legal duty across the four groups.\n\n"
        + table(["Legal-status classification", "Selected provisions"], legal_rows)
        + "\n\n### 5.2 Distribution across governance dimensions\n\n"
        "The following table counts the primary dimension assigned to each selected "
        "provision. It does not count secondary overlaps. A zero means that no provision "
        "in this pilot sample was assigned that primary dimension; it does not mean the "
        "framework contains no relevant rules on the subject.\n\n"
        + table(["Group"] + DIMENSIONS, dimension_rows)
        + "\n\n### 5.3 Dimension-by-dimension comparison\n\n"
        "The following comparison examines the substantive content of the selected "
        "records within each governance dimension. It reports the primary-dimension "
        "coding and retains the responsible-party and obligation labels used in the dataset.\n\n"
        + dimension_comparison(groups)
        + "\n\n### 5.4 From legal duties to institutional arrangements\\n\\nThe selected records represent three analytically distinct forms of governance. The EU sample contains binding provider-facing requirements and a related deployer role for human oversight. The India and UK samples primarily describe recommendations, policy principles and institutional arrangements operating through government bodies or existing sectoral regulators; these should not be presented as newly enacted AI-specific duties or sanctions. The OECD sample expresses non-binding expectations supported by reporting and peer exchange rather than coercive enforcement. These distinctions describe the selected records only and do not establish comparative regulatory effectiveness.\\n\\nThe obligation label 'Institutional' identifies an institutional function in this dataset, rather than a level of legal force equivalent to 'Mandatory' or 'Recommended'.\\n\\n### 5.5 Responsibility and enforcement\n\n"
        "The dataset indicates different approaches to allocating responsibility. "
        "The EU records generally identify providers, with a related deployer role "
        "for human oversight. The Indian records place emphasis on government, "
        "institutions, developers, deployers and existing sectoral regulators. "
        "The UK records rely on regulators and AI lifecycle actors within a "
        "principles-based model. The OECD principles address AI actors and adherent "
        "governments. These categories can overlap and should not be treated as "
        "mutually exclusive counts.\n\n"
        "Enforcement must be assessed separately from the existence of a governance "
        "principle. A statutory fine, an existing regulator's power, voluntary "
        "transparency reporting, peer scrutiny and international monitoring perform "
        "different functions. In particular, OECD monitoring and reporting do not "
        "constitute legal sanctions, and references to existing sectoral powers in "
        "India or the UK should not be described as new AI-specific enforcement powers."
    )


def sources_section(records: list[dict]) -> str:
    seen = set()
    lines = []
    for r in records:
        doc = clean(r.get("document"))
        ref = clean(r.get("source_reference"))
        key = (doc, ref)
        if key in seen:
            continue
        seen.add(key)
        lines.append(f"- **{doc}.** {ref}")
    return "\n".join(lines)


def build_report(data: dict) -> str:
    provisions = data.get("provisions", [])
    scope = data.get("research_scope", {})
    if not provisions:
        raise ValueError("The evidence pack contains no provisions.")

    groups: dict[str, list[dict]] = defaultdict(list)
    for record in provisions:
        groups[clean(record.get("country"))].append(record)

    for group in GROUP_ORDER:
        groups[group].sort(key=lambda r: clean(r.get("id")))

    n = len(provisions)
    jurisdiction_labels = [
        "the United Kingdom" if clean(item) == "United Kingdom" else clean(item)
        for item in scope.get("jurisdictions", [])
    ]
    jurisdiction_text = join_phrases(jurisdiction_labels)
    dimension_text = join_phrases(scope.get("governance_dimensions", DIMENSIONS))
    sample_design = clean(scope.get("sample_design"), "Purposive manually coded sample")

    executive = (
        f"This report examines **{n} manually coded provisions** in the AI Governance "
        f"Atlas project. The comparison covers {jurisdiction_text}, with the OECD "
        f"treated separately as an international benchmark. It examines the dimensions "
        f"of {dimension_text}. "
        "The pilot evidence indicates that the selected frameworks differ not only "
        "in the principles they recognise, but also in the legal force of those "
        "principles, the actors assigned responsibility, the institutional arrangements "
        "supporting implementation and the mechanisms available to secure compliance. "
        "The sample is exploratory and does not establish the effectiveness of any "
        "entire legal system."
    )

    method = (
        f"The dataset uses a **{sample_design.lower()}**. Each record contains a "
        "provision identifier, source instrument, legal status, primary governance "
        "dimension, provision summary, obligation type, responsible party, applicability "
        "status, implementation status and enforcement description. The analysis is "
        "qualitative and descriptive. Counts are used to summarise the selected sample, "
        "not to make statistical claims about the full universe of AI regulation.\n\n"
        "Four distinctions guide interpretation. Legal status is not the same as "
        "applicability; applicability is not the same as implementation; implementation "
        "is not the same as enforcement; and institutional monitoring is not necessarily "
        "a sanction. Where the dataset records 'not assessed', this is not interpreted "
        "as non-implementation. Similarly, 'no evidence of implementation found' is "
        "not treated as proof that implementation has not occurred. Primary governance "
        "dimensions are counted once per record, while secondary overlaps are retained "
        "as qualitative notes. Responsibility categories may overlap."
    )

    group_sections = []
    for group in GROUP_ORDER:
        if groups.get(group):
            group_sections.append(group_analysis(group, groups[group]))

    report = f"""# AI Governance Atlas
## Comparative Report: From Governance Principles to Institutional and Enforceable Obligations

**Generated by:** Python rule-based report generator  
**Generation date:** {date.today().isoformat()}  
**Evidence records analysed:** {n}

---

## Executive summary

{executive}

## 1. Introduction

Artificial intelligence governance increasingly depends on more than the articulation of high-level principles. Transparency, accountability, risk assessment and safety become operational only when frameworks clarify who is responsible, what conduct is expected, which institutions oversee implementation and what consequences may follow from non-compliance.

This report compares selected provisions from the European Union, India and the United Kingdom, while using the OECD Recommendation on Artificial Intelligence as an international benchmark. Its central analytical concern is the translation of governance principles into legal obligations, institutional responsibilities and enforcement arrangements.

## 2. Research scope and methodology

{method}

## 3. Analytical dimensions

The project uses five primary dimensions:

{chr(10).join(f"- **{d}:** " + {
    "Transparency": "information provision, disclosure and explainability.",
    "Accountability": "responsibility allocation, oversight and traceability.",
    "Risk Assessment": "risk identification, classification, evaluation and mitigation.",
    "Safety and Testing": "robustness, security, testing and lifecycle reliability.",
    "Enforcement": "compliance mechanisms, regulatory powers and sanctions."
}[d] for d in DIMENSIONS)}

## 4. Jurisdictional and international analysis

{chr(10).join(group_sections)}

## 5. Comparative analysis

{comparative_findings(groups)}

## 6. Limitations

The findings are limited by the purposive pilot sample and the number of provisions selected from each instrument. Five records per group cannot represent the full content or operation of any framework. The distribution of records across governance dimensions is also uneven and reflects the researcher's selection and coding decisions.

Implementation classifications depend on the evidence recorded in the dataset and should be revisited as official materials become available. The report does not independently verify every legal interpretation, amendment, application date or enforcement cross-reference. Those matters require checking against the original legal instruments and official institutional sources before academic submission.

The coding process is manual. Some provisions connect to more than one governance dimension or involve multiple actors. The report preserves the primary dimension for counting purposes and discusses overlaps in the source notes. The resulting counts should not be interpreted as mutually exclusive measures of responsibility or regulatory strength.

## 7. Conclusion

The selected provisions demonstrate that common AI governance principles can be translated into substantially different regulatory arrangements. The EU sample is characterised by binding legislation and role-specific duties. The Indian sample relies more heavily on non-binding guidance, institutional development and existing sectoral regulation. The UK sample uses a principles-based approach implemented through existing regulators. The OECD provides an international normative benchmark supported by monitoring and reporting, but not legal sanctions.

The comparison suggests that the practical significance of a governance principle depends on its normative force, the clarity of the responsible actor, institutional capacity and the availability of mechanisms to secure compliance. A larger sample, systematic source verification and longitudinal implementation evidence would be needed to move from this pilot mapping exercise to a stronger assessment of regulatory performance.

## 8. Sources represented in the evidence pack

{sources_section(provisions)}

---

*Automated report note: This document was assembled by deterministic Python rules from the project's evidence-pack JSON. No ChatGPT model, external generative-AI service or paid API was used to write or rewrite the report. The wording is template-based and data-driven; legal conclusions remain dependent on the quality and verification of the source dataset.*
"""
    return report


def main() -> None:
    input_path = DEFAULT_INPUT
    output_path = DEFAULT_OUTPUT

    if not input_path.exists():
        raise FileNotFoundError(
            f"Evidence pack not found: {input_path}\n"
            "Place stage_9_evidence_pack.json in research/evidence/."
        )

    with input_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    report = build_report(data)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")

    print("\nREPORT GENERATED SUCCESSFULLY")
    print(f"Input:  {input_path}")
    print(f"Output: {output_path}")
    print(f"Provisions analysed: {len(data.get('provisions', []))}")
    print("\nNo API key, internet connection, ChatGPT call or paid credits were used.")


if __name__ == "__main__":
    main()
