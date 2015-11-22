# Changelog #

## v0.6.0dev (work in progress) ##

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
