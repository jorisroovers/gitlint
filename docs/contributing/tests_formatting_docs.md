## Running tests
```sh
# Gitlint
hatch run dev:gitlint # run the local source copy of gitlint
hatch run dev:gitlint --version 
hatch run dev:gitlint --debug       

# Unit tests
hatch run test:unit-tests
# Variations to run specific tests
hatch run test:unit-tests gitlint-core/gitlint/tests/rules/test_body_rules.py::BodyRuleTests::test_body_missing 
hatch run test:unit-tests -k test_body_missing_merge_commit 
hatch run test:unit-tests-no-cov # don't run test coverage

# Integration tests
hatch run qa:install-local # required step (1)
hatch run qa:integration-tests

# Formatting check (black)
hatch run test:format

# Linting (ruff)
hatch run test:lint

# Type Check (mypy)
hatch run test:type-check

# Run unit-tests and all style checks (format, lint, type-check)
hatch run test:all

# Project stats
hatch run test:stats
```

1. Install the local gitlint source copy for integration testing. <br><br>
   The integration tests will just look for a `gitlint` command and test against that. 
   This means you can also run integration tests against released versions of gitlint:
   ```sh
   pip install gitlint==0.19.1
   hatch run qa:integration-tests
   ```


## Autoformatting and autofixing

We use [black](https://black.readthedocs.io/en/stable/) for code formatting.

```sh
# format all python code
hatch run test:autoformat

# format a specific file
hatch run test:autoformat gitlint-core/gitlint/lint.py
```

We use [ruff](https://github.com/charliermarsh/ruff) for linting, it can autofix many of the issue it finds
(although not always perfect).
```{.sh .copy}
hatch run test:autofix
```

## Documentation
We use [mkdocs](https://www.mkdocs.org/) with [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) and
[mike](https://github.com/jimporter/mike) for generating our documentation from markdown.

To browse the documentation locally (live reload enabled):
```{.sh .copy}
hatch run docs:serve
```

Then access the documentation website on [http://localhost:8000]().

!!! note "Documentation versioning"
    When browsing the docs locally, they will show up under the `latest` version ([http://localhost:8000/latest]()).
    
    However, the online docs at [https://jorisroovers.github.io/gitlint]() are versioned, with new changes first
    being published to `dev` ([https://jorisroovers.github.io/gitlint/dev]()) when they're merged in the `main` branch.
    Only with gitlint releases are the versioned docs updated - `latest` always points to the latest gitlint release.

## Tools
We keep a small set of scripts in the `tools/` directory:

```sh
# Create a test git repo in your /tmp directory
tools/create-test-repo.sh
# Windows: create git test repo
tools/windows/create-test-repo.bat
```
