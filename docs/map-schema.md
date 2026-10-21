# map/1: the Map of a run

`runs/<id>/map.json` is written by code (`j2_map.build`) beside `atoms.json`: once with the summary and again after the
report, additive, never changing a run (a failure is only an event). `/api/map` serves the same shape for a live run (drawn
from its live state), a saved run (`map.json`, else rebuilt from the folder) and an old run with no `artifacts.json` or
`atoms.json` (rebuilt from the folder and `workflows.json`). A missing run gives an empty map. No model call is involved.

Version 2 draws the Requester, the Functions row (Identity, Adaptation, Priority, Coordination, Audit) and the Work row.
The Knows row is a later version: its node kind is in the schema, nothing is drawn or invented for it.

## Top level

| Field | Meaning |
|---|---|
| schema | `"map/1"` |
| run | the run folder name |
| live | true when built from a running run |
| status | `{state, state_status, checks: {passed, run}}`: the top line ("Identity running", "Waiting on you", "Done", "Done with open items", "Stopped", "not recorded") and the checks of every work atom that ran |
| nodes, edges | below |
| legend | `[{key, label, drawn}]`: what the drawing explains; `drawn: false` for kinds a later version draws |
| built_from | the files the map was built from |
| not_recorded | what the run did not record and the map therefore shows as "not recorded" |

## Nodes: `{id, kind, row, label, status, version, detail, file, workflows, tag, color}`

| kind | row | what it is | built from |
|---|---|---|---|
| person | people | the Requester ("You") | chat (messages from the Requester, a pending question) |
| work | work | the Charter, each deliverable the run built (`types.json`: PRD, HLD, LLD, website), a send deed | `goal.json`, `artifacts.json` (version, workflows, file), atom/1 (status), `types.json` (label, tag, colour) |
| engine | work | the step between two work boxes, named by what its workflows do (Write, Build, Send) | the workflows of the box it leads to: count, and checks passed of those atoms |
| function | functions | Identity, Adaptation, Priority, Coordination, Audit | the live lanes (running run) or the chat (finished run); calls, seconds and tokens from the call log |
| know | | what the work draws on | a later version |

A function node also has `calls`, `seconds`, `tokens {input, output}`, `tab` (the existing tab that shows its work: Identity
Charter, Adaptation Workflows, Priority Conflicts, Coordination Timeline, Audit Audit), `wait_on` (who it waits for) and
`detail` (the one line on what it is doing). An engine node also has `made_by`.

**Function states.** A running run uses `lanes()`: working is `running`, waiting is `waiting` (`wait_on` names who; the
Requester gives `waiting_on_you`), blocked is `fault`, idle is `idle` with "last seen: ...". A finished or old run has no
live state: every function is `idle` with "last seen: <its last message>", never `running`. A question left unanswered
(live `paused`, or the last chat message carries `pause`) puts `waiting_on_you` on Identity and on the Requester node.
Without a chat the line says "no message recorded", and without `calls.jsonl` the counts are 0 and the gap is listed.

Ids are stable: `person:requester`, `work:charter`, `work:prd`, `work:<workflow id>` (a deed), `step:prd>hld`.
`file` is the artifact or record the box opens in the Artifacts tab (`goal.json` for the Charter, `receipts.jsonl` for a
deed). `version` is `null` when the run did not record one: the page says "version not recorded".

## Statuses

| status | from | drawn |
|---|---|---|
| filed | every atom of the box is `closed` (a file with no atoms recorded counts as filed) | solid edge, tinted |
| running | live run: an atom is `open`, or a function is working | double edge |
| left_open | finished run: an atom is still `open` | dashed edge |
| fault | an atom is `verify_failed`; a function is blocked | thick red edge and "!" |
| waiting | a function waits for another function | thick amber edge and "?" |
| waiting_on_you | a question to the Requester is pending | thick amber edge and "?" |
| not_made | planned but not built, or every atom `abandoned` | hollow |
| idle | nothing to say | plain |

In a finished run the page says "left open", never "running".

## Edges: `{from, to, kind, label, n, basis}`

- `step`: box to engine to box, `n` = workflows of the box it leads to.
- `handoff`: from atom `depends_on` between boxes (`basis: "recorded"`), from `types.json` dependencies not already seen, and
  Charter to the first box (`basis: "declared"`: by order, not recorded).
- `speaks_to`: message counts from the chat: Requester to Identity (their messages), Identity to the Requester (messages
  addressed to them), and function to function (`who` to `next`). Messages to and from workflow agents (W-n) are not drawn.
  Up to three function-to-function pairs are drawn as thin dotted lines with their counts; more go in a small table under
  the row, so lines never cross.
- `speaks_to` from a function to a work box (`to` is `work:...`), from recorded data only, `n` and `label` say what:
  - Identity to the Charter: `label: "wrote the charter"`, `n: null` (from `goal.json`; the run recorded no count).
  - each function to the PRD, HLD and LLD boxes: `label: "calls"`, `n` = its AI calls in the call range `documents.json`
    recorded for that document.
  - Audit to every box that has an audit in `stage-*.json` (documents and website; a plain site run uses `audits.json`):
    `label: "audits"`, `n` = the number of audits, unless the call range already gave Audit a `calls` edge.
  - The website and a deed get only the Audit line. Anything without a line is listed in `not_recorded`
    ("which function worked on X: not recorded", or "which other function worked on X (only Audit is recorded)").
  These replace the earlier `made` edges. A step node still has `made_by` (the same call counts per step) for the
  "Who made each step" table.
- `draws_on`: a later version.

## The page

Function-to-work lines use the same dotted "speaks to" style, are drawn under the boxes and stop at the top of a box, so
they never hide text. They are faint by default; hovering or clicking a function (or focusing it and pressing Enter)
highlights its lines and shows each count; a click keeps it highlighted until the next click. With more than 12 lines
none is shown until a function is hovered or clicked. A small "view" link on each function opens its tab.
`renderMap(map)` is one pure function: inline SVG at wide widths and a card list at 600px and under (the functions and the
work as a top-to-bottom list: "speaks to ...", "worked on: ..." on a function, "made with: Identity 3, Audit 2" on a work box,
"hands off to ...", and "made by ..." on a step; no SVG lines). Status is never colour alone. Every box with a `file` links to its Open view
in the Artifacts tab; the full text is in a tooltip. All text goes through the Detailed view's plain-words helper.
