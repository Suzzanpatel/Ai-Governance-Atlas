
import re
import pandas as pd
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = PROJECT_DIR / "data" / "processed" / "extracted_documents.csv"

OUTPUT_DIR = PROJECT_DIR / "results" / "tables"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

governance_keywords = {
    "Transparency": [
        "transparency", "disclosure", "disclose",
        "explainability", "information provision"
    ],
    "Accountability": [
        "accountability", "responsibility", "responsible",
        "human oversight", "audit"
    ],
    "Risk Assessment": [
        "risk assessment", "risk management",
        "systemic risk", "high-risk", "risk mitigation"
    ],
    "Safety and Testing": [
        "safety", "testing", "robustness",
        "cybersecurity", "evaluation"
    ],
    "Enforcement": [
        "enforcement", "penalty", "penalties",
        "compliance", "sanctions", "supervision"
    ]
}

df = pd.read_csv(INPUT_FILE)

documents = (
    df.groupby(["country", "document"])["text"]
    .apply(lambda pages: " ".join(pages.dropna().astype(str)))
    .reset_index()
)

results = []

for _, row in documents.iterrows():

    text = row["text"].lower()

    total_words = len(re.findall(r"\b[\w'-]+\b", text))

    for dimension, keywords in governance_keywords.items():

        dimension_count = 0

        for keyword in keywords:

            pattern = (
                r"(?<!\w)" + re.escape(keyword.lower()) + r"(?!\w)"
            )

            dimension_count += len(re.findall(pattern, text))

        normalised_frequency = (
            dimension_count / total_words * 1000
            if total_words > 0 else 0
        )

        results.append({
            "country": row["country"],
            "document": row["document"],
            "dimension": dimension,
            "keyword_count": dimension_count,
            "total_words": total_words,
            "frequency_per_1000_words": round(
                normalised_frequency, 3
            )
        })

results_df = pd.DataFrame(results)

results_df.to_csv(
    OUTPUT_DIR / "keyword_counts_by_document.csv",
    index=False
)

summary = (
    results_df
    .groupby(["country", "dimension"])
    .agg({
        "keyword_count": "sum",
        "total_words": "sum"
    })
    .reset_index()
)

summary["frequency_per_1000_words"] = (
    summary["keyword_count"] / summary["total_words"] * 1000
).round(3)

summary.to_csv(
    OUTPUT_DIR / "keyword_summary_by_country.csv",
    index=False
)

print("\nKEYWORD ANALYSIS COMPLETED!")
print("\nCOUNTRY-WISE SUMMARY:")
print(summary.to_string(index=False))

print("\nResults saved in:", OUTPUT_DIR)
