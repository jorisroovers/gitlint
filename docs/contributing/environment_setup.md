## Hatch

Gitlint uses [hatch](https://hatch.pypa.io/latest/) for project management, including package building,
environment management and script/test running.


## Local setup

```sh
# Clone gitlint repo
git clone https://github.com/jorisroovers/gitlint
cd gitlint

# You can choose whether to install hatch in a virtualenv or globally
# Either way, hatch will use virtualenvs under-the-hood for gitlint
virtualenv .venv && source .venv/bin/activate
pip install hatch==1.7.0

# Run gitlint
hatch run dev:gitlint --version # (1)

# Run unit tests
hatch run test:unit-tests # (2)
```

1. Hatch will automatically setup a `dev` environment for you the first time you run this command.
1. Hatch will automatically setup a `test` environment for you the first time you run this command. <br/><br/>
   See [Tests, Formatting, Docs](tests_formatting_docs.md) for more test commands.


## Github Codespace

We provide a devcontainer to use with github codespaces to make it easier to get started with gitlint development
using VSCode.

To start one, click the plus button under the *Code* dropdown on
[the gitlint repo on github](https://github.com/jorisroovers/gitlint). 

**It can take ~15min for all post installation steps to finish.**

![Gitlint Dev Container Instructions](../images/dev-container.png)

After the codespace is up, you can just run hatch:
```sh
# Run gitlint
hatch run dev:gitlint --version # (1)

# Run unit tests
hatch run test:unit-tests # (2)
```

1. Hatch will automatically setup a `dev` environment for you the first time you run this command.
1. Hatch will automatically setup a `test` environment for you the first time you run this command. <br/><br/>
   See [Tests, Formatting, Docs](tests_formatting_docs.md) for more test commands.

### Installing additional python versions
By default we have python 3.11 installed in the dev container, but you can also use [asdf](https://asdf-vm.com/)
(preinstalled) to install additional python versions:

```sh
# Ensure ASDF overrides system python in PATH
# You can also append this line to your ~/.bash_profile in the devcontainer to have this happen automatically on login
source "$(brew --prefix asdf)/libexec/asdf.sh"

# Install python 3.9.15
asdf install python 3.9.15
# Make python 3.9.15 the default python
asdf global python 3.9.15

# IMPORTANT: install hatch for this python version
pip install hatch==1.7.0
# You also need to prune your hatch environment first before running other commands
hatch env prune

# List all available python versions
asdf list all python
# List installed python versions
asdf list python
```