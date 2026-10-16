# atom/1: the work atom schema

One standard shape for a work atom. `j2_schema.atom_view(atom)` builds it from a stored atom; nothing stored is renamed.
`runs/<id>/atoms.json` holds the views at the end of a run: `{"schema": "atom/1", "atoms": [...], "warnings": [...]}`.
The machine form is `docs/atom-schema.json`.

## Fields

| Field | Meaning | Comes from today's atom |
|---|---|---|
| id, workflow, name, owner, status, attempt | who and where | id, workflow id, workflow name, how.agent, status (see Status), attempts |
| goal, how, constraints, context | what it was asked | same names |
| defined_output | what must exist when it is done | expected_output |
| verification | list of `{check, applies_to, method, met, evidence}` | results (the receipts) |
| output | list of `{name, type, kind, ref}` | agent_output |
| depends_on, used_by | lists of `{atom, why}` | recorded by the run (see Edges) |
| notes | plain words, 1 to 2 sentences | human_output |
| details | optional free object, type-specific | agent_output (selectors, ids, anchor), expected_output (elements) |

Website words (selectors, elements, sections) are never standard fields: they live in `details`.

## Status

Exactly four values: `open`, `closed`, `verify_failed`, `abandoned`.

| Today's name | Value | Note |
|---|---|---|
| atom `passed` | closed | clean |
| atom `escalated` | verify_failed | clean |
| atom `failed`, workflow not running or 3 attempts used | verify_failed | `failed` is also written after an attempt that will be retried, so it is only final by the workflow status or the attempt count |
| atom `failed`, workflow `running`, under 3 attempts | open | retry in progress |
| no status yet | open | clean while the run is live |
| no status yet, run ended, workflow not `done` (registered, held, running) | abandoned | clean: never built |
| no status yet, workflow `unfunded` | abandoned | clean |
| no status yet, workflow `done` | open | does not map cleanly: stored before atoms had a status; kept open, not forced |
| atom `could not run` | open | does not map cleanly: the check had no browser; it is neither failed nor verified |
| workflow `registered`, `held`, `running`, `done`, `failed`, `unfunded` | not an atom status | used only to decide the atom's value above |

Dropped or left-out items have no atom status of their own: an atom of a workflow the run never built is `abandoned` once
the run has ended.

## Output items

- `type`: `artifact` (a thing made) or `effect` (a change caused).
- `kind`: open-ended text; unknown kinds are recorded, never rejected. Artifact kinds start from `doc`, `code`, `page`,
  `test`, `plan`, `skill`, `app`. A built website section is `page` (ref: its anchor); PRD, HLD and LLD are `doc`
  (ref: file and heading). Their files use the same kinds by extension (`.md`, `.docx` are `doc`, `.html` is `page`).
  There is no `section` kind. Effect kinds: `behaviour` (scope self), `fetch`, `send` (the last two are external and not
  produced yet).
- `ref`: a file path, a section anchor (`site/index.html#hero`), a document heading (`prd.md#Problem`) or a trace id (`W-3.a1:1`, the receipt).
- An effect's `details.scope` is `self` (it changes only the thing built) or `external` (it reaches outside).

## Checks by type

| Type | Check | Meaning | Produced today |
|---|---|---|---|
| artifact | exists | the thing is there | yes (element-count, heading-present, section-not-empty, file-exists, grep-count) |
| artifact | matches the defined output | it is what was asked | yes (facts-present, lld-slice) |
| artifact | valid under the rules | it breaks no rule | yes (named-test, tap-targets, ids-unique) |
| effect | occurred | evidence is a trace or log | yes, for behaviour steps run in Chrome or by the fake driver (scope self); ref is the receipt |
| effect | observed result | what was seen after it | defined, not produced |
| effect | within limits | it stayed inside its limits | defined, not produced |
| effect, scope external | all three | fetching data, sending | defined, nothing produces them |

## Edges

`depends_on` is recorded from what the builder's prompt actually held, where the prompt is made:

- the manifest lines of other atoms (J2_SLIM=1): one edge per atom listed;
- an LLD slice: the LLD atoms that wrote the slice's sections, elements and fields;
- the HLD component summary: the HLD Components atoms;
- a document builder's charter: the PRD Requirements atoms (HLD, LLD), the HLD Components atoms (LLD).

`used_by` is the same edges from the other side, built by code. When a builder was given the whole page and no edge can
be attributed, edges come from the workflow's declared dependencies; if it has none, they stay empty. Edges are never
guessed. Runs stored before this schema have no record of what a prompt held, so only declared dependencies apply.

## Warnings (never change an outcome, a prompt or a retry)

An edge to a missing atom; a cycle; an atom whose output is never used and is not a final output (kinds `page`,
`doc`); an output item without a type.
