We'd love for you to [contribute to gitlint](https://github.com/jorisroovers/gitlint).
Just create an issue or open a pull request and we'll get right on it!
We maintain a [wishlist on our wiki](https://github.com/jorisroovers/gitlint/wiki/Wishlist),
but we're obviously open to any suggestions!

### Development ###

There is a Vagrantfile in this repository that can be used for development.
```bash
vagrant up
vagrant ssh
```

Or you can choose to use your local environment:

```bash
virtualenv .venv
pip install -r requirements.txt -r test-requirements.txt -r doc-requirements.txt
python setup.py develop
```

To run tests:
```bash
./run_tests.sh                       # run unit tests and print test coverage
./run_test.sh gitlint/tests/test_body_rules.py::BodyRuleTests::test_body_missing # run a single test
./run_tests.sh --no-coverage         # run unit tests without test coverage
./run_tests.sh --integration         # Run integration tests (requires that you have gitlint installed)
./run_tests.sh --pep8                # pep8 checks
./run_tests.sh --stats               # print some code stats
./run_tests.sh --git                 # inception: run gitlint against itself
./run_tests.sh --lint                # run pylint checks
```

To see the package description in HTML format
```
pip install docutils
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
python setup.py --long-description | rst2html.py > output.html
```

### Documentation ###
Outside the vagrant box (on your host machine):
```bash
mkdocs serve
```

Then access the documentation website on your host machine on [http://localhost:8000]().
