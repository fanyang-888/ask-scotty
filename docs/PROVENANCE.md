# Code Provenance Log

Every substantive piece of work in this repo gets an entry using the course
AI Use Modes guide's Minimal Submission Format, plus a review record. Each
entry names the commits/PR it covers (see [CONVENTIONS.md](../CONVENTIONS.md)).
No agent-generated change merges without a Critic/Red Teamer pass by a
teammate who did not prompt it.

## Summary table

| # | Artifact(s) | Origin | AI Use Mode | Review status |
|---|---|---|---|---|
| 1 | Entire initial scaffold (devcontainer, api/, infra/, docs/, Makefile, conventions) | Agent-generated | Operator/Agent | AI red-team done; Signed off (Siru Tao, 2026-07-16) |
| 2 | Personal-record guardrail robustness + clone-and-run fix (escalation.py, tests, pyproject, Makefile) | AI-assisted | Critic/Red Teamer + Editor/Refiner | Author-reviewed; Signed off (Siru Tao, 2026-07-16) |
| 3 | Crisis-detection hardening, corpus-validated (escalation.py, tests) | Agent-generated, corpus-driven | Operator/Agent + Critic/Red Teamer | Corpus-validated; Signed off (Siru Tao, 2026-07-16) |
| 4 | Learner Lab deploy verification (no code changes — closes Entry 1's "deploy not verified" gap) | AI-operated, human-supervised | Operator/Agent | Verified against live endpoint; evidence below |
| 5 | Independent red-team audit of merged `main` — 2 bugs found, no code change yet | AI-assisted audit | Critic/Red Teamer | Found by **Xin Xu**; both bugs independently re-verified; Xin Xu sign-off on writeup pending (offline) |

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
   **→ FIXED in Entry 3** (pattern-based lexicon, corpus-validated 44/45 caught,
   0/35 figurative false positives; one genuinely ambiguous phrasing recorded as
   a residual limit — the model-side second layer remains future work).
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
prompt the agent):** Reviewed by **Siru Tao, 2026-07-16**. Ran `make test` (24
passed), spot-checked `make invoke` on routine/crisis/personal-record
questions, and confirmed the dispositions above.

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
for the team rather than act on them silently. *Teammate confirmation (Siru
Tao, 2026-07-16): reviewed the Entry 1 findings/dispositions and agree with the
recorded handling and notes.*

**Final answer submitted:** Working-tree changes to `escalation.py`,
`test_handler.py`, `pyproject.toml`, `Makefile` (commit for TM1 submission).

