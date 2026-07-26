# AdaptiShield — Research Work So Far (Volume II)

**Adaptive Threat Modeling for Tool-Orchestrated LLM Systems in MCP Architectures**
Muhammad Ahmad Khan (23JZBCS0238) · Aleena Khan (23JZBCS0229)
Supervisor: Dr. Laeeq Ahmed · UET Peshawar (Jalozai Campus)

---

## What this file is

The continuation of the research log. **Volume I is
[researchworksofar.md](researchworksofar.md)**, which holds entries **I–XIV** and
is closed — it is not edited further. Every new entry goes here, numbered
continuing from XV.

Same conventions as Volume I:

- **Prose, not bullet points.** Each entry records what was attempted, what it
  returned, and what was concluded — in continuous form, so the reasoning can be
  followed rather than reconstructed from fragments.
- **Failures and reversals stay visible.** Several conclusions in Volume I
  contradict earlier ones. They are left standing rather than edited away,
  because the corrections have proved the most transferable part of the work.
- **State what a result does not establish.** Every entry ends by scoping its own
  claim.

### Where Volume I ended

Entry XIV closed with detection at 115 of 120, a false-positive rate of 3.3%
against externally-authored benign content, and the binding constraint identified
as the masked probe — which had fabricated an email address on a benign document
— together with the severity function, which accounted for four of the five
residual detection failures. None of the five was reachable by the threshold the
adaptive component controls.

It also recorded the pattern that had emerged across the preceding sessions: that
the instruments built to judge the system had failed more often than the system
itself. A credential check reported success without authenticating, an
orchestration poll could detect neither success nor failure, and a
cross-implementation comparison compared incommensurable quantities. Each
announced a verdict it had not tested.

---

## Index

| Entry | Date | Subject |
| :--- | :--- | :--- |
| XV | 26 Jul 2026, 21:30 | Where a fix belongs · the trainer executed · the human gate · a benchmark that could not measure what it was built for |

---

<!--
  New entries begin below, continuing the numbering from Volume I (I–XIV).

  Format:

  <date>

  XV. <Title>

  <opening paragraph stating what the entry records>

  A. <Section>
  ...
  <final section: what this does NOT establish>
-->

---

## 26 July 2026, 21:30 PKT

### XV. Where a Fix Belongs, a Benchmark That Could Not Measure What It Was Built For, and the Human Gate in Operation

This entry records a session with an unusual shape: almost every substantive
result came from an attempt that failed, and the failures were more informative
than the successes. Four pieces of work are covered — the repair of the probe
hallucination identified at the close of Volume I, the first execution of the
policy-gradient trainer on remote hardware, the construction of the
human-in-the-loop layer, and the first run of the eight-vector benchmark. The
last of these produced a result we then had to withdraw, for a reason that is the
most useful thing in the entry.

#### A. The hallucination, and the question of where a fix belongs

Volume I closed by naming the masked probe as the binding constraint, on the
strength of a single case: a birthday-party planning document — a guest list, a
menu, a set of decorations, containing no electronic address and no imperative of
any kind — on which the probe reported "forward the guest list to
eventplanning@company.com", inventing both the action and the recipient. The word
"forward" is a high-impact keyword, severity therefore reached its maximum, and
maximum severity alone is sufficient to declare a takeover. It was one of only
two false positives in the externally-authored benign cohort.

The obvious repair is to instruct the probe not to do this, and we attempted that
three times. The attempts were partially successful in the narrow sense: the
probe stopped inventing an address, and began naming a person who genuinely
appears in the document. It did not stop manufacturing an action. The compliance
bias installed deliberately in earlier work — the rewriting that taught the probe
to report an action even when the content softens or hedges it — proved stronger
than an instruction not to apply that bias.

The campaign run against those changes was worse on both axes: detection fell
from ninety-five point eight percent to eighty-nine percent, with the residual
failures rising from five to thirteen and now including targeted attacks that had
previously been caught, while the false-positive rate against external content
doubled. The most probable mechanism is that an instruction to name a recipient
"only if it appears in the content" made the probe reluctant to restate the
attacker's address at all — and that restatement is the single signal on which
the detector's strongest rule depends.

