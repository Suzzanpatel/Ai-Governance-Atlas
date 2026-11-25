"""Extract page-level text from the primary-source PDFs.

Each framework is read from exactly ONE PDF, listed in SOURCES below. This keeps
the computational corpus aligned with the version used for manual coding in
data/annotated/governance_dataset.csv, and stops a second copy of an
instrument (for example the original and the consolidated EU AI Act) from
being counted twice.

Folder and file names are matched ignoring case and whitespace variants, so the script behaves the
same on macOS, Windows and Linux.

Output: data/processed/extracted_documents.csv (country, document, page, text)
"""

import re
import unicodedata
from pathlib import Path

import pandas as pd

try:
    import pymupdf
except ImportError:  # PyMuPDF < 1.24 only provides the legacy name
    import fitz as pymupdf

PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_DIR / "data" / "raw"
OUTPUT_DIR = PROJECT_DIR / "data" / "processed"

# country label -> (folder under data/raw, PDF file name)
# The EU entry uses the consolidated text of 27 July 2026 (as amended by
# Regulation (EU) 2026/1744), which is the version cited in the coded dataset.
# To reproduce the earlier keyword results, switch it to
# "EU_AI_Act_Official_Journal_2024.pdf".
SOURCES = {
    "india": ("india", "India Al Governance Guidelines 5 Nov 2025.pdf"),
    "eu": ("eu", "EU_AI_Act_Consolidated_2026-07-27.pdf"),
    "uk": ("uk", "a-pro-innovation-approach-to-ai-regulation-amended-web-ready.pdf"),
    "oecd": ("oecd", "OECD-LEGAL-0449-en.pdf"),
}


def _normalise(name: str) -> str:
    """Lower-case, Unicode-normalise and collapse whitespace.

    Some downloaded file names contain non-breaking spaces (for example the
    India Guidelines PDF), which would otherwise not match an ordinary space.
    """
    name = unicodedata.normalize("NFKC", name)
    return re.sub(r"\s+", " ", name).strip().lower()


def find_case_insensitive(parent: Path, name: str) -> Path:
    """Return the child of `parent` whose name matches `name`.

    Matching ignores letter case and differences in whitespace characters.
    """
    if not parent.is_dir():
        raise FileNotFoundError(f"Folder not found: {parent}")
    for child in parent.iterdir():
        if _normalise(child.name) == _normalise(name):
            return child
    raise FileNotFoundError(f"'{name}' not found in {parent}")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    used = set()

    for country, (folder_name, file_name) in SOURCES.items():
        folder = find_case_insensitive(RAW_DIR, folder_name)
        pdf_file = find_case_insensitive(folder, file_name)
        used.add(pdf_file.resolve())
        print(f"Reading [{country}]: {pdf_file.relative_to(PROJECT_DIR)}")

        with pymupdf.open(pdf_file) as document:
            for page_number, page in enumerate(document, start=1):
                text = page.get_text("text")
                if text.strip():
                    rows.append({
                        "country": country,
                        "document": pdf_file.name,
                        "page": page_number,
                        "text": text,
                    })

    skipped = sorted(
        p.relative_to(PROJECT_DIR)
        for p in RAW_DIR.rglob("*")
        if p.suffix.lower() == ".pdf" and p.resolve() not in used
    )
    for path in skipped:
        print(f"Not in corpus (reference copy only): {path}")

    df = pd.DataFrame(rows, columns=["country", "document", "page", "text"])
    output_file = OUTPUT_DIR / "extracted_documents.csv"
    df.to_csv(output_file, index=False)

    print("\nExtraction completed!")
    print("Pages extracted by framework:")
    print(df.groupby("country").size().to_string())
    print("Total pages extracted:", len(df))
    print("Saved to:", output_file)


if __name__ == "__main__":
    main()
