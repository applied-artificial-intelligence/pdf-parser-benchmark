"""Blind, deterministic extraction for the declared controlled invoice task.

This file runs by itself with only the standard library and parser-output bytes.
"""

import argparse
import json
import re
import unicodedata
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

ALIASES = {
    "description": "description",
    "quantity": "quantity",
    "qty": "quantity",
    "unit": "unit",
    "unit price": "unit_price",
    "rate": "unit_price",
    "amount": "line_total",
}
REQUIRED_FIELDS = ("invoice_number", "vendor", "due_date", "grand_total", "currency_marker")
MONTHS = (
    "January February March April May June July August September October November December".split()
)
NUMBER = r"[+-]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?"
MONEY = rf"(?:[$€£][+-]?{NUMBER}|[+-]?[$€£]{NUMBER}|\([$€£]{NUMBER}\))"


def text_value(value: str) -> str:
    value = re.sub(r"<br\s*/?>", " ", value, flags=re.IGNORECASE)
    value = value.replace("**", "").replace("__", "")
    return " ".join(unicodedata.normalize("NFKC", value).split())


def number_value(value: str) -> tuple[str, str | None]:
    value = text_value(value)
    marker = next((c for c in value if c in "$€£"), None)
    negative = value.startswith("(") and value.endswith(")")
    raw = value.strip("()")
    for symbol in "$€£":
        raw = raw.replace(symbol, "")
    if not re.fullmatch(NUMBER, raw):
        raise ValueError("Unsupported numeric surface")
    number = Decimal(raw.replace(",", ""))
    if negative:
        number = number.copy_negate()
    result = format(number, "f")
    return (result.rstrip("0").rstrip(".") if "." in result else result), marker


def date_value(value: str) -> str:
    value = text_value(value)
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return date.fromisoformat(value).isoformat()
    if re.fullmatch(r"\d{2}/\d{2}/\d{4}", value):
        month, day, year = map(int, value.split("/"))
    else:
        match = re.fullmatch(r"([A-Za-z]+) (\d{1,2}), (\d{4})", value)
        if not match or match[1] not in MONTHS:
            raise ValueError("Unsupported or ambiguous date representation")
        month, day, year = MONTHS.index(match[1]) + 1, int(match[2]), int(match[3])
    return date(year, month, day).isoformat()


def header_roles(cells: list[str]) -> list[str] | None:
    names = [text_value(c).casefold() for c in cells]
    if not names or any(n not in ALIASES for n in names):
        return None
    roles = [ALIASES[n] for n in names]
    return roles if "description" in roles and len(set(roles)) == len(roles) else None


def record_values(cells: list[str], roles: list[str]) -> dict:
    if len(cells) != len(roles):
        return {"invalid_cells": cells}
    values, currencies = {}, {}
    try:
        for role, raw in zip(roles, cells, strict=True):
            if role in {"quantity", "unit_price", "line_total"}:
                values[role], marker = number_value(raw)
                if role != "quantity":
                    currencies[role] = marker
                elif marker is not None:
                    raise ValueError("Currency in quantity cell")
            else:
                values[role] = text_value(raw)
        if not values["description"]:
            raise ValueError("Empty description")
        return {
            **values,
            "currency_markers": currencies,
            "surfaces": dict(zip(roles, cells, strict=True)),
        }
    except ValueError:
        return {"invalid_cells": cells}


def markdown_rows(text: str) -> tuple[list[dict], bool]:
    rows: list[dict] = []
    roles: list[str] | None = None
    pending = ""
    found = False
    for line in text.splitlines():
        stripped = line.strip()
        if not pending and not stripped.startswith("|"):
            continue
        pending += ("\n" if pending else "") + stripped
        if not stripped.endswith("|"):
            continue
        cells = [c.strip() for c in pending.strip().strip("|").split("|")]
        pending = ""
        if all(re.fullmatch(r":?-+:?", c.replace(" ", "")) for c in cells):
            continue
        headers = header_roles(cells)
        if headers is not None:
            roles, found = headers, True
            continue
        names = [text_value(c).casefold() for c in cells]
        if "description" in names and any(n in ALIASES for n in names if n != "description"):
            return [{"invalid_cells": cells, "reason": "ambiguous_line_item_headers"}], True
        if roles is None or len(cells) != len(roles):
            continue
        description_index = roles.index("description")
        if (
            rows
            and cells[description_index]
            and all(not c for i, c in enumerate(cells) if i != description_index)
        ):
            previous = rows[-1]
            if "description" in previous:
                previous["surfaces"]["description"] += "\n" + cells[description_index]
                previous["description"] = text_value(previous["surfaces"]["description"])
            continue
        rows.append(record_values(cells, roles))
    if pending and roles is not None:
        rows.append({"invalid_cells": [pending]})
    return rows, found


