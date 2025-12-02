from __future__ import annotations
from fastapi import UploadFile
from typing import List, Dict, Any
from docx import Document
from io import BytesIO
import difflib

async def extract_lines(upload:UploadFile) -> list[str]:
    raw = await upload.read()
    filename = (upload.filename)

    if filename.endswith(".docx"):
        doc = Document(BytesIO(raw))
        return [p.text for p in doc.paragraphs]
    else:
        return raw.decode("utf-8", errors="replace").splitlines()

def _char_spans(old: str, new: str) -> tuple[list[dict[str, int]], list[dict[str, int]]]:
    """Char spans of differences within a single line."""
    sm = difflib.SequenceMatcher(a=old, b=new)
    a_spans: list[dict[str, int]] = []
    b_spans: list[dict[str, int]] = []

    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        if i1 != i2:
            a_spans.append({"start": i1, "end": i2})
        if j1 != j2:
            b_spans.append({"start": j1, "end": j2})

    return a_spans, b_spans


def build_chunks(lines_a: List[str], lines_b: List[str]) -> List[Dict[str, Any]]:
    """
    Simple line-based diff:
    - one chunk per changed line or inserted/deleted line
    - char-level spans for changed lines
    """
    chunks: List[Dict[str, Any]] = []
    max_len = max(len(lines_a), len(lines_b))

    for i in range(max_len):
        a = lines_a[i] if i < len(lines_a) else None
        b = lines_b[i] if i < len(lines_b) else None

        # both missing – shouldn't happen
        if a is None and b is None:
            continue

        # equal line → skip
        if a is not None and b is not None and a == b:
            continue

        # insert (only in B)
        if a is None and b is not None:
            chunks.append(
                {
                    "tag": "insert",
                    "line_a": None,
                    "line_b": i,
                    "a_text": None,
                    "b_text": b,
                    "a_spans": [],
                    "b_spans": [{"start": 0, "end": len(b)}],
                }
            )
            continue

        # delete (only in A)
        if a is not None and b is None:
            chunks.append(
                {
                    "tag": "delete",
                    "line_a": i,
                    "line_b": None,
                    "a_text": a,
                    "b_text": None,
                    "a_spans": [{"start": 0, "end": len(a)}],
                    "b_spans": [],
                }
            )
            continue

        # replace (both exist, different)
        a_spans, b_spans = _char_spans(a, b)
        chunks.append(
            {
                "tag": "replace",
                "line_a": i,
                "line_b": i,
                "a_text": a,
                "b_text": b,
                "a_spans": a_spans,
                "b_spans": b_spans,
            }
        )

    return chunks