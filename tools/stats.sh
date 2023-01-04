#!/bin/bash
# Script that displays some interesting stats about the gitlint project (LOC, # commits, downloads, etc)

BLUE="\033[94m"
NO_COLOR="\033[0m"

title(){
    echo -e "$BLUE=== $1 ===$NO_COLOR"
}

title Code
radon raw -s gitlint-core | tail -n 11 | sed 's/^    //' 

title Docs
echo "Markdown: $(cat docs/*.md | wc -l | tr -d " ") lines"

title Tests
nr_unit_tests=$(py.test gitlint-core/ --collect-only | grep TestCaseFunction | wc -l)
nr_integration_tests=$(py.test qa/ --collect-only | grep TestCaseFunction | wc -l)
echo "Unit Tests: ${nr_unit_tests//[[:space:]]/}"
echo "Integration Tests: ${nr_integration_tests//[[:space:]]/}"

title Git
echo "Commits: $(git rev-list --all --count)"
echo "Commits (main): $(git rev-list main --count)"
echo "First commit: $(git log --pretty="%aD" $(git rev-list --max-parents=0 HEAD))"
echo "Contributors: $(git log --format='%aN' | sort -u | wc -l | tr -d ' ')"
echo "Releases (tags): $(git tag --list | wc -l | tr -d ' ')"
latest_tag=$(git tag --sort=creatordate | tail -n 1)
echo "Latest Release (tag): $latest_tag"
echo "Commits since $latest_tag: $(git log --format=oneline HEAD...$latest_tag | wc -l | tr -d ' ')"
echo "Line changes since $latest_tag: $(git diff --shortstat $latest_tag)"

# PyPi API: https://pypistats.org/api/
title PyPi
info=$(curl -Ls https://pypi.python.org/pypi/gitlint/json)
echo "Current version: $(echo $info | jq -r .info.version)"

title "PyPI (Downloads)"
overall_stats=$(curl -s https://pypistats.org/api/packages/gitlint/overall)
recent_stats=$(curl -s https://pypistats.org/api/packages/gitlint/recent)
echo "Last 6 Months: $(echo $overall_stats | jq -r '.data[].downloads' | awk '{sum+=$1} END {print sum}')"
echo "Last Month: $(echo $recent_stats | jq .data.last_month)"
echo "Last Week: $(echo $recent_stats | jq .data.last_week)"
echo "Last Day: $(echo $recent_stats | jq .data.last_day)"