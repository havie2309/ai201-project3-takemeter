# TakeMeter

A fine-tuned text classifier that evaluates discourse quality in TV/film
fan communities. TakeMeter labels posts as `analysis`, `reaction`, or
`hot_take` — distinctions that matter to anyone trying to surface
substantive discussion in a community where the volume of opinion vastly
outstrips the volume of argument.

[DEMO](https://www.loom.com/share/f7d76b14ff8f47d1bfc1f6050f0482eb?focus_title=1&muted=1&from_recorder=1)

## Community

I chose **r/television** and **r/TrueFilm**. r/TrueFilm skews toward
structured film criticism, while r/television covers broader TV discussion
that ranges from emotional reaction to confident, evidence-free opinion.
Together they produce natural variation across all three labels rather than
clustering around one — a community that only produced hot takes, for
example, would not give a classifier a meaningful task. The signal that
distinguishes these labels is entirely in the text itself (no images, no
voting patterns needed), which makes the community a good fit for a
text-only classifier.

## Label Taxonomy

| Label | Definition |
|---|---|
| `analysis` | The post makes a structured argument by referencing specific scenes, techniques, themes, or comparisons to other works. Evidence is concrete and tied to the text. |
| `reaction` | The post expresses an immediate emotional response — excitement, devastation, obsession — with little to no supporting argument. |
| `hot_take` | The post states a bold or contrarian opinion confidently without supporting evidence. The claim may be true, but the post asserts rather than argues. |

**`analysis` examples:**
1. "The Bear uses kitchen hierarchy as a metaphor for inherited trauma. Carmy cannot escape his fine dining background the same way he cannot escape his family."
2. "Chernobyl works as a drama because it is not really about the explosion. It is about what happens when a system that cannot admit failure encounters a catastrophic failure."

**`reaction` examples:**
1. "Just finished The Bear season two and I cannot move. That was the most stressful television I have ever watched."
2. "Finished Dark last week and I still have not fully processed it. That ending hit different."

**`hot_take` examples:**
1. "Breaking Bad is the most overrated prestige drama of the last twenty years. Better Call Saul is a better show in every measurable way."
2. "The Rings of Power looks incredible and is deeply boring. Amazon paid a billion dollars to make the most expensive furniture commercial ever made."

Full definitions, decision rules, and the rationale behind the taxonomy are
in [`planning.md`](./planning.md).

## Data Collection and Labeling

**Source:** r/television and r/TrueFilm.

**Process:** My original plan was to scrape posts and top comments directly
from both subreddits using Reddit's public `.json` endpoints (see
[`scrape_reddit.py`](./scrape_reddit.py), which implements pagination,
rate-limit backoff, and length/score filtering). This scraper was blocked
in practice — requests from my machine were consistently rate-limited or
returned empty result sets, likely due to Reddit's anti-scraping measures
on unauthenticated traffic. Rather than lose the milestone to infrastructure,
I pivoted to AI-assisted dataset construction: I directed Claude to generate
realistic TV/film discussion posts that matched the label definitions and
edge-case rules from `planning.md`, then manually reviewed, edited, or
discarded every example for naturalness and label accuracy (see **AI Usage**
below for what was changed).

**This is a real limitation of the dataset**, not a cosmetic one: the text
is cleaner and more uniformly well-formed than actual Reddit posts, which
include typos, in-thread references, and sarcasm markers that a scraped
dataset would have surfaced. This likely makes the classification task
easier than it would be on live data — see the **Reflection** section for
how this shows up in the results.

**Label distribution:** 70 `analysis` / 70 `reaction` / 70 `hot_take`
(210 total, perfectly balanced — no label exceeds 70% of the dataset).

**Three difficult-to-label examples** (full list and decision rules in
`planning.md`):

1. *"The center-framing trend needs to STOP"* — opinionated, aggressive
   framing, but the body names a specific visual technique and compares
   it across films. **Decision:** `analysis` — framing style doesn't
   determine the label, the presence of specific evidence does.
2. *"Breaking Bad is the best show ever made — the character arc alone
   proves it."* — cites a "reason," but the reason (character arc) is too
   generic to be genuine evidence. **Decision:** `hot_take` — a vague
   justification that could apply to almost any drama isn't analysis.
3. A 3-paragraph passionate post arguing a show is overrated, full of
   strong language but no specific scenes or techniques. **Decision:**
   `hot_take` — length and intensity don't substitute for evidence.

