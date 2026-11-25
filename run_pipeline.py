"""Run the AI Governance Atlas analysis pipeline in the correct order.

Usage
-----
    python run_pipeline.py                  # run every automated stage
    python run_pipeline.py --stage text     # run one stage only
    python run_pipeline.py --list           # show stages and scripts

Stages
------
    text        PDF extraction, preprocessing, keyword analysis, keyword charts
    coding      dataset validation, comparative tables, enforcement coding, charts
    phase12     coding audit and automated review (read-only on human input)
    phase13     comparative analysis reports
    phase14     source validation, legal analysis and synthesis worksheets
    report      template-based comparative report

Human-input files are protected
-------------------------------
Two scripts create templates that a researcher then fills in by hand:

    src/analysis/create_coding_review.py      -> results/phase12/coding_review_template.csv
    src/analysis/generate_phase12_review.py   -> results/phase12/AI_Governance_Atlas_Phase12_Correction_Register.csv

They are NOT run by default, because re-running them would overwrite completed
review decisions. Run them only with --include-review-generators, and each
script additionally refuses to overwrite an existing file unless given --force.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent

STAGES: dict[str, list[str]] = {
    "text": [
        "src/extract_text.py",
        "src/preprocess.py",
        "src/keyword_analysis.py",
        "src/visualise.py",
    ],
    "coding": [
        "src/validate_dataset.py",
        "src/comparative_analysis.py",
        "src/normalise_governance_data.py",
        "src/build_comparative_matrix.py",
        "src/recode_enforcement.py",
        "src/build_enforcement_architecture.py",
        "src/finalise_enforcement_analysis.py",
        "src/advanced_visualisations.py",
    ],
    "phase12": [
        "src/analysis/coding_audit.py",
        "src/analysis/phase12_automated_review_engine.py",
        "src/analysis/apply_phase12_approved_corrections.py",
    ],
    "phase13": [
        "src/analysis/phase13/phase13_1_comparative_analysis.py",
        "src/analysis/phase13/phase13_2_governance_dimension_comparison.py",
        "src/analysis/phase13/phase13_3_legal_force_enforceability.py",
        "src/analysis/phase13/phase13_4_institutional_responsibility.py",
        "src/analysis/phase13/phase13_5_implementation_evidence.py",
        "src/analysis/phase13/phase13_6_consolidated_findings.py",
    ],
    "phase14": [
        "src/analysis/phase14/phase14_1_primary_source_locator.py",
        "src/analysis/phase14/phase14_2_source_context_validation_queue.py",
        "src/analysis/phase14/phase14_3_official_source_version_register.py",
        "src/analysis/phase14/phase14_4_provision_level_legal_analysis_worksheet.py",
        "src/analysis/phase14/phase14_5_comparative_legal_argument_matrix.py",
        "src/analysis/phase14/phase14_6_legal_validation_findings_review.py",
        "src/analysis/phase14/phase14_6_corrected_audit.py",
        "src/analysis/phase14/phase14_7_research_synthesis.py",
    ],
    "report": [
        "src/report_generator.py",
    ],
}

REVIEW_GENERATORS = [
    "src/analysis/create_coding_review.py",
    "src/analysis/generate_phase12_review.py",
]


def run_script(script: str) -> float:
    path = ROOT / script
    if not path.is_file():
        raise FileNotFoundError(f"Pipeline script not found: {script}")
    print(f"\n>>> {script}", flush=True)
    start = time.perf_counter()
    # Render charts to files without opening windows (works on servers and CI)
    env = {**os.environ, "MPLBACKEND": os.environ.get("MPLBACKEND", "Agg")}
    result = subprocess.run([sys.executable, str(path)], cwd=ROOT, env=env)
    elapsed = time.perf_counter() - start
    if result.returncode != 0:
        raise SystemExit(
            f"\nPipeline stopped: {script} exited with code {result.returncode}."
        )
    return elapsed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--stage",
        choices=list(STAGES),
        action="append",
        help="Run only this stage (may be repeated). Default: all stages.",
    )
    parser.add_argument(
        "--include-review-generators",
        action="store_true",
        help="Also run the scripts that create human-review templates. "
        "They still refuse to overwrite existing files without their own --force.",
    )
    parser.add_argument("--list", action="store_true", help="List stages and exit.")
    args = parser.parse_args()

    if args.list:
        for stage, scripts in STAGES.items():
            print(f"{stage}:")
            for script in scripts:
                print(f"    {script}")
        print("review generators (opt-in):")
        for script in REVIEW_GENERATORS:
            print(f"    {script}")
        return

    if sys.version_info < (3, 10):
        raise SystemExit("AI Governance Atlas requires Python 3.10 or newer.")

    selected = args.stage or list(STAGES)
    timings: list[tuple[str, float]] = []

    for stage in selected:
        scripts = list(STAGES[stage])
        if stage == "phase12" and args.include_review_generators:
            scripts = [
                "src/analysis/coding_audit.py",
                "src/analysis/create_coding_review.py",
                "src/analysis/generate_phase12_review.py",
                "src/analysis/phase12_automated_review_engine.py",
                "src/analysis/apply_phase12_approved_corrections.py",
            ]
        print(f"\n==================== Stage: {stage} ====================")
        for script in scripts:
            timings.append((script, run_script(script)))

    print("\n==================== Pipeline complete ====================")
    for script, seconds in timings:
        print(f"{seconds:7.1f}s  {script}")


if __name__ == "__main__":
    main()
