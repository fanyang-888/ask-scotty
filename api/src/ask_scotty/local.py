"""Run one question through the full handler locally, no AWS required.

    python -m ask_scotty.local "When is the last day to drop a course?"
"""

import json
import sys

from ask_scotty.handler import lambda_handler


def main() -> int:
    if len(sys.argv) < 2:
        print('usage: python -m ask_scotty.local "your question"', file=sys.stderr)
        return 2
    event = {"body": json.dumps({"question": " ".join(sys.argv[1:])})}
    result = lambda_handler(event)
    print(json.dumps(json.loads(result["body"]), indent=2))
    return 0 if result["statusCode"] == 200 else 1


if __name__ == "__main__":
    raise SystemExit(main())