**Critic/Red Teamer review:** Author self-review by **Fan Yang, 2026-07-11** —
walked through the full diff line by line (the personal-record regex and its
noun list, the check() call site, the pytest `pythonpath` and `PYTHONPATH=src`
changes); ran `make test` (22 passed); and probed the regex against 9 cases
including over-escalation traps ("How does financial aid work?", "My friend
asked about the drop deadline") — all classified correctly. Known limits
accepted: finite noun list (e.g. "my class schedule" is not caught) and a
30-character match window. **Team project — independent sign-off:** confirmed
by **Siru Tao, 2026-07-16**.

---

## Entry 3 — Crisis-detection hardening (fixes Entry 1 finding #1)

**AI Use Mode:** Operator/Agent + Critic/Red Teamer (Claude Opus 4.8) — the
agent designed, implemented, and corpus-validated the fix for the highest-
severity finding of the Entry 1 red-team pass.

**Prompt(s):** (translated from Chinese) "Fix it" — referring to Entry 1
finding #1 (crisis detection keyword-only, verified misses). Method was the
agent's: two parallel corpus-generation agents produced (a) 45 realistic
crisis phrasings a distressed student might type (paraphrase, slang,
indirection, mixed with logistics requests) and (b) 35 benign student
questions full of figurative death/harm idioms that must NOT trigger a 988
referral ("this deadline is killing me", "academic suicide", "I shot myself
in the foot", "I don't want to live in the dorms anymore"). The guard was then
rewritten from 8 fixed substrings to ~28 compiled patterns and iterated
against both corpora.

**How I improved or changed the output:** The corpus exposed two defects in
the agent's own first draft, which were fixed before commit: a lookahead
missing a word boundary made "can't go on **a**nymore" match the article "a"
and slip through; and "unalive" needed a suffix wildcard for "unaliving".
Guards were added for figurative collisions the corpus surfaced ("academic/
career/social suicide", "kms" as kilometres, "don't want to live **in the
dorms**").

**What I verified:** Corpus results: **44/45 crisis phrasings caught, 0/35
benign false positives** (script in session scratchpad; corpora reproduced in
the test suite's representative cases). End-to-end via `make invoke`: the two
originally-missed phrasings now return the CaPS/988 response with
`escalation_flag=true`. Full suite: **24 tests pass** (2 new: crisis
paraphrases must be caught; figurative death language must not be). NOT
achievable and recorded honestly: "How do I cancel my housing contract? Not
that it matters, I don't plan on being here" is indistinguishable by keywords
from a benign transfer-student question — this is the standing argument for a
model-side crisis check as a second layer (future work, per Entry 1
disposition).

**What I contributed:** Fan Yang decided to fix rather than merely document
the finding, accepted the safety-over-precision bias (a rare jarring referral
is preferred to a missed crisis), and accepted the residual limit above as a
documented boundary of keyword-layer detection. *Teammate confirmation (Siru
Tao, 2026-07-16): agree with the safety-over-precision stance and residual-limit
recording.*

**Final answer submitted:** escalation.py crisis-pattern rewrite + 2 test
additions on branch `fy/entry1-critic-review`.

**Critic/Red Teamer review:** Corpus validation above is the AI-side review.
**Human teammate sign-off:** **Siru Tao, 2026-07-16** — ran `make test`, read
the pattern list for over/under-match, and confirmed the residual-limit
disposition.

---

## Entry 4 — Learner Lab deploy verification (2026-07-12)

**AI Use Mode:** Operator/Agent (Claude Opus 4.8) — drove the browser to start
the AWS Academy Learner Lab session and ran the deploy/verify/teardown cycle
from the CLI. No application code changed in this entry. The human (Fan Yang)
authorized the Vocareum terms acceptance and pasted the session credentials
into `~/.aws/credentials` themselves — the agent never handled the secret
values (a permission guardrail blocked credential extraction, correctly).

**What was verified (closes Entry 1's "NOT yet verified: an actual Learner
Lab deploy"):**
- `sam deploy` of `infra/template.yaml` to the Learner Lab account
  (us-east-1, stack `ask-scotty-dev`, LabRole as execution role):
  **CREATE_COMPLETE** — Lambda + HTTP API + DynamoDB + S3 all provisioned as
  declared, cost tags applied.
- Live endpoint behavior, all four paths against the real API Gateway URL:
  routine question → cited stub answer (`escalation_flag=false`); crisis
  phrasing "I want to end it all" (an Entry 1 verified miss) → CaPS + 988
  referral (`escalation_flag=true`); personal-record phrasing "check my
  financial aid balance" (the Entry 2 bug) → HUB referral
  (`escalation_flag=true`); blank question → HTTP 400.
- **The env-gated DynamoDB logging path, which local tests never execute:**
  3 exchange records written, correct `escalation_flag` per question,
  `provider=stub`, and TTL = exactly 90 days (the IA1 retention line enforced
  structurally). The 400 request correctly produced no log record.
- Teardown: `sam delete` completed (per CONVENTIONS — delete stacks you're
  done with). Budget impact: $0 of $50.

**Still NOT verified:** devcontainer build on a clean machine; Bedrock model
access in the Learner Lab account (deploy used `ModelProvider=stub`).

**Critic/Red Teamer review:** the verification transcript IS the evidence;
⚠️ teammate should spot-check by re-running the same cycle in their own lab
session before TM1 submission if time allows.

---

## Entry 5 — Independent red-team audit of merged `main` (found by Xin Xu)

**AI Use Mode:** Critic/Red Teamer — **Xin Xu** ran an AI-assisted audit of the
merged `main` (post Entries 1–4): his assistant cloned the repo, read all files,
ran the suite (24 pass), and probed guardrail/handler behavior. This entry
*records a review*; it changes no code. Its writeup used Editor/Refiner mode
(Fan Yang, Claude Code) to transcribe Xin Xu's audit and independently re-run
every repro before recording — findings were re-confirmed, not taken on trust.

**Prompt(s):** Xin Xu directed his assistant to clone the repo and audit it
against the TM1 requirements and the safety narrative. Xin Xu is traveling and
offline; his findings are transcribed here on his behalf.

**How I improved or changed the output:** No code changed. The audit's two
"red" findings were **independently reproduced** by Fan Yang's agent (see below)
rather than accepted on trust; the same audit's ~5 "yellow/green" suggestions
are noted for the team but not acted on in this entry.

**What I verified (independent re-confirmation of Xin Xu's two findings):**

1. **[Safety/correctness] Immigration guardrail uses bare-substring matching →
   false OIE routing.** `escalation.py` matches immigration with
   `any(term in q for term in IMMIGRATION_TERMS)` where the list contains
   `"opt"` and `"cpt"`, so any word *containing* them trips the guard.
   Reproduced (all return the Office of International Education referral):
   "What are my enrollment **opt**ions?", "Is the writing course **opt**ional?",
   "How do I **opt** out of the meal plan?", "What are the best **opt**ions for
   electives?". This is the *same* bare-substring brittleness Entry 2
   (personal-record) and Entry 3 (crisis) already fixed twice — the third guard
   (immigration) was left on `term in q`. Fix: word-boundary regex
   (`\bopt\b`, `\bcpt\b`, …), mirroring Entries 2–3.
2. **[Robustness] `answer_question()` exceptions are uncaught → HTTP 502 with no
   contract.** `handler.py` wraps only `log_exchange` in try/except, not the
   generation call. Reproduced: injecting a provider whose `complete()` raises
   (simulating Bedrock throttling / timeout / AccessDenied) makes the exception
   escape `lambda_handler` entirely → API Gateway 502, with no
   `{answer, sources, confidence, escalation_flag}` and no referral. This
   contradicts the architecture narrative's "a malformed model answer must never
   reach a student," and it fires the moment `MODEL_PROVIDER=bedrock` serves real
   traffic (the Bedrock `FALLBACK` covers JSON-parse failure, not call failure).
   Fix: wrap generation in the handler and degrade any exception to a safe
   referral.

**What Xin Xu contributed:** The audit and both bugs are Xin Xu's discovery. He
also flagged, for the team (recorded, not reproduced here): no CI running tests
on PRs; no read/aggregation side for the pilot's DynamoDB metrics
(no `make report`); no API Gateway throttling; no CloudWatch log-group
retention; no input-length cap. He deliberately did **not** touch code, citing
this repo's rule that agent-generated changes need a provenance entry plus an
independent teammate sign-off.

**Final answer submitted:** This entry records the audit only — no code change.
Disposition (team decision): the two bugs are strong candidates for the TM2
"Pipeline, Observability & Hardening" milestone, each landing with a regression
test; fix earlier if TM1 is re-touched before final submission.

**Critic/Red Teamer review:** The two findings were independently re-verified by
Fan Yang's agent (repros re-run, 2026-07-19). ⚠️ **Xin Xu's own sign-off on this
writeup is pending** — he is offline (traveling); this entry was transcribed on
his behalf and should be confirmed by him on return.

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
