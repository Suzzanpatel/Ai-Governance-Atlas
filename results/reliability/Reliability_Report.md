# Inter-coder reliability

Second coder: **AI-assisted** (`data/reliability/second_coder_ai.csv`), 24 provisions compared.

> **AI-assisted second coding.** The second coder was an AI agent working blind: it saw each provision's text, location and instrument and the coding framework, never the primary codes. Agreement with an AI coder is not equivalent to agreement between two trained human coders and should be reported as AI-assisted.

| Variable | n | Agreement | Cohen's κ | Interpretation |
|---|---|---|---|---|
| Legal force of instrument | 24 | 100.0% | 1.0 | almost perfect |
| Primary governance dimension | 24 | 87.5% | 0.843 | almost perfect |
| Obligation force | 24 | 95.8% | 0.927 | almost perfect |
| Enforcement linkage | 24 | 70.8% | 0.632 | substantial |
| Obligation nature (multi-label) | 24 | 83.3% |  | mean Jaccard overlap 0.90 |

Kappa benchmarks follow Landis and Koch (1977). With small n, kappa is unstable and sensitive to
category prevalence; read it together with percentage agreement and the disagreement list in
`results/reliability/disagreements.csv`.
