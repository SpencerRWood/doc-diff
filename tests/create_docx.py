#!/usr/bin/env python3
import argparse
from pathlib import Path
from docx import Document


def txt_to_docx(input_path: Path, output_path: Path):
    text = input_path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    doc = Document()
    for line in lines:
        doc.add_paragraph(line)

    doc.save(output_path)
    print(f"Saved DOCX: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Convert a .txt file into a .docx file."
    )
    parser.add_argument("input", type=Path, help="Path to input .txt file")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Optional output .docx file path",
    )

    args = parser.parse_args()

    if args.output:
        output_path = args.output
    else:
        output_path = args.input.with_suffix(".docx")

    txt_to_docx(args.input, output_path)


if __name__ == "__main__":
    main()
