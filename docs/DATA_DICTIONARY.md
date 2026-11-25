# Data Dictionary

This file describes the coded evidence dataset and the main derived tables.
Category definitions and coding rules are in
[`research/methodology/coding_framework.md`](../research/methodology/coding_framework.md).

## 1. Coded evidence dataset

**File:** `data/annotated/governance_dataset.csv`
**Unit:** one row per selected provision (20 rows: 5 each for EU, India, UK and the OECD benchmark)
**Status:** the master dataset. Every analysis script reads it, and none of them write to it.
Corrections go through the Phase 12 review process and are written to
`results/phase12/governance_dataset_phase12_revised.csv`.

| Column | Meaning | Values used |
|---|---|---|
| `id` | Unique record identifier: framework prefix + number | `EU001`–`EU005`, `IND001`–`IND005`, `UK001`–`UK005`, `OECD001`–`OECD005` |
| `country` | Jurisdiction, or the international benchmark | `EU`, `India`, `UK`, `OECD (international benchmark)` |
| `document` | Full citation of the instrument, including amendments and revisions | Free text |
| `document_type` | Form of the instrument | `Legislation`, `Government guidelines`, `White paper`, `International recommendation` |
| `legal_status` | Legal force of the **instrument** (not of the individual provision) | `Binding legislation`, `Non-binding guidance`, `Government policy (non-statutory)`, `International recommendation (non-binding)` |
| `article_or_section` | Precise location of the provision in the instrument | Free text |
| `page_number` | Page reference. Where printed and PDF page numbers differ, both are given; for the EU, consolidated and original OJ pages are given | Free text |
| `governance_dimension` | **Primary** governance dimension: the provision's principal regulatory purpose | `Transparency`, `Accountability`, `Risk Assessment`, `Safety and Testing`, `Enforcement` |
| `secondary_dimension` | Optional additional function supported by the text (blank in 3 rows) | The five dimensions above, plus `Data Governance`* |
| `exact_text` | Verbatim extract from the primary source | Free text |
| `provision_summary` | Researcher's plain-language summary | Free text |
| `obligation_type` | Force of the obligation in this provision | `Mandatory`, `Recommended`, `Institutional`* |
| `responsible_party` | Actor(s) on whom the responsibility falls, in the source's terminology | Free text |
| `applicability` | Scope: which systems, actors or situations the provision covers | Free text |
| `enforcement_mechanism` | Enforcement route established by, or cross-referenced from, the provision | Free text with article and page references |
| `source_reference` | Official URL(s) and identifiers (ELI, CP number, OECD/LEGAL number) | Free text |
| `verification_notes` | Notes from checking the coding against the primary source | Free text |
| `version_used` | Exact version or edition of the instrument coded | Free text |
| `applicability_status` | Whether the provision currently has legal effect | `Legally adopted but not yet applicable`, `Not legally binding (policy or international instrument)` |
| `implementation_status` | Documented implementation evidence | `Implemented`, `Partially implemented`, `Not yet implemented`, `No evidence of implementation found`, `Not assessed` |
| `implementation_notes` | Evidence and reasoning behind `implementation_status` | Free text |

\* **Known inconsistencies with the coding framework.** These are recorded here and the data is left unchanged.
- `obligation_type` uses `Institutional` for 5 records. The coding framework treats *Institutional* as an **obligation nature** (§4), not an **obligation force** (§3: Mandatory / Recommended / Voluntary / Not specified). Consider splitting this column into `obligation_force` and `obligation_nature`.
- `secondary_dimension` uses `Data Governance` (EU002), which is not one of the five framework dimensions.

**Reading the status fields.** `Not assessed` means that no assessment was made. It does not mean that implementation failed. `No evidence of implementation found` records the result of a documented search, not proof of non-implementation.

## 2. Derived columns

**File:** `results/tables/normalised_governance_dataset.csv`
(produced by `src/normalise_governance_data.py`)

| Column | Meaning |
|---|---|
| `responsibility_categories` | Standardised actor categories derived from `responsible_party`, separated by ` \| ` |
| `enforcement_categories` | Standardised mechanism categories derived from `enforcement_mechanism`, separated by ` \| ` |

A provision can belong to several categories, so in the `*_long.csv` and
`*_matrix.csv` tables built from these columns, totals can exceed the number of provisions.

## 3. Text corpus

| File | Produced by | Contents |
|---|---|---|
| `data/processed/extracted_documents.csv` | `src/extract_text.py` | `country`, `document`, `page`, `text`: one row per PDF page, from one source PDF per framework |
| `data/processed/cleaned_documents.csv` | `src/preprocess.py` | As above, plus `cleaned_text` (lower-cased, punctuation and stopwords removed; legal modals such as *must*, *shall* and *may* kept) |
| `results/tables/keyword_counts_by_document.csv` | `src/keyword_analysis.py` | Keyword hits per dimension per document, with `total_words` and `frequency_per_1000_words` |
| `results/tables/keyword_summary_by_country.csv` | `src/keyword_analysis.py` | The same, aggregated by framework |

The source PDF for each framework is set in `SOURCES` in `src/extract_text.py`.
The EU corpus uses the **consolidated text of 27 July 2026**. That is the
version cited in the coded dataset, and it contains the operative articles and
annexes **without recitals**, so its word count is lower than the 2024
Official Journal edition. Keyword frequencies are descriptive indicators only;
see `research/methodology/limitations.md` §7.

## 4. Where to find the main results

| Question | File |
|---|---|
| Records by framework × dimension | `results/phase13/comparative_analysis/jurisdiction_by_governance_dimension_counts.csv` |
| Legal status and obligation force | `results/phase13/comparative_analysis/phase13_3_*` |
| Responsible actors | `results/phase13/comparative_analysis/phase13_4_*` |
| Implementation evidence | `results/phase13/comparative_analysis/phase13_5_*` |
| Enforcement mechanisms (final coding) | `results/tables/final_enforcement_matrix.csv`, `results/tables/final_enforcement_mechanisms.csv` |
| Source and version validation | `results/phase14/source_validation/phase14_3_official_source_version_validation_register.csv` |
| Synthesis worksheet (to be completed by the researcher) | `results/phase14/research_synthesis/phase14_7_research_synthesis_worksheet.csv` |

## 5. Files that hold human review input

The following files contain decisions entered by hand. The pipeline never regenerates them by default:

- `results/phase12/coding_review_template.csv`: reviewer coding decisions and rationales
- `results/phase12/AI_Governance_Atlas_Phase12_Correction_Register.csv`: `review_decision`, `approved_revised_value`, `reviewer_comments`
