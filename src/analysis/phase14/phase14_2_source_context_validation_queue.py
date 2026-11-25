"""
Phase 14.2 — Provision-Level Source Context and Validation Queue
AI Governance Atlas

Re-scans local PDFs and extracts the source-page context around each dataset
exact_text excerpt. Creates a human validation queue. It NEVER marks a
provision legally verified automatically.

Run from project root:
    python src/analysis/phase14/phase14_2_source_context_validation_queue.py

Requires PyMuPDF:
    python -m pip install pymupdf
"""

from pathlib import Path
import re
import sys
import hashlib
import pandas as pd

try:
    import fitz
except ImportError as exc:
    raise SystemExit(
        "PyMuPDF is required. Install with: python -m pip install pymupdf"
    ) from exc


def locate_root() -> Path:
    here = Path(__file__).resolve()
    for candidate in [here.parent, *here.parents]:
        if (candidate / "data/annotated/governance_dataset.csv").is_file():
            return candidate
    raise FileNotFoundError("Cannot locate data/annotated/governance_dataset.csv.")


def normalize_with_map(text: str):
    """
    Collapse whitespace and normalise case/hyphens while preserving a map
    from each normalised character back to its source-text character offset.
    """
    output = []
    positions = []
    i = 0
    text = text.replace("\u00ad", "")
    while i < len(text):
        char = text[i]
        if char.isspace():
            start = i
            while i < len(text) and text[i].isspace():
                i += 1
            if output and output[-1] != " ":
                output.append(" ")
                positions.append(start)
            continue
        if char in "\u2010\u2011\u2012\u2013\u2014\u2015":
            char = "-"
        for lowered in char.casefold():
            output.append(lowered)
            positions.append(i)
        i += 1
    return "".join(output).strip(), positions


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_sources(raw_dir: Path, root: Path):
    sources = []
    for path in sorted(raw_dir.rglob("*.pdf")):
        try:
            doc = fitz.open(path)
            pages = []
            for page_number, page in enumerate(doc, start=1):
                text = page.get_text("text") or ""
                norm, mapping = normalize_with_map(text)
                pages.append({
                    "page_number": page_number,
                    "text": text,
                    "normalised": norm,
                    "mapping": mapping,
                })
            metadata = doc.metadata or {}
            doc.close()
            sources.append({
                "path": path,
                "relative_path": str(path.relative_to(root)),
                "name": path.name,
                "sha256": sha256(path),
                "pages": pages,
                "page_count": len(pages),
                "metadata_title": metadata.get("title") or "",
            })
        except Exception as exc:
            print(f"WARNING: Could not read {path}: {exc}")
    return sources


def locate_excerpt(quote: str, page):
    normalised_quote, _ = normalize_with_map(quote)
    page_norm = page["normalised"]
    if len(normalised_quote) < 35:
        return None

    match_type = ""
    start = page_norm.find(normalised_quote)
    matched_length = len(normalised_quote)

    if start >= 0:
        match_type = "NORMALISED_FULL_EXCERPT_MATCH"
    else:
        # A prefix is a weaker locator clue only.
        prefix = normalised_quote[:140]
        if len(prefix) < 80:
            return None
        start = page_norm.find(prefix)
        if start < 0:
            return None
        match_type = "NORMALISED_PREFIX_MATCH"
        matched_length = len(prefix)

    mapping = page["mapping"]
    if start >= len(mapping):
        return None
    raw_start = mapping[start]
    final_norm_index = min(start + matched_length - 1, len(mapping) - 1)
    raw_end = mapping[final_norm_index] + 1

    raw_text = page["text"]
    context_start = max(0, raw_start - 700)
    context_end = min(len(raw_text), raw_end + 700)
    return {
        "match_type": match_type,
        "raw_start": raw_start,
        "raw_end": raw_end,
        "source_excerpt": raw_text[raw_start:raw_end],
        "context_before_and_after": raw_text[context_start:context_end],
    }


