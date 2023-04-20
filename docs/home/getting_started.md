# Getting Started
## Installation
```sh
# Pip is recommended to install the latest version
pip install gitlint

# Alternative: by default, gitlint is installed with pinned dependencies.
# To install gitlint with looser dependency requirements, only install gitlint-core.
pip install gitlint-core

# Community maintained packages:
brew install gitlint       # Homebrew (macOS)
sudo port install gitlint  # Macports (macOS)
apt-get install gitlint    # Ubuntu
# Other package managers, see https://repology.org/project/gitlint/versions

# Docker: https://hub.docker.com/r/jorisroovers/gitlint
docker run --ulimit nofile=1024 -v $(pwd):/repo jorisroovers/gitlint
# NOTE: --ulimit is required to work around a limitation in Docker
# Details: https://github.com/jorisroovers/gitlint/issues/129
```

## Usage
```sh
# Check the last commit message
gitlint
# Alternatively, pipe a commit message to gitlint:
cat examples/commit-message-1 | gitlint
# or
git log -1 --pretty=%B | gitlint
# Or read the commit-msg from a file, like so:
gitlint --msg-filename examples/commit-message-2
# Lint all commits in your repo
gitlint --commits HEAD

# To install a gitlint as a commit-msg git hook:
gitlint install-hook
```

Output example:
```sh
$ cat examples/commit-message-2 | gitlint
1: T1 Title exceeds max length (134>80): "This is the title of a commit message that 	is over 80 characters and contains hard tabs and trailing whitespace and the word wiping  "
1: T2 Title has trailing whitespace: "This is the title of a commit message that 	is over 80 characters and contains hard tabs and trailing whitespace and the word wiping  "
1: T4 Title contains hard tab characters (\t): "This is the title of a commit message that 	is over 80 characters and contains hard tabs and trailing whitespace and the word wiping  "
2: B4 Second line is not empty: "This line should not contain text"
3: B1 Line exceeds max length (125>80): "Lines typically need to have 	a max length, meaning that they can't exceed a preset number of characters, usually 80 or 120. "
3: B2 Line has trailing whitespace: "Lines typically need to have 	a max length, meaning that they can't exceed a preset number of characters, usually 80 or 120. "
3: B3 Line contains hard tab characters (\t): "Lines typically need to have 	a max length, meaning that they can't exceed a preset number of characters, usually 80 or 120. "
```
!!! note
    The returned exit code equals the number of errors found. [Some exit codes are special](index.md#exit-codes).

## Shell completion

```sh
# Bash: add to ~/.bashrc
eval "$(_GITLINT_COMPLETE=bash_source gitlint)"

# Zsh: add to ~/.zshrc
eval "$(_GITLINT_COMPLETE=zsh_source gitlint)"

# Fish: add to ~/.config/fish/completions/foo-bar.fish
eval (env _GITLINT_COMPLETE=fish_source gitlint)
```