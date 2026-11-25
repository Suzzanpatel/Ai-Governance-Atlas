# AI Governance Atlas
### From AI Principles to Regulatory Practice

**AI Governance Atlas** is a computational legal research project. It examines how AI governance principles translate into regulatory obligations, institutional accountability and enforcement mechanisms.

It compares AI governance in the **European Union, India and the United Kingdom**, using the **OECD AI Principles** as an international benchmark. The OECD is a reference point, not a fourth jurisdiction.

> **Central research question.** To what extent do India, the EU and the UK translate AI governance principles into specific, measurable and enforceable regulatory obligations?
>
> Supporting questions RQ1–RQ5 are in [`research/methodology/research_questions.md`](research/methodology/research_questions.md).

---

## Contents

- [Frameworks and source versions](#frameworks-and-source-versions)
- [Governance dimensions](#governance-dimensions)
- [System requirements](#system-requirements)
- [Quick start](#quick-start)
- [Pipeline](#pipeline)
- [Repository structure](#repository-structure)
- [Project status and roadmap](#project-status-and-roadmap)
- [Methodology and limitations](#methodology-and-limitations)
- [Licence, citation and disclaimer](#licence-citation-and-disclaimer)

---

## Frameworks and source versions

| Framework | Instrument | Version coded | Legal status |
|---|---|---|---|
| European Union | Regulation (EU) 2024/1689 (AI Act), as amended by Regulation (EU) 2026/1744 (Digital Omnibus on AI) | Consolidated text, 27 July 2026 | Binding legislation |
| India | *India AI Governance Guidelines: Enabling Safe and Trusted AI Innovation* (MeitY) | 5 November 2025 | Non-binding guidance |
| United Kingdom | *A pro-innovation approach to AI regulation* (DSIT White Paper, CP 815) | March 2023, amended web-ready PDF | Government policy (non-statutory) |
| OECD (benchmark) | Recommendation of the Council on Artificial Intelligence, OECD/LEGAL/0449 | As revised 3 May 2024 | International recommendation (non-binding) |

The official PDFs are in `data/raw/`. The 2024 Official Journal edition of the EU AI Act is kept as a reference copy but is **not** part of the text corpus.

## Governance dimensions

Each coded provision is assigned one **primary** dimension, and optionally a secondary one:

1. **Transparency**: information provision, disclosure and explainability
2. **Accountability**: allocation of responsibility, human oversight and traceability
3. **Risk Assessment**: identifying, classifying, evaluating and mitigating risk
4. **Safety and Testing**: robustness, security, testing and lifecycle reliability
5. **Enforcement**: compliance mechanisms, regulatory powers and sanctions

Human oversight is coded under **Accountability** (for example EU004, Art. 14).

## System requirements

| Requirement | Detail |
|---|---|
| Python | **3.10 or newer** (tested on 3.10 and 3.13) |
| Operating system | macOS, Linux or Windows. File matching ignores letter case and whitespace variants, so results are the same on every OS |
| Python packages | pandas ≥ 2.0, numpy ≥ 1.24, matplotlib ≥ 3.7, seaborn ≥ 0.13, PyMuPDF ≥ 1.23 (see [`requirements.txt`](requirements.txt)) |
| Disk space | About 20 MB for the repository and outputs |
| Memory | Under 1 GB |
| Run time | About 20 seconds for the full pipeline on a laptop |
| Network | **Not needed.** No API keys, downloads or external services |

`requirements.txt` gives tested version ranges.
[`requirements-lock.txt`](requirements-lock.txt) pins the exact versions that produced the committed results. Use it if you need byte-identical outputs, because different PyMuPDF releases can extract a few words differently from the same PDF.

## Quick start

```bash
git clone https://github.com/Suzzanpatel/ai-governance-atlas.git
cd ai-governance-atlas

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt    # or requirements-lock.txt for exact reproduction

python run_pipeline.py             # run every stage
python run_pipeline.py --list      # list stages and scripts
python run_pipeline.py --stage text --stage coding   # run selected stages
```

## Pipeline

`run_pipeline.py` runs the scripts in dependency order and stops at the first error.

| Stage | What it does | Main outputs |
|---|---|---|
| `text` | Extracts PDF text (one source per framework), preprocesses it, counts keywords per 1,000 words and draws keyword charts | `data/processed/`, `results/tables/keyword_*.csv`, `results/charts/` |
| `coding` | Validates the coded dataset, builds comparative tables, normalises responsibility and enforcement categories, draws charts | `results/tables/`, `results/charts/01–07_*.png` |
| `phase12` | Runs the coding audit and automated review, and applies approved corrections | `results/phase12/` |
| `phase13` | Comparative analysis by jurisdiction, dimension, legal force, responsibility and implementation | `results/phase13/` |
| `phase14` | Locates primary sources, validates versions, builds the legal-analysis worksheet, argument matrix and research synthesis | `results/phase14/` |
| `report` | Template-based comparative report | `research/reports/AI_Governance_Atlas_Report.md` |

**Human review input is protected.** `results/phase12/coding_review_template.csv` and the Phase 12 correction register hold decisions entered by hand. The scripts that create them are left out of the default run, and they refuse to overwrite an existing file unless given `--force`.

Column definitions and a guide to the output files are in [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md).

## Repository structure

```
ai-governance-atlas/
├── run_pipeline.py              # runs the full analysis
├── requirements.txt             # dependency ranges
├── requirements-lock.txt        # exact versions for reproduction
├── data/
│   ├── raw/                     # official source PDFs (eu, India, uk, oecd)
│   ├── processed/               # extracted and cleaned page text
│   ├── annotated/               # governance_dataset.csv: the 20 coded provisions (master)
│   └── backups/                 # dataset snapshot before Phase 12 corrections
├── src/
│   ├── *.py                     # text, keyword and comparative-coding scripts
│   └── analysis/                # Phase 12 audit and Phase 13–14 analysis scripts
├── results/
│   ├── tables/                  # comparative and keyword tables
│   ├── charts/                  # figures
│   ├── phase12/                 # coding audit and review
│   ├── phase13/                 # comparative analysis tables and reports
│   └── phase14/                 # source validation, legal analysis and synthesis
├── research/
│   ├── methodology/             # research questions, case selection, coding framework, limitations
│   ├── evidence/                # evidence pack (JSON) and verification audit
│   └── reports/                 # generated comparative report
└── docs/
    └── DATA_DICTIONARY.md
```

## Project status and roadmap

**Completed**
- Research design: questions, case selection, coding framework and limitations
- Text extraction and keyword analysis of the four instruments (320 pages)
- 20 provisions coded by hand, with exact text, page references and enforcement cross-references
- Phase 12 coding audit and correction workflow
- Phase 13 comparative analysis (jurisdiction, dimension, legal force, responsibility, implementation)
- Phase 14 source and version validation and synthesis framework
- EU coding updated to the consolidated text as amended by Regulation (EU) 2026/1744
- Reproducible pipeline runner and documentation

**Remaining**
1. **Academic paper**: write up the findings, centred on how each duty links to an enforcement route
2. **Interactive dashboard**: a provision explorer and enforcement-pathway views built on the coded dataset
3. **Full GitHub documentation**: contribution guide, citation file and published releases

**Open research tasks before the paper**
- Complete the researcher fields in `results/phase14/research_synthesis/phase14_7_research_synthesis_worksheet.csv` and resolve the Phase 14.6 "source validation required" flags
- Decide on the Phase 12 correction register entries marked `Pending`
- Consider adding records for later instruments: India's IT (Intermediary Guidelines and Digital Media Ethics Code) Amendment Rules, 2026 on synthetically generated information, and the UK Government's February 2024 response to the White Paper
- Resolve the coding-category inconsistencies listed in the data dictionary

## Methodology and limitations

The project combines computational text analysis with manual legal coding. Computational patterns are **descriptive indicators**: a keyword count does not establish that an obligation is binding, enforceable or implemented. The 20-provision sample is purposive, five per framework, and does not represent each framework as a whole. Equal record counts do not imply that the frameworks are equivalent.

- [Research methodology](research/methodology/research_methodology.md)
- [Research questions](research/methodology/research_questions.md)
- [Case selection criteria](research/methodology/case_selection_criteria.md)
- [Coding framework](research/methodology/coding_framework.md)
- [Limitations](research/methodology/limitations.md)

## Licence, citation and disclaimer

**Licence:** not yet chosen. The `LICENSE` file is currently empty, which means no reuse rights are granted. Add a licence for the code and data (for example MIT for code and CC BY 4.0 for data and text) before publication. The source PDFs in `data/raw/` remain under their publishers' own terms.

**Disclaimer:** this project is for academic and research purposes and does not constitute legal advice. Check regulatory interpretations against the applicable official instruments and amendments.
