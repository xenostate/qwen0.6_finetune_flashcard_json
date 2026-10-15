# Evaluation method

The project used two evaluation sets with different purposes.

## Family-held-out evaluation

The 35-record targeted set contains five examples for each expected card count from zero through six. Structurally related examples were kept together when constructing splits, so a template family could not be divided between training and evaluation.

This set measured whether each training round fixed known behavioral failures without relying only on validation loss.

## Frozen regression evaluation

The 20-record frozen set was created before training and never used for gradient updates or checkpoint selection. It contains short and long passages, empty cases, exact values, qualifications, distractor text, and instruction-like content embedded in source passages.

It served as a final regression check after a checkpoint had already been selected.

## Deterministic generation

Every comparison used the same settings:

- Temperature: `0`
- Top-p: `1`
- Top-k: `0`
- Maximum new tokens: `1024`
- Random seed: `42`
- Thinking mode: disabled
- Same system prompt and chat template

## Automated checks

The scoring script checks:

1. Whether the raw response parses as JSON without preprocessing.
2. Whether the root contains exactly `source` and `flashcards`.
3. Whether the copied source exactly matches the input.
4. Whether every flashcard contains nonempty question and answer strings.
5. Whether the empty/nonempty decision agrees with the reference.
6. The absolute difference between generated and reference card counts.

## Semantic audit

Formatting metrics cannot detect a reversed threshold or a missing exception. Outputs were therefore reviewed against reference concepts.

A strict semantic pass required complete concept coverage, correct conditions and exceptions, no unsupported statements, no promoted document artifacts, and no substantial duplication.

## Model-selection rule

Validation loss selected the candidate checkpoint. The targeted evaluation checked its behavior, and the frozen evaluation acted as the final regression gate. This prevented choosing a checkpoint only because it achieved a lower loss.

## Selected-checkpoint results

| Metric | Previous checkpoint | Selected checkpoint |
|---|---:|---:|
| Valid raw JSON | 34/35 | **35/35** |
| Schema and exact source | 33/35 | **35/35** |
| Correct empty/nonempty decision | 28/35 | **33/35** |
| Strict semantic passes | 5/35 | **10/35** |
| Reference concepts covered | 55/105 | **74/105** |

The selected adapter also achieved 20/20 valid JSON, exact source copies, and correct empty/nonempty decisions on the frozen regression set.

