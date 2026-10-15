---
base_model: lmstudio-community/Qwen3-0.6B-MLX-4bit
library_name: mlx
tags:
  - mlx
  - lora
  - qwen3
  - structured-output
  - flashcards
---

# Qwen3 0.6B Flashcard QLoRA

This is an MLX LoRA adapter for converting one supplied source passage into grounded study flashcards represented as strict JSON.

## Base model

`lmstudio-community/Qwen3-0.6B-MLX-4bit`

The adapter requires the matching 4-bit MLX base model.

## Intended use

The model accepts one passage and returns:

```json
{
  "source": "exact source passage",
  "flashcards": [
    {
      "question": "...",
      "answer": "..."
    }
  ]
}
```

The system prompt is included in the accompanying GitHub repository. Thinking mode should be disabled, and deterministic generation is recommended for evaluation.

## Training

- 621 training examples
- 28 validation examples
- MLX-LM 0.32.0
- LoRA rank 8, scale 20
- Learning rate `1e-5`
- Batch size 1
- Maximum sequence length 2,048
- One epoch / 621 optimizer updates
- 5.05M trainable parameters out of 596.05M (`0.847%`)

Training examples were grouped by structural family before splitting to reduce near-duplicate leakage.

## Evaluation

| Family-held-out metric | Previous checkpoint | This adapter |
|---|---:|---:|
| Valid raw JSON | 34/35 | **35/35** |
| Schema and exact source | 33/35 | **35/35** |
| Correct empty/nonempty decision | 28/35 | **33/35** |
| Strict semantic passes | 5/35 | **10/35** |
| Reference concepts covered | 55/105 | **74/105** |

The adapter also achieved 20/20 valid JSON, exact source copies, and correct empty/nonempty decisions on a separate frozen regression set.

Generation settings were temperature 0, top-p 1, top-k 0, seed 42, disabled thinking, and a maximum of 1,024 new tokens.

## Files

- `adapters.safetensors`: LoRA weights
- `adapter_config.json`: portable MLX-LM adapter configuration
- `system_prompt.txt`: inference-time task instructions
- `training_metadata.json`: training and evaluation summary
- `SHA256SUMS`: integrity checksums
- `README.md`: model card

## Limitations

This is an experimental 0.6B adapter. Dense passages with multiple interacting conditions can still produce omissions or altered qualifications. Outputs should be reviewed before use in high-stakes learning workflows. Training and evaluation data are synthetic.