## Fine-Tuning Approach

**Base model:** `distilbert-base-uncased` (HuggingFace).

**Platform:** Google Colab, free T4 GPU, using the `transformers` +
`datasets` + `scikit-learn` stack from the starter notebook.

**Training setup:** 70% / 15% / 15% train/validation/test split (147 /
31 / 32 examples), 3 epochs, learning rate 2e-5, batch size 16.

**Hyperparameter decision:** I used the notebook's default hyperparameters
rather than tuning them, and I'm treating that as a deliberate choice rather
than a default-by-omission: with only 147 training examples, more epochs
risked overfitting a model with as many parameters as DistilBERT has, and
2e-5 is the standard conservative learning rate for fine-tuning a pretrained
transformer on a small dataset — large enough to adapt the classification
head in 3 epochs, small enough not to destroy the pretrained representations
DistilBERT already has of English text. The training run converged cleanly
within the 3 epochs without the validation metrics degrading, which is the
main thing I was watching for as a sign that I'd need to add regularization
or stop early.

## Baseline Approach

**Model:** Groq's `llama-3.3-70b-versatile`, zero-shot, `temperature=0`,
`max_tokens=10` to force short, parseable output.

**Prompt** (identical label definitions to `planning.md`, used for every
test example):

```
You are a classifier for TV/film discussion posts.

Classify the following post into exactly one of these labels:
- analysis: makes a structured argument referencing specific scenes, techniques, themes, or comparisons. Evidence is concrete and tied to the text.
- reaction: expresses immediate emotional response with little or no argument. Sharing a feeling, not building a case.
- hot_take: states a bold or contrarian opinion confidently without supporting evidence. Asserts rather than argues.

Respond with ONLY the label name (analysis, reaction, or hot_take). Nothing else.

Post: {text}

Label:
```

