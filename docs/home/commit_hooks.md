## Commit-msg hook
[:octicons-tag-24: v0.4.0][v0.4.0]

You can install gitlint as a git `commit-msg` hook so that gitlint checks your commit messages automatically
after each commit.

```sh
gitlint install-hook
# To remove the hook
gitlint uninstall-hook
```

!!! important

    Gitlint cannot work together with an existing hook. If you already have a `.git/hooks/commit-msg`
    file in your local repository, gitlint will refuse to install the `commit-msg` hook. Gitlint will also only
    uninstall unmodified commit-msg hooks that were installed by gitlint.
    If you're looking to use gitlint in conjunction with other hooks, you should consider
    [using gitlint with pre-commit](#using-gitlint-through-pre-commit).

## Pre-commit

`gitlint` can be configured as a plugin for the [pre-commit](https://pre-commit.com) git hooks
framework.  Simply add the configuration to your `.pre-commit-config.yaml`:

```yaml
-   repo: https://github.com/jorisroovers/gitlint
    rev:  # Fill in a tag / sha here
    hooks:
    -   id: gitlint
```

You then need to install the pre-commit hook like so:
```sh
pre-commit install --hook-type commit-msg
```
!!! important

    It's important that you run `pre-commit install --hook-type commit-msg`, even if you've already used
    `pre-commit install` before. `pre-commit install` does **not** install commit-msg hooks by default!

To manually trigger gitlint using `pre-commit` for your last commit message, use the following command:
```sh
pre-commit run gitlint --hook-stage commit-msg --commit-msg-filename .git/COMMIT_EDITMSG
```

In case you want to change gitlint's behavior, you should either use a `.gitlint` file
(see [Configuration](configuration.md)) or modify the gitlint invocation in
your `.pre-commit-config.yaml` file like so:
```yaml
-   repo: https://github.com/jorisroovers/gitlint
    rev:  # Fill in a tag / sha here (e.g. v0.18.0)
    hooks:
    -   id: gitlint
        args: [--contrib=CT1, --msg-filename]
```

!!! important

    You need to add `--msg-filename` at the end of your custom `args` list as the gitlint-hook will fail otherwise.


### gitlint and pre-commit in CI
gitlint also supports a `gitlint-ci` pre-commit hook that can be used in CI environments.

Configure it like so:
```yaml
-   repo: https://github.com/jorisroovers/gitlint
    rev:  # insert ref, e.g. v0.18.0
    hooks:
    -   id: gitlint    # this is the regular commit-msg hook
    -   id: gitlint-ci # hook for CI environments
```

And invoke it in your CI environment like this:

```sh
pre-commit run --hook-stage manual gitlint-ci
```

By default this will only lint the latest commit.
If you want to lint more commits you can modify the `gitlint-ci` hook like so:

```yaml
-   repo: https://github.com/jorisroovers/gitlint
    rev:  # insert ref, e.g. v0.18.0
    hooks:
    -   id: gitlint
    -   id: gitlint-ci
        args: [--debug, --commits, mybranch] # enable debug mode, lint all commits in mybranch
```