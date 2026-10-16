# atom/1: the work atom schema

One standard shape for a work atom. `j2_schema.atom_view(atom)` builds it from a stored atom; nothing stored is renamed.
`runs/<id>/atoms.json` holds the views at the end of a run: `{"schema": "atom/1", "atoms": [...], "warnings": [...]}`.
The machine form is `docs/atom-schema.json`.

## Fields

| Field | Meaning | Comes from today's atom |
|---|---|---|
| id, workflow, name, owner, status, attempt | who and where | id, workflow id, workflow name, how.agent, status, attempts |
| goal, how, constraints, context | what it was asked | same names |
| defined_output | what must exist when it is done | expected_output |
| verification | list of `{check, applies_to, method, met, evidence}` | results (the receipts) |
| output | list of `{name, type, kind, ref}` | agent_output |
| depends_on, used_by | lists of `{atom, why}` | recorded by the run (see Edges) |
| notes | plain words, 1 to 2 sentences | human_output |
| details | optional free object, type-specific | agent_output (selectors, ids, anchor), expected_output (elements) |

Website words (selectors, elements, sections) are never standard fields: they live in `details`.

## Output items

- `type`: `artifact` (a thing made) or `effect` (a change caused).
- `kind`: open-ended text. Today: `section`, `document-section`, `file` (artifacts); `behaviour` (effect).
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

An edge to a missing atom; a cycle; an atom whose output is never used and is not a final output (kinds `section`,
`document-section`, `document`, `page`); an output item without a type.
