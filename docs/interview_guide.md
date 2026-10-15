# Interview refresher

## Thirty-second explanation

I fine-tuned a quantized Qwen3 0.6B model to turn source passages into grounded flashcards with a strict JSON schema. I built the dataset, leakage-safe splits, MLX QLoRA training workflow, deterministic evaluation harness, and a manual semantic audit. On the frozen evaluation set, strict raw-JSON compliance improved from 0/20 for the prompted base model to 20/20 for the selected adapter.

## What problem was being solved?

The model had to return a JSON object containing the original passage and a set of concise flashcards. It had to copy the source exactly, avoid outside knowledge, preserve conditions and exceptions, ignore document noise, and return an empty array when the passage contained nothing useful to study.

This made the task useful for studying structured generation, grounding, coverage, and small-model reliability.

## Why use a 0.6B model?

The goal was to test how far a very small model could be specialized for one narrow task. It ran locally on Apple Silicon, trained quickly enough for repeated experiments, and made data quality and evaluation more important than raw model scale.

## Data and splitting

- Final accepted pool: **684 examples**
- Training: **621 examples**
- Validation: **28 examples**
- Family-held-out evaluation: **35 examples**
- Frozen regression set: **20 examples**

Synthetic examples were reviewed for source grounding, output schema, useful card coverage, and duplicates. Related five-record families were assigned as units so near-paraphrases could not cross between training and evaluation. Exact source overlap was checked across every split.

## Training setup

- Base model: 4-bit Qwen3 0.6B in MLX format
- Method: QLoRA/LoRA with the quantized base weights frozen
- Trainable parameters: **5.05M of 596.05M (0.847%)**
- LoRA rank: `8`
- LoRA scale: `20`
- Learning rate: `1e-5`
- Batch size: `1`
- Maximum sequence length: `2048`
- Prompt tokens masked from the loss
- One epoch, **621 optimizer updates**

The checkpoint was first selected using the unchanged validation set, then evaluated on held-out behavioral and regression sets.

## How evaluation worked

Automated checks measured raw JSON parsing, schema compliance, exact source copying, empty-case decisions, and card-count error. A separate semantic audit checked whether each intended concept was preserved, including thresholds, qualifications, and exceptions.

Generation was deterministic: temperature zero, fixed seed, disabled thinking, and the same system prompt for every model.

## Main result

Compared with the prompted base model on the frozen set, the selected adapter improved:

- Strict raw JSON: **0/20 → 20/20**
- Schema plus exact source after removing one baseline Markdown fence: **14/20 → 20/20**
- Correct empty/nonempty decisions after the same normalization: **11/20 → 20/20**

The base model fenced every response, so its official strict score was zero. The normalized figures show that fine-tuning also improved the response contents rather than only removing the fences.

Compared with the preceding fine-tuned checkpoint on the family-held-out set, it also improved:

- Schema plus exact-source success: **33/35 → 35/35**
- Correct empty/nonempty decisions: **28/35 → 33/35**
- Reference-concept coverage: **55/105 → 74/105**
- Strict semantic passes: **5/35 → 10/35**

These two comparisons answer different questions: baseline versus selected adapter measures the overall project gain, while the checkpoint comparison measures improvement from the final data iteration.

## What I learned

Validation loss was necessary but insufficient. Later experiments showed that a checkpoint could improve on a narrow targeted set while regressing on broader JSON escaping or semantic atomicity. I therefore kept the checkpoint that performed best across both the targeted and frozen gates.

Constrained decoding can guarantee the JSON envelope, but it cannot correct omitted concepts, reversed conditions, or unsupported facts. Those failures require better data, training, and semantic evaluation.

## Likely interview questions

### Why QLoRA instead of full fine-tuning?

It reduced memory use by keeping the quantized base model frozen and training only small low-rank matrices. This made repeated local experiments practical while still adapting the model strongly to the output format and task.

### Why group examples by family?

Random record-level splitting could place close paraphrases in both training and evaluation, inflating results. Grouping complete families made the behavioral evaluation more realistic.

### Why was exact source copying a metric?

The output contract required the original passage verbatim. Exact equality also catches subtle escaping, whitespace, and truncation failures that ordinary semantic similarity would miss.

### Why use manual semantic review?

A response can be valid JSON while still reversing a threshold or dropping an exception. Reference-concept review measured correctness that structural metrics could not see.

### What would you do next?

Add more diverse human-reviewed passages, increase representation of dense multi-condition examples, automate concept-level grading with a separately validated judge, and compare the 0.6B adapter with larger base models under the same evaluation protocol.
