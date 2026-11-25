# Contributing

This guide covers the most common changes: adding a provision, correcting a coded value, and adding a source document.

## Adding a provision

1. Add a row to `data/annotated/governance_dataset.csv` with every column filled in, following the [data dictionary](docs/DATA_DICTIONARY.md) and the [coding framework](research/methodology/coding_framework.md).
   - Use the next free ID for the framework (`EU006`, `IND006`, …).
   - Copy `exact_text` verbatim from the official source and give both PDF and printed page numbers.
   - Record the exact version used in `version_used`.
2. Add the provision's enforcement coding to `src/recode_enforcement.py` and `src/finalise_enforcement_analysis.py`, which map each ID to its enforcement linkage.
3. Run `python run_pipeline.py`. `validate_dataset.py` will flag structural problems, and the paper and dashboard will update.
4. Check the paper's word count and re-read its fixed framing paragraphs (see [Paper](docs/PAPER.md)).

## Correcting a coded value

Do not edit the master dataset silently. Record the change in the Phase 12 correction register (`results/phase12/AI_Governance_Atlas_Phase12_Correction_Register.csv`): set `review_decision` to `Approve`, `Reject` or `Needs evidence` (it starts as `Pending`), fill in `approved_revised_value` for approvals and add `reviewer_comments`, then run `python run_pipeline.py --stage phase12`. Only rows marked `Approve` are applied; they are written to `results/phase12/governance_dataset_phase12_revised.csv`, with a change log.

## Adding or replacing a source document

1. Put the official PDF in `data/raw/<framework>/`.
2. Update `SOURCES` in `src/extract_text.py` if it should become the analysed text for that framework.
3. Record the new version in `version_used` for the affected records, then re-run the pipeline.

## Conventions

- Scripts resolve paths relative to the repository root. Never hard-code a path to your own computer.
- Generated outputs are committed so readers can browse the results without running anything. Regenerate them with the pipeline rather than editing them by hand.
- Use a branch and a pull request for changes, and note material coding changes in `CHANGELOG.md`.
