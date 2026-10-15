# Resume entry

## Local LLM fine-tuning and evaluation pipeline

**Python, MLX, QLoRA, Qwen3, JSON Schema**

- Fine-tuned a 4-bit Qwen3 0.6B model with MLX QLoRA using 621 curated examples, family-grouped leakage-safe splits, and validation-based checkpoint selection.
- Built a deterministic evaluation harness for JSON compliance, exact source retention, empty-case classification, card coverage, and semantic correctness.
- Improved family-held-out schema and source accuracy from **33/35 to 35/35**, empty/nonempty decisions from **28/35 to 33/35**, and audited concept coverage from **52.4% to 70.5%**.

### Short project description

Developed an end-to-end local LLM specialization workflow covering data curation, QLoRA training, checkpoint selection, regression testing, and semantic error analysis for grounded flashcard generation.
