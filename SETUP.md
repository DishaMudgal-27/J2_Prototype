# Setup: running the J2 demo

J2 is a group of AI agents (Identity, Adaptation, Priority, Coordination, Audit) that build a website from your
brief in a group chat. You type the brief in a local web page; the agents ask you questions, plan, build and
check the site. See `README.md` for how the flow works.

## What you need

| Need | Why |
|---|---|
| Python 3.9 or newer | Runs the server (`python3 --version` to check) |
| **Claude Code CLI, logged in to a Claude subscription** (Pro or Max) | The normal way to run: every agent call goes through `claude -p` on your subscription, so no API key and no API bill |
| Google Chrome (optional) | Audit screenshots the site at 360px and 1280px. Without Chrome, Audit judges from code only. Set `J2_CHROME=/path/to/chrome` if it is not in the usual place |
| An API key (optional) | Only if you do not use the Claude subscription: `ANTHROPIC_API_KEY` or `GEMINI_API_KEY` |

### Install and log in to Claude Code

```bash
npm install -g @anthropic-ai/claude-code   # or see https://docs.claude.com/en/docs/claude-code
claude                                      # first run: log in with your Claude account, then exit
claude -p "say hi"                          # check: should print a reply
```

The server removes `ANTHROPIC_API_KEY` from the environment it gives `claude -p`, so subscription runs never bill
the API, even if the key is set.

## One-time setup

```bash
git clone https://github.com/DishaMudgal-27/J2_Prototype.git
cd J2_Prototype
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # optional: fill in only what you use. .env is never committed
```

## Run it

Always activate the virtual env first:

```bash
source .venv/bin/activate
```

### Normal run: your Claude subscription (recommended)

```bash
STUDIO_PROVIDER=claude-cli python3 j2_server.py
```

Opens http://127.0.0.1:8773. Type a brief (or pick an example card) and answer the team's questions.

### Clean test run: fixed budget, no memory, no delay

```bash
J2_FIXES=0 J2_BUDGET=40 J2_MEMORY=0 STUDIO_PROVIDER=claude-cli J2_DELAY=0 python3 j2_server.py
```

- `J2_FIXES=0`: baseline flow, as close to the J2 diagram as possible
- `J2_BUDGET=40`: starts with a budget of 40 instead of 100, so budget pressure shows up sooner
- `J2_MEMORY=0`: no lessons read or written, so runs do not affect each other
- `J2_DELAY=0`: no pause between AI calls (the pause is only for free-tier API rate limits)

### Other ways to run

```bash
# With the fixes turned on (over-budget rulings go back to Priority once; change requests go to Identity first)
J2_FIXES=1 STUDIO_PROVIDER=claude-cli python3 j2_server.py

# Pick the Claude model (default: sonnet)
CLAUDE_CLI_MODEL=opus STUDIO_PROVIDER=claude-cli python3 j2_server.py

# API key instead of the subscription: leave STUDIO_PROVIDER empty and set ANTHROPIC_API_KEY or GEMINI_API_KEY in .env
python3 j2_server.py

# Offline demo: scripted agents, no Claude and no key needed
STUDIO_MOCK=1 python3 j2_server.py

# Different port, or do not open a browser
STUDIO_PROVIDER=claude-cli python3 j2_server.py --port 8780 --no-browser
```

Provider order: `STUDIO_PROVIDER=claude-cli` wins. Otherwise `ANTHROPIC_API_KEY`, then `GEMINI_API_KEY`, then mock.

## Settings

Set any of these before `python3 j2_server.py`, like the examples above.

| Setting | Default | What it does |
|---|---|---|
| `STUDIO_PROVIDER` | unset | `claude-cli` runs on your Claude subscription |
| `CLAUDE_CLI_MODEL` | `sonnet` | Model for `claude -p` |
| `STUDIO_MOCK` | off | `1` runs offline with scripted agents |
| `J2_FIXES` | 0 | `1` turns on the two flow fixes |
| `J2_BUDGET` | 100 | Starting budget |
| `J2_BUDGET_CAP` | 2 x budget | Most your approvals can raise the budget to |
| `J2_MEMORY` | 1 | `0` turns lessons and playbooks off |
| `J2_DELAY` | 2 | Seconds between AI calls |
| `J2_MAX_CYCLES` | 6 | Plan, build, audit cycles before Identity asks you what to do |
| `J2_MAX_TURNS` | 30 | Agent turns per cycle |
| `J2_LIMIT_ADD` | 30 | Budget "keep working" adds when the budget runs out |
| `J2_RATES` | 1 | `0` turns the rate card off |
| `J2_CHROME` | auto | Path to Chrome for Audit screenshots |
| `J2_OVERRIDE_KEY` | unset | Owner override key, set in `.env` only (see `README.md`) |

## Checks

```bash
python3 j2_flow_test.py           # offline flow test in mock mode, both J2_FIXES modes
python3 j2_check.py site.html     # render check on any HTML page
```

## Where output goes

Each run is saved under `runs/` (chat log, AI calls, site versions, screenshots). Past runs open read-only from
the page. Lessons are kept in `memory/`. Both folders are git-ignored.

## Troubleshooting

| Problem | Fix |
|---|---|
| `claude -p failed` | Run `claude -p "say hi"` in a terminal. If it fails, log in again with `claude` |
| `claude: command not found` | Install Claude Code and make sure it is on your `PATH` |
| `Chrome not found` in Audit | Install Chrome or set `J2_CHROME` |
| Port 8773 in use | Add `--port 8780` |
