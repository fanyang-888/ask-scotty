# Code Provenance Log

Every substantive piece of work in this repo gets an entry using the course
AI Use Modes guide's Minimal Submission Format, plus a review record. Each
entry names the commits/PR it covers (see [CONVENTIONS.md](../CONVENTIONS.md)).
No agent-generated change merges without a Critic/Red Teamer pass by a
teammate who did not prompt it.

## Summary table

| # | Artifact(s) | Origin | AI Use Mode | Review status |
|---|---|---|---|---|
| 1 | Entire initial scaffold (devcontainer, api/, infra/, docs/, Makefile, conventions) | Agent-generated | Operator/Agent | AI red-team done; ⚠️ teammate sign-off pending |
| 2 | Personal-record guardrail robustness + clone-and-run fix (escalation.py, tests, pyproject, Makefile) | AI-assisted | Critic/Red Teamer + Editor/Refiner | Author-reviewed; ⚠️ teammate sign-off pending |

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

**Critic/Red Teamer review:**

*AI red-team pass — Claude Opus 4.8, 2026-07-11.* An automated critique read the
full scaffold (providers, handler, contract, guardrails, system prompt, SAM
template, tests), ran the suite (22 pass), and probed the safety boundaries.
This is an **input to** the human Critic review below, **not a substitute** for
it. Findings:

1. **[Safety — highest] Crisis detection is keyword-only and misses common
   phrasings.** Verified: "I want to end it all" and "I can't go on anymore" are
   NOT recognized and fall through to a generic refusal instead of the CaPS/988
   response. Same brittleness class as the personal-record bug fixed in Entry 2,
   but higher stakes. Recommend defense-in-depth (broader lexicon + a model-side
   crisis check) before this is anything more than a pilot.
2. **[Privacy] The exchange log stores the raw `question` text.** IA2 itself
   flags query text as sensitive; "anonymized" (no user id) is not "no PII"
   (free text can contain names and situations). The 90-day TTL mitigates but
   does not remove this. Recommend documenting it explicitly or scrubbing before
   the write.
3. **[Bedrock path] The contract validates structure, not groundedness.** A
   hallucinated answer with a fabricated `sources` string and
   `escalation_flag=false` passes `validate()` and would reach a student.
   Source-whitelisting is deferred to the RAG milestone — fine — but it is a
   live risk the moment `MODEL_PROVIDER=bedrock` serves real traffic. (The
   malformed-JSON → safe-refusal fallback is good and is tested.)
4. **[Cost/abuse] The HTTP API endpoint has no auth or throttling.** In a
   budget-capped Learner Lab, an open POST endpoint is a cost/DoS risk. Consider
   API Gateway throttling on deploys.
5. **[Ops hygiene — minor] No explicit CloudWatch Log Group retention**, so the
   Lambda's auto-created log group never expires (the 90-day commitment is
   enforced on DynamoDB, not CloudWatch). Note: the handler does not write
   question text to CloudWatch, so no PII lives there.
6. **[Test coverage] The Bedrock `converse` network call and the `log_exchange`
   DynamoDB write are not unit-tested** (only JSON parsing and env-gating are).
   Acceptable for TM1; flagged.
7. **[Not verified] devcontainer clean build, a real Learner Lab deploy, and
   Bedrock availability** remain unverified.

*Proposed disposition (the team decides):* fix #1 or explicitly scope it out in
the narrative; #2 and #3 are accepted pilot limitations already consistent with
IA2 but should be named; #4 and #5 are cheap hardening for the deploy step; #6
and #7 are verification debt to close before final submission.

**Human teammate sign-off (required by CONVENTIONS — a teammate who did NOT
prompt the agent):** ________________________ (name, date). The reviewer should
independently read the scaffold, run `make test`, and confirm the dispositions
above.

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

**What I contributed:** Fan Yang directed this review pass, judged the
personal-record slip-through worth fixing before submission, accepted the "bias
toward referral over precision" tradeoff and its known limits (finite noun
list, 30-char window), and chose to record the AI red-team findings in Entry 1
for the team rather than act on them silently. *(Teammate: confirm and add your
own notes.)*

**Final answer submitted:** Working-tree changes to `escalation.py`,
`test_handler.py`, `pyproject.toml`, `Makefile` (commit for TM1 submission).

**Critic/Red Teamer review:** Author self-review by **Fan Yang, 2026-07-11** —
walked through the full diff line by line (the personal-record regex and its
noun list, the check() call site, the pytest `pythonpath` and `PYTHONPATH=src`
changes); ran `make test` (22 passed); and probed the regex against 9 cases
including over-escalation traps ("How does financial aid work?", "My friend
asked about the drop deadline") — all classified correctly. Known limits
accepted: finite noun list (e.g. "my class schedule" is not caught) and a
30-character match window. **Team project — independent sign-off still
pending:** this is the author's own review; per CONVENTIONS.md a teammate who
did not prompt the change should confirm and sign here: ________ (name, date).

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
