# TakeMeter — Planning Document

## Community
I chose r/television and r/TrueFilm because both communities produce active,
text-heavy discourse that varies significantly in depth and argumentative quality.
r/TrueFilm skews toward structured film criticism; r/television covers broader
TV discussion including emotional reactions and bold opinions. Together they
provide natural variation across all three labels. The signal is entirely in
the text itself, making them ideal for a text classifier.

## Label Taxonomy

### `analysis`
A post makes a structured argument about a film or TV show by referencing
specific scenes, techniques, themes, narrative structure, or comparisons to
other works. Evidence is concrete and tied to the text.

**Examples:**
1. "The Bear uses kitchen hierarchy as a metaphor for inherited trauma. Carmy
   cannot escape his fine dining background the same way he cannot escape his
   family. The restaurant is literally built inside his brothers old space."
2. "Chernobyl works as a drama because it is not really about the explosion.
   It is about what happens when a system that cannot admit failure encounters
   a catastrophic failure. The disaster is institutional before it is physical."

### `reaction`
A post expresses an immediate emotional response — excitement, devastation,
shock, obsession — with little to no supporting argument. The post is sharing
a feeling, not building a case.

**Examples:**
1. "Just finished The Bear season two and I cannot move. That was the most
   stressful television I have ever watched."
2. "Finished Dark last week and I still have not fully processed it.
   That ending hit different."

### `hot_take`
A post states a bold or contrarian opinion confidently without supporting it
with specific evidence. The claim may be true, but the post asserts rather
than argues.

**Examples:**
1. "Breaking Bad is the most overrated prestige drama of the last twenty years.
   Better Call Saul is a better show in every measurable way."
2. "The Rings of Power looks incredible and is deeply boring. Amazon paid a
   billion dollars to make the most expensive furniture commercial ever made."

## Exclusion Rule
Posts that contain no personal opinion — purely news items, casting
announcements, question prompts, or links with no user commentary — are
excluded from the dataset entirely and not labeled.

## Hard Edge Cases

### Edge case 1: Analysis with hot_take framing
**Post:** A post titled aggressively like "The center-framing trend needs to
STOP" but the body names a specific visual technique, references real films,
and explains why it weakens cinematic language.

**Decision rule:** If a post uses opinionated framing BUT provides at least
one specific textual mechanism (a named technique, a scene, a film comparison),
label it `analysis`. Framing style does not determine the label — the presence
of supporting evidence does.

### Edge case 2: Reaction with one weak reason
**Post:** "Breaking Bad is the best show ever made — the character arc alone
proves it."

**Decision rule:** A single vague reason ("the character arc") without
specific reference to scenes or technique is not enough for `analysis`.
If the evidence could apply to almost any drama, it is not genuinely
analytical. Label it `hot_take`.

### Edge case 3: Long hot_take
**Post:** A 3-paragraph post passionately arguing a show is overrated,
with many adjectives but no specific scenes or techniques cited.

**Decision rule:** Length alone does not make a post `analysis`. If the
argument consists of strong opinions without specific textual evidence,
it remains `hot_take` regardless of word count.

## Data Collection Plan
- **Source:** r/television and r/TrueFilm public posts and comments
- **Target:** 70 examples per label, 210 total
- **Collection method:** Manual collection and labeling using defined rules
- **Label distribution:** 70 analysis / 70 reaction / 70 hot_take (perfectly balanced)
- **If underrepresented:** Return to r/TrueFilm for more analysis examples,
  sort by controversial for more hot_take examples

## Evaluation Metrics
I will use **per-class F1 score** as the primary metric, not just overall
accuracy. Reason: even with balanced classes, a model could learn to predict
one label well and fail on the subtler boundaries. F1 captures both precision
and recall per class, revealing whether the model handles all three distinctions
or collapses on one.

I will also report a **confusion matrix** to identify which specific label
pair the model struggles with most — likely `analysis` vs `hot_take` since
the boundary is the subtlest (both involve opinions, but one has evidence).

## Definition of Success
The fine-tuned model must achieve:
- Overall accuracy ≥ 0.72 on the test set
- Per-class F1 ≥ 0.65 for all three labels
- Meaningful improvement over the zero-shot baseline on at least 2 of 3
  per-class F1 scores

A classifier meeting these thresholds would be genuinely useful as a
moderation or recommendation tool — correctly identifying analytical posts
most of the time and distinguishing them from reactions and hot takes
reliably enough to surface quality discourse.

## AI Tool Plan

### Label stress-testing
I gave Claude my label definitions and edge case description and asked it
to generate boundary posts between `analysis` and `hot_take`. Several posts
it produced were genuinely hard to classify, which helped me sharpen the
decision rule: framing does not determine the label, evidence does.

### Annotation assistance
I used an LLM to help generate realistic post examples across all three
labels after manual Reddit scraping was blocked. Every example was reviewed
and edited for naturalness and label accuracy before inclusion.

### Failure analysis
After fine-tuning, I will paste misclassified examples into Claude and ask
it to identify common patterns — post length, sarcasm, specific label pair
confusion, or low-information posts. I will verify any pattern by re-reading
the examples myself before including it in the evaluation report.