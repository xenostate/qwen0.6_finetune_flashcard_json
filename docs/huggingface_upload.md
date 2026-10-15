# Hugging Face upload

The release bundle is named:

```text
qwen3-0.6b-flashcards-qlora-v6-hf.zip
```

It contains the LoRA weights, portable adapter configuration, system prompt, training metadata, and model card. Hugging Face should receive the extracted files.

After creating an empty model repository on Hugging Face and logging in with the `hf` CLI, upload the folder contents:

```bash
unzip qwen3-0.6b-flashcards-qlora-v6-hf.zip

hf upload YOUR_USERNAME/qwen3-0.6b-flashcards-qlora-v6 \
  qwen3-0.6b-flashcards-qlora-v6-hf .
```

The adapter depends on `lmstudio-community/Qwen3-0.6B-MLX-4bit`; the base weights are not duplicated in the upload.
