# Phase 14.5 — Comparative Legal Argument Matrix

Generated: 2026-11-26 12:09:45

## Purpose

This phase converts the existing provision dataset and Phase 14 source-review
records into a structured matrix for developing a comparative legal argument.
It does not decide which jurisdiction is stronger, more effective, or more
compliant. Those conclusions require source-verified legal analysis and
implementation evidence.

## Files created

1. `results/phase14/comparative_argument/phase14_5_comparative_legal_argument_matrix.csv`
2. `results/phase14/comparative_argument/phase14_5_claim_evidence_register.csv`

## Input availability

- Dataset provisions processed: 24
- Jurisdictions represented in dataset: 4
- Primary governance dimensions represented: 5
- Phase 14.2 source-context rows available: 29
- Phase 14.3 source/version register rows available: 29
- Phase 14.4 legal-analysis worksheet rows available: 24
- Rows with a source status explicitly labelled Verified/Confirmed/Validated: 0

## How to use the argument matrix

For each provision:

1. Confirm the official legal text and the version applicable to the research period.
2. Complete the legal questions using the provision and its surrounding context.
3. Compare only provisions with a genuinely similar regulatory function.
4. Record the argument and cite the supporting provision IDs.
5. Record counter-evidence, limitations, and unresolved interpretive questions.
6. Do not treat a statutory obligation as proof that it has been implemented.
7. Do not treat enforcement powers as proof that enforcement has occurred.

## Important distinction

The `recorded_*` fields are copied from the project's annotated dataset.
The `comparative_question_*` fields are prompts, not answers.
The claim register contains only cautious descriptions of dataset records.
Blank interpretive and outcome fields are intentional.

## Governance dimensions present

- Accountability
- Enforcement
- Risk Assessment
- Safety and Testing
- Transparency

## Limitations

- Missing Phase 14 input files are not treated as evidence that a provision is invalid.
- A candidate PDF page or extracted excerpt is not, by itself, source verification.
- This script does not access the internet or independently check official legislation.
- No legal conclusion or effectiveness ranking is generated.
