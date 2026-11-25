"""
Phase 14.1 — Primary Source Inventory and Provision Locator
AI Governance Atlas

Scans local PDF files under data/raw/, inventories them, extracts page text,
and attempts to locate each provision's exact_text in the local PDFs.

This is a source-discovery aid, not legal verification. A text match does not
prove that the quotation is current, complete, legally operative, or correctly
interpreted. No dataset or source PDF is modified.

Run from project root:
    python src/analysis/phase14/phase14_1_primary_source_locator.py

Requires PyMuPDF:
    python -m pip install pymupdf
"""

from pathlib import Path
import re
import sys
import hashlib
import pandas as pd

try:
    import fitz  # PyMuPDF
except ImportError as exc:
    raise SystemExit(
        "PyMuPDF is required. Install it with: python -m pip install pymupdf"
    ) from exc


def locate_root() -> Path:
    here = Path(__file__).resolve()
    for candidate in [here.parent, *here.parents]:
        if (candidate / "data/annotated/governance_dataset.csv").is_file():
            return candidate
    raise FileNotFoundError(
        "Cannot find data/annotated/governance_dataset.csv. "
        "Run this script from the project root."
    )


def normalise(value: str) -> str:
    value = str(value or "").casefold()
    value = value.replace("\u00ad", "")
    value = re.sub(r"[\u2010-\u2015]", "-", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def short_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def extract_pdf(path: Path):
    pages = []
    try:
        with fitz.open(path) as document:
            metadata = document.metadata or {}
            for index, page in enumerate(document):
                pages.append({
                    "page_number": index + 1,
                    "text": page.get_text("text") or "",
                })
            return {
                "ok": True,
                "pages": pages,
                "page_count": len(document),
                "title": metadata.get("title") or "",
                "author": metadata.get("author") or "",
                "error": "",
            }
    except Exception as exc:
        return {
            "ok": False,
            "pages": [],
            "page_count": 0,
            "title": "",
            "author": "",
            "error": str(exc),
        }


def find_quote_on_page(quote: str, page_text: str):
    q = normalise(quote)
    t = normalise(page_text)
    if len(q) < 35 or len(t) < 35:
        return None
    if q in t:
        start = t.find(q)
        return {
            "match_type": "normalised_exact_text_match",
            "matched_chars": len(q),
            "quote_length": len(q),
            "position": start,
        }

    # A shorter leading excerpt is only a locator hint, not confirmation.
    excerpt = q[:140].strip()
    if len(excerpt) >= 80 and excerpt in t:
        return {
            "match_type": "leading_excerpt_match",
            "matched_chars": len(excerpt),
            "quote_length": len(q),
            "position": t.find(excerpt),
        }
    return None


def main():
    root = locate_root()
    dataset_path = root / "data/annotated/governance_dataset.csv"
    raw_dir = root / "data/raw"
    output_dir = root / "results/phase14/source_validation"
    reports_dir = root / "results/phase14/reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    if not raw_dir.exists():
        raise FileNotFoundError(f"Raw source folder not found: {raw_dir}")

    df = pd.read_csv(dataset_path, dtype=str).fillna("")
    required = ["id", "country", "document", "exact_text"]
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")
    if df.empty:
        raise ValueError("Annotated dataset is empty.")
    if df["id"].duplicated().any():
        raise ValueError("Duplicate provision IDs detected.")

    pdf_paths = sorted(path for path in raw_dir.rglob("*")
                       if path.is_file() and path.suffix.lower() == ".pdf")

    inventory_rows = []
    extracted_sources = []
    for pdf_path in pdf_paths:
        extracted = extract_pdf(pdf_path)
        relative_path = str(pdf_path.relative_to(root))
        inventory_rows.append({
            "file_name": pdf_path.name,
            "relative_path": relative_path,
            "file_size_bytes": pdf_path.stat().st_size,
            "sha256": short_hash(pdf_path),
            "pdf_readable": extracted["ok"],
            "page_count": extracted["page_count"],
            "pdf_metadata_title": extracted["title"],
            "pdf_metadata_author": extracted["author"],
            "extraction_error": extracted["error"],
        })
        if extracted["ok"]:
            extracted_sources.append({
                "path": relative_path,
                "name": pdf_path.name,
                "pages": extracted["pages"],
                "page_count": extracted["page_count"],
                "title": extracted["title"],
            })

    inventory_path = output_dir / "phase14_1_local_pdf_source_inventory.csv"
    pd.DataFrame(inventory_rows).to_csv(inventory_path, index=False)

    # Try to locate each provision's recorded exact_text across all local PDFs.
    match_rows = []
    for _, row in df.iterrows():
        quote = row["exact_text"].strip()
        base = {
            "id": row["id"],
            "country": row["country"],
            "dataset_document": row["document"],
            "quote_available": bool(quote),
        }
        if not quote:
            match_rows.append({
                **base,
                "match_status": "NO_EXACT_TEXT_IN_DATASET",
                "source_pdf": "",
                "source_relative_path": "",
                "pdf_page_number": "",
                "match_type": "",
                "matched_chars": "",
                "quote_length": "",
            })
            continue

        matches = []
        for source in extracted_sources:
            for page in source["pages"]:
                result = find_quote_on_page(quote, page["text"])
                if result:
                    matches.append({
                        **base,
                        "match_status": "LOCATOR_MATCH_REQUIRES_HUMAN_CHECK",
                        "source_pdf": source["name"],
                        "source_relative_path": source["path"],
                        "pdf_page_number": page["page_number"],
                        "match_type": result["match_type"],
                        "matched_chars": result["matched_chars"],
                        "quote_length": result["quote_length"],
                    })

        if matches:
            match_rows.extend(matches)
        else:
            match_rows.append({
                **base,
                "match_status": "NO_LOCAL_TEXT_MATCH",
                "source_pdf": "",
                "source_relative_path": "",
                "pdf_page_number": "",
                "match_type": "",
                "matched_chars": "",
                "quote_length": len(normalise(quote)),
            })

    matches_df = pd.DataFrame(match_rows)
    matches_path = output_dir / "phase14_1_provision_source_locator_results.csv"
    matches_df.to_csv(matches_path, index=False)

    # Summarise locator outcomes by provision; a provision may match multiple PDFs.
    if not matches_df.empty:
        per_provision = (
            matches_df.groupby(
                ["id", "country", "dataset_document"], dropna=False
            )
            .agg(
                locator_rows=("match_status", "size"),
                matched_source_pages=(
                    "pdf_page_number",
                    lambda values: int(values.astype(str).str.strip().ne("").sum())
                ),
                locator_statuses=(
                    "match_status",
                    lambda values: "; ".join(sorted(set(values)))
                ),
            )
            .reset_index()
        )
    else:
        per_provision = pd.DataFrame()
    per_provision.to_csv(
        output_dir / "phase14_1_provision_locator_summary.csv", index=False
    )

    readable = sum(1 for item in inventory_rows if item["pdf_readable"])
    matched_ids = (
        matches_df.loc[
            matches_df["match_status"] == "LOCATOR_MATCH_REQUIRES_HUMAN_CHECK",
            "id"
        ].nunique()
        if not matches_df.empty else 0
    )
    no_match_ids = (
        matches_df.loc[
            matches_df["match_status"] == "NO_LOCAL_TEXT_MATCH", "id"
        ].nunique()
        if not matches_df.empty else 0
    )

    report = f"""# Phase 14.1 — Primary Source Inventory and Provision Locator

## Purpose

This phase inventories local PDF sources and attempts to locate the dataset's
recorded exact-text excerpts within those PDFs. It creates a traceable starting
point for primary-source validation.

## Scope

- Dataset provisions: **{len(df)}**
- Local PDF files found under `data/raw/`: **{len(pdf_paths)}**
- PDFs successfully read: **{readable}**
- Provision IDs with at least one text locator match: **{matched_ids}**
- Provision IDs with no local text match: **{no_match_ids}**
- Original annotated dataset modified: **No**
- Source PDFs modified: **No**

## Outputs

- `phase14_1_local_pdf_source_inventory.csv`: file paths, file sizes, SHA-256
  hashes, PDF metadata, page counts and extraction status.
- `phase14_1_provision_source_locator_results.csv`: possible page locations
  for each dataset excerpt.
- `phase14_1_provision_locator_summary.csv`: provision-level summary.

## How to interpret locator results

- `normalised_exact_text_match` means the recorded excerpt was found after
  normalising whitespace, case and selected hyphen characters.
- `leading_excerpt_match` means only the first part of a long excerpt was found.
- `LOCATOR_MATCH_REQUIRES_HUMAN_CHECK` is a page-location lead, not a verified
  quotation or legal conclusion.
- `NO_LOCAL_TEXT_MATCH` means no matching text was found in the PDFs scanned.
  The source may be absent, scanned as an image, OCR-incompatible, differently
  worded, or stored outside `data/raw/`.
- A PDF's metadata title is not authoritative proof of its legal status,
  version, commencement, or currency.

## Required human/source validation

For every proposed source match, compare the dataset excerpt against the actual
PDF page and check:
1. The instrument's official title and issuing institution.
2. Version, amendment and consolidation date.
3. Article, section, paragraph and page.
4. Whether the excerpt is verbatim and complete enough for its stated use.
5. Whether surrounding text, exceptions, definitions or cross-references
   change the meaning.
6. Whether the provision was in force at the relevant date.

## Limitations

This script only scans local text-based PDF content. It does not perform OCR,
web retrieval, source authentication, legal interpretation, or independent
verification. A match does not prove that the PDF is an official or current
version. A non-match does not prove that the citation is wrong.

## Next step

Phase 14.2 should validate the located passages against official source
versions, capture surrounding context, and create a provision-by-provision
validation record with explicit verified, discrepancy, and unresolved states.
"""
    report_path = reports_dir / "Phase14_1_Primary_Source_Inventory_and_Locator.md"
    report_path.write_text(report, encoding="utf-8")

    print("\nPHASE 14.1 COMPLETED")
    print(f"Dataset provisions: {len(df)}")
    print(f"Local PDFs found: {len(pdf_paths)}")
    print(f"Readable PDFs: {readable}")
    print(f"Provision IDs with locator matches: {matched_ids}")
    print(f"Provision IDs with no local text match: {no_match_ids}")
    print(f"Source inventory: {inventory_path}")
    print(f"Locator results: {matches_path}")
    print(f"Report: {report_path}")
    print("No source files or annotated dataset rows were modified.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\nPHASE 14.1 FAILED: {exc}", file=sys.stderr)
        raise
