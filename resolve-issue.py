#!/usr/bin/env python3
import argparse

from resolve_issue.resolver import get_issue, get_code_diff, apply_code_diff

if __name__ == "__main__":
    argParser = argparse.ArgumentParser()
    argParser.add_argument("url", help="the URL of the Github issue to resolve", type=str)
    args = argParser.parse_args()

    # Fetch issue data
    owner, repo, issue = get_issue(args.url)

    # Generate the code diff
    code_diff = get_code_diff(issue, owner, repo)

    # Apply the code diff
    apply_code_diff(code_diff)
