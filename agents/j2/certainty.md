---
axis: certainty
used_by: adaptation (only when J2_CERTAINTY=1)
source: Cynefin (Snowden): Clear, Complicated, Complex, Chaotic
replaces: decomposition.md (first draft)
---

# Certainty: read it before you cut

Before you propose, read how well cause and effect are known for this goal. The reading decides the
approach, and the approach decides how you cut the goal into workflows. A formula does not work on an
experiment problem: if you had the formula, you would not need the experiment. The reverse also holds:
running experiments on a fully specified request wastes the budget.

Certainty is not intelligence. Your knowledge decides *where* to cut (which sections, which seams).
Certainty decides *what kind* of cut is allowed (build, analyse first, probe first, or stabilise).

## The four zones

| Zone | Cynefin | Cause and effect | Approach | What your workflows must look like |
|---|---|---|---|---|
| `operate` | Clear | Known. Facts given, a known pattern turns them into the output | sense, categorise, respond | Direct build workflows along the obvious seams. No analysis, no probes |
| `analyze` | Complicated | Knowable by analysis. The material is there but the insight is not: several valid structures or interpretations, and a wrong pick wastes budget | sense, analyse, respond | Your `analysis` comes first: options you weighed, what you chose and why, each assumption. Then build workflows that follow the choice |
| `experiment` | Complex | Knowable only by trying. Success depends on how people react (visitors, customers), and no analysis settles it in advance | probe, sense, respond | 1 to 3 small probe workflows, each with a hypothesis, the signal that tests it, what would prove it wrong and a limit. Items that depend on the result go in `deferred`, not in a full plan now |
| `stabilize` | Chaotic | Unknown, and the site is broken now: the cause is unclear, or the last fix for the same failure did not work | act, sense, respond | One small workflow that returns the broken section to a working state (simplest version that passes, or the last version that passed). No new items. Say what is still unknown |

Two mistakes this framework exists to stop:
- **Missing facts are not `experiment`.** If a name, price, date or email is missing, nobody can find it by
  trying. Ask Identity (POLICY_QUESTION) or use what J2.a recorded as "to be confirmed". Experiment is for
  questions that only people's reactions can answer.
- **An ordinary fix is not `stabilize`.** A JS error, an overflow or a missing button with an obvious cause is
  `operate`: fix it directly. Stabilize is for a break whose cause you can't name, or a fix that already
  failed once.

## Read the signals, then apply the rule

Answer each signal for the goal as a whole, with `yes`, `no` or `unknown`, and quote the brief, charter or
finding that decided it. "unknown" is a valid answer; a guess is not.

| Id | Signal | Points to |
|---|---|---|
| `broken` | Is the site broken in a way whose cause is unclear, or did a fix for the same finding already fail? | stabilize |
| `reaction` | Does success depend on how people will react, in a way no analysis can settle before trying? (e.g. "make it convert", "find out which offer people pick") | experiment |
| `facts_given` | Are the facts the output needs given (names, numbers, prices, dates, content, rules)? | operate |
| `known_pattern` | Is there a known pattern or formula that turns those facts into the output? | operate |
| `open_choices` | Are there several reasonable structures or interpretations, where a wrong pick wastes budget? (unranked feature lists, style words like "earthy", a lot of material with no priority) | analyze |

**The rule** (code applies the same rule and checks your reading against it):
1. `broken` yes → `stabilize`.
2. `reaction` yes → `experiment`.
3. `facts_given` yes and `known_pattern` yes and `open_choices` no → `operate`.
4. Otherwise → `analyze`.
5. Then, if two or more signals are `unknown`, move one zone toward less certainty (operate → analyze →
   experiment). When in doubt, choose more learning: a confident plan aimed the wrong way costs the most.

## Per workflow

The overall zone is the reading for the goal. Each workflow also carries its own zone, because one goal can
mix them: a countdown to a fixed date is `operate`, "feel sporty" is `analyze`, "which hero gets more sign-ups"
is `experiment`. A workflow's zone can be equal to or more certain than the overall zone, never less, unless
you say why in `approach`.

- `operate` workflow: normal fields. `approach` names the pattern ("standard contact form, every field given").
- `analyze` workflow: `approach` names the choice it follows from your `analysis`.
- `experiment` workflow: fill `experiment`: `hypothesis` (what you believe), `signal` (what Audit or the
  Requester will show: an Audit check, a screenshot finding, or the Requester's answer to a question Identity
  asks after the build), `fails_if` (the result that would prove the hypothesis wrong) and `limit` (at most
  what it may cost). A probe is real work on the site, kept to the minimum that tests the hypothesis.
- `stabilize` workflow: `parts: ["fix"]`, `revises` the broken section, `fixes` the finding ids, no `covers`
  of items not built before.

## The dial moves between cycles

Read certainty again at every J2.b. `LAST CERTAINTY READING` in your task shows your previous reading.
- After a probe: the signal came in, so certainty rises. Propose the deferred items as `analyze` or `operate`.
- After a fix fails twice: certainty drops to `stabilize`.
- After the Requester answers a question: re-read `facts_given` and `open_choices`.
Say in `rationale` what changed since the last reading.

## Reply fields (on PROPOSE)

```json
{
  "certainty_assessment": {
    "zone": "analyze",
    "signals": {
      "broken": {"answer": "no", "evidence": "no open findings"},
      "reaction": {"answer": "no", "evidence": "brief asks for a catalogue, not a result to test"},
      "facts_given": {"answer": "yes", "evidence": "prices and sizes listed in the charter"},
      "known_pattern": {"answer": "yes", "evidence": "product grid with filters"},
      "open_choices": {"answer": "yes", "evidence": "11 features, no priority; 'earthy and elegant'"}
    },
    "rationale": "Facts are given but the structure is open: grouping decides cost and coverage."
  },
  "analysis": {
    "options": ["group by user journey", "one workflow per feature"],
    "chosen": "group by user journey: browse, buy, trust",
    "why": "fewer sections, each closes several items, browse is the entry point",
    "assumptions": ["'earthy' means warm browns and off-white, serif headings"]
  },
  "deferred": [],
  "workflows": [
    {"name": "Browse", "certainty": "analyze", "certainty_signals": ["features unranked"],
     "approach": "Follows the journey grouping chosen in analysis", "experiment": null, "...": "the usual fields"}
  ]
}
```

For `experiment`, `analysis` may be null and `deferred` lists the items waiting on the probe:

```json
{
  "deferred": [{"item": 4, "until": "W-1 probe signal: does the Requester pick the weekend-bundle hero?"}],
  "workflows": [
    {"name": "Hero probe", "certainty": "experiment", "certainty_signals": ["'whatever converts best'"],
     "approach": "Two hero offers on one page; keep the one the Requester picks",
     "experiment": {"hypothesis": "A bundle price beats a single-game price as the main offer",
                    "signal": "Identity shows v1 and asks the Requester which offer to keep",
                    "fails_if": "the Requester rejects both offers",
                    "limit": "one hero section, no other sections changed"}}
  ]
}
```

## Boundaries and failure patterns

- Low certainty changes the approach; it is never a reason to do less or to refuse.
- Don't call work `operate` to skip analysis, or `experiment` to look careful.
- Don't put new features inside a `stabilize` workflow.
- Don't write a zone without the signals that justify it.
- Deferred items are still owed: propose them in the next cycle once the signal is in.
