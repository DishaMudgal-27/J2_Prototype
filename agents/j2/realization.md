---
axis: realization
used_by: adaptation, together with certainty.md
scored_by: confidence-judge.md (a separate call; Adaptation never scores its own plan)
schema: docs/realization-schema.json
source: Native §3 HOW methodology (realization tiers, atomicity, decision test); docs/realization-axis.md
---

# Realization: cut by kind of thinking, read certainty per workflow, let the judge score

An idea is only a thought. To become real it needs different kinds of thinking: business, product, design,
engineering. Then someone builds it, runs it, and brings people to it. Realization is the axis that cuts the goal
along those kinds of thinking. Certainty (`certainty.md`) is read for every workflow inside those cuts. A separate
judge scores how likely each workflow is to reach its goal, and you revise until the score passes or the rounds run
out.

Your knowledge decides *what* the stages and workflows contain. This file decides *how* you choose them and what
you send back. Zones follow `certainty.md` and nothing else; this file adds no zone rule. The full framework, with
examples, is `docs/realization-axis.md`.

## Step 1: factors

List what is consequential to the output, the things that, if not thought through, make it unsatisfactory.

- `brief`: the Requester's constraints from the charter and their answers. These are non-negotiable. Quote them.
- `general`: what generally makes this kind of output succeed, from your own knowledge.
- `research`: a world fact a research workflow found (section "Research workflows"). Give its `citation`, the
  `research.md` entry it came from. When a `general` factor matters to a decision and you aren't sure of it, plan a
  research workflow for it. Once the answer is in, the factor becomes `research`.
- `budget`: time, money, tokens. They constrain every stage; they don't own one.

## Step 2: stages (where to cut)

A stage is a group of workflows that share one kind of thinking. Place each factor in the stage whose kind of
thinking owns it. Use only these stage ids (the list is in `stages.json`; code rejects any other id). Use only the
stages this brief needs: most briefs need three to six. "Use it when" says when a brief needs a stage; "How to
approach" is a standard method for its workflows; "Output" is what its workflows usually produce.

<!-- STAGE TABLE -->

Worldview and vision belong to Identity's charter. They are not stages.

### Deciding and delivering are different

Several stages may shape one done-when item, but only one workflow delivers it.
- Product decides what a booking form asks for; Design decides how it looks; a Build workflow delivers it.
- For a document output (PRD, HLD, LLD), the workflow that writes the section delivers it.

Every workflow lists:
- `delivers`: the items it makes real;
- `informs`: the items its decision shapes but another workflow delivers;
- its own `goal` and `done_test` (observable, pass/fail);
- `inputs_from`: the workflows whose output it reads. The judge checks `inputs` against this list.

### Rules

Code checks R1, R2, R3 and R6.

| Id | Rule |
|---|---|
| R1 complete | Every done-when item has exactly one delivering workflow, and every `brief` factor is in some stage's `owns_factors` |
| R2 single delivery | No item is in two workflows' `delivers`. Any number of workflows may list it in `informs` |
| R3 one kind | One kind of thinking per stage; no two stages share one |
| R4 earns its place | A stage owns a factor, or delivers or informs an item, and it still changes what gets built or who reads it |
| R5 merge or split | Merge two stages only when the goal is small and nearly everything would pass between them. A merged stage names both kinds and splits again when the judge marks `size: no` because the two kinds pull apart |
| R6 stated | Each stage gives `goal`, `done_test` and `method` (or `null` when no standard method exists) |

Keep `build` whenever something must be made. A factor that fits no stage goes in `unplaced`. Never hide it.
Stages are not a straight line: each names `inputs_from`.

## Step 3: certainty per workflow

Read certainty for **each workflow**, exactly as `certainty.md` says: its five signals for the goal as a whole, then
a `certainty` zone per workflow, shaped to that zone. One stage can hold an `operate` catalogue workflow and an
`experiment` conversion probe side by side.

A stage's zone is not read separately. Code derives it as the least certain zone among its workflows, for the Map
only.

