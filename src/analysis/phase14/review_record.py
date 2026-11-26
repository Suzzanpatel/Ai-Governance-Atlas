"""Merge the persistent Phase 14 review record into generated worksheets.

The Phase 14 scripts rebuild their worksheets on every run. Reviewer input is
therefore kept in one persistent, human-editable file:

    research/evidence/phase14_review_record.csv   (one row per provision id)

Before writing, each Phase 14 script calls `apply_review_record(frame)`. For
every column that exists in both files, the reviewer's value is copied in
where the generated value is blank or a placeholder such as PENDING or
NOT_ASSESSED. A generated value that already contains real content is never
replaced, and the record itself is never written by the pipeline.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
REVIEW_RECORD = ROOT / "research" / "evidence" / "phase14_review_record.csv"

PLACEHOLDERS = {
    "", "PENDING", "NOT_ASSESSED", "NOT_YET_REVIEWED", "NOT_RECORDED",
    "REQUIRES_RESEARCHER_COMPLETION", "PENDING_HUMAN_COMPLETION", "PENDING_HUMAN_ANALYSIS",
    "PENDING_SOURCE_REVIEW", "NOT_CHECKED", "NOT_CONFIRMED_IN_REGISTER", "UNSPECIFIED",
    "INCOMPLETE", "LEGAL_ANALYSIS_INCOMPLETE", "UNRESOLVED", "NAN", "NONE",
}


def _is_placeholder(value) -> bool:
    return str(value if value is not None else "").strip().upper() in PLACEHOLDERS


def load_review_record() -> pd.DataFrame | None:
    if not REVIEW_RECORD.is_file():
        return None
    record = pd.read_csv(REVIEW_RECORD, dtype=str, keep_default_na=False)
    if "id" not in record.columns:
        raise ValueError(f"{REVIEW_RECORD} must have an 'id' column")
    if record["id"].duplicated().any():
        raise ValueError(f"Duplicate ids in {REVIEW_RECORD}")
    return record.set_index("id")


def apply_review_record(frame: pd.DataFrame, id_column: str = "id") -> pd.DataFrame:
    """Return a copy of `frame` with reviewer values merged in by provision id."""
    record = load_review_record()
    if record is None or frame.empty or id_column not in frame.columns:
        return frame
    shared = [c for c in record.columns if c in frame.columns and c != id_column]
    if not shared:
        return frame
    out = frame.copy()
    for col in shared:
        out[col] = out[col].astype(object)
    for idx, pid in out[id_column].items():
        pid = str(pid).strip()
        if pid not in record.index:
            continue
        for col in shared:
            reviewed = record.at[pid, col]
            if str(reviewed).strip() and _is_placeholder(out.at[idx, col]):
                out.at[idx, col] = reviewed
    return out


def apply_review_record_rows(rows: list[dict], id_column: str = "id") -> list[dict]:
    """Same as apply_review_record, for scripts that write lists of dicts."""
    if not rows:
        return rows
    merged = apply_review_record(pd.DataFrame(rows).fillna(""), id_column)
    return merged.to_dict("records")
