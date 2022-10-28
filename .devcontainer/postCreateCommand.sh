#!/bin/sh

brew install asdf
source "$(brew --prefix asdf)/libexec/asdf.sh"

# Install latest python
asdf plugin add python
asdf install python 3.11.0
asdf global python 3.11.0

# You can easily install other python versions like so:
# asdf install python 3.6.15
# asdf install python 3.7.15
# asdf install python 3.8.15
# asdf install python 3.9.15
# asdf install python 3.10.8
# asdf install python pypy3.9-7.3.9

# Setup virtualenv, install all dependencies
cd workspaces/gitlint
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r test-requirements.txt -r doc-requirements.txt