# Resume entry

## Local LLM fine-tuning and evaluation pipeline

**Python, MLX, QLoRA, Qwen3, JSON Schema**

- Fine-tuned a 4-bit Qwen3 0.6B model with MLX QLoRA using 621 curated examples, family-grouped leakage-safe splits, and validation-based checkpoint selection.
- Built a deterministic evaluation harness for JSON compliance, exact source retention, empty-case classification, card coverage, and semantic correctness.
- Improved strict raw-JSON compliance from **0/20 to 20/20** versus the prompted base model; after removing the baseline's Markdown fences, improved schema and source accuracy from **14/20 to 20/20** and empty/nonempty decisions from **11/20 to 20/20**.

### Short project description

Developed an end-to-end local LLM specialization workflow covering data curation, QLoRA training, checkpoint selection, regression testing, and semantic error analysis for grounded flashcard generation.