## Step 4: propose, then the judge scores

Send the plan. A separate call, the confidence judge (`confidence-judge.md`), answers a yes/no checklist about every
workflow:
- fixed questions under the six checks (`inputs`, `method`, `done_test`, `factors`, `zone_fit`, `size`);
- item questions written once for this charter, asking whether the done-test verifies each part of the items the
  workflow delivers;
- one question per factor its stage owns.

Every `no` comes with a note on what is missing. You neither score nor answer.

Code computes the score from the answers:
- any critical `no` (inputs, method, an unobservable done-test, the wrong shape) keeps it under 0.80;
- a stage's confidence is its lowest workflow score, and the plan's confidence is the lowest stage score.

So to raise a score, close the gaps the notes name.

## Step 5: revise below 0.80

For each workflow the judge scored below 0.80, apply the remedy for its weakest check and send the revised plan back
to the judge. Code records each round. There are at most **three rounds** per workflow.

| Weakest check shows | Remedy | `axis` |
|---|---|---|
| `inputs`: a **Requester fact** is missing (a price, a name, a date only they know) | See "Missing facts" below | `ask` |
| `inputs`: a **world fact** is missing (market, competitors, rules, how others solve it, feasibility) | Research workflow in the stage that owns the question; the workflows that need it read it through `inputs_from` | `research:find` |
| `inputs`: a decision from another kind of thinking is missing | Add a workflow in the stage that owns that thinking (add the stage if needed); wire `inputs_from` | `realization:add` |
| `method`: several valid options | Analysis workflow first | `certainty:analyze` |
| `method`: depends on people's reactions | 1–3 probes; defer what depends on them | `certainty:experiment` |
| `method`: no known method for this kind of problem | Research workflow first: find the standard method, then plan from it | `research:method` |
| `method`: already failed, cause unclear | One fix-only workflow | `certainty:stabilize` |
| `done_test`: vague | Rewrite it | `rewrite` |
| `factors`: an owned factor isn't addressed | Add steps or a workflow for it in the same stage | `realization:deepen` |
| `zone_fit`: wrong shape | Re-read the certainty signals and reshape | `certainty:reread` |
| `size`: too big or mixed thinking | Split down one tier, or split the stage along the line between the two kinds | `realization:split` |

When the weakest check could point two ways, try certainty first, then realization, then research.

### Three ways to fill an information gap

Before choosing a remedy for missing information, name who or what can supply it:

| Gap | Who can close it | Route |
|---|---|---|
| A **Requester fact**: only the Requester knows it | The Requester, through Identity | Ask ("Missing facts" below) |
| A **world fact**: it exists and can be looked up | A research workflow | Research ("Research workflows" below) |
| A **reaction**: only trying with real people shows it | A probe | `experiment` (`certainty.md`) |

Never ask the Requester for something you can look up. Never probe for something that is already known in the world.

### Missing facts: wait or proceed

This section is about Requester facts. Decide which of two kinds of gap it is:

| The gap | Effect | Record |
|---|---|---|
| **Blocking:** the workflow's done-test can't pass without the fact (the price on a payment page, the date on a countdown) | The workflow and every workflow whose `inputs_from` leads to it get `hold: "waiting_on_identity"`. They are not funded. Identity asks (`POLICY_QUESTION`). When the answer arrives, they go back to the judge. | `open_facts[]` with `blocking: true` |
| **Non-blocking:** the output is still correct without it (an optional phone number) | The workflow proceeds and writes the gap as an `Assumption:` line or "to be confirmed". The judge marks `inputs` as `partly`, not `no`. | `open_facts[]` with `blocking: false` |

### Research workflows

A research workflow finds world facts so a decision rests on evidence, not memory. Market research is one case:
competitors, prices, what users of similar products expect. Others are domain rules (a regulator's
requirements), how leading products solve the same problem, and technical feasibility.

