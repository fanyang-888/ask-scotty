# Ask Scotty — one command per lifecycle step. "CLI/IaC for repeatability."

.PHONY: install test invoke run validate deploy clean

install:  ## dev dependencies (run once per environment)
	pip install -e "api[dev]"

test:  ## full test suite
	cd api && python -m pytest -q

invoke:  ## run one question through the handler locally, no AWS/Docker needed
	cd api && PYTHONPATH=src python -m ask_scotty.local "$(or $(Q),When is the last day to drop a course?)"

run:  ## local HTTP API on :3000 (requires Docker for sam local)
	sam local start-api --template infra/template.yaml --parameter-overrides LabRoleArn=arn:aws:iam::000000000000:role/local-dev

validate:  ## lint the SAM template
	sam validate --template infra/template.yaml --lint

deploy:  ## deploy to the active AWS session (Learner Lab: start lab, copy credentials first)
ifndef LAB_ROLE_ARN
	$(error Set LAB_ROLE_ARN, e.g. make deploy LAB_ROLE_ARN=arn:aws:iam::<account-id>:role/LabRole)
endif
	sam deploy --template infra/template.yaml --config-file samconfig.toml --parameter-overrides LabRoleArn=$(LAB_ROLE_ARN)

clean:
	rm -rf .aws-sam api/.pytest_cache api/src/ask_scotty.egg-info
	find . -name __pycache__ -type d -exec rm -rf {} +
