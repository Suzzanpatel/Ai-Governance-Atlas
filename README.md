# AI Governance Atlas
### From AI Principles to Regulatory Practice

AI Governance Atlas is a computational legal research project. It examines how AI governance principles become regulatory obligations, institutional accountability and enforcement mechanisms in the **European Union, India and the United Kingdom**, with the **OECD AI Principles** as an international benchmark.

> **Research question.** To what extent do India, the EU and the UK translate AI governance principles into specific, measurable and enforceable regulatory obligations?

| 📄 **Paper** | 📊 **Dashboard** | 📚 **Documentation** |
|---|---|---|
| [*From Principles to Enforceable Obligations*](results/paper/AI_Governance_Atlas_Paper.pdf): about 4,000 words, generated from the data | [`results/dashboard/index.html`](results/dashboard/index.html): download and open in a browser, or get it from the [latest release](https://github.com/Suzzanpatel/ai-governance-atlas/releases/latest) | [`docs/`](docs/README.md): setup, pipeline, data dictionary, paper, dashboard, methodology |

---

## Key findings

Based on the 20 coded provisions at release v0.1.0:

- **Mandatory duties are confined to the EU.** All 5 mandatory provisions in the sample come from the AI Act. The 15 provisions from India, the UK and the OECD are recommendations (10) or institutional assignments (5).
- **The frameworks differ in *who* is obliged.** The EU provisions address private providers and deployers, while the UK and Indian provisions mainly address regulators, government and new institutions. The non-statutory frameworks delegate the step that turns a principle into a duty on industry.
- **Only EU duties are linked to sanctions.** All 5 EU provisions are linked by cross-reference to administrative fines. Outside the EU, one Indian and one UK provision name a compliance route (voluntary reporting and peer scrutiny; existing regulator powers). The rest rely on the general powers of existing regulators or have no identified route.
- **Implementation evidence runs the other way.** None of the EU provisions could yet be assessed, because they were not yet applicable. UK and Indian provisions show partial implementation, mostly of measures addressed to the state.

These describe a purposive sample and do not rank the frameworks. See the [paper](results/paper/AI_Governance_Atlas_Paper.pdf) for the full analysis and its limitations.

## Frameworks and source versions

| Framework | Instrument | Version coded | Legal status |
|---|---|---|---|
| European Union | Regulation (EU) 2024/1689 (AI Act), as amended by Regulation (EU) 2026/1744 (Digital Omnibus on AI) | Consolidated text, 27 July 2026 | Binding legislation |
| India | *India AI Governance Guidelines* (MeitY) | 5 November 2025 | Non-binding guidance |
| United Kingdom | *A pro-innovation approach to AI regulation* (DSIT White Paper, CP 815) | March 2023, amended web-ready PDF | Government policy (non-statutory) |
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
| [Pipeline](docs/PIPELINE.md) | The seven stages and 32 scripts, inputs and outputs, protected files |
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
│   ├── annotated/             # governance_dataset.csv: the 20 coded provisions (source of truth)
│   └── backups/
├── src/
│   ├── *.py                   # text analysis and comparative coding
│   ├── analysis/              # Phase 12 audit, Phase 13 comparison, Phase 14 validation
│   └── publish/               # paper generator, dashboard builder, shared data layer
├── results/
│   ├── paper/                 # generated paper (PDF, Markdown, figures)
│   ├── dashboard/             # interactive dashboard (single HTML file)
│   ├── tables/  charts/       # comparative tables and figures
│   └── phase12/ phase13/ phase14/
├── research/
│   ├── methodology/           # research questions, case selection, coding framework, limitations
│   ├── evidence/              # evidence pack and verification audit
│   └── reports/               # template-based report
└── docs/                      # project documentation
```

## Project status

**v0.1.0: working paper and dashboard released.** The pipeline, paper generator and dashboard are complete. Open research tasks:

- [x] Sign off the 37 source-verification corrections in the Phase 12 correction register (approved 26 November 2026)
- [ ] Complete the researcher fields in the Phase 14.7 synthesis worksheet
- [ ] Code later instruments, such as India's 2026 amendments to the IT Rules on synthetically generated information and the UK Government's February 2024 response
- [ ] Extend the paper's literature review and add an inter-coder reliability check
- [ ] Choose a licence (see below)

## Citation

Citation metadata is in [`CITATION.cff`](CITATION.cff); GitHub's "Cite this repository" button uses it.

## Licence and disclaimer

**Licence: not yet chosen.** The `LICENSE` file is empty, so no reuse rights are currently granted. A common choice is MIT for code and CC BY 4.0 for data and text. The source PDFs in `data/raw/` remain under their publishers' own terms.

This project is for academic research and is not legal advice. Check regulatory interpretations against the official instruments and amendments.
