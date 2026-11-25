# Pipeline

`run_pipeline.py` runs 32 scripts in seven stages, in dependency order. Each stage can also be run on its own with `--stage`.

## Stages

### 1. `text`: computational text analysis
| Script | Reads | Writes |
|---|---|---|
| `src/extract_text.py` | One PDF per framework, listed in `SOURCES` | `data/processed/extracted_documents.csv` |
| `src/preprocess.py` | extracted text | `data/processed/cleaned_documents.csv` |
| `src/keyword_analysis.py` | extracted text | `results/tables/keyword_counts_by_document.csv`, `keyword_summary_by_country.csv` |
| `src/visualise.py` | keyword summary | `results/charts/comparative_bar_chart.png`, `governance_heatmap.png`, `stacked_bar_chart.png` |

The EU corpus uses the consolidated AI Act text of 27 July 2026, which has no recitals. Change the EU entry in `SOURCES` to use the 2024 Official Journal edition instead.

### 2. `coding`: comparative tables from the coded dataset
| Script | Purpose |
|---|---|
| `src/validate_dataset.py` | Structural checks: IDs, missing values, categories |
| `src/comparative_analysis.py` | Framework × category tables |
| `src/normalise_governance_data.py` | Standard responsibility and enforcement categories |
| `src/build_comparative_matrix.py` | Comparative matrices |
| `src/recode_enforcement.py` | Provision-specific enforcement coding (direct, cross-referenced, system-level) |
| `src/build_enforcement_architecture.py` | System-level enforcement architecture |
| `src/finalise_enforcement_analysis.py` | Final enforcement linkage per provision |
| `src/advanced_visualisations.py` | Charts `results/charts/01–07_*.png` |

### 3. `phase12`: coding audit
| Script | Purpose |
|---|---|
| `src/analysis/coding_audit.py` | Distribution matrices for review |
| `src/analysis/phase12_automated_review_engine.py` | Automated consistency review and human review queue |
| `src/analysis/apply_phase12_approved_corrections.py` | Applies **approved** corrections to a revised copy of the dataset (never to the master) |

### 4. `phase13`: comparative analysis
Six scripts in `src/analysis/phase13/` (13.1–13.6) compare jurisdictions, governance dimensions, legal force, institutional responsibility and implementation evidence, then consolidate the findings. Outputs: `results/phase13/`.

### 5. `phase14`: source validation and synthesis
Eight scripts in `src/analysis/phase14/` (14.1–14.7) locate each provision in its source PDF, validate the official source and version, prepare the legal-analysis worksheet and argument matrix, audit completeness and build the research-synthesis worksheet. Outputs: `results/phase14/`.

### 6. `report`: template-based report
`src/report_generator.py` → `research/reports/AI_Governance_Atlas_Report.md`

### 7. `publish`: paper and dashboard
| Script | Writes |
|---|---|
| `src/publish/generate_paper.py` | `results/paper/AI_Governance_Atlas_Paper.pdf` and `.md`, `figures/`, `paper_word_count.txt` |
| `src/publish/build_dashboard.py` | `results/dashboard/index.html` |

Both use the shared data layer `src/publish/atlas_data.py`, so the paper and the dashboard always report the same figures. See [Paper](PAPER.md) and [Dashboard](DASHBOARD.md).

## Protected files

Two files hold decisions entered by hand:

- `results/phase12/coding_review_template.csv`
- `results/phase12/AI_Governance_Atlas_Phase12_Correction_Register.csv`

The scripts that create them (`create_coding_review.py`, `generate_phase12_review.py`) are **not** part of the default run. They only run with `--include-review-generators`, and even then each refuses to overwrite an existing file unless called directly with `--force`.

## Reproducibility

- Every script resolves paths relative to the repository, so the project runs from any folder on any operating system.
- Outputs contain no absolute paths or machine-specific details.
- With `requirements-lock.txt` installed, a full run reproduces every committed table exactly. Only generation timestamps and PNG byte encodings differ.
