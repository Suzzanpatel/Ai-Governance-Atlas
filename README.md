# AI Governance Atlas
### From AI Principles to Regulatory Practice

AI Governance Atlas is a computational legal research project. It examines how AI governance principles become regulatory obligations, institutional accountability and enforcement mechanisms in the **European Union, India and the United Kingdom**, with the **OECD AI Principles** as an international benchmark.

> **Research question.** To what extent do India, the EU and the UK translate AI governance principles into specific, measurable and enforceable regulatory obligations?

| 📄 **Paper** | 📊 **Dashboard** | 📚 **Documentation** |
|---|---|---|
| [*From Principles to Enforceable Obligations*](results/paper/AI_Governance_Atlas_Paper.pdf): about 4,000 words, generated from the data | [`results/dashboard/index.html`](results/dashboard/index.html): download and open in a browser, or get it from the [latest release](https://github.com/Suzzanpatel/ai-governance-atlas/releases/latest) | [`docs/`](docs/README.md): setup, pipeline, data dictionary, paper, dashboard, methodology |

---

## Key findings

Based on the 24 coded provisions at release v0.2.0:

- **Binding duties come from the EU and, since February 2026, India.** All 5 EU provisions and India's 2 intermediary-rule provisions on synthetically generated content are mandatory duties in binding instruments. The UK's 7 provisions and India's 5 Guidelines provisions are recommendations, a government undertaking (UK003) or a statement of no specified force (UK007).
- **The frameworks differ in *who* is obliged.** All 7 binding provisions address private actors (providers, deployers, intermediaries), whereas 14 of the 17 non-binding provisions address governments, regulators or institutions. Non-statutory frameworks delegate the step that turns a principle into a duty on industry.
- **Statutory sanctions attach in two ways.** EU duties are cross-referenced to administrative fines; India's rules withdraw the intermediary's safe-harbour protection under section 79 of the IT Act. Elsewhere, enforcement relies on existing regulators' general powers or no route is identified.
- **Enforceability and implementation diverge.** The EU's duties were not yet applicable; India's targeted rules took effect ten days after notification by extending an existing regime. Implementation speed depends less on bindingness than on existing legal machinery.
- **Coding reliability:** a blind, AI-assisted second coding agreed at κ = 1.00 (legal force), 0.84 (dimension), 0.93 (obligation force) and 0.63 (enforcement linkage).

These describe a purposive sample and do not rank the frameworks. See the [paper](results/paper/AI_Governance_Atlas_Paper.pdf) for the full analysis and its limitations.

## Frameworks and source versions

| Framework | Instrument | Version coded | Legal status |
|---|---|---|---|
| European Union | Regulation (EU) 2024/1689 (AI Act), as amended by Regulation (EU) 2026/1744 (Digital Omnibus on AI) | Consolidated text, 27 July 2026 | Binding legislation |
| India | *India AI Governance Guidelines* (MeitY) | 5 November 2025 | Non-binding guidance |
| India | IT (Intermediary Guidelines and Digital Media Ethics Code) Rules 2021, as amended 2026 (G.S.R. 120(E)) | Consolidated text, 10 February 2026; in force 20 February 2026 | Binding (subordinate legislation) |
| United Kingdom | *A pro-innovation approach to AI regulation* (DSIT White Paper, CP 815) | March 2023, amended web-ready PDF | Government policy (non-statutory) |
| United Kingdom | *A pro-innovation approach to AI regulation: government response* (CP 1019) | February 2024 | Government policy (non-statutory) |
| OECD (benchmark) | Recommendation of the Council on AI, OECD/LEGAL/0449 | As revised 3 May 2024 | International recommendation |

## Quick start

Requires **Python 3.10+** and runs on macOS, Linux and Windows with no internet access needed. Full [system requirements](docs/GETTING_STARTED.md#system-requirements).

```bash
git clone https://github.com/Suzzanpatel/ai-governance-atlas.git
cd ai-governance-atlas
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run_pipeline.py          # analysis, paper and dashboard (about 25 seconds)
```

## Documentation

| Guide | Contents |
|---|---|
| [Getting started](docs/GETTING_STARTED.md) | System requirements, installation, running, troubleshooting |
| [Pipeline](docs/PIPELINE.md) | The seven stages and 33 scripts, inputs and outputs, protected files |
| [Data dictionary](docs/DATA_DICTIONARY.md) | Every column in the coded dataset and where to find each result |
| [Paper](docs/PAPER.md) | How the paper is generated, what is computed vs fixed, word-count rule, pre-submission checklist |
| [Dashboard](docs/DASHBOARD.md) | Views, accessibility and how to share or host it |
| [Methodology](docs/METHODOLOGY.md) | Research design, the translation chain and interpretive safeguards |
| [Contributing](CONTRIBUTING.md) | Adding provisions, correcting values, adding sources |
| [Changelog](CHANGELOG.md) | Version history |

## Repository structure

```
ai-governance-atlas/
├── run_pipeline.py            # runs the whole project
├── requirements.txt           # dependency ranges (requirements-lock.txt: exact versions)
├── data/
│   ├── raw/                   # official source PDFs
│   ├── processed/             # extracted and cleaned text
│   ├── annotated/             # governance_dataset.csv: the 24 coded provisions (source of truth); coding_change_log.csv
│   ├── reliability/           # blind second coding and template for a human second coder
│   └── backups/
├── src/
│   ├── *.py                   # text analysis and comparative coding
│   ├── analysis/              # Phase 12 audit, Phase 13 comparison, Phase 14 validation
│   └── publish/               # paper generator, dashboard builder, shared data layer
├── results/
│   ├── paper/                 # generated paper (PDF, Markdown, figures)
│   ├── dashboard/             # interactive dashboard (single HTML file)
│   ├── tables/  charts/       # comparative tables and figures
│   ├── reliability/           # inter-coder agreement
│   └── phase12/ phase13/ phase14/
├── research/
│   ├── methodology/           # research questions, case selection, coding framework, limitations
│   ├── evidence/              # evidence pack and verification audit
│   └── reports/               # template-based report
└── docs/                      # project documentation
```

## Project status

**v0.2.0: research completion release.** Coding inconsistencies fixed, India's 2026 IT Rules amendments and the UK's 2024 response coded, Phase 14 review recorded, and an AI-assisted reliability check added. Remaining tasks:

- [x] Sign off the 37 source-verification corrections (approved 26 November 2026)
- [x] Code later instruments (India IT Rules 2026; UK CP 1019)
- [x] Fix coding inconsistencies (obligation force vs nature; secondary dimension)
- [x] Record Phase 14 source review and draft synthesis
- [x] Blind second coding (AI-assisted)
- [ ] **Review the drafted Phase 14 legal analysis** in `research/evidence/phase14_review_record.csv` and set `analysis_status` to `REVIEWED`
- [ ] Download the India IT Rules and UK CP 1019 PDFs into `data/raw/` and confirm page numbers for IND006, IND007, UK006, UK007
- [ ] Have a human second coder complete `data/reliability/blind_coding_template.csv`
- [ ] Extend the paper's literature review

## Citation

Citation metadata is in [`CITATION.cff`](CITATION.cff); GitHub's "Cite this repository" button uses it.

## Copyright and disclaimer

**No licence.** The project is published without an open-source licence, so all rights are reserved: others may view and cite it but need the author's permission to reuse the code or data. The source PDFs in `data/raw/` remain under their publishers' own terms.

This project is for academic research and is not legal advice. Check regulatory interpretations against the official instruments and amendments.
