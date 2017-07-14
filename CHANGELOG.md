# Changelog #

## v0.9.0 (In Progress) ##

- New Rule: ```author-valid-email``` enforces a valid author email address. Details can be found in the
  [Rules section of the documentation](http://jorisroovers.github.io/gitlint/rules/).
- **Breaking change**: The ```--commits``` commandline flag now strictly follows the refspec format as interpreted
  by the [```git rev-list <refspec>```](https://git-scm.com/docs/git-rev-list) command. This means
  that linting a single commit using ```gitlint --commits <SHA>``` won't work anymore. Instead, for single commits,
  users now need to specificy ```gitlint --commits <SHA>^...<SHA>```. On the upside, this change also means
  that gitlint will now understand all refspec formatters, including ```gitlint --commits HEAD``` to lint all commits
  in the repository.
- Debug output improvements

## v0.8.2 (2017-04-25) ##

The 0.8.2 release brings minor improvements, bugfixes and some under-the-hood changes. Special thanks to 
[tommyip](https://github.com/tommyip) for his contributions.
- ```--extra-path``` now also accepts a file path (in the past only directory paths where accepted).
Thanks to [tommyip](https://github.com/tommyip) for implementing this!
- gitlint will now show more information when using the ```--debug``` flag. This is initial work and will continue to
be improved upon in later releases.
- Bugfixes:
    - [#24: --commits doesn't take commit specific config into account](https://github.com/jorisroovers/gitlint/issues/24)
    - [#27: --commits returns the wrong exit code](https://github.com/jorisroovers/gitlint/issues/27)
- Development: better unit and integration test coverage for ```--commits```

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
- Debug output improvements: Gitlint will now print your active configuration when using ```--debug```
- The ```general.target``` option can now also be set via ```-c``` flags or a ```.gitlint``` file
- Bugfixes:
    - Various important fixes related to configuration precedence
    - [#17: Body MinLength is not working properly](https://github.com/jorisroovers/gitlint/issues/17).
      **Behavior Change**: Gitlint now always applies this rule, even if the body has just a single line of content.
      Also, gitlint now counts the body-length for the entire body, not just the length of the first line.
- Various documentation improvements
- Development: 
    - Pylint compliance for all supported python versions
    - Updated dependencies to latest versions
    - Various ```run_tests.sh``` improvements for developer convenience

## v0.7.1 (2016-06-18) ##
Bugfixes:

- **Behavior Change**: gitlint no longer prints the file path by default when using a ```.gitlint``` file. The path
will still be printed when using the new ```--debug``` flag. Special thanks to [Slipcon](https://github.com/slipcon)
for submitting this.
- Gitlint now prints a correct violation message for the ```title-match-regex``` rule.  Special thanks to
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
  general option ```ignore-merge-commit=false```.
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

- Fix: ```install-hook``` and ```generate-config``` commands not working when gitlint is installed from pypi.

## v0.6.0 (2015-11-22) ##

- Python 3 (3.3+) support!
- All documentation is now hosted on [http://jorisroovers.github.io/gitlint/]()
- New ```generate-config``` command generates a sample gitlint config file
- New ```--target``` flag allows users to lint different directories than the current working directory
- **Breaking change**: exit code behavior has changed. More details in the
  [Exit codes section of the documentation](http://jorisroovers.github.io/gitlint/#exit-codes).
- **Breaking change**: ```--install-hook``` and ```--uninstall-hook``` have been renamed to ```install-hook``` and
  ```uninstall-hook``` respectively to better express that they are commands instead of options.
- Better error handling when gitlint is executed in a directory that is not a git repository or 
  when git is not installed.
- The git commit message hook now uses pretty colored output
- Fix: ```--config``` option no longer accepts directories as value
- Development: unit tests are now ran using py.test

## v0.5.0 (2015-10-04) ##

- New Rule: ```title-match-regex```. Details can be found in the
  [Rules section of the documentation](http://jorisroovers.github.io/gitlint/rules/).
- Uninstall previously installed gitlint git commit hooks using: ```gitlint --uninstall-hook```
- Ignore rules on a per commit basis by adding e.g.: ```gitlint-ignore: T1, body-hard-tab``` to your git commit message.
  Use ```gitlint-ignore: all``` to disable gitlint all together for a specific commit.
- ```body-is-missing``` will now automatically be disabled for merge commits (use the ```ignore-merge-commit: false```
  option to disable this behavior)
- Violations are now sorted by line number first and then by rule id (previously the order of violations on the
  same line was arbitrary).

## v0.4.1 (2015-09-19) ##

- Internal fix: added missing comma to setup.py which prevented pypi upload

## v0.4.0 (2015-09-19) ##

- New rules: ```body-is-missing```, ```body-min-length```, ```title-leading-whitespace```,
  ```body-changed-file-mention```. Details can be found in the
  [Rules section of the documentation](http://jorisroovers.github.io/gitlint/rules/).
- The git ```commit-msg```  hook now allows you to keep or discard the commit when it fails gitlint validation
- gitlint is now also released as a [python wheel](http://pythonwheels.com/) on pypi.
- Internal: rule classes now have access to a gitcontext containing body the commit message and the files changed in the
  last commit.

## v0.3.0 (2015-09-11) ##
- ```title-must-not-contain-word``` now has a ```words``` option that can be used to specify which words should not
  occur in the title
- gitlint violations are now printed to the stderr instead of stdout
- Various minor bugfixes
- gitlint now ignores commented out lines (i.e. starting with #) in your commit messages
- Experimental: git commit-msg hook support
- Under-the-hood: better test coverage :-)

## v0.2.0 (2015-09-10) ##
 - Rules can now have their behavior configured through options. 
   For example, the ```title-max-length``` rule now has a ```line-length``` option.
 - Under-the-hood: The codebase now has a basic level of unit test coverage, increasing overall quality assurance
 
## v0.1.1 (2015-09-08) ##
- Bugfix: added missing ```sh``` dependency

## v0.1.0 (2015-09-08) ##
- Initial gitlint release
- Initial set of rules: title-max-length, title-trailing-whitespace, title-trailing-punctuation , title-hard-tab, 
  title-must-not-contain-word, body-max-line-length, body-trailing-whitespace, body-hard-tab 
- General gitlint configuration through a ```gitlint``` file
- Silent and verbose mode
- Vagrantfile for easy development
- gitlint is available on [pypi](https://pypi.python.org/pypi/gitlint)
