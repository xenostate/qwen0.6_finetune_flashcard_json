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

This adapter turns one supplied passage into study flashcards in JSON format. It uses only the supplied text, copies that text into the response, and returns an empty flashcard list when the passage has no useful facts.

Training code, data, and evaluation details are available in the [GitHub repository](https://github.com/xenostate/qwen0.6_finetune_flashcard_json).

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

| Frozen-set metric | Prompted base model | This adapter |
|---|---:|---:|
| Strict raw JSON | 0/20 | **20/20** |
| Schema and exact source after removing one baseline Markdown fence | 14/20 | **20/20** |
| Correct empty/nonempty decision after the same normalization | 11/20 | **20/20** |

The base model wrapped every response in a Markdown fence. The normalized baseline rows remove only that fence; this adapter required no output cleanup.

Further training iterations produced the following family-held-out improvement over the previous fine-tuned checkpoint:

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
