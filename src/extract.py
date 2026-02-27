from __future__ import annotations

import json
import logging
import re
import sys
from datetime import datetime
from pathlib import Path

from pypdf import PdfReader


DATE_PATTERN = re.compile(r"^\d{2}/\d{2}/\d{4}$")
MONEY_PATTERN = re.compile(r"^-?£[\d,]+(?:\.\d{2})?$")


def parse_money(value: str) -> float:
    normalized = value.replace("£", "").replace(",", "").strip()
    return round(float(normalized), 2)


def to_iso_date(value: str) -> str:
    return datetime.strptime(value, "%d/%m/%Y").strftime("%Y-%m-%d")




def normalize_description(value: str) -> str:
    cleaned = " ".join(value.split())
    cleaned = re.sub(r"\b([A-Za-z])\s+([a-z]{2,})\b", r"\1\2", cleaned)
    return cleaned.strip()

def extract_transactions(statement_text: str) -> list[dict[str, object]]:
    lines = [line.strip() for line in statement_text.splitlines() if line.strip()]

    transactions: list[dict[str, object]] = []
    current_category: str | None = None
    i = 0

    while i < len(lines):
        line = lines[i]

        if line in {"Income", "Expenditure"}:
            current_category = line
            i += 1
            continue

        if DATE_PATTERN.match(line) and current_category:
            date_value = to_iso_date(line)
            i += 1

            description_parts: list[str] = []
            while i < len(lines) and not MONEY_PATTERN.match(lines[i]):
                if lines[i] in {"Subtotal", "Closing Balance", "Income", "Expenditure"}:
                    break
                description_parts.append(lines[i])
                i += 1

            if i + 2 >= len(lines):
                raise ValueError(
                    f"Incomplete monetary values for transaction on {date_value}. "
                    f"Remaining lines: {lines[i:i+5]}"
                )

            net = parse_money(lines[i])
            vat = parse_money(lines[i + 1])
            gross = parse_money(lines[i + 2])
            i += 3

            transactions.append(
                {
                    "date": date_value,
                    "description": normalize_description(" ".join(description_parts)),
                    "net": net,
                    "vat": vat,
                    "gross": gross,
                    "category": current_category,
                }
            )
            continue

        i += 1

    return transactions


def extract_statement(pdf_path: Path) -> dict[str, object]:
    reader = PdfReader(str(pdf_path))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)

    statement_text = text.split("\nInvoices\n", maxsplit=1)[0]

    property_match = re.search(r"Property:\s*(.+)", statement_text)
    if not property_match:
        raise ValueError(f"Property not found in statement: {pdf_path}")

    opening_match = re.search(r"Opening Balance\s*(-?£[\d,]+\.\d{2})", statement_text)
    if not opening_match:
        raise ValueError(f"Opening balance not found in statement: {pdf_path}")

    closing_match = re.search(r"Closing Balance\s*(-?£[\d,]+\.\d{2})", statement_text)
    if not closing_match:
        raise ValueError(f"Closing balance not found in statement: {pdf_path}")

    return {
        "property_name": property_match.group(1).strip(),
        "opening_balance": parse_money(opening_match.group(1)),
        "closing_balance": parse_money(closing_match.group(1)),
        "transactions": extract_transactions(statement_text),
    }


def main() -> int:
    logging.basicConfig(level=logging.ERROR)

    if len(sys.argv) != 2:
        print("Usage: python src/extract.py <statement.pdf>", file=sys.stderr)
        return 1

    pdf_path = Path(sys.argv[1])
    output_path = pdf_path.with_suffix(".json")

    try:
        payload = extract_statement(pdf_path)
        output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    except Exception:
        logging.exception("Failed to extract statement", extra={"pdf_path": str(pdf_path)})
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
