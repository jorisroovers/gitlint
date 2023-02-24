# ruff: noqa: T201 (Allow print statements)
# Simple script to generate a rough changelog from git log.
# This changelog is manually edited before it goes into CHANGELOG.md

import re
import subprocess
import sys
from collections import defaultdict

if len(sys.argv) != 2:
    print("Usage: python changelog.py <tag>")
    sys.exit(1)

tag = sys.argv[1]
# Get all commits since the last release
cmd = ["git", "log", "--pretty=%s|%aN", f"{tag}..HEAD"]
log_lines = subprocess.Popen(cmd, stdout=subprocess.PIPE).stdout.read().decode("UTF-8")
log_lines = log_lines.split("\n")[:-1]

# Group commits by type
commit_groups = defaultdict(list)
for log_line in log_lines:
    message, author = log_line.split("|")
    # skip dependabot commits
    if author == "dependabot[bot]":
        group = "dependabot"
    else:
        type_parts = message.split(":")
        if len(type_parts) == 1:
            group = "other"
        else:
            group = type_parts[0]

    commit_groups[group].append((message, author))

# Print the changelog
for group, commits in commit_groups.items():
    print(group)
    for message, author in commits:
        # Thank authors other than maintainer
        author_thanks = ""
        if author != "Joris Roovers":
            author_thanks = f" - Thanks {author}"

        # Find the issue number in message using regex, format: (#1234)
        issue_number = re.search(r"\(#(\d+)\)", message)
        if issue_number:
            issue_url = f"https://github.com/jorisroovers/gitlint/issues/{issue_number.group(1)}"
            message = message.replace(issue_number.group(0), f"([#{issue_number.group(1)}]({issue_url}))")

        print(f" - {message}{author_thanks}")