def main():
    root = locate_root()
    dataset_path = root / "data/annotated/governance_dataset.csv"
    raw_dir = root / "data/raw"
    out_dir = root / "results/phase14/source_validation"
    report_dir = root / "results/phase14/reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    if not raw_dir.exists():
        raise FileNotFoundError(f"Source folder does not exist: {raw_dir}")

    df = pd.read_csv(dataset_path, dtype=str).fillna("")
    required = ["id", "country", "document", "exact_text"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Dataset missing columns: {missing}")
    if df.empty or df["id"].duplicated().any():
        raise ValueError("Dataset is empty or contains duplicate IDs.")

    sources = read_sources(raw_dir, root)
    records = []

    for _, row in df.iterrows():
        quote = row["exact_text"].strip()
        base = {
            "id": row["id"],
            "country": row["country"],
            "dataset_document": row["document"],
            "dataset_article_or_section": row.get("article_or_section", ""),
            "dataset_page_number": row.get("page_number", ""),
            "dataset_exact_text": quote,
            "dataset_source_reference": row.get("source_reference", ""),
            "dataset_version_used": row.get("version_used", ""),
        }

        if not quote:
            records.append({
                **base,
                "locator_status": "NO_EXACT_TEXT_TO_LOCATE",
                "source_pdf": "",
                "source_relative_path": "",
                "source_pdf_sha256": "",
                "pdf_metadata_title": "",
                "pdf_page_number": "",
                "match_type": "",
                "source_excerpt": "",
                "context_before_and_after": "",
                "human_validation_status": "UNRESOLVED",
                "source_is_official": "NOT_ASSESSED",
                "version_and_currency_checked": "NOT_ASSESSED",
                "article_and_paragraph_checked": "NOT_ASSESSED",
                "reviewer_notes": "",
            })
            continue

        found = False
        for source in sources:
            for page in source["pages"]:
                match = locate_excerpt(quote, page)
                if match is None:
                    continue
                found = True
                records.append({
                    **base,
                    "locator_status": "LOCATED_REQUIRES_HUMAN_VALIDATION",
                    "source_pdf": source["name"],
                    "source_relative_path": source["relative_path"],
                    "source_pdf_sha256": source["sha256"],
                    "pdf_metadata_title": source["metadata_title"],
                    "pdf_page_number": page["page_number"],
                    "match_type": match["match_type"],
                    "source_excerpt": match["source_excerpt"],
                    "context_before_and_after": match["context_before_and_after"],
                    "human_validation_status": "PENDING",
                    "source_is_official": "NOT_ASSESSED",
                    "version_and_currency_checked": "NOT_ASSESSED",
                    "article_and_paragraph_checked": "NOT_ASSESSED",
                    "reviewer_notes": "",
                })

        if not found:
            records.append({
                **base,
                "locator_status": "NO_LOCAL_TEXT_MATCH",
                "source_pdf": "",
                "source_relative_path": "",
                "source_pdf_sha256": "",
                "pdf_metadata_title": "",
                "pdf_page_number": "",
                "match_type": "",
                "source_excerpt": "",
                "context_before_and_after": "",
                "human_validation_status": "UNRESOLVED",
                "source_is_official": "NOT_ASSESSED",
                "version_and_currency_checked": "NOT_ASSESSED",
                "article_and_paragraph_checked": "NOT_ASSESSED",
                "reviewer_notes": (
                    "Check whether source is missing, image-only, OCR-required, "
                    "or text differs from the dataset excerpt."
                ),
            })

    queue = pd.DataFrame(records)
    queue_path = out_dir / "phase14_2_source_context_validation_queue.csv"
    queue.to_csv(queue_path, index=False)

    # Provision-level status summary.
    summary = (
        queue.groupby(["id", "country", "dataset_document"], dropna=False)
        .agg(
            candidate_source_rows=("locator_status", "size"),
            located_source_rows=(
                "locator_status",
                lambda s: int(s.eq("LOCATED_REQUIRES_HUMAN_VALIDATION").sum())
            ),
            locator_statuses=(
                "locator_status",
                lambda s: "; ".join(sorted(set(s)))
            ),
        )
        .reset_index()
    )
    summary_path = out_dir / "phase14_2_validation_queue_summary.csv"
    summary.to_csv(summary_path, index=False)

    located_ids = queue.loc[
        queue["locator_status"] == "LOCATED_REQUIRES_HUMAN_VALIDATION", "id"
    ].nunique()
    unresolved_ids = queue.loc[
        queue["locator_status"] != "LOCATED_REQUIRES_HUMAN_VALIDATION", "id"
    ].nunique()

    report = f"""# Phase 14.2 — Provision-Level Source Context and Validation Queue

## Purpose

This phase provides the text surrounding possible source matches and creates
a structured queue for human validation of each provision's primary-source
citation and quotation.

## Results

- Dataset provisions: **{len(df)}**
- Local PDFs successfully read: **{len(sources)}**
- Provision IDs with at least one located candidate: **{located_ids}**
- Provision IDs with no located candidate or no dataset excerpt: **{unresolved_ids}**
- Candidate source rows: **{len(queue)}**
- Automatically verified provisions: **0**
- Original dataset modified: **No**

## Main output

`results/phase14/source_validation/phase14_2_source_context_validation_queue.csv`

Each row includes:
- Dataset provision ID and recorded citation details.
- Candidate local PDF path, SHA-256 hash and PDF metadata title.
- Candidate page number and match type.
- Extracted source excerpt and surrounding page context.
- Explicit human-validation fields, initially left pending or not assessed.

## Validation procedure

For each candidate row, a researcher must compare the extracted passage with
the source PDF itself and verify:
1. The PDF is an official source from the competent issuing institution.
2. The instrument title, version, amendments and relevant date are correct.
3. The article, paragraph and page reference are accurate.
4. The quotation is verbatim and its surrounding context is not misleading.
5. Definitions, exceptions, qualifications and cross-references are considered.
6. The provision's legal status and commencement are confirmed from authoritative
   sources.

## Status meanings

- `LOCATED_REQUIRES_HUMAN_VALIDATION`: a possible text location was found.
- `NO_LOCAL_TEXT_MATCH`: no matching text was found in the local PDF corpus.
- `NO_EXACT_TEXT_TO_LOCATE`: the dataset row has no exact-text excerpt.
- `PENDING`: no human validation has yet been recorded.
- `NOT_ASSESSED`: the script has not determined whether the source is official
  or current.

No candidate match is labelled verified by this script.

## Limitations

The script searches extracted text from PDFs under `data/raw/`. It does not
perform OCR, authenticate source websites, retrieve newer versions, or provide
legal interpretation. Text matching may miss OCR differences, formatting
changes, amendments, or excerpts split across pages.

## Next step

Phase 14.3 should add official-source metadata and version checks, then support
a documented validation decision for each provision. Unresolved items should
remain explicitly unresolved until primary evidence is obtained.
"""
    report_path = report_dir / "Phase14_2_Source_Context_and_Validation_Queue.md"
    report_path.write_text(report, encoding="utf-8")

    print("\nPHASE 14.2 COMPLETED")
    print(f"Dataset provisions: {len(df)}")
    print(f"Readable local PDFs: {len(sources)}")
    print(f"Provision IDs with candidate matches: {located_ids}")
    print(f"Provision IDs without candidate matches: {unresolved_ids}")
    print(f"Validation queue: {queue_path}")
    print(f"Summary: {summary_path}")
    print(f"Report: {report_path}")
    print("No provision was automatically marked as legally verified.")
    print("Original annotated dataset and PDFs were not modified.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\nPHASE 14.2 FAILED: {exc}", file=sys.stderr)
        raise