We record a confound that could have led us to the wrong conclusion. That same
campaign executed on the processor rather than the accelerator, because an
earlier transient fault had silently dropped the inference server to CPU-only
operation; sampling disagreement rose from roughly a third of a percent to one
and a third percent, and the machine's memory was almost entirely consumed. Two
variables had moved at once, so the run could not by itself attribute the
regression to either. Restoring the accelerator and reverting only the prompt
isolated it: detection returned to ninety-six point seven percent, higher than
the original baseline. The prompt was the cause; the backend was not.

**The fix that shipped is one layer down.** The severity function now requires
*grounding*: a high-impact verb in the probe's answer escalates only if the
untrusted content asked for something of that kind, matched by intent group
rather than exact wording, since the attack families paraphrase deliberately. The
property that makes this the right place for the repair is that the check is
**monotone** — it can only ever withhold an escalation, never create one — so its
failure mode is bounded and its effect is covered by unit tests rather than by a
ninety-minute campaign.

The general principle, which cost two campaigns to learn: **prefer the fix whose
failure mode you can bound.** A prompt that is load-bearing for detection trades
one measured false positive against an unknown number of unmeasured false
negatives, and that trade cannot be evaluated from the thing you were trying to
fix.

#### B. The false positive survived, and that is the finding

The grounding did exactly what it was designed to do. The document's severity
fell from maximum to intermediate, closing the standalone rule's route to a
takeover verdict. **The case remained a false positive.** Sanitisation removes
the content, the sanitised probe therefore reports nothing, the difference
between the two regimes becomes non-zero, and the causal rule fires where the
severity rule no longer does.

Closing one route to a takeover verdict simply routed the same case through
another. The detector has three independent routes — a target lifted from the
content, standalone severity, and the causal contrast — and a false positive is
eliminated only when every route has been considered. Repairing the severity
function was necessary and insufficient.

We are leaving it open, and the reasoning matters more than the number. The
surviving route is the causal rule, which Volume I established as the mechanism
responsible for fourteen detections that the simpler rule cannot make. Weakening
it would purchase a change from two false positives in sixty to one, a difference
lying well inside a confidence interval spanning roughly one to eleven percent —
which is to say, not a measurable improvement at this sample size. The causal
reading is moreover arguably correct: sanitisation genuinely changed the probe's
behaviour, and that is a real effect. The document is benign; the measurement is
not lying. This is the boundary already identified in Volume I — the detector
cannot distinguish an authorised recipient from an attacker-controlled one —
appearing in a new form. It is recorded as a known bounded false positive rather
than repaired.

#### C. The trainer executed, and the hardware premise retired

Half of the policy-gradient trainer had never been run. It is implemented twice —
once for accelerated hardware and once in the standard library — and every result
in Volume I came from the second, because the development machine has no torch
and the regression suite is deliberately free of it. Two implementations of one
algorithm that have never been compared are two algorithms.

They now agree to exactly zero on the incumbent's reward, on each
implementation's reported reward when independently recomputed, on the
accept-or-reject verdict, and on the final proposed action. One difference is
worth recording: the two policies selected *different* preferred actions and
nonetheless produced the same proposal, because the stochastic search diverged
while the deterministic verification converged. That is the verification step
performing its function, and independent evidence for Volume I's argument that a
learned policy's preference cannot serve as a decision rule, since it is not
stable across random streams let alone across implementations. The verifier
rejected the policy's preferred action for a fourth time.

The phase had been framed throughout as training on a freely available
accelerator. That is not possible: the card offered is of a compute capability
below the minimum the installed torch supports, and the availability predicate
returns true regardless, so the failure arrives at the first tensor allocation
rather than at the capability check. Device selection now probes with a real
allocation and falls back to the processor. Nothing of substance is lost — the
search is a few thousand floating-point operations over a small table and
completes in about a quarter of a second on one core — and the honest restatement
is that the phase is validated as an off-machine cross-check of two
implementations, not as accelerated training.

Reaching that result took six attempts and exposed five defects, each visible
only once its predecessor was repaired. The one worth carrying forward is the
orchestration script's status poll, whose case-sensitive patterns could match
neither the success nor the failure string: it ran to its iteration limit against
an already-dead job, downloaded whatever was present, printed a completion
message and exited zero. It converted every other failure in the sequence into a
reported success.