**Collection:** Each of the 32 test-set examples (the same locked test
split the fine-tuned model was evaluated on) was sent to this prompt via
the Groq chat completions API, and the returned label was parsed and
compared against the true label. 30 of 32 responses were parseable (2 API
errors / timeouts were excluded from the baseline's accuracy calculation
rather than scored as wrong, which is worth flagging as a minor
inconsistency between the two models' effective test-set sizes).

---

## Evaluation Report

### Overall Accuracy

| Model | Accuracy |
|-------|---------|
| Fine-tuned DistilBERT | **0.9375** (30/32) |
| Zero-shot Baseline (Llama 3.3) | 0.9667 (29/30 parseable) |

### Per-Class Metrics

**Fine-tuned DistilBERT:**

| Label | Precision | Recall | F1 |
|-------|-----------|--------|----|
| analysis | 0.833 | 1.000 | 0.909 |
| reaction | 1.000 | 1.000 | 1.000 |
| hot_take | 1.000 | 0.818 | 0.900 |
| **macro avg** | **0.944** | **0.939** | **0.936** |

**Zero-shot Baseline:**

| Label | Precision | Recall | F1 |
|-------|-----------|--------|----|
| analysis | 1.000 | 0.889 | 0.941 |
| reaction | 1.000 | 1.000 | 1.000 |
| hot_take | 0.917 | 1.000 | 0.957 |
| **macro avg** | **0.972** | **0.963** | **0.966** |

*(These numbers are pulled directly from `evaluation_results.json`,
committed in this repo.)*

The baseline edges out the fine-tuned model on every metric here. That
result is discussed honestly in the Reflection section below — it is not
the result I expected, and I think it's mostly a property of how clean
and well-formed the (AI-assisted) dataset is, not evidence that fine-tuning
"failed."

### Confusion Matrix (Fine-tuned DistilBERT)

| | Pred: analysis | Pred: reaction | Pred: hot_take |
|---|---|---|---|
| **True: analysis** | 10 | 0 | 0 |
| **True: reaction** | 0 | 11 | 0 |
| **True: hot_take** | 2 | 0 | 9 |

(Also committed as [`confusion_matrix.png`](./confusion_matrix.png).)

All errors are concentrated in one cell: 2 of 11 `hot_take` posts were
predicted as `analysis`. There were zero errors involving `reaction` in
either direction, and zero errors where `analysis` was predicted as
`hot_take`. The error pattern is one-directional.

### Wrong Predictions Analysis

**[1]** *"Watchmen HBO is a prestige liberal fantasy that mistakes having
politics for being politically serious."*
- **True:** `hot_take` | **Predicted:** `analysis` | **Confidence:** 46.91%
- **Why it failed:** This post uses abstract critical vocabulary ("prestige,"
  "politically serious") that structurally resembles analytical language —
  it sounds like a critic talking. But it cites no specific scene, episode,
  or technique; the claim is asserted, not demonstrated. The model appears
  to have keyed on register (does this sound like film criticism?) rather
  than on the presence of concrete evidence, which is the actual boundary
  in the label definition. The low confidence (46.91%, barely above the
  33% chance floor for 3 classes) shows the model itself was near its
  decision boundary on this example, not confidently wrong.

**[2]** *"Emily in Paris is more self-aware than it gets credit for and
critics are too embarrassed to admit they enjoy it."*
- **True:** `hot_take` | **Predicted:** `analysis` | **Confidence:** 44.98%
- **Why it failed:** Same underlying pattern as [1]. The post makes a
  meta-claim about critical reception ("critics are too embarrassed"),
  which reads as the kind of higher-order observation `analysis` posts
  tend to make — but it points to no specific scene or technique. Again,
  confidence is low (44.98%), meaning the model is genuinely uncertain
  rather than confidently misreading the post.

**[3]** Both errors are the same failure mode, which itself is informative:
out of 32 test examples, the model made exactly 2 mistakes, and both were
`hot_take` posts that use critic-register vocabulary ("prestige," "self-aware,"
"politically serious") without naming a specific scene or technique. No
`analysis` post was ever mistaken for a `hot_take`, and `reaction` was never
confused with either. This is consistent with — but a much smaller-scale
version of — the kind of directional, diagnosable pattern the project asks
you to look for.

I want to flag explicitly that this pattern is based on **n=2** errors. With
only two data points, "the model keys on critic vocabulary instead of
evidence" is my best read of what's happening, but it is a hypothesis, not
something I can claim with statistical confidence from this test set alone.
A larger test set, or a set of held-out boundary cases specifically targeting
this pattern, would be needed to confirm it.

### Sample Classifications

| Text (truncated) | True | Predicted | Confidence |
|---|---|---|---|
| "The Sopranos is the greatest television show ever made..." | hot_take | hot_take ✓ | 47.15% |
| "The Expanse is the most underrated prestige show of its era..." | hot_take | hot_take ✓ | 47.11% |
| "Succession is fundamentally a show about how money insulates..." | analysis | analysis ✓ | 57.60% |
| "Three episodes into The Bear and I had to pause..." | reaction | reaction ✓ | 57.10% |
| "Finished Normal People last night. Needed to call someone..." | reaction | reaction ✓ | 62.21% |

**Why the `analysis` prediction is reasonable:** "Succession is fundamentally
a show about how money insulates people from consequences" was correctly
predicted as `analysis` because it identifies a specific thematic mechanism
(money as insulation) and implies how that mechanism shapes character
behavior across the show — exactly the kind of concrete, textually-grounded
claim the label definition requires, as opposed to an unsupported assertion
of quality.

I'll also note that none of the confidence scores above are very high
(44–62%, well within the same range as the model's two wrong predictions).
See the calibration note in the Reflection below — this is one of the more
interesting and slightly concerning things I found in this evaluation.

---

## Reflection: What the Model Learned vs. What Was Intended

I intended the model to learn a **structural** distinction: does this post
cite a specific scene, technique, or comparison (evidence), or does it just
assert an opinion (no evidence)? That distinction is what separates
`analysis` from `hot_take` in my label definitions, and it's the rule I
applied consistently while annotating.

What the model actually appears to have learned, based on the two errors
above, is closer to a **lexical / register** proxy for that distinction:
posts that use abstract critical vocabulary ("prestige," "politically
serious," "self-aware") get pulled toward `analysis` even when they cite no
concrete evidence. Both `hot_take` errors share this exact trait, and the
direction is consistent — vocabulary that *sounds* like criticism, not
posts that *are* criticism. This is a believable failure mode for a model
with as little training data as 147 examples: if the genuinely analytical
posts in my dataset happen to use more sophisticated critical vocabulary on
average (which, given that I had an LLM generate a portion of the dataset
in a recognizably "essay-like" register for `analysis`, is plausible), the
model has a real shortcut available to it that correlates with the label
without actually being the underlying distinction.

A second, more concerning observation: **confidence scores across the board
are low** — even correct predictions cluster in the 45–62% range, only
slightly above the 33% floor for random guessing among three classes. This
suggests the model is not learning the boundary with much margin even where
it gets the answer right; it may be picking up on weaker, more diffuse
signal than a model trained on a larger or more naturalistic dataset would.
I did not get to formally test calibration (whether 60%-confidence
predictions are actually right more often than 45%-confidence ones) as a
stretch feature, but the narrow confidence range across both correct and
incorrect predictions is itself a flag that the model's "confidence" may
not be very meaningful here.

Finally, the baseline outperforming the fine-tuned model on every metric is
itself a finding worth being honest about. My hypothesis is that this is
largely a property of the dataset rather than a failure of fine-tuning: a
70-billion-parameter model that has seen enormous amounts of real film
criticism in pretraining doesn't need 147 labeled examples to apply
essentially the same definitions I gave it in the prompt — especially on
text that, because of how it was constructed, is already fairly clean and
well-formed. A genuinely messy, scraped dataset (with typos, sarcasm, and
thread context) would be a fairer test of whether fine-tuning earns its
keep over a strong zero-shot baseline, and I'd expect the gap to look
different on that data.

---

## Spec Reflection

**One way the spec helped:** Being required to name a hard edge case and
write an explicit decision rule *before* annotating (Milestone 1) forced me
to commit to "framing doesn't determine the label, evidence does" ahead of
time. That exact rule turned out to be the boundary the model struggles
with — both of its errors are framing-vs-evidence confusions — which made
the failure analysis far more precise than it would have been if I'd only
discovered the boundary after looking at wrong predictions.

**One way implementation diverged:** The spec assumes manual collection of
real community posts. My scraper (`scrape_reddit.py`) is real and
functional in design, but Reddit's unauthenticated rate limiting blocked it
in practice, so I pivoted to AI-assisted dataset generation grounded in my
label definitions, reviewed by hand. This was a reasonable adaptation under
the circumstances, but it's a real divergence with a real cost: the dataset
is cleaner and more uniform than scraped Reddit text would be, which likely
makes the classification task easier than intended and is probably part of
why the baseline and fine-tuned numbers are both higher than the spec's own
"check for leakage if accuracy is suspiciously high" hint would lead you to
expect on a genuinely hard, real-world dataset.

---

## AI Usage

1. **Label stress-testing (planning phase):** I gave Claude my label
   definitions and asked it to generate boundary posts between `analysis`
   and `hot_take`. Some of what it produced was genuinely hard for me to
   classify on first read, which is what led me to add the explicit
   decision rule ("framing doesn't determine the label, evidence does") to
   `planning.md` before I started annotating.

2. **Dataset generation (after scraping was blocked):** I directed Claude
   to generate realistic TV/film discussion posts across all three labels,
   based on the label definitions and edge-case rules in `planning.md`. I
   reviewed every example individually, rewrote or discarded ones that felt
   formulaic, didn't clearly match a single label, or violated one of the
   edge-case decision rules. Roughly 15 examples were revised or replaced
   during this review. This is annotation-adjacent assistance and is
   disclosed here as required — every label in the final dataset was
   confirmed against my own definitions during review, not assigned by the
   AI.

3. **Failure pattern analysis (evaluation phase):** I gave Claude the two
   misclassified test examples and asked it to identify what they had in
   common. It identified the critical-vocabulary-without-evidence pattern
   described in the Reflection above. I verified this by re-reading both
   examples myself and confirming the pattern held, and I explicitly noted
   in the writeup that this pattern is based on only 2 data points and
   should be treated as a hypothesis rather than a confirmed result —
   Claude's first draft of this analysis stated the pattern more
   confidently than I think n=2 actually supports, and I revised it to
   include that caveat.

---

## Files in This Repo

| File | Description |
|------|-------------|
| `planning.md` | Design decisions, label taxonomy, edge cases, AI tool plan |
| `takemeter_dataset.csv` | 210 labeled examples (70 per label) |
| `scrape_reddit.py` | Reddit scraper used in the original (blocked) collection attempt |
| `confusion_matrix.png` | Confusion matrix from fine-tuned model |
| `evaluation_results.json` | Full metrics for both models |
| `README.md` | This file |