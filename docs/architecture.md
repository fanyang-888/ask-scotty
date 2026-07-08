# Architecture Narrative — Ask Scotty, TM1

## What we built

TM1 delivers the walking skeleton of "Ask Scotty," the student-support Q&A
pilot scoped in IA1: a service that accepts a question over an API and returns
a structured, source-cited answer — or a deliberate refusal that hands the
student to a human. It is the course's "smallest viable service": accept a
question via API, run it through a model-driven workflow, return a structured
response. No front end, no multi-turn state, no orchestration — those are
deferred on purpose, not forgotten.

The one route, `POST /ask`, returns a real contract rather than free-form
chat: `{answer, sources, confidence, escalation_flag}`. API-first forces
contracts, explicit errors, and testability — the grader, a future web UI, and
our own test suite all consume the same endpoint. The model layer is stubbed
for TM1 (canned, cited answers for a few routine questions; refusal-plus-
referral for everything else), which means the entire pipeline — validation,
guardrails, prompt assembly, response checking, logging — runs and is tested
end-to-end today, with zero model cost.

## Which cloud services, and why

We follow the baseline cloud architecture taught in Week 2 — one compute
service, one bucket, one model access path, logs, least privilege, budget
awareness — and add complexity only when we feel the pain.

**AWS Lambda + API Gateway (HTTP API).** The service is glue logic and a
light API — exactly the serverless sweet spot. In a Learner Lab with a hard
budget ceiling, idle cost is the dominant risk, and serverless makes idle
free; a container would work equally well per the course baseline, but brings
always-on cost and more moving parts than a single function needs. We accept
the known serverless watch-outs — cold starts and time limits — as
non-issues at pilot scale: responses are short and synchronous, and a
30-second timeout bounds the worst case.

**DynamoDB (ExchangeLog).** Measurement is the entire point of a pilot, so
every deployed exchange is logged — anonymized, no user identifiers — with a
DynamoDB TTL that enforces the IA1 90-day retention commitment *structurally*
rather than by policy memo. Pay-per-request billing again means idle is free.

**Amazon Bedrock (behind a config switch).** Model access is abstracted
behind one `ModelProvider` interface — swap models by config, not rewrite.
`MODEL_PROVIDER=stub` (default) runs anywhere; `MODEL_PROVIDER=bedrock` turns
on managed inference with the model id itself also config
(`BEDROCK_MODEL_ID`). This is our hedge against the Learner Lab's "some
services restricted by design": if Bedrock access is unavailable, TM1 still
runs, demos, and grades identically, and the seam for a real model (or an
external API provider) is one small class.

**S3 (SourceDocsBucket) — reserved.** IA1 commits us to answers grounded in a
whitelisted corpus of published pages. The bucket exists so the retrieval
seam is visible in the architecture diagram; it is deliberately empty until
the RAG milestone.

**CloudWatch** gives logs and metrics with no work. **IAM**: the Learner Lab
prohibits creating roles, so the stack takes the pre-provisioned `LabRole`
ARN as a parameter — a documented constraint, not a hidden assumption.

Everything above is declared in one SAM template. The course rule is
"ClickOps for learning, code for operating": the console is for exploring,
but the system of record is `infra/template.yaml`, and a fresh Learner Lab
session rebuilds the stack with one `make deploy`. Every resource carries the
four cost-allocation tags (Owner/Project/Environment/CostCenter) — untagged
resources are ungoverned resources. SAM over CDK/Terraform is a satisficing
choice: for one function, one table, one bucket, it is the lightest tool that
also gives us `sam local` for free — right-sized beats impressive.

## Trust boundaries as design, not aspiration

The IA1 scope lines that must never fail are enforced in code *before* any
model call: crisis language returns only the CaPS 24/7 line and 988;
visa/immigration questions route to OIE; personal-record questions are
refused. A model cannot cross a boundary it is never allowed to touch. The
same philosophy shapes the contract: `escalation_flag` makes "hand this to a
human" a first-class, machine-readable outcome, and a malformed model output
parses into a safe refusal rather than reaching a student. The system prompt
encoding the remaining behavioral rules is treated as a spec — versioned in
the repo and covered by tests, because prompt drift is code drift.

## How this maps to the operating model

Against the AI/MLOps hierarchy of needs, TM1 delivers level 1, a reproducible
environment (the devcontainer: clone → reopen in container → `make test`
with no setup), and level 2, versioned code *and prompts*, with the first
slice of level 3 (automated tests over the contract, guardrails, and prompt
spec). We are deliberately "light" MLOps — git, tests, scripts, simple
deploy, logs — which is the right size for a two-week-old pilot. The
provenance log (`docs/PROVENANCE.md`) and the Critic-review rule in
`CONVENTIONS.md` are our first governance gate: AI generates, humans own.
Bounded rationality applies to architecture too — this is a satisficing
design, good enough to learn from real usage, with the expensive decisions
(retrieval corpus, personalization, real model choice) deferred to when the
logs can inform them.
