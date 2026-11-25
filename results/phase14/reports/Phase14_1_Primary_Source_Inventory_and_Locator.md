# Phase 14.1 — Primary Source Inventory and Provision Locator

## Purpose

This phase inventories local PDF sources and attempts to locate the dataset's
recorded exact-text excerpts within those PDFs. It creates a traceable starting
point for primary-source validation.

## Scope

- Dataset provisions: **20**
- Local PDF files found under `data/raw/`: **5**
- PDFs successfully read: **5**
- Provision IDs with at least one text locator match: **20**
- Provision IDs with no local text match: **0**
- Original annotated dataset modified: **No**
- Source PDFs modified: **No**

## Outputs

- `phase14_1_local_pdf_source_inventory.csv`: file paths, file sizes, SHA-256
  hashes, PDF metadata, page counts and extraction status.
- `phase14_1_provision_source_locator_results.csv`: possible page locations
  for each dataset excerpt.
- `phase14_1_provision_locator_summary.csv`: provision-level summary.

## How to interpret locator results

- `normalised_exact_text_match` means the recorded excerpt was found after
  normalising whitespace, case and selected hyphen characters.
- `leading_excerpt_match` means only the first part of a long excerpt was found.
- `LOCATOR_MATCH_REQUIRES_HUMAN_CHECK` is a page-location lead, not a verified
  quotation or legal conclusion.
- `NO_LOCAL_TEXT_MATCH` means no matching text was found in the PDFs scanned.
  The source may be absent, scanned as an image, OCR-incompatible, differently
  worded, or stored outside `data/raw/`.
- A PDF's metadata title is not authoritative proof of its legal status,
  version, commencement, or currency.

## Required human/source validation

For every proposed source match, compare the dataset excerpt against the actual
PDF page and check:
1. The instrument's official title and issuing institution.
2. Version, amendment and consolidation date.
3. Article, section, paragraph and page.
4. Whether the excerpt is verbatim and complete enough for its stated use.
5. Whether surrounding text, exceptions, definitions or cross-references
   change the meaning.
6. Whether the provision was in force at the relevant date.

## Limitations

This script only scans local text-based PDF content. It does not perform OCR,
web retrieval, source authentication, legal interpretation, or independent
verification. A match does not prove that the PDF is an official or current
version. A non-match does not prove that the citation is wrong.

## Next step

Phase 14.2 should validate the located passages against official source
versions, capture surrounding context, and create a provision-by-provision
validation record with explicit verified, discrepancy, and unresolved states.
