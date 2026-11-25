# AI Governance Atlas — Documentation

Start here to find your way around the project. Each guide covers one topic.

| If you want to… | Read |
|---|---|
| Install the project and run the analysis | [Getting started](GETTING_STARTED.md) |
| Understand what each script does and the order it runs in | [Pipeline](PIPELINE.md) |
| Know what each column and output file means | [Data dictionary](DATA_DICTIONARY.md) |
| Regenerate or edit the academic paper | [Paper](PAPER.md) |
| Open, use or share the interactive dashboard | [Dashboard](DASHBOARD.md) |
| Understand the research design, coding rules and limitations | [Methodology](METHODOLOGY.md) |
| Add or correct coded provisions | [Contributing](../CONTRIBUTING.md) |
| See what changed between versions | [Changelog](../CHANGELOG.md) |

## The project in one paragraph

AI Governance Atlas compares how the European Union, India and the United Kingdom turn AI governance principles into obligations, using the OECD AI Principles as an international benchmark. Twenty provisions (five per framework) are coded by hand for legal force, obligation force, duty-holder, enforcement linkage and implementation evidence. Keyword analysis of the full texts adds context. A single command reproduces every table, chart, the academic paper and the dashboard from the coded dataset.

## How the pieces fit together

```
data/raw/*.pdf ──► text stage ──► keyword tables and charts ─────────────────┐
                                                                             │
data/annotated/governance_dataset.csv ──► coding ──► phase12 ──► phase13 ──► phase14
                                             │                                │
                                             └───────────► publish ◄──────────┘
                                                            │
                                     results/paper/AI_Governance_Atlas_Paper.pdf
                                     results/dashboard/index.html
```

The coded dataset is the single source of truth. Every downstream file, including the paper and the dashboard, is generated from it, so a correction made in the dataset reaches every output on the next run.
