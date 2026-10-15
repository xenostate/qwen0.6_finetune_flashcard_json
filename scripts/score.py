#!/usr/bin/env python3
"""Score strict JSON, schema, source-copy, empty-case, and card-count metrics."""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def inspect(parsed: object, source: str) -> tuple[bool, bool, list[dict] | None]:
    root_ok = isinstance(parsed, dict) and set(parsed) == {"source", "flashcards"}
    source_exact = bool(root_ok and parsed.get("source") == source)
    cards = parsed.get("flashcards") if root_ok else None
    cards_ok = isinstance(cards, list) and all(
        isinstance(card, dict)
        and set(card) == {"question", "answer"}
        and isinstance(card["question"], str)
        and bool(card["question"].strip())
        and isinstance(card["answer"], str)
        and bool(card["answer"].strip())
        for card in cards
    )
    return bool(root_ok and source_exact and cards_ok), source_exact, cards if cards_ok else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gold", type=Path, required=True)
    parser.add_argument("--responses", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    gold_rows = read_jsonl(args.gold)
    responses = {row["id"]: row for row in read_jsonl(args.responses)}
    details = []
    for gold in gold_rows:
        response = responses.get(gold["id"], {})
        raw = response.get("response_text", "")
        try:
            parsed = json.loads(raw)
            parse_error = None
        except Exception as exc:
            parsed = None
            parse_error = f"{type(exc).__name__}: {exc}"
        schema_ok, source_exact, cards = inspect(parsed, gold["source"])
        reference_count = len(gold["reference_flashcards"])
        generated_count = len(cards) if cards is not None else None
        expected_empty = reference_count == 0
        details.append(
            {
                "id": gold["id"],
                "raw_json_parse": parsed is not None,
                "parse_error": parse_error,
                "schema_success": schema_ok,
                "exact_source_copy": source_exact,
                "expected_empty": expected_empty,
                "empty_decision_correct": bool(
                    schema_ok and (generated_count == 0) == expected_empty
                ),
                "reference_card_count": reference_count,
                "generated_card_count": generated_count,
                "card_count_absolute_error": (
                    abs(generated_count - reference_count)
                    if generated_count is not None
                    else None
                ),
            }
        )

    count = len(details)
    card_errors = [
        row["card_count_absolute_error"]
        for row in details
        if row["card_count_absolute_error"] is not None
    ]
    metrics = {
        "record_count": count,
        "raw_json_parse_success": sum(row["raw_json_parse"] for row in details),
        "schema_success": sum(row["schema_success"] for row in details),
        "exact_source_copy": sum(row["exact_source_copy"] for row in details),
        "correct_empty_nonempty_decision": sum(
            row["empty_decision_correct"] for row in details
        ),
        "mean_card_count_absolute_error_on_valid_outputs": (
            statistics.mean(card_errors) if card_errors else None
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps({"metrics": metrics, "details": details}, indent=2) + "\n"
    )
    print(json.dumps(metrics, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
