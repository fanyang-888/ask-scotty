# Ask Scotty

A pilot Q&A service that answers routine CMU student questions (deadlines,
registration logistics, financial aid *process*, campus resources) from
published university pages — with a citation every time — and hands anything
personal, consequential, or judgment-based to a human.

95-731 team milestone project. Product scope: see the IA1 scoping document.
Architecture: [docs/architecture.md](docs/architecture.md) ·
Diagram: [docs/architecture-diagram.md](docs/architecture-diagram.md) ·
AI provenance: [docs/PROVENANCE.md](docs/PROVENANCE.md) ·
Team conventions: [CONVENTIONS.md](CONVENTIONS.md)

## Quickstart (new teammate, three steps)

1. **Clone and open in the devcontainer** — VS Code will prompt "Reopen in
   Container" (needs Docker Desktop). Everything (Python 3.12, AWS CLI, SAM
   CLI, dependencies) installs automatically.
2. **Run the tests**: `make test`
3. **Ask a question**: `make invoke Q="Where is the registrar office?"`

That's the whole loop. No AWS account needed — the default model provider is
a stub, so the service runs anywhere.

Without the devcontainer: Python 3.12 + `make install`, then the same commands.

## What it does today (TM1)

`POST /ask` accepts a question and returns the response contract:

```json
{
  "answer": "The University Registrar's Office is located in Warner Hall ...",
  "sources": ["University Registrar — cmu.edu/hub/registrar"],
  "confidence": "high",
  "escalation_flag": false
}
```

- A few routine questions get canned, source-cited stub answers.
- Everything else refuses politely and refers to The HUB (`escalation_flag: true`).
- Crisis language, visa/immigration topics, and personal-record questions are
  intercepted by guardrails in code before any model is called.
- Deployed, every exchange is logged (anonymized) to DynamoDB with a 90-day TTL.

There is deliberately **no front end and no multi-turn chat yet** — smallest
viable service first.

## Commands

| Command | What it does |
|---|---|
| `make test` | run the test suite |
| `make invoke Q="..."` | one question through the full handler, locally, no AWS |
| `make run` | local HTTP API on `localhost:3000` (Docker required); then `curl -s -X POST localhost:3000/ask -d '{"question":"When is the last day to drop?"}'` |
| `make validate` | lint the SAM template |
| `make deploy LAB_ROLE_ARN=...` | deploy to AWS (see below) |

## Deploying to the AWS Academy Learner Lab

1. Start the lab, open **AWS Details → CLI credentials**, paste them into
   your shell (they rotate every session — never commit them).
2. Find your LabRole ARN: `aws iam get-role --role-name LabRole --query Role.Arn --output text`
3. `make deploy LAB_ROLE_ARN=arn:aws:iam::<account-id>:role/LabRole`
4. The stack outputs the `POST /ask` endpoint URL.

To use a real model instead of the stub, redeploy with
`--parameter-overrides ModelProvider=bedrock` — **after** confirming Bedrock
model access is enabled in your lab region (some services are restricted by
design). Model choice is config (`BEDROCK_MODEL_ID`), not code.

## Repo map

```
.devcontainer/   reproducible dev environment (level 1 of the hierarchy of needs)
api/             the service: handler, contract, guardrails, model providers, versioned prompt, tests
infra/           SAM template + config — the whole system as code
docs/            architecture narrative, diagram, AI provenance log
CONVENTIONS.md   how we branch, commit, review, and label AI-generated work
Makefile         one command per lifecycle step
```
