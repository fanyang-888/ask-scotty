# Code Provenance Log

Every substantive piece of work in this repo gets an entry using the course
AI Use Modes guide's Minimal Submission Format, plus a review record. Commit
messages carry matching tags (`[human]` / `[ai-gen]` / `[ai-assisted]` — see
[CONVENTIONS.md](../CONVENTIONS.md)). Nothing `[ai-gen]` merges without a
Critic/Red Teamer pass by a teammate who did not prompt it.

## Summary table

| # | Artifact(s) | Origin | AI Use Mode | Review status |
|---|---|---|---|---|
| 1 | Entire initial scaffold (devcontainer, api/, infra/, docs/, Makefile, conventions) | Agent-generated | Operator/Agent | ⚠️ pending team Critic review |

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
