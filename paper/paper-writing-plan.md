# Paper 1 — writing plan and supervisor comments

**Source:** `paper/UnderGraduate_Research_comments by supervisor.pdf` (24 highlight comments, pages 1–2, received Sep 2026).
**Scope of review:** abstract and introduction only. Pages 3–14 carry no comments yet.
**Status:** 🔲 comments recorded verbatim; revisions not started. Items marked 💬 need a conversation with the supervisor before anything is changed.

---

## 1. Supervisor comments (verbatim, in order)

### Abstract

| # | Highlighted text | Supervisor comment | Type |
| :-- | :--- | :--- | :--- |
| 1 | "Proposed defenses cluster into prompt-level marking and gate-level constraint." | Not sure what you want to say here. | clarity |
| 2 | "third framing" | What is third framing, never used before. See abstract should be written in a way that a new person can easily understand it. | clarity |
| 3 | "Abstract—" | Normally abstract has only five to six lines in total. 1. Problem/gap 2. Why it matters (motivation, can merge with #1) 3. Objective 4. Method (very short) 5. Results 6. Implications (what your results mean going forward) | structure |
| 4 | "asks instead whether the model's proposed action changed because of the untrusted span, which is a causal question." | I am not sure what you want to say here. | clarity |
| 5 | "such" | Because earlier lines were not correct, hence we don't know what such is referring to. | clarity |
| 6 | "component by component." | English need to be improved. | language |
| 7 | "corpus." | You mean dataset?? What do you want to say here? | terminology |
| 8 | "from 96.7%" | need to improve english, when you say from, you also need to say "to" from this to this. from 96.7% to 18%. | language |
| 9 | "negative results," | Remove negative results. We don't want to emphasize on negative results, otherwise the paper will not publish or very hard to publish. | framing |
| 10 | "The evaluation is largely negative and the negative results are the contribution." | Don't highlight it, we need to discuss. | 💬 framing |
| 11 | "spotlighting" | Very generic word, what do you mean | terminology |
| 12 | "Widening" | Again a generic word which does not clear the meaning. The abstract should be written in a way which is clear and concise and easily understandable. | terminology |
| 13 | "harm taxonomy," | Is this word commonly used in the Literature. | terminology |
| 14 | "Finally, two pre-registered multi-turn experiments found the adaptive layer's temporal-drift rule unable to fire, and measured why: … 24 of 30 turns, so the causal contrast is zero for any threshold on any content." | Break a long sentence. It will make it easily understandable. | language |
| 15 | "The causal contrast carries discriminative signal when the injected content contains a liftable target, an address or URL an action can name, and close to none otherwise." | This is not good, we need to discuss. How we can bring the contribution in front and not overemphasize the weaknesses of the work. | 💬 framing |
| 16 | "Every number reported here is regenerable by a committed command over a released artifact, and the two headline experiments were pre-registered." | Ahmed you are much much better than this line. Its clear you are using AI too much. Its simple to write that "all the results are reproducible as all the code for the experiments is provided in the Github." | voice |

### Introduction

| # | Highlighted text | Supervisor comment | Type |
| :-- | :--- | :--- | :--- |
| 17 | "tool" | a tool | language |
| 18 | "Proposed defenses cluster" | Not clear what you want to say. Maybe "The earlier work proposed a defense cluster with two . . ." | clarity |
| 19 | "instruct the model" | Does it actually asks the model not the check for internal details or it just ignores those details. If it just ignores, then write "and does not check the internal details." | accuracy |
| 20 | "Not does" | Doesn't this . . . | language |
| 21 | "corpora," | Use simple language | terminology |
| 22 | "steering rate" | Please discuss | 💬 terminology |
| 23 | "Contributions" | Currently the contributions section is long and lot of experimental details are also provided. Here we only write about the contributions. I think may be headlines and may be one line would be enough and make a one concrete paragraph out of it rather than giving experimental details here. The details need to go into their appropriate sections e.g. in the experiments section. | structure |
| 24 | "Three negative results about adaptive security configuration, each invisible from inside the component that produced it: …" (page 2) | I know this is hard, but would suggest to take your time and think about it without stress and try to find out innovative way. Don't be afraid and think positive, if we do better here, we can make it really a good paper. | 💬 framing |

---

## 2. What the comments add up to

1. **Reframe, do not hide.** Items 9, 10, 15, 24 all say one thing: lead with the contribution, not the weaknesses. The current stance ("the negative results are the contribution") has to change.
2. **Plain words.** Items 1, 2, 4, 5, 11, 12, 13, 18, 21 are all jargon. Every term that is not standard in the literature gets replaced or defined once, simply.
3. **Own voice.** Item 16 is explicit. Every sentence is rewritten by hand in short, direct English.
4. **Shorter abstract, thinner contributions.** Items 3 and 23.

### Decision needed from the supervisor (💬 items 10, 15, 22, 24)

The reframing must stay honest, since the journal target requires every number to carry n, a CI and a named external baseline. Proposal to bring to the meeting:

> Keep every result and every number. Change only the **order and the verbs**: lead with what works (causal detection reaches 96.7% on our attacks and 93.3% on InjecAgent attacks that name a target an action can copy), then state the boundary as a **scope condition** ("applies when…") instead of as a failure. Move the adaptive-layer findings out of the abstract's headline and into a short "future work" sentence that motivates paper 2.

Questions to ask:
- Is it acceptable to keep the negative findings in the body (Sections 7–8) but not in the abstract or the contributions?
- What does the supervisor want in place of "steering rate" (item 22)? Candidate: "attack success rate" (the common term) or define it once.
- Is the adaptive-layer material (Section 8) kept in paper 1 or moved to paper 2? See `paper2-plan.md`.

---

## 3. Revision checklist

Work in this order. Tick each item only when the supervisor-visible text has changed.

### A. Abstract (target: 5–6 lines, one sentence per element)
- [ ] 1. Problem / gap: indirect prompt injection against tool-using agents; existing defenses either mark the untrusted text or restrict actions, and neither checks whether the text *caused* the action.
- [ ] 2. Why it matters (merged with 1).
- [ ] 3. Objective: test whether comparing the agent's action with and without the untrusted text can detect injections.
- [ ] 4. Method (one clause): masked vs. unmasked comparison, evaluated per attack type on a pre-registered test.
- [ ] 5. Results: **one** headline pair with "from X to Y" wording, e.g. on InjecAgent, detection of 93.3% when the attack contains an address or URL, and 10.0% when it does not.
- [ ] 6. Implications: the method is reliable where attacks name a target; extending it beyond that is the next step.
- [ ] **Factual fix (found 15 Oct, not a supervisor comment):** the abstract says "96.7% where the detector's target-match path can fire against 10.0% where it cannot". 96.7% is our own corpus (phase 7). The InjecAgent target-match stratum is **93.3%** [78.7%, 98.2%] (`paper/05-external-validity.md`). Use 93.3% vs 10.0%, or name both corpora.
- [ ] Replace: "third framing", "spotlighting", "widening", "harm taxonomy", "corpus" (→ dataset), "negative results".
- [ ] Split the long drift sentence (item 14), or move it to the body.
- [ ] Replace the item-16 sentence with: "All results are reproducible, and the code for every experiment is on GitHub."

### B. Introduction
- [ ] Rewrite the "Proposed defenses cluster…" opening (items 1, 18) as plain prose: what earlier work did, in two named groups.
- [ ] Item 19: check what the prompt-level defenses actually do (instruct the model to ignore vs. not inspect the span) and write exactly that. Source: `paper/04-external-baselines.md` and the cited defense papers.
- [ ] Fix "a tool", "Doesn't this…", "corpora" → "datasets".
- [ ] Resolve "steering rate" with the supervisor (item 22).
- [ ] **Contributions:** cut to one short paragraph of 3–4 one-line headlines. Move all numbers and experimental detail to the experiment sections.
- [ ] Remove or reframe the "Three negative results…" paragraph (item 24) per the meeting outcome.

### C. After the meeting
- [ ] Re-read Sections 2–10 for the same problems (jargon, long sentences, AI-sounding phrasing). The supervisor has only reviewed pages 1–2.
- [ ] Rebuild `manuscript.docx`, the figures and `external_numbers.json` if any number moves.
- [ ] Update the root README handover, `paper/handover.md`, and the Obsidian vault research log (documentation-tracking rule).

---

## 4. Style rules for this rewrite (from the comments)

- One idea per sentence; break anything past ~25 words.
- Write "from X to Y", never "from X" alone.
- Prefer common terms: *dataset* not corpus, *attack success rate* not steering rate (pending), *mark the untrusted text* not spotlighting.
- Define a new term once, in a plain sentence, at first use. Do not invent labels like "third framing".
- No filler phrasing ("regenerable by a committed command over a released artifact"). Say what a reader needs: the code is on GitHub.
- State the contribution first, then the scope condition. Never open a sentence with a weakness.
- Keep every claim traceable to `results/`. Reframing changes order and wording, never numbers.