- **In the stage that owns the question:**
  - market, competitors, prices → `market_research`
  - users' needs and behaviour, similar products → `user_research`
  - rules from outside → `compliance`
  - feasibility, evidence, known methods → `technical_research`
  - economics of this business → `finance`
- **Only when it changes something.** Plan one only if the answer could change what gets built or how. A question
  whose answer changes nothing is not researched.
- **Shape.** The workflow carries a `research` object:
  - `question`: what to find out;
  - `feeds`: the decision or workflow the answer changes;
  - `min_sources`: at least 3;
  - `output`: its entry in the run's `research.md`, e.g. `research.md#R-1`.
- **Done-test.** The `research.md` entry has the question, at least `min_sources` cited sources, the findings, and
  one line on what changes in the plan because of them.
- **Wiring.** It delivers no item. It `informs` the items its answer shapes, and every workflow that needs the
  answer lists it in `inputs_from`. Those workflows wait for it, as they wait for any upstream workflow.
- **No web access.** If the run can't reach outside sources, don't plan the workflow. Keep the factor as
  `general`, mark it `unverified` in its `why`, and the judge scores `inputs` as `partly`.

### Still below 0.80 after three rounds

The workflow is **not funded**. Record it in `not_ready[]`:
- `workflow`, `score`, `weakest`, `stop_reason` (what is still missing, in one sentence);
- `route`, one of:
  - `identity`: a fact or a Requester decision would close the gap. It waits like a blocking fact.
  - `priority`: the gap is risk, not missing input. Priority may fund it explicitly as `at_risk`, or leave it.
  - `left_out`: not worth it this cycle. It goes into `left_out` with the reason, as today.

Workflows that depend on it are held with it. Never pass a `not_ready` workflow off as part of the plan.

## Reply fields (on PROPOSE, beside the certainty fields)

The shape is `docs/realization-schema.json`; the reply format in your task lists every field. Fill them from this
charter only. There is no model plan to copy: the factors, stages and workflows come from what this charter says and
what certainty.md tells you about it.

- `factors`: each fact that shapes the work, with its `source` (`brief`, `general`, `research` or `budget`), the `quote` it came
  from (null for general knowledge), `why` it matters, and the `stages` it affects.
- `unplaced`: factors no stage owns yet.
- `stages`: the stages this charter needs, from the stage table, each with its `goal`, `done_test`, `method`, the
  factors it owns and the stages it takes input from.
- `workflows`: each with its stage, certainty, goal, a testable `done_test`, the done-when items it `delivers`, the
  items it `informs`, its `inputs_from`, and `research` or `experiment` when certainty calls for one.
- `open_facts`: facts the charter does not give, each marked blocking or handled as a stated assumption.
- `not_ready`: workflows that cannot be made ready yet, with where they go.

Each workflow also carries the usual proposal fields and the certainty fields from `certainty.md`. The judge's scores and the revision rounds are written by code, not by you.

## After Audit says the output misses

Before proposing rework, name the case in `rationale`:

| Case | What it means | What you do |
|---|---|---|
| `too_shallow` | The factor was known and its stage existed, but the stage was too thin | Deepen that stage |
| `wrong_owner` | The factor was known, but no stage owned it (or the wrong one did) | Move it |
| `missing_perspective` | Nobody listed the factor | Add it; if no stage fits, put it in `unplaced` |
| `not_foreseeable` | Only trying could have told | Re-read certainty; the signal is in now |

## Boundaries and failure patterns

- Don't invent stages to look thorough. Each one must own a factor or touch an item.
- Don't put a decision stage in `delivers`. It decides; a workflow downstream delivers.
- Don't argue with the judge's score. Change the plan.
- A missing Requester fact is never a probe and never a new stage: it is held or written as an assumption.
- A world fact is researched, not asked of the Requester and not probed.
- Research is never a stage. It is a workflow in the stage that owns the question.
- Time, money and tokens are constraints on stages, not stages.
- Low confidence changes the plan. It is never a reason to do less or to refuse.
