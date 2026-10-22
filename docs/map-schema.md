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

The Map is a calm graph drawn in inline SVG, laid out the same way every time (no physics, no random positions). From the
top: You, the Management layer (the five functions), then the work as a tree down the middle. Charter is the root; below
it, each deliverable sits under the team persona that made it. Every node is a circle with its name beside or under it;
the version, status word, calls, last seen and the rest are in the tooltip and in a click panel. Status is never colour
alone: solid ring = filed and checked, dashed = left open, double = running now, thick red plus "!" = fault, thick amber
plus "?" = waiting, hollow and faint = not made.

Lines are thin and grey. Hand-off (down the spine, deliverable to persona to deliverable) is solid, "speaks to" is dotted,
and "given to" is a faint loop beside the spine. A "given to" loop ends on the persona that consumed the document (the step
that leads to the deliverable the hand-off recorded), never on a later document, so a deliverable that feeds more than one
step branches. If the map has no such step the loop ends on the box and the gap is listed under "Not recorded". The wording
stays "given to": the run records what was given, not proof of use.

No two drawn lines cross. Loops that would interleave go on opposite sides of the spine; the code then checks every pair of
lines for a crossing. A line that cannot be placed without one is drawn round the outside and listed under "Not recorded"
as "could not be drawn without crossing". Function-to-function lines that would cross another go in the "Messages between
functions" table instead. Function-to-deliverable lines are never drawn by default: hovering or focusing a dot lights it, the
lines that touch it and the dots at their other ends, and fades the rest; a click opens the panel and keeps it lit until the
next click, Close or Esc.

Every display label comes from one table in the page (`MAPLABEL`): rows (You, Management layer, Team layer and
deliverables), functions as "Persona (Function)" (Client Lead (Identity), Strategist (Adaptation), Prioritiser (Priority),
Scheduler (Coordination), Quality Reviewer (Audit)), team personas chosen from the step's output type (drafting a PRD:
Product Analyst; an HLD: Solution Architect; an LLD: Technical Designer; any other document: Specialist; building the
website: Web Developer; sending: Messenger) with a small line "drafting, building or sending, N workflows", and
"Checker (automatic)" for the validator. Ids and map.json are unchanged.

`renderMap(map)` is one pure function: SVG at wide widths and a card list at 600px and under (the same words: "speaks to
...", "worked on: ...", "made with: ...", "given to ..." and "made by ..."; no SVG lines). Every deliverable with a `file`
links to its Open view in the Artifacts tab, from the card and from the panel. All text goes through the Detailed view's
plain-words helper.

## Home and navigation

The Detailed view's home is the department name, the Needs you strip (with one plain outcome line and a See report link), the Map and the Chat (docked on the right; stacked below 900px). The left
rail has Map, Chat and one collapsed Internals folder holding every other tab (Preview, Goal, Workflows, Conflicts,
Timeline, Audit, Charter, Documents, Artifacts, Style guide, Lessons, Playbooks, Report, Run details, Run settings). Run settings holds what
to build, the saved-run selector, New run and Back to simple view; the full outcome banner is at the top of the Report. Each internal view
has a "Back to map" link. Needs you lists every open Requester question (the items that make a node "waiting on you"), each
with a button that scrolls to and focuses that question in the Chat.

A click on a node opens its panel; the panel's Open button goes to: a node waiting on you, its question in the Chat; You,
the Needs you strip; Client Lead (Identity), the Chat; Quality Reviewer (Audit), the Audit tab; the other functions, the
two tables under the Map filtered to them; a team persona's step, the Workflows tab filtered to that step's
workflows ("Show all" clears it); the Website, the site preview; the Charter, the Charter tab; any other deliverable, its
document in Artifacts. The page-side state for this (`MAPFILT`, `WFSTEP`) is never stored in map.json.
