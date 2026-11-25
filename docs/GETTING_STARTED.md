# Getting started

## System requirements

| Requirement | Detail |
|---|---|
| Python | **3.10 or newer** (tested on 3.10 and 3.13) |
| Operating system | macOS, Linux or Windows. File names are matched ignoring case and whitespace differences, so results are identical on every system |
| Python packages | pandas ≥ 2.0, numpy ≥ 1.24, matplotlib ≥ 3.7, seaborn ≥ 0.13, PyMuPDF ≥ 1.23, reportlab ≥ 3.6 |
| Disk space | About 25 MB for the repository and generated outputs |
| Memory | Under 1 GB |
| Run time | About 25 seconds for the full pipeline on a laptop |
| Network | **Not needed.** No API keys, downloads or external services |
| Browser (dashboard only) | Any current version of Chrome, Edge, Firefox or Safari |

## Install

```bash
git clone https://github.com/Suzzanpatel/ai-governance-atlas.git
cd ai-governance-atlas

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

`requirements.txt` lists the tested version ranges. To reproduce the committed outputs byte for byte, install `requirements-lock.txt` instead. Different PyMuPDF releases can extract a few words differently from the same PDF.

## Run

```bash
python run_pipeline.py                      # everything: analysis, paper and dashboard
python run_pipeline.py --list               # list the stages and their scripts
python run_pipeline.py --stage publish      # regenerate only the paper and dashboard
python run_pipeline.py --stage text --stage coding
```

The runner stops at the first script that fails and prints which one.

## What you get

| Output | Location |
|---|---|
| Academic paper (PDF and editable Markdown) | `results/paper/` |
| Interactive dashboard | `results/dashboard/index.html`: double-click to open |
| Comparative tables | `results/tables/`, `results/phase13/`, `results/phase14/` |
| Figures | `results/charts/`, `results/paper/figures/` |
| Template-based report | `research/reports/AI_Governance_Atlas_Report.md` |

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `ModuleNotFoundError: fitz` or `pymupdf` | PyMuPDF is not installed: `pip install -r requirements.txt` |
| `Required input not found … run the earlier pipeline stages first` | The analysis outputs are missing (for example after deleting `results/`). Run `python run_pipeline.py` once |
| `Main text is N words, outside 3600–4400` | The paper's length moved outside the target after a data change. See [Paper](PAPER.md#word-count) |
| `Refusing to overwrite … human review decisions` | Working as intended. See [Pipeline](PIPELINE.md#protected-files) |
