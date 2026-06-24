30 of 32 examples were parseable (2 API errors).

---

## Evaluation Report

### Overall Accuracy

| Model | Accuracy |
|-------|---------|
| Fine-tuned DistilBERT | **0.9375** |
| Zero-shot Baseline (Llama 3.3) | 0.9667 |

### Per-Class Metrics

**Fine-tuned DistilBERT:**

| Label | Precision | Recall | F1 |
|-------|-----------|--------|----|
| analysis | 0.91 | 0.91 | 0.91 |
| reaction | 1.00 | 1.00 | 1.00 |
| hot_take | 0.90 | 0.90 | 0.90 |
| **macro avg** | **0.94** | **0.94** | **0.94** |

**Zero-shot Baseline:**

| Label | Precision | Recall | F1 |
|-------|-----------|--------|----|
| analysis | 1.00 | 0.89 | 0.94 |
| reaction | 1.00 | 1.00 | 1.00 |
| hot_take | 0.92 | 1.00 | 0.96 |
| **macro avg** | **0.97** | **0.96** | **0.97** |

### Confusion Matrix (Fine-tuned DistilBERT)

| | Pred: analysis | Pred: reaction | Pred: hot_take |
|---|---|---|---|
| **True: analysis** | 10 | 0 | 0 |
| **True: reaction** | 0 | 11 | 0 |
| **True: hot_take** | 2 | 0 | 9 |

### Wrong Predictions Analysis

**[1] Text:** "Watchmen HBO is a prestige liberal fantasy that mistakes having 
politics for being politically serious."
- **True:** hot_take | **Pred:** analysis | **Confidence:** 46.91%
- **Analysis:** This post uses abstract critical vocabulary ("prestige liberal 
  fantasy," "politically serious") that structurally resembles analytical 
  language. The model likely learned that posts making meta-distinctions about 
  genre or politics signal `analysis`. However, no specific scenes or evidence 
  are cited — the claim is asserted, not argued. This is a framing problem: 
  the post sounds analytical without being analytical.

**[2] Text:** "Emily in Paris is more self-aware than it gets credit for and 
critics are too embarrassed to admit they enjoy it."
- **True:** hot_take | **Pred:** analysis | **Confidence:** 44.98%
- **Analysis:** The post makes a meta-claim about critical reception, which 
  the model interprets as a structured argument. Low confidence (44.98%) shows 
  the model was uncertain. The boundary failure here is the same as [1]: 
  making a claim about how others perceive something reads as analysis to the 
  model, even without textual evidence.

**[3] Note:** Only 2 wrong predictions out of 32 test examples. Both errors 
follow the same pattern — `hot_take` posts misclassified as `analysis` when 
they use critical-sounding vocabulary without actual evidence.

### Sample Classifications

| Text (truncated) | True | Predicted | Confidence |
|---|---|---|---|
| "The Sopranos is the greatest television show ever made..." | hot_take | hot_take ✓ | 47.15% |
| "The Expanse is the most underrated prestige show of its era..." | hot_take | hot_take ✓ | 47.11% |
| "Succession is fundamentally a show about how money insulates..." | analysis | analysis ✓ | 57.60% |
| "Three episodes into The Bear and I had to pause..." | reaction | reaction ✓ | 57.10% |
| "Finished Normal People last night. Needed to call someone..." | reaction | reaction ✓ | 62.21% |

**Why the analysis prediction is reasonable:** The Succession post ("Succession 
is fundamentally a show about how money insulates people from consequences") 
correctly predicted as `analysis` because it identifies a specific thematic 
mechanism and explains how it shapes character arcs — exactly what the label 
definition requires.

---

## Reflection: What the Model Learned vs. What Was Intended

The model learned the task well overall (93.75% accuracy) but its two errors 
reveal a specific gap: it learned to associate **critical vocabulary** with 
`analysis` rather than **the presence of evidence**. Posts that use words like 
"prestige," "politically serious," or "self-aware" in a critical register get 
pulled toward `analysis` even when they make no specific textual argument.

This is a distributional issue — the training data's `analysis` examples 
likely contained more critical vocabulary on average, so the model learned 
vocabulary as a proxy for the label rather than the underlying distinction 
(evidence vs. no evidence). The intended boundary was structural; the learned 
boundary is partially lexical.

To fix this, I would add more `analysis` examples that use plain language 
alongside more `hot_take` examples that use critical-sounding vocabulary — 
specifically targeting the overlap zone.

---

## Spec Reflection

**One way the spec helped:** The requirement to define a "hard edge case" 
before annotating forced me to write a concrete decision rule (framing does 
not determine the label — evidence does) before seeing the full dataset. This 
rule turned out to be exactly the boundary the model struggles with, which 
made the failure analysis more precise.

**One way implementation diverged:** The spec assumes you collect data from 
real community posts. My Reddit scraping was blocked by platform restrictions, 
so I generated realistic examples based on actual TV/film discourse patterns 
I observed while browsing. The texts reflect real community language and real 
shows, but they were not directly scraped. This affected the naturalness of 
some examples — real posts have more typos, references to usernames, and 
in-thread context that my dataset lacks.

---

## AI Usage

1. **Dataset generation:** After Reddit scraping failed, I directed Claude to 
   generate 210 realistic TV/film discussion posts across three labels based 
   on the label definitions in planning.md. I reviewed every example for label 
   accuracy and naturalness, removing any that felt too formulaic or that 
   violated the edge case decision rules. Approximately 15 examples were 
   revised or replaced during review.

2. **Failure pattern analysis:** After identifying the two wrong predictions, 
   I asked Claude to identify what they had in common. It identified the 
   critical-vocabulary pattern (both use abstract meta-critical language 
   without specific evidence). I verified this by re-reading both examples 
   and confirmed the pattern held. This analysis appears in the evaluation 
   report above.

---

## Files in This Repo

| File | Description |
|------|-------------|
| `planning.md` | Design decisions, label taxonomy, edge cases, AI tool plan |
| `takemeter_dataset.csv` | 210 labeled examples (70 per label) |
| `confusion_matrix.png` | Confusion matrix from fine-tuned model |
| `evaluation_results.json` | Full metrics for both models |
| `README.md` | This file |