def plain_rows(text: str) -> list[dict]:
    rows: list[dict] = []
    roles: list[str] | None = None
    description: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        names = re.findall(r"Unit Price|Description|Quantity|Qty|Unit|Rate|Amount", line)
        if names and text_value(" ".join(names)) == text_value(line):
            roles = header_roles(names)
            description = []
            continue
        if roles is None:
            continue
        if re.match(r"(?i)^(subtotal|total|tax|payment terms|notes|[A-Z]{2} sales tax)\s*:", line):
            break
        if len(roles) == 5:
            pattern = rf"^(.*?)\s*({NUMBER})\s+(.+?)\s+({MONEY})\s+({MONEY})$"
        elif len(roles) == 4:
            pattern = rf"^(.*?)\s*({NUMBER})\s+({MONEY})\s+({MONEY})$"
        elif len(roles) == 3:
            pattern = rf"^(.*?)\s*({NUMBER})\s+({MONEY})$"
        else:
            return [{"invalid_cells": ["Unsupported plain column count"]}]
        match = re.fullmatch(pattern, line)
        if match:
            cells = list(match.groups())
            cells[0] = "\n".join([*description, cells[0]]).strip()
            rows.append(record_values(cells, roles))
            description = []
        else:
            description.append(line)
    if description:
        rows.append({"invalid_cells": description})
    return rows


def extract_invoice(text: str) -> dict:
    """Use only text, with no document identity, paths, reference facts or row counts."""
    value: Any
    fields = dict.fromkeys(REQUIRED_FIELDS)
    surfaces: dict[str, list[str]] = {}
    ambiguities = []
    clean = "\n".join(line.replace("|", " ").replace("**", "") for line in text.splitlines())
    patterns = {
        "invoice_number": r"Invoice\s*(?:#|Number)\s*:\s*([^\s|]+)",
        "due_date": (
            r"(?:Due Date|Payment Due|Due)\s*:\s*"
            r"(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|[A-Za-z]+ \d{1,2}, \d{4})"
        ),
        "grand_total": rf"(?m)^\s*TOTAL\s*:\s*({MONEY})\s*$",
    }
    for key, pattern in patterns.items():
        values = set()
        surfaces[key] = []
        for match in re.finditer(pattern, clean, re.IGNORECASE):
            try:
                raw = match[1]
                surfaces[key].append(raw)
                value = (
                    date_value(raw)
                    if key == "due_date"
                    else number_value(raw)
                    if key == "grand_total"
                    else text_value(raw)
                )
                values.add(value)
            except ValueError:
                ambiguities.append(key)
        if len(values) == 1:
            value = next(iter(values))
            if key == "grand_total":
                fields[key], fields["currency_marker"] = value
            else:
                fields[key] = value
        elif len(values) > 1:
            ambiguities.append(key)
    lines = [text_value(line) for line in text.splitlines() if line.strip()]
    candidates = []
    for i, line in enumerate(lines[:-1]):
        if line.casefold() == "invoice":
            following = lines[i + 1]
            if following.casefold() == "from:":
                if i + 2 < len(lines):
                    candidates.append(lines[i + 2])
            elif following.casefold().startswith("from:"):
                ambiguities.append("vendor: merged FROM/TO columns")
            else:
                candidates.append(re.split(r"(?i)\s+Invoice\s*(?:#|Number)\s*:", following)[0])
    vendors = {text_value(v) for v in candidates}
    surfaces["vendor"] = candidates
    if len(vendors) == 1:
        fields["vendor"] = next(iter(vendors))
    elif len(vendors) > 1:
        ambiguities.append("vendor")
    records, structured = markdown_rows(text)
    if not structured:
        records = plain_rows(text)
    return {
        "schema_version": 1,
        "fields": fields,
        "field_surfaces": surfaces,
        "records": records,
        "ambiguities": sorted(set(ambiguities)),
        "representation": "markdown_tables" if structured else "plain_linear_rows",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    prediction = extract_invoice(args.input.read_text(encoding="utf-8"))
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(prediction, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write("\n")


if __name__ == "__main__":
    main()
