# Changelog #

## v0.3.0dev (master) ##
- ```title-must-not-contain-word``` now has a ```words``` option that can be used to specify which words should not
  occur in the title
- gitlint violations are now printed to the stderr instead of stdout
- Various minor bugfixes
- gitlint now ignores commented out lines (i.e. starting with #) in your commit messages
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
