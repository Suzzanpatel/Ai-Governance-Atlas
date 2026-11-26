# Changelog

## v0.2.0 — 2026-11-26 — research completion

### Added
- **Four new coded provisions** from later instruments: India's IT (Intermediary Guidelines and Digital Media Ethics Code) Amendment Rules, 2026 (IND006: due diligence on synthetically generated information; IND007: loss of section 79 safe harbour under rule 7) and the UK's February 2024 government response, CP 1019 (UK006: regulators' strategic approaches; UK007: anticipated targeted mandatory interventions). The dataset now has 24 records.
- **`obligation_nature`** column (coding framework §4) for every record.
- **Phase 14 review record** (`research/evidence/phase14_review_record.csv`), merged into the Phase 14 worksheets on every run. It records the completed source verification and drafted legal analysis, comparative argument and synthesis fields, marked for researcher review.
- **Inter-coder reliability** (`src/analysis/reliability.py`): blind, AI-assisted second coding of all 24 provisions, with Cohen's kappa per variable, a disagreement list and a template for a human second coder.
- `data/annotated/coding_change_log.csv` logging every coding change.

### Changed
- `obligation_type` now records **force** only. Five records previously coded `Institutional` were recoded (IND004, IND005, UK005 → Recommended; UK003 → Voluntary; OECD005 → Mandatory as an internal OECD instruction).
- EU002 secondary dimension `Data Governance` → `Safety and Testing`; the string `None` in `secondary_dimension` → empty.
- **Paper** regenerated: India's binding rules and the UK response are now covered; the findings on addressees, enforcement and implementation speed are revised accordingly; a reliability paragraph has been added; Tables 1 and 2 show every instrument and the new force categories. The main text is 4,383 words.
- **Dashboard**: 24 provisions, obligation nature in the explorer, an updated translation-profile table, and "Intermediary" as a private actor.
- Phase 14.7 reads the corrected 14.6 audit, and the 14.6 audit reports completion statuses. Fixed a whitespace regex in `phase14_6_corrected_audit.py`.

### Removed
- The empty `LICENSE` file. The project is published without a licence (all rights reserved).

## v0.1.1 — 2026-11-26

### Fixed
- **Paper wording on source-verification corrections.** v0.1.0 said that the 37 corrections "awaited a decision" and that the findings used the values *before* correction. In fact all 37 corrections are already in the dataset, so the findings use the corrected values. Only formal sign-off is outstanding. The paper now checks each register value against the dataset and reports that, together with the number signed off.
- The dashboard footer, README, paper guide, methodology overview and contributing guide are updated to match.

### Reviewed
- **All 37 source-verification corrections approved** in the Phase 12 correction register (`review_decision = Approve`, with the approved value and a reviewer note). The Phase 12 change log records all 37. The paper now reports that all corrections are signed off.

## v0.1.0 — 2026-11-26 — working paper and dashboard

### Added
- **Academic paper generator** (`src/publish/generate_paper.py`): a 4,000-word manuscript (±10%, enforced) typeset as PDF, with an editable Markdown copy, four figures, three tables and a provision appendix. All counts, patterns and figures are computed from the coded dataset. It runs offline and is deterministic.
- **Interactive dashboard** (`src/publish/build_dashboard.py`): a single self-contained HTML file with an overview, a provision explorer and text indicators; shared filters; a table view for every chart; and light and dark themes with color-vision-checked palettes.
- Shared data layer (`src/publish/atlas_data.py`) so the paper and dashboard always agree.
- `publish` stage in `run_pipeline.py`; `reportlab` dependency.
- Documentation hub in `docs/` (getting started, pipeline, paper, dashboard, methodology), `CONTRIBUTING.md` and `CITATION.cff`; README reorganised as a landing page.

## Reproducibility and repository hygiene (merged before v0.1.0)

### Fixed
- **Text extraction skipped India on Linux and Windows CI.** `extract_text.py` looked for `data/raw/india`, but the folder is `data/raw/India`, which only matches on macOS's case-insensitive file system. The India PDF's file name also contains non-breaking spaces. Folder and file names are now matched ignoring case and whitespace variants.
- **EU AI Act counted twice.** With both the 2024 Official Journal PDF and the 2026 consolidated PDF in `data/raw/eu/`, a fresh run extracted both. Each framework is now read from exactly one PDF, listed in `SOURCES` in `extract_text.py`.
- **Enforcement categories split into single words.** `normalise_governance_data.py` called `.str.split(" | ")` without `regex=False`, so pandas read the separator as a regular expression and split on spaces. As a result, `normalised_enforcement_matrix.csv` and `enforcement_categories_long.csv` held fragments such as `Financial`, `Penalties`, `|` and `and`. They now hold the intended categories (`Financial Penalties`, `Market Surveillance`, …).
- **Crash with pandas 3.** `explode()` left duplicate index labels, which `pd.crosstab` rejects in pandas 3. Fixed with `ignore_index=True`.
- **Report generator paths.** `report_generator.py` looked for the evidence pack in `research/` and wrote to `research/`; it now uses `research/evidence/` and `research/reports/`.
- **Absolute local paths in outputs.** `phase13_6_phase_output_check.csv` recorded a path on the author's computer; it now records project-relative paths.

### Changed
- **EU text corpus now uses the consolidated text of 27 July 2026**, the version cited in the coded dataset. The consolidated text has no recitals, so the EU corpus is about 63k words instead of about 94k. Most EU keyword frequencies move only slightly; Transparency falls from 0.605 to 0.347 per 1,000 words. India, UK and OECD figures are unchanged. To reproduce the earlier figures, set the EU entry in `SOURCES` to `EU_AI_Act_Official_Journal_2024.pdf`.
- Regenerated derived tables that were out of date with `data/annotated/governance_dataset.csv`: the enforcement text in the dataset had been revised after they were produced.
- `extract_text.py` uses `import pymupdf` (the `fitz` name is deprecated), with a fallback for older PyMuPDF.

### Added
- `run_pipeline.py`: runs all 30 analysis scripts in dependency order, by stage, and stops at the first error.
- Overwrite protection on `create_coding_review.py` and `generate_phase12_review.py`, which produce files holding human review decisions.
- `requirements.txt` (tested ranges) and `requirements-lock.txt` (exact versions behind the committed outputs).
- `docs/DATA_DICTIONARY.md`.
- README sections on system requirements, quick start, pipeline, structure and roadmap. The dimension list now matches the methodology and the dataset.
