# Phase 14.4 — Provision-Level Legal Analysis Worksheet

## Purpose

This phase creates one structured legal-analysis worksheet row for each
provision in `data/annotated/governance_dataset.csv`. It carries forward the
dataset's existing coding and any available local source-locator information,
while leaving legal analysis fields blank for evidence-led research.

## Main output

`results/phase14/legal_analysis/phase14_4_provision_level_legal_analysis_worksheet.csv`

Each row corresponds to one unique provision ID. Existing dataset values are
labelled `as_coded` to distinguish them from the researcher's legal conclusions.

## Recommended analysis sequence

1. **Identify the legal issue.** State the narrow legal question raised by
   the provision.
2. **Establish the legal basis.** Cite the official instrument and relevant
   interpretive method; distinguish text, context, purpose and authoritative
   interpretation.
3. **Separate instrument-level and provision-level effect.** Do not assume
   that every provision in a binding instrument creates an independently
   enforceable duty.
4. **Analyse operative language.** Identify mandatory, conditional,
   discretionary, permissive or recommendatory wording.
5. **Define scope.** Identify addressees, regulated activities, thresholds,
   territorial reach and material scope.
6. **Check qualifications.** Record exceptions, definitions, derogations,
   transitional rules and cross-references.
7. **Analyse institutional roles.** Distinguish the regulated actor from
   supervisory, notifying, coordinating and enforcement authorities.
8. **Trace enforcement.** Identify the legal basis for supervision, remedies,
   sanctions, procedural routes and any cross-instrument dependencies.
9. **Consider counterarguments.** Record ambiguities, competing readings and
   unresolved issues.
10. **State a proportionate provisional conclusion.** Tie it to the cited
    source evidence and disclose uncertainty.

## Important distinctions

- Legal status of an instrument is not identical to the legal effect of each
  provision within it.
- A duty-holder is not necessarily the supervisory or enforcement authority.
- A sanction elsewhere in an instrument should not be attributed to a specific
  duty without checking the legal cross-reference and scope.
- Policy commitments, voluntary standards and recommendations should not be
  described as statutory obligations unless the legal source supports that.
- The existence of a legal duty does not establish implementation or compliance.

## Evidence standard

For each material legal proposition, record an authoritative source reference
and a pinpoint citation (article, paragraph, page or section). Where possible,
retain the exact operative wording and relevant surrounding context. Distinguish
primary legal text from official guidance, explanatory material and academic
commentary.

## Status discipline

All rows begin as `NOT_YET_REVIEWED`. Do not mark a row complete merely because
a PDF text match exists or because the dataset already contains a summary.
The Phase 14.3 source-validation register is a separate source-authentication
workflow.

## Limitations

This script prepares a worksheet; it does not perform legal interpretation,
retrieve current law, authenticate documents, or complete the blank analysis
fields. It does not modify the original dataset, PDFs, or previous phase files.
