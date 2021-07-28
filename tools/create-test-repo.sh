#!/bin/bash

set -o errexit

GREEN="\033[32m"
NO_COLOR="\033[0m"

CWD="$(pwd)"
echo "pwd=$CWD"
# Create the repo
cd /tmp
reponame="$(date +gitlint-test-%Y-%m-%d_%H-%M-%S)"
git init --initial-branch main "$reponame"
cd "$reponame"

# Do some basic config
git config user.name gïtlint-test-user
git config user.email gitlint@test.com
git config core.quotePath false
git config core.precomposeUnicode true

# Add a test commit
echo "tëst 123" > test.txt
git add test.txt
# commit -m -> use multiple -m args to add multiple paragraphs (/n in strings are ignored)
git commit -m "test cömmit title" -m "test cömmit body that has a bit more text"
cd "$CWD"

# Let the user know
echo ""
echo -e "Created $GREEN/tmp/${reponame}$NO_COLOR"
echo "Hit key up to access 'cd /tmp/$reponame'"
echo "(Run this script using 'source' for this to work)"
history -s "cd /tmp/$reponame"
