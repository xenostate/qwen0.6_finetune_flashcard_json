#!/usr/bin/env python3
"""Run deterministic evaluation for a local MLX-LM LoRA adapter."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import mlx.core as mx
from mlx_lm import load, stream_generate
from mlx_lm.sample_utils import make_sampler


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help="Local path or Hugging Face model ID")
    parser.add_argument("--adapter", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--system-prompt", type=Path, default=Path("prompts/system.txt"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--run-name", required=True)
    parser.add_argument("--max-tokens", type=int, default=1024)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    output_path = args.output_dir / "responses.jsonl"
    if output_path.exists() and not args.overwrite:
        raise SystemExit(f"Refusing to overwrite {output_path}; pass --overwrite")

    rows = read_jsonl(args.input)
    system_prompt = args.system_prompt.read_text()
    started = datetime.now(timezone.utc)
    model, tokenizer = load(args.model, adapter_path=str(args.adapter))
    sampler = make_sampler(temp=0.0, top_p=1.0, top_k=0, min_p=0.0)
    results = []

    for index, row in enumerate(rows, 1):
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": row["source"]},
        ]
        prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )
        mx.random.seed(args.seed)
        began = time.perf_counter()
        pieces = []
        final = None
        for response in stream_generate(
            model,
            tokenizer,
            prompt=prompt,
            max_tokens=args.max_tokens,
            sampler=sampler,
        ):
            pieces.append(response.text)
            final = response
        elapsed = time.perf_counter() - began
        result = {
            "id": row["id"],
            "source": row["source"],
            "response_text": "".join(pieces),
            "finish_reason": final.finish_reason if final else None,
            "completion_tokens": final.generation_tokens if final else None,
            "latency_seconds": round(elapsed, 6),
        }
        results.append(result)
        output_path.write_text(
            "".join(json.dumps(item, ensure_ascii=False) + "\n" for item in results)
        )
        print(f"[{index:02d}/{len(rows):02d}] {row['id']} {elapsed:.2f}s", flush=True)

    ended = datetime.now(timezone.utc)
    manifest = {
        "run_name": args.run_name,
        "status": "complete",
        "started_at_utc": started.isoformat(),
        "ended_at_utc": ended.isoformat(),
        "model": args.model,
        "adapter": str(args.adapter.resolve()),
        "input": str(args.input.resolve()),
        "input_sha256": sha256(args.input),
        "system_prompt_sha256": sha256(args.system_prompt),
        "generation": {
            "temperature": 0.0,
            "top_p": 1.0,
            "top_k": 0,
            "max_new_tokens": args.max_tokens,
            "seed": args.seed,
            "enable_thinking": False,
        },
        "versions": {
            "mlx": importlib.metadata.version("mlx"),
            "mlx_lm": importlib.metadata.version("mlx-lm"),
        },
        "record_count": len(results),
        "responses_sha256": sha256(output_path),
    }
    (args.output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

