# Changelog

## Unreleased — reproducibility and repository hygiene

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
