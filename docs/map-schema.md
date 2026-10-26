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

## Nodes: `{id, kind, row, label, status, version, detail, file, workflows, tag, color, lane}`

`lane` (work and step nodes): `"trunk"` for the Charter, the documents and the site, in order; `"branch"` for a side job (a send
deed) and its step. A branch's step starts at the document the deed was built from (its recorded `depends_on`, else the last trunk
box before it), so a deed never sits between two documents, and the site's step takes the last document as its input. Nodes are
listed in drawing order: each trunk box, the side jobs that leave it (step, then deed), then the step to the next trunk box.

**Every workflow is placed.** Each workflow in `workflows.json` sits on one box, decided in this order: a realization decide
workflow (the plan's kind, else an `artifacts/` file with a stage) gets its own spec box `work:<workflow id>`, labelled with its
stage's `output` from `agents/j2/stages.json`; a revision joins the box of the workflow that owns its section; a workflow of a
stage joins the box that holds its stage-mates; a section in `stage-<doc>.json` or `sections.json` names its document (or the
current one); last, the output refs (`artifacts.json`). One that fits none is listed by id in `not_recorded` as "workflows not
placed on the map: W-n, ...", never dropped. A realization run's trunk is Charter, the specs, then the Website. A spec has a
hand-off labelled "given to W-n, ..." to every box whose workflows read it (`dependencies`, the plan's `inputs_from`).
The style guide (`style.json`) is a small side job `work:style`, made by the workflow with `style_guide` true.

| kind | row | what it is | built from |
|---|---|---|---|
| person | people | the Requester ("You") | chat (messages from the Requester, a pending question) |
| work | work | the Charter, each deliverable the run built (`types.json`: PRD, HLD, LLD, website), a send deed | `goal.json`, `artifacts.json` (version, workflows, file), atom/1 (status), `types.json` (label, tag, colour) |
| engine | work | the step between two work boxes, named by what its workflows do (Write, Build, Send) | the workflows of the box it leads to: count, and checks passed of those atoms |
| function | functions | Identity, Adaptation, Priority, Coordination, Audit | the live lanes (running run) or the chat (finished run); calls, seconds and tokens from the call log |
| know | | what the work draws on | a later version |

A function node also has `calls`, `seconds`, `tokens {input, output}`, `tab` (the existing tab that shows its work: Identity
Charter, Adaptation Workflows, Priority Conflicts, Coordination Timeline, Audit Audit), `wait_on` (who it waits for) and
`detail` (the one line on what it is doing). An engine node also has `made_by`, `team` (the role of its box's stage from
`stages.json`, or null: the page then names it from the output type) and `unchecked` (the workflows set to done whose atom did
not pass its checks; the page counts them in the team label).

**Function states.** A running run uses `lanes()`: working is `running`, waiting is `waiting` (`wait_on` names who), blocked is
`fault`, idle is `idle` with "last seen: ...". Waiting on the Requester is `waiting_on_you` only while a question to the Requester
is open (the page's Needs you strip reads the same question); otherwise it is `idle`. A finished or old run has no
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
| done_unchecked | a workflow is `done` in `workflows.json` but its atom is `verify_failed` or still `open`: "done · checks did not pass" | thick amber dotted edge |
| running | live run: an atom is `open`, or a function is working | double edge |
| left_open | finished run: an atom is still `open` | dashed edge |
| fault | an atom is `verify_failed` and its workflow is not `done`; a function is blocked | thick red edge and "!" |
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

**Wide (900px and up): a metro line.** One horizontal trunk: the Charter, the documents and the site are diamonds on the line,
evenly spaced; the team that made each one (a ring of five dots, "<Persona> · N workflows") sits on the stretch of line leading into
it. Under each diamond (or above, when a line or a side job leaves from below): its name and one fact line ("v6 · 13/13 checks", or
"not recorded"). A side job (a send) leaves its parent diamond on a short branch below the line (above it when a line already
passes under that diamond): its team, then a letter icon with "Test email · dry run, not sent". "Given to" lines that skip a stop
run faintly above the line, flat over the labels, or under it and up to the team that used the document; two that would
interleave go on opposite sides, and the code checks every pair of drawn lines for a crossing. A line that cannot be placed is
drawn round the outside and listed under "Not recorded". The Management layer is one row of chips above: You (with the messages
from you), then Client Lead, Strategist, Prioritiser, Scheduler and Quality Reviewer (each with its AI calls). Lines from a chip to
the work it did, and messages between functions, are shown on hover or in the "Messages between functions" table.

**Narrow (under 900px)** the trunk runs top to bottom with side jobs in a column beside it; at 600px and under the map is a list of
cards.

**Colour means status only:** green = filed and checked, amber = waiting on you, red = fault, grey = not made or idle; a dashed
outline = left open, a double outline = running now; "!" and "?" marks as before. The status chip is green when the checks pass,
amber with "Audit: needs revision" when the latest Audit says the work is not workable yet, and neutral "No checks yet" before any
check ran. The Needs you strip's outcome line names what is left open (for example "1 item left open: test email (dry run)").

Every display label comes from one table in the page (`MAPLABEL`). `renderMap(map)` is one pure function; all text goes through the
Detailed view's plain-words helper.

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
