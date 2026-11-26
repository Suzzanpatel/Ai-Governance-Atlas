# Phase 14.2 — Provision-Level Source Context and Validation Queue

## Purpose

This phase provides the text surrounding possible source matches and creates
a structured queue for human validation of each provision's primary-source
citation and quotation.

## Results

- Dataset provisions: **24**
- Local PDFs successfully read: **5**
- Provision IDs with at least one located candidate: **20**
- Provision IDs with no located candidate or no dataset excerpt: **4**
- Candidate source rows: **29**
- Automatically verified provisions: **0**
- Original dataset modified: **No**

## Main output

`results/phase14/source_validation/phase14_2_source_context_validation_queue.csv`

Each row includes:
- Dataset provision ID and recorded citation details.
- Candidate local PDF path, SHA-256 hash and PDF metadata title.
- Candidate page number and match type.
- Extracted source excerpt and surrounding page context.
- Explicit human-validation fields, initially left pending or not assessed.

## Validation procedure

For each candidate row, a researcher must compare the extracted passage with
the source PDF itself and verify:
1. The PDF is an official source from the competent issuing institution.
2. The instrument title, version, amendments and relevant date are correct.
3. The article, paragraph and page reference are accurate.
4. The quotation is verbatim and its surrounding context is not misleading.
5. Definitions, exceptions, qualifications and cross-references are considered.
6. The provision's legal status and commencement are confirmed from authoritative
   sources.

## Status meanings

- `LOCATED_REQUIRES_HUMAN_VALIDATION`: a possible text location was found.
- `NO_LOCAL_TEXT_MATCH`: no matching text was found in the local PDF corpus.
- `NO_EXACT_TEXT_TO_LOCATE`: the dataset row has no exact-text excerpt.
- `PENDING`: no human validation has yet been recorded.
- `NOT_ASSESSED`: the script has not determined whether the source is official
  or current.

No candidate match is labelled verified by this script.

## Limitations

The script searches extracted text from PDFs under `data/raw/`. It does not
perform OCR, authenticate source websites, retrieve newer versions, or provide
legal interpretation. Text matching may miss OCR differences, formatting
changes, amendments, or excerpts split across pages.

## Next step

Phase 14.3 should add official-source metadata and version checks, then support
a documented validation decision for each provision. Unresolved items should
remain explicitly unresolved until primary evidence is obtained.
