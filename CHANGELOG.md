# Changelog #

## v0.17.0 (2021-11-28) ##
Contributors:
Special thanks to all contributors for this release, in particular [andersk](https://github.com/andersk) and [sigmavirus24](https://github.com/sigmavirus24).

- Gitlint is now split in 2 packages: `gitlint` and `gitlint-core`. This allows users to install gitlint without pinned dependencies (which is the default) ([#162](https://github.com/jorisroovers/gitlint/issues/162))
- Under-the-hood: dependencies updated
## v0.16.0 (2021-10-08) ##

Contributors:
Special thanks to all contributors for this release, in particular [sigmavirus24](https://github.com/sigmavirus24), [l0b0](https://github.com/l0b0) and [rafaelbubach](https://github.com/rafaelbubach).

- Python 3.10 support
- **New Rule**: [ignore-by-author-name](http://jorisroovers.github.io/gitlint/rules/#i4-ignore-by-author-name) allows users to skip linting commit messages made by specific authors
- `--commit <SHA>` flag to more easily lint a single commit message ([#141](https://github.com/jorisroovers/gitlint/issues/141))
- `--fail-without-commits` flag will force gitlint to fail ([exit code 253](https://jorisroovers.com/gitlint/#exit-codes)) when the target commit range is empty (typically when using `--commits`)  ([#193](https://github.com/jorisroovers/gitlint/issues/193))
- Bugfixes:
  - [contrib-title-conventional-commits (CT1)](https://jorisroovers.com/gitlint/contrib_rules/#ct1-contrib-title-conventional-commits)  now properly enforces the commit type ([#185](https://github.com/jorisroovers/gitlint/issues/185))
  - [contrib-title-conventional-commits (CT1)](https://jorisroovers.com/gitlint/contrib_rules/#ct1-contrib-title-conventional-commits) now supports the BREAKING CHANGE symbol "!" ([#186](https://github.com/jorisroovers/gitlint/issues/186))
- Heads-up: [Python 3.6 will become EOL at the end of 2021](https://endoflife.date/python). It's likely that future gitlint releases will stop supporting Python 3.6 as a result. We will continue to support Python 3.6 as long as it's easily doable, which in practice usually means as long as our dependencies support it.
- Under-the-hood: dependencies updated, test and github action improvements.
## v0.15.1 (2021-04-16) ##

Contributors:
Special thanks to all contributors for this release, in particular [PW999](https://github.com/PW999), [gsemet](https://github.com/gsemet) and [Lorac](https://github.com/Lorac).

Bugfixes:
  - Git commit message body with only new lines is not longer considered empty by `body-is-missing` ([#176](https://github.com/jorisroovers/gitlint/issues/176))
  - Added compatibility with `git commit -s` for `contrib-requires-signed-off-by` rule ([#178](https://github.com/jorisroovers/gitlint/pull/178))
- Minor tweak to gitlint commit-hook output ([#173](https://github.com/jorisroovers/gitlint/pull/173))
- All dependencies have been upgraded to the latest available versions (`Click==7.1.2`, `arrow==1.0.3`, `sh==1.14.1`).
- Minor doc fixes
## v0.15.0 (2020-11-27) ##

Contributors:
Special thanks to [BrunIF](https://github.com/BrunIF), [lukech](https://github.com/lukech), [Cielquan](https://github.com/Cielquan), [harens](https://github.com/harens) and [sigmavirus24](https://github.com/sigmavirus24).

**This release drops support for Python 2.7 and Python 3.5 ([both are EOL](https://endoflife.date/python)). Other than a few minor fixes, there are no functional differences from the 0.14.0 release.**

Other call-outs:
- **Mac users**: Gitlint can now be installed using both homebrew (upgraded to latest) and macports. Special thanks to [@harens](https://github.com/harens) for maintaining these packages (best-effort).
- Bugfix: Gitlint now properly handles exceptions when using its built-in commit-msg hook ([#166](https://github.com/jorisroovers/gitlint/issues/166)).
- All dependencies have been upgraded to the latest available versions (`Click==7.1.2`, `arrow==0.17.0`, `sh==1.14.1`).
- Much under-the-hood refactoring as a result of dropping Python 2.7

## v0.14.0 (2020-10-24) ##

Contributors:
Special thanks to all contributors for this release, in particular [mrshu](https://github.com/mrshu), [glasserc](https://github.com/glasserc), [strk](https://github.com/strk), [chgl](https://github.com/chgl), [melg8](https://github.com/melg8) and [sigmavirus24](https://github.com/sigmavirus24).


- **IMPORTANT: Gitlint 0.14.x will be the last gitlint release to support Python 2.7 and Python 3.5, as [both are EOL](https://endoflife.date/python) which makes it difficult to keep supporting them.**
- Python 3.9 support
- **New Rule**: [title-min-length](http://jorisroovers.github.io/gitlint/rules/#t8-title-min-length) enforces a minimum length on titles (default: 5 chars) ([#138](https://github.com/jorisroovers/gitlint/issues/138))
- **New Rule**: [body-match-regex](http://jorisroovers.github.io/gitlint/rules/#b8-body-match-regex) allows users to enforce that the commit-msg body matches a given regex ([#130](https://github.com/jorisroovers/gitlint/issues/130))
- **New Rule**: [ignore-body-lines](http://jorisroovers.github.io/gitlint/rules/#i3-ignore-body-lines) allows users to
[ignore parts of a commit](http://jorisroovers.github.io/gitlint/gitlint/#ignoring-commits) by matching a regex against
the lines in a commit message body ([#126](https://github.com/jorisroovers/gitlint/issues/126))
- [Named Rules](http://jorisroovers.github.io/gitlint/#named-rules) allow users to have multiple instances of the same rule active at the same time. This is useful when you want to enforce the same rule multiple times but with different options ([#113](https://github.com/jorisroovers/gitlint/issues/113), [#66](https://github.com/jorisroovers/gitlint/issues/66))
- [User-defined Configuration Rules](http://jorisroovers.github.io/gitlint/user_defined_rules/#configuration-rules) allow users to dynamically change gitlint's configuration and/or the commit *before* any other rules are applied.
- The `commit-msg` hook has been re-written in Python (it contained a lot of Bash before), fixing a number of platform specific issues. Existing users will need to reinstall their hooks (`gitlint uninstall-hook; gitlint install-hook`) to make use of this.
- Most general options can now be set through environment variables (e.g. set the `general.ignore` option via `GITLINT_IGNORE=T1,T2`). The list of available environment variables can be found in the [configuration documentation](http://jorisroovers.github.io/gitlint/configuration).
- Users can now use `self.log.debug("my message")` for debugging purposes in their user-defined rules. Debug messages will show up when running `gitlint --debug`.
- **Breaking**: User-defined rule id's can no longer start with 'I', as those are reserved for [built-in gitlint ignore rules](http://jorisroovers.github.io/gitlint/rules/#i1-ignore-by-title).
-  New `RegexOption` rule [option type for use in user-defined rules](http://jorisroovers.github.io/gitlint/user_defined_rules/#options). By using the `RegexOption`, regular expressions are pre-validated at gitlint startup and compiled only once which is much more efficient when linting multiple commits.
- Bugfixes:
  -  Improved UTF-8 fallback on Windows (ongoing - [#96](https://github.com/jorisroovers/gitlint/issues/96))
  - Windows users can now use the 'edit' function of the `commit-msg` hook ([#94](https://github.com/jorisroovers/gitlint/issues/94))
  -  Doc update: Users should use `--ulimit nofile=1024` when invoking gitlint using Docker ([#129](https://github.com/jorisroovers/gitlint/issues/129))
  - The `commit-msg` hook was broken in Ubuntu's gitlint package due to a python/python3 mismatch ([#127](https://github.com/jorisroovers/gitlint/issues/127))
  - Better error message when no git username is set ([#149](https://github.com/jorisroovers/gitlint/issues/149))
  - Options can now actually be set to `None` (from code) to make them optional.
  -  Ignore rules no longer have `"None"` as default regex, but an empty regex - effectively disabling them by default (as intended).
- Contrib Rules:
  - Added 'ci' and 'build' to conventional commit types ([#135](https://github.com/jorisroovers/gitlint/issues/135))
- Under-the-hood: minor performance improvements (removed some unnecessary regex matching), test improvements, improved debug logging, CI runs on pull requests, PR request template.

## v0.13.1 (2020-02-26)

- Patch to enable `--staged` flag for pre-commit.
- Minor doc updates ([#109](https://github.com/jorisroovers/gitlint/issues/109))

## v0.13.0 (2020-02-25)

- **Behavior Change**: Revert Commits are now recognized and ignored by default ([#99](https://github.com/jorisroovers/gitlint/issues/99))
- `--staged` flag: gitlint can now detect meta-data (such as author details, changed files, etc) of staged/pre-commits. Useful when you use [gitlint's commit-msg hook](https://jorisroovers.github.io/gitlint/#using-gitlint-as-a-commit-msg-hook) or [precommit](https://jorisroovers.github.io/gitlint/#using-gitlint-through-pre-commit) ([#105](https://github.com/jorisroovers/gitlint/issues/105))
- New branch properties on `GitCommit` and `GitContext`, useful when writing your own user-defined rules: `commit.branches` and `commit.context.current_branch` ([#108](https://github.com/jorisroovers/gitlint/issues/108))
- Python 3.8 support
- Python 3.4 no longer supported. Python 3.4 has [reached EOL](https://www.python.org/dev/peps/pep-0429/#id4) and an increasing
  of gitlint's dependencies have dropped support which makes it hard to maintain.
- Improved Windows support: better unicode handling. [Issues remain](https://github.com/jorisroovers/gitlint/issues?q=is%3Aissue+is%3Aopen+label%3Awindows) but the basic functionality works.
- Bugfixes:
  - Gitlint no longer crashes when acting on empty repositories (this only occurred in specific circumstances).
  - Changed files are now better detected in repos that only have a root commit
- Improved performance and memory (gitlint now caches git properties) 
- Improved `--debug` output
- Improved documentation
- Under-the-hood: dependencies updated, unit and integration test improvements, migrated from TravisCI to Github Actions.

## v0.12.0 (2019-07-15) ##

Contributors:
Special thanks to all contributors for this release, in particular [@rogalksi](https://github.com/rogalski) and [@byrney](https://github.com/byrney).

- [Contrib Rules](http://jorisroovers.github.io/gitlint/contrib_rules): community-contributed rules that are disabled
   by default, but can be enabled through configuration. Contrib rules are meant to augment default gitlint behavior by
   providing users with rules for common use-cases without forcing these rules on all gitlint users.
    - **New Contrib Rule**: `contrib-title-conventional-commits` enforces the [Conventional Commits](https://www.conventionalcommits.org) spec. Details in our [documentation](http://jorisroovers.github.io/gitlint/contrib_rules/#ct1-contrib-title-conventional-commits).
    - **New Contrib Rule**: `cc1-contrib-requires-signed-off-by` ensures that all commit messages contain a `Sign-Off-By` line. Details in our [documentation](http://jorisroovers.github.io/gitlint/contrib_rules/#cc1-contrib-requires-signed-off-by).
    - If you're interested in adding new Contrib rules to gitlint, please start by reading the
      [Contributing](http://jorisroovers.github.io/gitlint/contributing/) page. Thanks for considering!
- *Experimental (!)* Windows support: Basic functionality is working, but there are still caveats. For more details, please refer to [#20](https://github.com/jorisroovers/gitlint/issues/20) and the [open issues related to Windows](https://github.com/jorisroovers/gitlint/issues?q=is%3Aissue+is%3Aopen+label%3Awindows).
- Python 3.3 no longer supported. Python 3.4 is likely to follow in a future release as it has [reached EOL](https://www.python.org/dev/peps/pep-0429/#id4) as well.
- PyPy 3.5 support
- Support for `--ignore-stdin` command-line flag to ignore any text send via stdin. ([#56](https://github.com/jorisroovers/gitlint/issues/56), [#89](https://github.com/jorisroovers/gitlint/issues/89))
- Bugfixes:
  - [#68: Can't use install-hooks in with git worktree](https://github.com/jorisroovers/gitlint/issues/68)
  - [#59: gitlint failed with configured commentchar](https://github.com/jorisroovers/gitlint/issues/59)
- Under-the-hood: dependencies updated, experimental Dockerfile, github issue template.

## v0.11.0 (2019-03-13) ##

- Python 3.7 support
- Python 2.6 no longer supported
- Various dependency updates and under the hood fixes (see [#76](https://github.com/jorisroovers/gitlint/pull/76) for details).

Special thanks to @pbregener for his contributions related to python 3.7 support and test fixes.

## v0.10.0 (2018-04-15) ##
The 0.10.0 release adds the ability to ignore commits based on their contents,
support for [pre-commit](https://pre-commit.com/), and important fix for running gitlint in CI environments
(such as Jenkins, Gitlab, etc).

Special thanks to [asottile](https://github.com/asottile), [bdrung](https://github.com/bdrung), [pbregener](https://github.com/pbregener), [torwald-sergesson](https://github.com/torwald-sergesson), [RykHawthorn](https://github.com/RykHawthorn), [SteffenKockel](https://github.com/SteffenKockel) and [tommyip](https://github.com/tommyip) for their contributions.

**Since it's becoming increasingly hard to support Python 2.6 and 3.3, we'd like to encourage our users to upgrade their
python version to 2.7 or 3.3+. Future versions of gitlint are likely to drop support for Python 2.6 and 3.3.**

Full Changelog:

- **New Rule**: `ignore-by-title` allows users to
[ignore certain commits](http://jorisroovers.github.io/gitlint/#ignoring-commits) by matching a regex against
a commit message title. ([#54](https://github.com/jorisroovers/gitlint/issues/54), [#57](https://github.com/jorisroovers/gitlint/issues/57)).
- **New Rule**: `ignore-by-body` allows users to
[ignore certain commits](http://jorisroovers.github.io/gitlint/#ignoring-commits) by matching a regex against
a line in a commit message body.
- Gitlint now supports [pre-commit.com](https://pre-commit.com).
[Details in our documentation](http://jorisroovers.github.io/gitlint/#using-gitlint-through-pre-commit)
([#62](https://github.com/jorisroovers/gitlint/issues/62)).
- Gitlint now has a `--msg-filename` commandline flag that allows you to specify the commit message to lint via
  a file ([#39](https://github.com/jorisroovers/gitlint/issues/39)).
- Gitlint will now be silent by default when a specified commit range is empty ([#46](https://github.com/jorisroovers/gitlint/issues/46)).
- Gitlint can now be installed on MacOS by brew via the [homebrew-devops](https://github.com/rockyluke/homebrew-devops) tap. To get the latest version of gitlint, always use pip for installation.
- If all goes well,
[gitlint will also be available as a package in the Ubuntu 18.04 repositories](https://launchpad.net/ubuntu/+source/gitlint).
- Bugfixes:
  - We fixed a nasty and recurring issue with running gitlint in CI. Hopefully that's the end of it :-) ([#40](https://github.com/jorisroovers/gitlint/issues/40)).
  - Fix for custom git comment characters ([#48](https://github.com/jorisroovers/gitlint/issues/48)).

## v0.9.0 (2017-12-03) ##
The 0.9.0 release adds a new default `author-valid-email` rule, important bugfixes and special case handling.
Special thanks to [joshholl](https://github.com/joshholl), [ron8mcr](https://github.com/ron8mcr),
[omarkohl](https://github.com/omarkohl), [domo141](https://github.com/domo141), [nud](https://github.com/nud)
and [AlexMooney](https://github.com/AlexMooney) for their contributions.

- New Rule: `author-valid-email` enforces a valid author email address. Details can be found in the
  [Rules section of the documentation](http://jorisroovers.github.io/gitlint/rules/#m1-author-valid-email).
- **Breaking change**: The `--commits` commandline flag now strictly follows the refspec format as interpreted
  by the [`git rev-list <refspec>`](https://git-scm.com/docs/git-rev-list) command. This means
  that linting a single commit using `gitlint --commits <SHA>` won't work anymore. Instead, for single commits,
  users now need to specificy `gitlint --commits <SHA>^...<SHA>`. On the upside, this change also means
  that gitlint will now understand all refspec formatters, including `gitlint --commits HEAD` to lint all commits
  in the repository. This fixes [#23](https://github.com/jorisroovers/gitlint/issues/23).
- **Breaking change**: Gitlint now always falls back on trying to read a git message from a local git repository, only
  reading a commit message from STDIN if one is passed. Before, gitlint only read from the local git repository when
  a TTY was present. This is likely the expected and desired behavior for anyone running gitlint in a CI environment.
  This fixes [#40](https://github.com/jorisroovers/gitlint/issues/40) and
  [#42](https://github.com/jorisroovers/gitlint/issues/42).
- **Behavior Change**: Gitlint will now by default
  [ignore squash and fixup commits](http://jorisroovers.github.io/gitlint/#merge-fixup-and-squash-commits)
  (fix for [#33: fixup messages should not trigger a gitlint violation](https://github.com/jorisroovers/gitlint/issues/33))
- Support for custom comment characters ([#34](https://github.com/jorisroovers/gitlint/issues/34))
- Support for [`git commit --cleanup=scissors`](https://git-scm.com/docs/git-commit#git-commit---cleanupltmodegt)
  ([#34](https://github.com/jorisroovers/gitlint/issues/34))
- Bugfix: [#37: Prevent Commas in text fields from breaking git log printing](https://github.com/jorisroovers/gitlint/issues/37)
- Debug output improvements

## v0.8.2 (2017-04-25) ##

The 0.8.2 release brings minor improvements, bugfixes and some under-the-hood changes. Special thanks to
[tommyip](https://github.com/tommyip) for his contributions.

- `--extra-path` now also accepts a file path (in the past only directory paths where accepted).
Thanks to [tommyip](https://github.com/tommyip) for implementing this!
- gitlint will now show more information when using the `--debug` flag. This is initial work and will continue to
be improved upon in later releases.
- Bugfixes:
    - [#24: --commits doesn't take commit specific config into account](https://github.com/jorisroovers/gitlint/issues/24)
    - [#27: --commits returns the wrong exit code](https://github.com/jorisroovers/gitlint/issues/27)
- Development: better unit and integration test coverage for `--commits`

## v0.8.1 (2017-03-16) ##

The 0.8.1 release brings minor tweaks and some experimental features. Special thanks to
[tommyip](https://github.com/tommyip) for his contributions.

- Experimental: Linting a range of commits.
  [Documentation](http://jorisroovers.github.io/gitlint/#linting-a-range-of-commits).
  Known Caveats: [#23](https://github.com/jorisroovers/gitlint/issues/23),
  [#24](https://github.com/jorisroovers/gitlint/issues/24).
  Closes [#14](https://github.com/jorisroovers/gitlint/issues/14). Thanks to [tommyip](https://github.com/tommyip)
  for implementing this!
- Experimental: Python 3.6 support
- Improved Windows error messaging: gitlint will now show a more descriptive error message when ran on windows.
  See [#20](https://github.com/jorisroovers/gitlint/issues/20) for details on the lack of Windows support.

## v0.8.0 (2016-12-30) ##

The 0.8.0 release is a significant release that has been in the works for a long time. Special thanks to
[Claymore](https://github.com/Claymore), [gernd](https://github.com/gernd) and
[ZhangYaxu](https://github.com/ZhangYaxu) for submitting bug reports and pull requests.

- Full unicode support: you can now lint messages in any language! This fixes
  [#16](https://github.com/jorisroovers/gitlint/issues/16) and [#18](https://github.com/jorisroovers/gitlint/pull/18).
- User-defined rules: you can now
  [define your own custom rules](http://jorisroovers.github.io/gitlint/user_defined_rules/)
  if you want to extend gitlint's functionality.
- Pypy2 support!
- Debug output improvements: Gitlint will now print your active configuration when using `--debug`
- The `general.target` option can now also be set via `-c` flags or a `.gitlint` file
- Bugfixes:
    - Various important fixes related to configuration precedence
    - [#17: Body MinLength is not working properly](https://github.com/jorisroovers/gitlint/issues/17).
      **Behavior Change**: Gitlint now always applies this rule, even if the body has just a single line of content.
      Also, gitlint now counts the body-length for the entire body, not just the length of the first line.
- Various documentation improvements
- Development: 
    - Pylint compliance for all supported python versions
    - Updated dependencies to latest versions
    - Various `run_tests.sh` improvements for developer convenience

## v0.7.1 (2016-06-18) ##
Bugfixes:

- **Behavior Change**: gitlint no longer prints the file path by default when using a `.gitlint` file. The path
will still be printed when using the new `--debug` flag. Special thanks to [Slipcon](https://github.com/slipcon)
for submitting this.
- Gitlint now prints a correct violation message for the `title-match-regex` rule.  Special thanks to
[Slipcon](https://github.com/slipcon) for submitting this.
- Gitlint is now better at parsing commit messages cross-platform by taking platform specific line endings into account
- Minor documentation improvements

## v0.7.0 (2016-04-20) ##
This release contains mostly bugfix and internal code improvements. Special thanks to
[William Turell](https://github.com/wturrell) and [Joe Grund](https://github.com/jgrund) for bug reports and pull
requests.

- commit-msg hooks improvements: The new commit-msg hook now allows you to edit your message if it contains violations,
  prints the commit message on aborting and is more compatible with GUI-based git clients such as SourceTree.
  *You will need to uninstall and reinstall the commit-msg hook for these latest features*.
- Python 2.6 support
- **Behavior change**: merge commits are now ignored by default. The rationale is that the original commits
  should already be linted and that many merge commits don't pass gitlint checks by default
  (e.g. exceeding title length or empty body is very common). This behavior can be overwritten by setting the
  general option `ignore-merge-commit=false`.
- Bugfixes and enhancements:
    - [#7: Hook compatibility with SourceTree](https://github.com/jorisroovers/gitlint/issues/7)
    - [#8: Illegal option -e](https://github.com/jorisroovers/gitlint/issues/8)
    - [#9: print full commit msg to stdout if aborted](https://github.com/jorisroovers/gitlint/issues/9)
    - [#11 merge commit titles exceeding the max title length by default](https://github.com/jorisroovers/gitlint/issues/11)
    - Better error handling of invalid general options
- Development: internal refactoring to extract more info from git. This will allow for more complex rules in the future.
- Development: initial set of integration tests. Test gitlint end-to-end after it is installed.
- Development: pylint compliance for python 2.7

## v0.6.1 (2015-11-22) ##

- Fix: `install-hook` and `generate-config` commands not working when gitlint is installed from pypi.

## v0.6.0 (2015-11-22) ##

- Python 3 (3.3+) support!
- All documentation is now hosted on [http://jorisroovers.github.io/gitlint/]()
- New `generate-config` command generates a sample gitlint config file
- New `--target` flag allows users to lint different directories than the current working directory
- **Breaking change**: exit code behavior has changed. More details in the
  [Exit codes section of the documentation](http://jorisroovers.github.io/gitlint/#exit-codes).
- **Breaking change**: `--install-hook` and `--uninstall-hook` have been renamed to `install-hook` and
  `uninstall-hook` respectively to better express that they are commands instead of options.
- Better error handling when gitlint is executed in a directory that is not a git repository or 
  when git is not installed.
- The git commit message hook now uses pretty colored output
- Fix: `--config` option no longer accepts directories as value
- Development: unit tests are now ran using py.test

## v0.5.0 (2015-10-04) ##

- New Rule: `title-match-regex`. Details can be found in the
  [Rules section of the documentation](http://jorisroovers.github.io/gitlint/rules/).
- Uninstall previously installed gitlint git commit hooks using: `gitlint --uninstall-hook`
- Ignore rules on a per commit basis by adding e.g.: `gitlint-ignore: T1, body-hard-tab` to your git commit message.
  Use `gitlint-ignore: all` to disable gitlint all together for a specific commit.
- `body-is-missing` will now automatically be disabled for merge commits (use the `ignore-merge-commit: false`
  option to disable this behavior)
- Violations are now sorted by line number first and then by rule id (previously the order of violations on the
  same line was arbitrary).

## v0.4.1 (2015-09-19) ##

- Internal fix: added missing comma to setup.py which prevented pypi upload

## v0.4.0 (2015-09-19) ##

- New rules: `body-is-missing`, `body-min-length`, `title-leading-whitespace`,
  `body-changed-file-mention`. Details can be found in the
  [Rules section of the documentation](http://jorisroovers.github.io/gitlint/rules/).
- The git `commit-msg`  hook now allows you to keep or discard the commit when it fails gitlint validation
- gitlint is now also released as a [python wheel](http://pythonwheels.com/) on pypi.
- Internal: rule classes now have access to a gitcontext containing body the commit message and the files changed in the
  last commit.

## v0.3.0 (2015-09-11) ##
- `title-must-not-contain-word` now has a `words` option that can be used to specify which words should not
  occur in the title
- gitlint violations are now printed to the stderr instead of stdout
- Various minor bugfixes
- gitlint now ignores commented out lines (i.e. starting with #) in your commit messages
- Experimental: git commit-msg hook support
- Under-the-hood: better test coverage :-)

## v0.2.0 (2015-09-10) ##
 - Rules can now have their behavior configured through options. 
   For example, the `title-max-length` rule now has a `line-length` option.
 - Under-the-hood: The codebase now has a basic level of unit test coverage, increasing overall quality assurance
 
## v0.1.1 (2015-09-08) ##
- Bugfix: added missing `sh` dependency

## v0.1.0 (2015-09-08) ##
- Initial gitlint release
- Initial set of rules: title-max-length, title-trailing-whitespace, title-trailing-punctuation , title-hard-tab, 
  title-must-not-contain-word, body-max-line-length, body-trailing-whitespace, body-hard-tab 
- General gitlint configuration through a `gitlint` file
- Silent and verbose mode
- Vagrantfile for easy development
- gitlint is available on [pypi](https://pypi.python.org/pypi/gitlint)
