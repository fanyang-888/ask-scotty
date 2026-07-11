# Code Provenance Log

Every substantive piece of work in this repo gets an entry using the course
AI Use Modes guide's Minimal Submission Format, plus a review record. Each
entry names the commits/PR it covers (see [CONVENTIONS.md](../CONVENTIONS.md)).
No agent-generated change merges without a Critic/Red Teamer pass by a
teammate who did not prompt it.

## Summary table

| # | Artifact(s) | Origin | AI Use Mode | Review status |
|---|---|---|---|---|
| 1 | Entire initial scaffold (devcontainer, api/, infra/, docs/, Makefile, conventions) | Agent-generated | Operator/Agent | ⚠️ pending team Critic review |
| 2 | Personal-record guardrail robustness + clone-and-run fix (escalation.py, tests, pyproject, Makefile) | AI-assisted | Critic/Red Teamer + Editor/Refiner | ⚠️ pending team Critic review |

---

## Entry 1 — Initial repository scaffold

**AI Use Mode:** Operator/Agent (Claude Code, Fable 5) — generated the full
initial scaffold: devcontainer, repo structure, `POST /ask` Lambda handler,
response contract, structural guardrails, stub + Bedrock model providers,
versioned system prompt, test suite, SAM template, Makefile, and first drafts
of all documentation. Also Researcher/Analyst — before generating, the agent
read the Week 1–3 course decks and the AI Use Modes guide and derived the
design constraints from them.

**Prompt(s):** (translated from Chinese) *(1)* "Give me recommended
architecture options for TM1" → agent proposed three options grounded in
Learner Lab constraints; human chose serverless. *(2)* "Scaffold the
framework first, then check it against the course slide decks in my folder
and apply the changes they suggest." Agent planned in plan mode; human
approved the plan and three explicit decisions (repo location, stub+Bedrock
dual provider, locally-runnable + deployable).

**How I improved or changed the output:** The slide review reshaped the
original proposal before any code was written: the S3 static frontend was cut
(Week 3: "not yet: front end"), the response contract was changed to the
course's exact four fields, the model layer became a config-switched provider
interface, the system prompt became a versioned+tested spec, cost tags and
90-day TTL were added, and the IA1 exclusions moved from prompt text into
pre-model code guardrails. *(Team: record your own edits here as you make
them.)*

**What I verified:** Test suite passes locally (`make test`); `make invoke`
returns the four-field contract for a routine question, a refusal for an
unknown question, and the CaPS/988 referral for crisis language; SAM template
validated (see repo history for the verification commit). NOT yet verified:
devcontainer build on a clean machine, an actual Learner Lab deploy, Bedrock
availability in the lab account.

**What I contributed:** The architecture decision itself (serverless option
over EC2/ECS alternatives), the three scoping decisions above, the IA1
scoping document whose will/will-not lines the guardrails encode, and
acceptance of the slide-driven design changes. The agent generated; the
judgment stays with us.

**Final answer submitted:** This repository at the commit tagged for TM1
submission.

**Critic/Red Teamer review:** ⚠️ Pending. Before submission a teammate who
did not run the agent must: read the diff end-to-end, run `make test` and
`make invoke` locally, challenge at least the guardrail keyword lists (known
limitation: keyword matching is crude) and the Bedrock parse-fallback path,
and sign off here with name + date.

---

## Entry 2 — Personal-record guardrail robustness & clone-and-run fix

**AI Use Mode:** Critic/Red Teamer + Editor/Refiner (Claude Code, Opus 4.8) — a
review pass over the TM1 scaffold that found and fixed two defects in the risk
areas Entry 1's Critic note had named ("keyword matching is crude").

**Prompt(s):** (translated from Chinese) "Open the repo, review it against the
TM1 requirements, and fix what's weak." No specific fix was pre-specified; the
agent was asked to audit and improve.

**How I improved or changed the output:** Two changes. *(1) Guardrail
correctness.* The personal-record guard used fixed-phrase matching (`"my
balance"`, `"my aid"`, …), so `"Can you check my financial aid balance?"`
slipped through — `"my balance"` is not a contiguous substring of `"my
financial aid balance"` — and was answered as a process question with
`escalation_flag=false`, violating the IA1 promise that personal-record
questions are refused before any model call. Replaced the fixed phrases with a
possessive-pattern regex (`my … <record noun>`; nouns: balance, account, aid,
gpa, grade(s), hold, record(s), transcript, bill, refund, status, standing)
that tolerates intervening words and errs toward referral. Added regression
tests for the phrasings that broke it, plus a negative test asserting a general
financial-aid *process* question is still answered (not over-escalated).
*(2) Clone-and-run.* `make test`/`make invoke` depended on the editable install
being present in the active interpreter; on a bare clone — or any shell whose
`python` is not the project venv — they failed with `ModuleNotFoundError`.
Added `pythonpath = ["src"]` to the pytest config and `PYTHONPATH=src` to the
`invoke` target so both run on any Python 3.12 without `make install` first.

**What I verified:** Full suite passes (22 tests, up from 20) run through a
bare `make test` on an interpreter with **no** editable install — the true
fresh-clone case. `make invoke Q="Can you check my financial aid balance?"`
now returns `escalation_flag=true` with the HUB referral; `make invoke Q="How
does financial aid work at CMU?"` still returns the cited process answer with
`escalation_flag=false`. NOT verified: devcontainer build, Learner Lab deploy,
Bedrock path (unchanged by this entry).

**What I contributed:** *(Team: fill in your own review here.)* The decision to
bias the guard toward referral over precision, the noun-list scope, and the
sign-off are the team's to own.

**Final answer submitted:** Working-tree changes to `escalation.py`,
`test_handler.py`, `pyproject.toml`, `Makefile` (commit for TM1 submission).

**Critic/Red Teamer review:** Reviewed by **Fan Yang, 2026-07-11.** Walked
through the full diff line by line (the personal-record regex and its noun
list, the check() call site, the pytest `pythonpath` and `PYTHONPATH=src`
changes); ran `make test` (22 passed); and probed the regex against 9 cases
including over-escalation traps (e.g. "How does financial aid work?" and "My
friend asked about the drop deadline") — all classified correctly. Known
limits accepted: the noun list is finite (e.g. "my class schedule" is not
caught) and the match window is 30 characters. *Honest caveat: this is a solo
submission, so the reviewer is the same person who prompted the agent; the
"independent teammate" standard in CONVENTIONS.md cannot be met here and is
recorded rather than glossed.*

---

<!-- Template for new entries:

## Entry N — <artifact>

**AI Use Mode:** <Operator/Agent | Generator/Creator | Editor/Refiner | none (human-written)>
**Prompt(s):** <the prompts used, or "n/a">
**How I improved or changed the output:** <edits made to AI output>
**What I verified:** <tests run, claims checked — and what was NOT verified>
**What I contributed:** <the human judgment in this change>
**Final answer submitted:** <commit / PR>
**Critic/Red Teamer review:** <reviewer name, date, what was challenged, outcome>
-->
