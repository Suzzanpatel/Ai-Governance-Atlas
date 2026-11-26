# Contributing

This guide covers the most common changes: adding a provision, correcting a coded value, and adding a source document.

## Adding a provision

1. Add a row to `data/annotated/governance_dataset.csv` with every column filled in, following the [data dictionary](docs/DATA_DICTIONARY.md) and the [coding framework](research/methodology/coding_framework.md).
   - Use the next free ID for the framework (`EU006`, `IND006`, …).
   - Copy `exact_text` verbatim from the official source and give both PDF and printed page numbers.
   - Record the exact version used in `version_used`.
2. Add the provision's ID to the maps in `src/normalise_governance_data.py` (responsibility and enforcement categories), `src/recode_enforcement.py` and `src/finalise_enforcement_analysis.py` (enforcement linkage). The scripts stop with an error if an ID is missing.
3. Add a row for it to `research/evidence/phase14_review_record.csv` and log it in `data/annotated/coding_change_log.csv`.
4. Run `python run_pipeline.py`. `validate_dataset.py` will flag structural problems, and the paper and dashboard will update.
5. Check the paper's word count and re-read its fixed framing paragraphs (see [Paper](docs/PAPER.md)).

## Correcting a coded value

**Signing off existing corrections.** The 37 corrections from the source-verification audit are already in the dataset. Their register rows are marked `Pending` only because they have not been formally accepted. Review each row, then set `review_decision` to `Approve` (or `Reject` with a comment, then revert the field by hand).

**New corrections.** Do not edit the master dataset silently. Record the change in the Phase 12 correction register (`results/phase12/AI_Governance_Atlas_Phase12_Correction_Register.csv`): set `review_decision` to `Approve`, `Reject` or `Needs evidence` (it starts as `Pending`), fill in `approved_revised_value` for approvals and add `reviewer_comments`, then run `python run_pipeline.py --stage phase12`. Only rows marked `Approve` are applied; they are written to `results/phase12/governance_dataset_phase12_revised.csv`, with a change log.

## Reviewing the drafted Phase 14 analysis

Open `research/evidence/phase14_review_record.csv`. For each provision, check or rewrite the drafted fields (`researcher_legal_analysis`, `provisional_conclusion`, `proposed_argument`, `researcher_conclusion` and so on), then set `analysis_status` to `REVIEWED` and put your initials in `reviewer_name_or_initials`. Re-run `python run_pipeline.py --stage phase14`; the audit then reports that provision as complete.

## Adding a human second coder

Give a colleague `data/reliability/blind_coding_template.csv` and `research/methodology/coding_framework.md`, but not the dataset. Save their completed sheet as `data/reliability/second_coder_human.csv` and run `python run_pipeline.py`. The reliability script and the paper then use the human coding instead of the AI-assisted one.

## Adding or replacing a source document

1. Put the official PDF in `data/raw/<framework>/`.
2. Update `SOURCES` in `src/extract_text.py` if it should become the analysed text for that framework.
3. Record the new version in `version_used` for the affected records, then re-run the pipeline.

## Conventions

- Scripts resolve paths relative to the repository root. Never hard-code a path to your own computer.
- Generated outputs are committed so readers can browse the results without running anything. Regenerate them with the pipeline rather than editing them by hand.
- Use a branch and a pull request for changes, and note material coding changes in `CHANGELOG.md`.
