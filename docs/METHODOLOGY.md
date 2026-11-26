# Methodology overview

The full methodological record is in [`research/methodology/`](../research/methodology/). This page summarises it and shows where each part is documented.

| Document | Covers |
|---|---|
| [Research questions](../research/methodology/research_questions.md) | Central question, RQ1–RQ5, objectives and scope |
| [Research methodology](../research/methodology/research_methodology.md) | Design, sources, provision selection, processing, coding, implementation evidence, comparison, reliability |
| [Case selection criteria](../research/methodology/case_selection_criteria.md) | Why the EU, India and the UK, and why the OECD is a benchmark rather than a fourth case |
| [Coding framework](../research/methodology/coding_framework.md) | Definitions and decision rules for every coded category |
| [Limitations](../research/methodology/limitations.md) | Sample, comparability, extraction, NLP, coding subjectivity and implementation evidence |

## Central research question

> To what extent do India, the European Union and the United Kingdom translate AI governance principles into specific, measurable and enforceable regulatory obligations?

## The translation chain

Each provision is coded on five separate links. Strength at one link is never taken as evidence of strength at another.

1. **Legal force** of the instrument: binding legislation, government policy, non-binding guidance or international recommendation
2. **Obligation force** of the provision: mandatory, recommended, voluntary or not specified (with **obligation nature** coded separately: institutional, procedural, substantive, reporting, other)
3. **Duty-holder**: the actor who must act (provider, deployer, developer, regulator, government, institution…)
4. **Enforcement linkage**: direct, cross-referenced, system-level only, none identified, or not applicable
5. **Implementation evidence**: implemented, partially implemented, not yet implemented, no evidence found, or not assessed

## Evidence base

- **24 provisions**: 5 from each framework's principal instrument, selected purposively across five governance dimensions (transparency, accountability, risk assessment, safety and testing, enforcement), plus 4 from later instruments: India's 2026 IT Rules amendments (IND006–IND007) and the UK's 2024 government response (UK006–UK007).
- Each record carries the verbatim text, article or section, PDF and printed page numbers, source URL and version.
- **Verification:** 180 field-level checks against the primary sources. The 37 corrections that resulted were made in the dataset and approved in the Phase 12 correction register.
- **Phase 14 review:** source checks for all 24 records and drafted legal analysis are kept in `research/evidence/phase14_review_record.csv` and merged into the Phase 14 worksheets. Drafted analysis stays marked as a draft until the researcher reviews it.
- **Reliability:** a blind second coding by an AI agent (which saw only the provision text and the coding framework) is compared with the primary coding in `results/reliability/`. Agreement: κ = 1.00 legal force, 0.84 dimension, 0.93 obligation force, 0.63 enforcement linkage. This is reported as AI-assisted and is not a substitute for a human second coder; a blank template for one is in `data/reliability/`.

## Interpretive safeguards

- "Not assessed" is never read as non-implementation, and "no evidence found" is never read as proof of absence.
- Keyword frequencies are descriptive indicators of drafting emphasis, not evidence of legal obligation.
- Equal record counts do not imply that the frameworks are equivalent, and the sample does not rank them.
