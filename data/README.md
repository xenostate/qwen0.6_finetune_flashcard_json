# Data

The repository contains the exact prepared data used for the selected run:

| File | Records | Purpose |
|---|---:|---|
| `training/train.jsonl` | 621 | QLoRA training |
| `training/valid.jsonl` | 28 | Checkpoint selection by validation loss |
| `evaluation/targeted.jsonl` | 35 | Family-held-out behavioral evaluation |
| `evaluation/frozen.jsonl` | 20 | Fixed regression evaluation |

Training records use the MLX-LM chat format. Evaluation records contain an ID, the source passage, and reference flashcards.

The targeted split was grouped by five-record structural families so paraphrased members of one family could not cross between training and evaluation. Exact source overlap was also checked across all splits.

All passages and flashcards in this repository are synthetic. No private or user-supplied text is included.