#### D. The human gate, and what it found immediately

The commit function had always refused to act without an explicit approval flag,
so the seam was correct; what was missing was anything on the far side of it, the
only caller having supplied the flag as a constant. The gate now recomputes both
the incumbent and the proposed configuration from the labelled episodes and
presents its own arithmetic beside the proposer's claim, on the principle that a
proposal's self-report is exactly what cannot be trusted. It recommends and never
decides, and requires a recorded reason, since an approval without one cannot be
audited afterwards.

On its first execution against a real proposal it reported a defect present in
every proposal the trainer has ever produced: the candidate blocking patterns
cannot fire. The static triage layer matches such patterns against the agent's
*proposed action*, while the trainer harvests candidates from the screener's
*matched markers*, which describe untrusted content. These are different
namespaces; the string in question appears as a marker on forty-eight of one
hundred eighty-eight episodes and in none of the proposed actions. A rule that
presents as protection while providing none is worse than no rule. We note that
this was invisible to the trainer, to its reward function, to the verification
step and to the minimality pass, because all four reason about reward, and an
inert rule changes reward by exactly nothing.

#### E. A benchmark that could not measure what it was built for

The eight-vector benchmark was constructed to answer the question the campaign
cannot: not "does the system work" but "which layer is doing the work". Four
configurations of the same pipeline were run over a fixed vector set drawn from
the published threat taxonomies — undefended, static-only, complete, and complete
without the egress allowlist — with the ablation implemented inside the pipeline
rather than in the runner, so that the arms share one code path and differ only
in flags.

The first result appeared clean and we reported it. Attack success fell from one
hundred percent undefended to fourteen point three percent under static defenses
alone, and the complete system matched that figure exactly while raising workflow
continuation from zero to seventy-one point four percent. The apparent finding
was that the causal sub-layer contributes no additional detection and instead
contributes usability.

**That finding is withdrawn.** Inspecting which component actually stopped each
case shows that in the static-only arm nothing was blocked by any detection
layer: every stop came from the egress allowlist, because six of the eight
vectors were written to point at an exfiltration host. The complete arm scores
identically for the same reason. The benchmark cannot distinguish detection
layers, because a static allowlist intercepts almost every vector before any
detection layer is consulted, and the two arms are therefore equal by
construction rather than by measurement.

The lesson is one this project had already learned and then repeated. Volume I
added address-free attacks precisely because the allowlist was concealing
detection failures, and we then designed a vector set in which the allowlist
conceals everything. The remedy is the same as before: point the malicious
vectors at the legitimate destination so that a detection failure becomes
visible, and record which layer stopped each case rather than only whether it was
stopped.

#### F. The pattern, restated

Volume I observed that the instruments built to judge this system have failed
more often than the system itself. This session added three more. The report that
computes the false-positive rate served figures from a campaign that had crashed
part-way, because it reads whatever file is present and cannot tell whether it is
current; it now refuses to print without saying how old the data is. The
cross-implementation check produced a confident failure verdict by comparing the
rewards of two different actions. And the benchmark above produced a headline
result that measured its own construction.

None of these was part of the defended system. All three were tools written to
establish confidence, and each announced a conclusion it had not tested. We
continue to find that code which reports an untested verdict is more hazardous
than code that fails outright, because a crash is self-reporting whereas a false
pass is indistinguishable from success — and is trusted precisely because it was
written to be trustworthy.

#### G. State, and what this does not establish

Detection stands at one hundred sixteen of one hundred twenty, with four residual
failures, none of them reachable by the threshold the adaptive component
controls. The false-positive rate against externally-authored benign content is
three and three-tenths percent. The regression suite comprises one hundred
thirty-five deterministic tests requiring no language model, no network and no
accelerator.

What this entry does not establish: whether the causal sub-layer detects attacks
that static defenses miss remains **untested in either direction**, because the
only benchmark built to answer it could not. We do not claim the answer is
negative; we claim we have not yet measured it. The workflow-continuation result
survives — the removal of the sanitiser genuinely converts safe continuations
into blanket blocks — but it was obtained from the same flawed run and should be
re-derived once the vector set is repaired. Finally, the false-positive column of
that benchmark rests on a single benign vector, which is the very weakness Volume
I spent an entire entry correcting for the campaign corpus.
