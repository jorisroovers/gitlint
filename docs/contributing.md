# Contributing

We'd love for you to contribute to gitlint. Thanks for your interest!
The [source-code and issue tracker](https://github.com/jorisroovers/gitlint) are hosted on Github.

Often it takes a while for us (well, actually just [me](https://github.com/jorisroovers)) to get back to you
(sometimes up to a few months, this is a hobby project), but rest assured that we read your message and appreciate
your interest!
We maintain a [loose roadmap on our wiki](https://github.com/jorisroovers/gitlint/wiki/Roadmap), but
that's open to a lot of change and input.

## Guidelines

When contributing code, please consider all the parts that are typically required:

- [Unit tests](https://github.com/jorisroovers/gitlint/tree/main/gitlint-core/gitlint/tests) (automatically
  [enforced by CI](https://github.com/jorisroovers/gitlint/actions)). Please consider writing
  new ones for your functionality, not only updating existing ones to make the build pass.
- [Integration tests](https://github.com/jorisroovers/gitlint/tree/main/qa) (also automatically
  [enforced by CI](https://github.com/jorisroovers/gitlint/actions)). Again, please consider writing new ones
  for your functionality, not only updating existing ones to make the build pass.
- [Documentation](https://github.com/jorisroovers/gitlint/tree/main/docs)

Since we want to maintain a high standard of quality, all of these things will have to be done regardless before code
can make it as part of a release. If you can already include them as part of your PR, it's a huge timesaver for us
and it's likely that your PR will be merged and released a lot sooner. Thanks!

!!! Important
    **On the topic of releases**: Gitlint releases typically go out when there's either enough new features and fixes
    to make it worthwhile or when there's a critical fix for a bug that fundamentally breaks gitlint. While the amount
    of overhead of doing a release isn't huge, it's also not zero. In practice this means that it might take weeks
    or months before merged code actually gets released - we know that can be frustrating but please understand it's
    a well-considered trade-off based on available time.

## Development

There is a Vagrantfile (Ubuntu) in this repository that can be used for development.
It comes pre-installed with all Python versions that gitlint supports.
```sh
vagrant up
vagrant ssh
```

Or you can choose to use your local environment:

```sh
python -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt -r test-requirements.txt -r doc-requirements.txt
python setup.py develop
```

To run tests:
```sh
./run_tests.sh                       # run unit tests and print test coverage
./run_tests.sh gitlint/tests/rules/test_body_rules.py::BodyRuleTests::test_body_missing # run a single test
./run_tests.sh --no-coverage         # run unit tests without test coverage
./run_tests.sh --collect-only --no-coverage  # Only collect, don't run unit tests
./run_tests.sh --integration         # Run integration tests (requires that you have gitlint installed)
./run_tests.sh --build               # Run build tests (=build python package)
./run_tests.sh --format              # format checks
./run_tests.sh --stats               # print some code stats
./run_tests.sh --git                 # inception: run gitlint against itself
./run_tests.sh --lint                # run pylint checks
./run_tests.sh --all                 # Run unit, integration, format and gitlint checks
```

The `Vagrantfile` comes with `virtualenv`s for python 3.6, 3.7, 3.8, 3.9 and pypy3.6.
You can easily run tests against specific python environments by using the following commands *inside* of the Vagrant VM:
```sh
./run_tests.sh --envs 36               # Run the unit tests against Python 3.6
./run_tests.sh --envs 36,37,pypy36     # Run the unit tests against Python 3.6, Python 3.7 and Pypy3.6
./run_tests.sh --envs 36,37 --format   # Run format checks against Python 3.6 and Python 3.7 (also works for --git, --integration, --format, --stats and --lint.
./run_tests.sh --envs all --all        # Run all tests against all environments
./run_tests.sh --all-env --all         # Idem: Run all tests against all environments
```

!!! important
    Gitlint commits and pull requests are gated on all of our tests and checks.

## Packaging

To see the package description in HTML format
```sh
pip install docutils
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
python setup.py --long-description | rst2html.py > output.html
```

## Documentation
We use [mkdocs](https://www.mkdocs.org/) for generating our documentation from markdown.

To use it, do the following outside of the vagrant box (on your host machine):
```sh
pip install -r doc-requirements.txt # install doc requirements
mkdocs serve
```

Then access the documentation website on your host machine on [http://localhost:8000]().

## Tools
We keep a small set of scripts in the `tools/` directory:

```sh
tools/create-test-repo.sh            # Create a test git repo in your /tmp directory
tools/windows/create-test-repo.bat   # Windows: create git test repo
tools/windows/run_tests.bat          # Windows run unit tests
```

## Contrib rules
Since gitlint 0.12.0, we support [Contrib rules](../contrib_rules): community contributed rules that are part of gitlint
itself. Thanks for considering to add a new one to gitlint!

Before starting, please read all the other documentation on this page about contributing first.
Then, we suggest taking the following approach to add a Contrib rule:

1. **Write your rule as a [user-defined rule](../user_defined_rules)**. In terms of code, Contrib rules are identical to
   user-defined rules, they just happen to have their code sit within the gitlint codebase itself.
2. **Add your user-defined rule to gitlint**. You should put your file(s) in the [gitlint/contrib/rules](https://github.com/jorisroovers/gitlint/tree/main/gitlint-core/gitlint/contrib/rules) directory.
3. **Write unit tests**. The gitlint codebase contains [Contrib rule test files you can copy and modify](https://github.com/jorisroovers/gitlint/tree/main/gitlint-core/gitlint/tests/contrib/rules).
4. **Write documentation**. In particular, you should update the [gitlint/docs/contrib_rules.md](https://github.com/jorisroovers/gitlint/blob/main/docs/contrib_rules.md) file with details on your Contrib rule.
5. **Create a Pull Request**: code review typically requires a bit of back and forth. Thanks for your contribution!


### Contrib rule requirements
If you follow the steps above and follow the existing gitlint conventions wrt naming things, you should already be fairly close to done.

In case you're looking for a slightly more formal spec, here's what gitlint requires of Contrib rules.

- Since Contrib rules are really just user-defined rules that live within the gitlint code-base, all the [user-rule requirements](../user_defined_rules/#rule-requirements) also apply to Contrib rules.
- All contrib rules **must** have associated unit tests. We *sort of* enforce this by a unit test that verifies that there's a
  test file for each contrib file.
- All contrib rules **must** have names that start with `contrib-`. This is to easily distinguish them from default gitlint rules.
- All contrib rule ids **must** start with `CT` (for LineRules targeting the title), `CB` (for LineRules targeting the body) or `CC` (for CommitRules). Again, this is to easily distinguish them from default gitlint rules.
- All contrib rules **must** have unique names and ids.
- You **can** add multiple rule classes to the same file, but classes **should** be logically grouped together in a single file that implements related rules.
- Contrib rules **should** be meaningfully different from one another. If a behavior change or tweak can be added to an existing rule by adding options, that should be considered first. However, large [god classes](https://en.wikipedia.org/wiki/God_object) that implement multiple rules in a single class should obviously also be avoided.
- Contrib rules **should** use [options](../user_defined_rules/#options) to make rules configurable.
