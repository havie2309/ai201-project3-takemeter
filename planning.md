# TakeMeter — Planning Document

## Community
I chose r/television and r/TrueFilm because both communities produce active,
text-heavy discourse that varies significantly in depth and argumentative quality.
r/TrueFilm skews toward structured film criticism; r/television covers broader
TV discussion including emotional reactions and bold opinions. Together they
provide natural variation across all three of my labels. This makes them a
strong fit for a discourse-quality classifier — the signal is entirely in the
text, not in metadata or formatting.

## Label Taxonomy

### `analysis`
A post makes a structured argument about a film or TV show by referencing
specific scenes, techniques, themes, narrative structure, or comparisons to
other works. Evidence is concrete and tied to the text.

**Examples:**
1. Nolan’s recent films all seem to be converging on the same muted, tactile realism. Oppenheimer, Tenet, and Dunkirk all use similar restrained color palettes and physical staging, unlike Villeneuve’s more monumental visual style.
2. Succession’s handheld camera makes the family dysfunction feel almost documentary-like. Instead of making every betrayal look dramatic, the shaky framing makes it feel mundane and routine, which fits the show’s view of power.

### `reaction`
A post expresses an immediate emotional response — excitement, disappointment,
shock, love — with little to no supporting argument. The post is sharing a
feeling, not building a case.

**Examples:**
1. "I love it! It's one of my favourite adaptations…" posted under a thread
   about The Expanse after finishing the show.
2. "Just finished The Bear S2 and I'm genuinely shaking. That was television."

### `hot_take`
A post states a bold or contrarian opinion confidently without supporting it
with specific evidence. The claim may be true, but the post asserts rather
than argues.

**Examples:**
1. "Oppenheimer is really mediocre" with no elaboration on why.
2. "Game of Thrones Season 8 is actually fine and people are being dramatic."

## Exclusion Rule
Posts that contain no personal opinion — purely news items, casting
announcements, question prompts ("What's a show that…"), or links with
no user commentary — are excluded from the dataset entirely and not labeled.
These posts are not classifiable under the taxonomy and including them would
introduce noise.
Because TakeMeter classifies opinion-bearing discourse, I will filter out non-opinion posts before annotation. Within the filtered dataset, the three labels should cover at least 90% of examples.

## Hard Edge Cases

### Edge case 1: Analysis with hot_take framing
**Post:** "The Center-framing Trend Needs to STOP" — aggressive title, but
the body names center-framing as a visual trend, references Mad Max: Fury Road,
explains why it once worked, and argues it now weakens cinematic language.

**Decision rule:** If a post uses opinionated framing BUT provides at least
one specific textual mechanism (a named technique, a scene, a film comparison),
label it `analysis`. Framing style does not determine the label — the presence
of supporting evidence does. → `analysis`

### Edge case 2: Hot take with vague evidence
**Post:** "Breaking Bad is the best show ever made — the character arc alone
proves it."

**Decision rule:** A single vague reason ("the character arc") without
specific reference to scenes or technique is not enough to qualify as
`analysis`. If the evidence could apply to almost any drama, it's not
genuinely analytical. → `hot_take`

### Edge case 3: Long hot_take
**Post:** A 3-paragraph post passionately arguing a show is overrated,
with many adjectives but no specific scenes, episodes, or techniques cited.

**Decision rule:** Length alone does not make a post `analysis`. If the
argument consists of strong opinions without specific textual evidence,
it remains `hot_take` regardless of word count. → `hot_take`

## Data Collection Plan
- **Source:** r/television and r/TrueFilm public posts and comments
- **Target:** 70+ examples per label (minimum), aiming for ~210 total
- **Collection method:** Manual — read and copy posts/comments into a CSV
- **If a label is underrepresented:** Return to r/TrueFilm specifically
  for more `analysis` examples, or sort by "controversial" for more
  `hot_take` examples
- **Exclusion:** News posts, question prompts, and link posts with no
  user opinion are excluded before labeling

## Evaluation Metrics
I will use **per-class F1 score** as the primary metric, not just overall
accuracy. Reason: my three classes may not be perfectly balanced, and a
model that predicts `analysis` for everything could achieve misleadingly
high accuracy if `analysis` dominates. F1 captures both precision and
recall per class, revealing whether the model handles all three distinctions
or ignores a minority class entirely.

I will also report a **confusion matrix** to identify which specific label
pair the model struggles with most (likely `analysis` vs `hot_take`, since
the boundary is the subtlest).

## Definition of Success
The fine-tuned model must achieve:
- Overall accuracy ≥ 0.72 on the test set
- Per-class F1 ≥ 0.65 for all three labels
- Meaningful improvement over the zero-shot baseline on at least 2 of 3
  per-class F1 scores

A classifier meeting these thresholds would be genuinely useful as a
moderation or recommendation tool in a film discussion community —
it would correctly identify analytical posts most of the time and
distinguish them from reactions and hot takes reliably enough to surface
quality discourse.

## AI Tool Plan

### Label stress-testing
I will give Claude my label definitions and edge case rules and ask it
to generate 10 posts that sit at the boundary between `analysis` and
`hot_take`. If it produces posts I cannot classify cleanly, I will tighten
the definitions before annotating 200 examples.

### Annotation assistance
I may use an LLM to pre-label batches of 20–30 examples at a time, then
review and correct every label myself. I will track which examples were
pre-labeled in a notes column and disclose this in the AI usage section.

### Failure analysis
After fine-tuning, I will paste my misclassified examples into Claude and
ask it to identify common patterns — post length, sarcasm, label pair
confusion, low-information posts. I will verify any pattern it identifies
by re-reading the examples myself before including it in my evaluation report.