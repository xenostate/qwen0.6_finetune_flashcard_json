# Qwen3 0.6B flashcard QLoRA

This project teaches a small local language model to read a passage and return useful study flashcards as JSON. The model only uses the supplied passage and can return an empty list when there is nothing worth studying.

The repository contains the prepared data, training setup, evaluation scripts, and a short explanation of how the model was tested.

- [Model adapter on Hugging Face](https://huggingface.co/tenroman/qwen0.6_finetune_flashcard_json)
- [Source repository](https://github.com/xenostate/qwen0.6_finetune_flashcard_json)

## Results

The selected adapter was trained on 621 examples and chosen using a fixed 28-record validation set. It was then evaluated on a 35-record family-held-out set and a separate 20-record frozen regression set.

| Frozen-set metric | Prompted base model | Selected adapter |
|---|---:|---:|
| Strict raw JSON | 0/20 | **20/20** |
| Schema and exact source after removing one baseline Markdown fence | 14/20 | **20/20** |
| Correct empty/nonempty decision after the same normalization | 11/20 | **20/20** |

The base model wrapped every response in a Markdown code fence, which violated the output contract. The second and third rows remove only that fence to provide a fairer view of the underlying response.

Additional training rounds improved the selected checkpoint on the family-held-out evaluation:

| Family-held-out metric | Previous checkpoint | Selected checkpoint |
|---|---:|---:|
| Valid raw JSON | 34/35 | **35/35** |
| Schema and exact source | 33/35 | **35/35** |
| Correct empty/nonempty decision | 28/35 | **33/35** |
| Strict semantic passes | 5/35 | **10/35** |
| Reference concepts covered | 55/105 | **74/105** |

The family-held-out comparison is against the preceding fine-tuned checkpoint, while the frozen comparison above is against the untouched base model.

## Workflow

```mermaid
flowchart LR
    A[Curated synthetic examples] --> B[Family-grouped splits]
    B --> C[MLX QLoRA training]
    C --> D[Validation-loss selection]
    D --> E[Targeted behavioral evaluation]
    E --> F[Frozen regression check]
    F --> G[Structural and semantic audit]
```

## Training configuration

- Base model: `lmstudio-community/Qwen3-0.6B-MLX-4bit`
- Training method: LoRA on a 4-bit quantized base model
- Trainable parameters: 5.05M / 596.05M (`0.847%`)
- LoRA rank: `8`
- LoRA scale: `20`
- Learning rate: `1e-5`
- Batch size: `1`
- Maximum sequence length: `2048`
- Optimizer updates: `621` (one epoch)
- Prompt masking: enabled

## Repository structure

```text
configs/          Portable MLX-LM training and smoke-test configs
data/             Prepared train, validation, and evaluation JSONL
docs/             Evaluation notes, interview refresher, resume entry
model-card/       Hugging Face model card source
prompts/          Inference-time task prompt
results/          Compact machine-readable result summary
schemas/          Output JSON schema
scripts/          Data validation, deterministic evaluation, and scoring
```

The repository intentionally excludes data-generation prompts, rejected data, exploratory reports, intermediate adapters, and historical run logs.

## Reproduce the data checks

Python 3.12 and Apple Silicon are recommended.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/validate_data.py
```

Expected result:

```json
{
  "status": "pass",
  "records": {
    "train": 621,
    "valid": 28,
    "targeted": 35,
    "frozen": 20
  },
  "exact_source_overlap_across_splits": 0
}
```

## Train

Run the two-update smoke test first:

```bash
mlx_lm.lora --config configs/smoke.yaml
```

Then start the full one-epoch run:

```bash
mlx_lm.lora --config configs/train.yaml
```

The training configuration writes adapter checkpoints under `outputs/`, which is ignored by Git.

## Evaluate an adapter

```bash
python scripts/evaluate.py \
  --model lmstudio-community/Qwen3-0.6B-MLX-4bit \
  --adapter /path/to/adapter \
  --input data/evaluation/frozen.jsonl \
  --output-dir runs/frozen \
  --run-name frozen

python scripts/score.py \
  --gold data/evaluation/frozen.jsonl \
  --responses runs/frozen/responses.jsonl \
  --output runs/frozen/metrics.json
```

All published comparisons use temperature zero, seed 42, disabled thinking, and a 1,024-token generation limit.

## Evaluation design

Automated checks cover raw JSON parsing, schema validity, exact source copying, empty-case decisions, and card-count error. A manual concept-level audit checks grounding, coverage, conditions, exceptions, atomicity, and unsupported content.

See [docs/evaluation.md](docs/evaluation.md) for the concise protocol and [docs/interview_guide.md](docs/interview_guide.md) for an interview-ready explanation.

## Limitations

This adapter is an experimental small-model specialization. Dense passages with several interacting conditions remain difficult, so outputs should be reviewed before being used as authoritative study material. The datasets are synthetic and are intended for controlled model-development experiments.
