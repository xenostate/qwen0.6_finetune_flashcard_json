#!/usr/bin/env python3
"""Validate prepared chat data and evaluation-set isolation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    for line_number, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: {exc}") from exc
    return rows


def validate_cards(cards: object, label: str) -> None:
    if not isinstance(cards, list):
        raise ValueError(f"{label}: flashcards must be an array")
    for index, card in enumerate(cards):
        if not isinstance(card, dict) or set(card) != {"question", "answer"}:
            raise ValueError(f"{label}: invalid card {index}")
        if not all(isinstance(card[key], str) and card[key].strip() for key in card):
            raise ValueError(f"{label}: empty question or answer at card {index}")


def validate_training(path: Path, expected_system_prompt: str) -> tuple[list[dict], set[str]]:
    rows = read_jsonl(path)
    sources: set[str] = set()
    for index, row in enumerate(rows, 1):
        messages = row.get("messages")
        label = f"{path}:{index}"
        if not isinstance(messages, list) or len(messages) != 3:
            raise ValueError(f"{label}: expected exactly three messages")
        if [message.get("role") for message in messages] != ["system", "user", "assistant"]:
            raise ValueError(f"{label}: expected system/user/assistant roles")
        if messages[0].get("content") != expected_system_prompt:
            raise ValueError(f"{label}: system prompt does not match prompts/system.txt")
        source = messages[1].get("content")
        if not isinstance(source, str) or not source:
            raise ValueError(f"{label}: missing user source")
        try:
            target = json.loads(messages[2].get("content", ""))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{label}: assistant target is invalid JSON: {exc}") from exc
        if not isinstance(target, dict) or set(target) != {"source", "flashcards"}:
            raise ValueError(f"{label}: assistant target has the wrong schema")
        if target["source"] != source:
            raise ValueError(f"{label}: assistant source is not an exact copy")
        validate_cards(target["flashcards"], label)
        if source in sources:
            raise ValueError(f"{label}: duplicate source within split")
        sources.add(source)
    return rows, sources


def validate_evaluation(path: Path) -> tuple[list[dict], set[str]]:
    rows = read_jsonl(path)
    sources: set[str] = set()
    ids: set[str] = set()
    for index, row in enumerate(rows, 1):
        label = f"{path}:{index}"
        if set(row) != {"id", "source", "reference_flashcards"}:
            raise ValueError(f"{label}: unexpected evaluation keys")
        if not isinstance(row["id"], str) or row["id"] in ids:
            raise ValueError(f"{label}: missing or duplicate ID")
        if not isinstance(row["source"], str) or not row["source"]:
            raise ValueError(f"{label}: missing source")
        validate_cards(row["reference_flashcards"], label)
        if row["source"] in sources:
            raise ValueError(f"{label}: duplicate source within split")
        ids.add(row["id"])
        sources.add(row["source"])
    return rows, sources


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    system_prompt = (root / "prompts/system.txt").read_text()

    train, train_sources = validate_training(root / "data/training/train.jsonl", system_prompt)
    valid, valid_sources = validate_training(root / "data/training/valid.jsonl", system_prompt)
    targeted, targeted_sources = validate_evaluation(root / "data/evaluation/targeted.jsonl")
    frozen, frozen_sources = validate_evaluation(root / "data/evaluation/frozen.jsonl")

    splits = {
        "train": train_sources,
        "valid": valid_sources,
        "targeted": targeted_sources,
        "frozen": frozen_sources,
    }
    names = list(splits)
    for left_index, left in enumerate(names):
        for right in names[left_index + 1 :]:
            overlap = splits[left] & splits[right]
            if overlap:
                raise ValueError(f"source leakage between {left} and {right}: {len(overlap)}")

    result = {
        "status": "pass",
        "records": {
            "train": len(train),
            "valid": len(valid),
            "targeted": len(targeted),
            "frozen": len(frozen),
        },
        "exact_source_overlap_across_splits": 0,
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

