#!/bin/bash

RED="\033[31m"
YELLOW="\033[33m"
BLUE="\033[94m"
GREEN="\033[32m"
NO_COLOR="\033[0m"

# Create the repo
echo -e "${YELLOW}Creating new temp repo...${NO_COLOR}"
cd /tmp
reponame=$(date +gitlint-test-%Y-%m-%d_%H-%M-%S)
git init --initial-branch main $reponame

cd $reponame

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


echo -e "${YELLOW}Reconfiguring hatch...${NO_COLOR}"
hatch config set projects.gitlint /workspaces/gitlint


# Let the user know
echo -e "${YELLOW}All Done!${NO_COLOR}"
echo ""
echo -e "Entering subshell at $GREEN/tmp/${reponame}$NO_COLOR. Type 'exit' to exit."

bash --rcfile <(echo "source ~/.bash_profile; cd /tmp/$reponame; alias gitlint='HATCH_PROJECT=gitlint hatch run dev:gitlint --target /tmp/$reponame'")