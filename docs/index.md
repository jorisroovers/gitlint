# Intro #
Gitlint is a git commit message linter written in python: it checks your commit messages for style.

Great for use as a ```commit-msg``` git hook or as part of your gating script in a CI/CD pipeline (e.g. jenkins).

<script type="text/javascript" src="https://asciinema.org/a/2vld64abf1tmwm6f5jw8fsrge.js" id="asciicast-2vld64abf1tmwm6f5jw8fsrge" async></script>

Many of the gitlint validations are based on
[well-known](http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html),
[community](http://addamhardy.com/blog/2013/06/05/good-commit-messages-and-enforcing-them-with-git-hooks/),
[standards](http://chris.beams.io/posts/git-commit/), others are based on checks that we've found
useful throughout the years. Gitlint has sane defaults, but you can also easily customize it to your own liking.

If you are looking for an alternative written in Ruby, have a look at
[fit-commit](https://github.com/m1foley/fit-commit).

## Getting Started ##
```bash
# Install gitlint
pip install gitlint

# Check the last commit message
gitlint
# Alternatively, pipe a commit message to gitlint:
cat examples/commit-message-1 | gitlint
# or
git log -1 --pretty=%B | gitlint

# To install a gitlint as a commit-msg git hook:
gitlint --install-hook
```

Output example:
```bash
$ cat examples/commit-message-2 | gitlint
1: T1 Title exceeds max length (134>80): "This is the title of a commit message that 	is over 80 characters and contains hard tabs and trailing whitespace and the word wiping  "
1: T2 Title has trailing whitespace: "This is the title of a commit message that 	is over 80 characters and contains hard tabs and trailing whitespace and the word wiping  "
1: T4 Title contains hard tab characters (\t): "This is the title of a commit message that 	is over 80 characters and contains hard tabs and trailing whitespace and the word wiping  "
2: B4 Second line is not empty: "This line should not contain text"
3: B1 Line exceeds max length (125>80): "Lines typically need to have 	a max length, meaning that they can't exceed a preset number of characters, usually 80 or 120. "
3: B2 Line has trailing whitespace: "Lines typically need to have 	a max length, meaning that they can't exceed a preset number of characters, usually 80 or 120. "
3: B3 Line contains hard tab characters (\t): "Lines typically need to have 	a max length, meaning that they can't exceed a preset number of characters, usually 80 or 120. "
```
NOTE: The returned exit code equals the number of errors found. [Some exit codes are special](index.md#exit-codes).

For a list of available rules and their configuration options, have a look at the [Rules](rules.md) page.

You can modify verbosity using the ```-v``` flag, like so:
```bash
$ cat examples/commit-message-2 | gitlint -v
1: T1
1: T2
[removed output]
$ cat examples/commit-message-2 | gitlint -vv
1: T1 Title exceeds max length (134>80)
1: T2 Title has trailing whitespace
1: T4 Title contains hard tab characters (\t)
[removed output]
$ cat examples/commit-message-2 | gitlint -vvv
1: T1 Title exceeds max length (134>80): "This is the title of a commit message that 	is over 80 characters and contains hard tabs and trailing whitespace and the word wiping  "
1: T2 Title has trailing whitespace: "This is the title of a commit message that 	is over 80 characters and contains hard tabs and trailing whitespace and the word wiping  "
[removed output]
```
The default verbosity is ```-vvv```.

Other commands and variations:

```
Usage: gitlint [OPTIONS]

  Git lint tool, checks your git commit messages for styling issues

Options:
  --install-hook      Install gitlint as a git commit-msg hook
  --uninstall-hook    Uninstall gitlint commit-msg hook
  --target DIRECTORY  Path of the target git repository (defaults to the
                      current directory).
  -C, --config PATH   Config file location (default: .gitlint).
  -c TEXT             Config flags in format <rule>.<option>=<value> (e.g.: -c
                      T1.line-length=80). Flag can be used multiple times to
                      set multiple config values.
  --ignore TEXT       Ignore rules (comma-separated by id or name).
  -v, --verbose       Verbosity, more v's for more verbose output (e.g.: -v,
                      -vv, -vvv). Default: -vvv
  -s, --silent        Silent mode (no output). Takes precedence over -v, -vv,
                      -vvv.
  --version           Show the version and exit.
  --help              Show this message and exit.
```


## Using gitlint as a commit-msg hook ##
You can also install gitlint as a git ```commit-msg``` hook so that gitlint checks your commit messages automatically
after each commit.

```bash
gitlint --install-hook
# To remove the hook
gitlint --uninstall-hook
```

Important: Gitlint cannot work together with an existing hook. If you already have a ```.git/hooks/commit-msg```
file in your local repository, gitlint will refuse to install the ```commit-msg``` hook. gitlint will also only
uninstall unmodified commit-msg hooks that were installed by gitlint.

## Exit codes ##
Gitlint uses the exit code as a simple way to indicate the number of violations found.
Some exit codes are used to indicate special errors as indicated in the table below.

Because of these special error codes and the fact that
[bash only supports exit codes between 0 and 255](http://tldp.org/LDP/abs/html/exitcodes.html), the maximum number
of violations counted by the exit code is 252. Note that gitlint does not have a limit on the number of violations
it can detect, it will just always return with exit code 252 when the number of violations is greater than or equal
to 252.

Exit Code  | Description
-----------|------------------------------------------------------------
253        | Wrong invocation of the ```gitlint``` command.
254        | Something went wrong when invoking git.
255        | Invalid gitlint configuration
