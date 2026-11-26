# Data Dictionary

This file describes the coded evidence dataset and the main derived tables.
Category definitions and coding rules are in
[`research/methodology/coding_framework.md`](../research/methodology/coding_framework.md).

## 1. Coded evidence dataset

**File:** `data/annotated/governance_dataset.csv`
**Unit:** one row per selected provision (24 rows: EU 5, India 7, UK 7, OECD benchmark 5; five per framework from each principal instrument, plus four from later instruments)
**Status:** the master dataset. Every analysis script reads it, and none of them write to it.
Corrections go through the Phase 12 review process and are written to
`results/phase12/governance_dataset_phase12_revised.csv`. Coding changes made
directly to the master (recodes, new records) are logged in
`data/annotated/coding_change_log.csv`.

| Column | Meaning | Values used |
|---|---|---|
| `id` | Unique record identifier: framework prefix + number | `EU001`–`EU005`, `IND001`–`IND007`, `UK001`–`UK007`, `OECD001`–`OECD005` |
| `country` | Jurisdiction, or the international benchmark | `EU`, `India`, `UK`, `OECD (international benchmark)` |
| `document` | Full citation of the instrument, including amendments and revisions | Free text |
| `document_type` | Form of the instrument | Free text, e.g. `Legislation`, `Subordinate legislation`, `Government response (policy)`, `International recommendation` |
| `legal_status` | Legal force of the **instrument** (not of the individual provision) | `Binding legislation`, `Non-binding guidance`, `Government policy (non-statutory)`, `International recommendation (non-binding)` |
| `article_or_section` | Precise location of the provision in the instrument | Free text |
| `page_number` | Page reference. Where printed and PDF page numbers differ, both are given; for the EU, consolidated and original OJ pages are given | Free text |
| `governance_dimension` | **Primary** governance dimension: the provision's principal regulatory purpose | `Transparency`, `Accountability`, `Risk Assessment`, `Safety and Testing`, `Enforcement` |
| `secondary_dimension` | Optional additional function supported by the text (blank where none) | The five dimensions above |
| `exact_text` | Verbatim extract from the primary source | Free text |
| `provision_summary` | Researcher's plain-language summary | Free text |
| `obligation_type` | **Force** of the obligation in this provision (coding framework §3) | `Mandatory`, `Recommended`, `Voluntary`, `Not specified` |
| `obligation_nature` | **Nature** of the obligation (coding framework §4); several allowed, separated by ` \| ` | `Institutional`, `Procedural`, `Substantive`, `Reporting`, `Other` |
| `responsible_party` | Actor(s) on whom the responsibility falls, in the source's terminology | Free text |
| `applicability` | Scope: which systems, actors or situations the provision covers | Free text |
| `enforcement_mechanism` | Enforcement route established by, or cross-referenced from, the provision | Free text with article and page references |
| `source_reference` | Official URL(s) and identifiers (ELI, CP number, OECD/LEGAL number) | Free text |
| `verification_notes` | Notes from checking the coding against the primary source | Free text |
| `version_used` | Exact version or edition of the instrument coded | Free text |
| `applicability_status` | Whether the provision currently has legal effect | `In force (from <date>)`, `Legally adopted but not yet applicable`, `Not legally binding (policy or international instrument)` |
| `implementation_status` | Documented implementation evidence | `Implemented`, `Partially implemented`, `Not yet implemented`, `No evidence of implementation found`, `Not assessed` |
| `implementation_notes` | Evidence and reasoning behind `implementation_status` | Free text |

**Coding changes of 26 November 2026** (all logged in `coding_change_log.csv`): the five records previously coded `Institutional` in `obligation_type` were recoded by force (IND004, IND005, UK005 → Recommended; UK003 → Voluntary; OECD005 → Mandatory, an internal OECD instruction that binds no state or AI actor), and *Institutional* moved to the new `obligation_nature` column. EU002's secondary dimension changed from `Data Governance` (not a framework dimension) to `Safety and Testing`, and the string `None` in `secondary_dimension` was replaced by an empty value.

**Reading the status fields.** `Not assessed` means that no assessment was made. It does not mean that implementation failed. `No evidence of implementation found` records the result of a documented search, not proof of non-implementation.

## 2. Derived columns

**File:** `results/tables/normalised_governance_dataset.csv`
(produced by `src/normalise_governance_data.py`)

| Column | Meaning |
|---|---|
| `responsibility_categories` | Standardised actor categories derived from `responsible_party`, separated by ` \| `. Private actors: AI Provider, AI Deployer, Developer, Intermediary, End User, AI Lifecycle Actors, Multiple Stakeholders. Public bodies: Government, Regulator, Institution |
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
| Generated paper | `results/paper/AI_Governance_Atlas_Paper.pdf` (word count in `paper_word_count.txt`) |
| Interactive dashboard | `results/dashboard/index.html` |
| Synthesis worksheet (to be completed by the researcher) | `results/phase14/research_synthesis/phase14_7_research_synthesis_worksheet.csv` |

## 5. Review and reliability files

| File | Contents |
|---|---|
| `research/evidence/phase14_review_record.csv` | Persistent Phase 14 review record, one row per provision: source checks (from the verification audit), drafted legal analysis, comparative argument and synthesis fields. Merged into the Phase 14 worksheets on every run. Set `analysis_status` to `REVIEWED` once you have checked a row |
| `data/reliability/second_coder_ai.csv` | Blind AI-assisted second coding of all provisions |
| `data/reliability/blind_coding_template.csv` | Blank sheet for a human second coder (no primary codes); save the completed file as `second_coder_human.csv` |
| `results/reliability/agreement_summary.csv` | Percentage agreement and Cohen's kappa per variable |
| `results/reliability/disagreements.csv` | Every provision and variable where the coders differ |

## 6. Files that hold human review input

The following files contain decisions entered by hand. The pipeline never regenerates them by default:

- `results/phase12/coding_review_template.csv`: reviewer coding decisions and rationales
- `results/phase12/AI_Governance_Atlas_Phase12_Correction_Register.csv`: `review_decision`, `approved_revised_value`, `reviewer_comments`
