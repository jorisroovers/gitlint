# Using gitlint in a CI environment
By default, when just running `gitlint` without additional parameters, gitlint lints the last commit in the current
working directory.

This makes it easy to use gitlint in a CI environment (Jenkins, TravisCI, Github Actions, pre-commit, CircleCI, Gitlab, etc).
In fact, this is exactly what we do ourselves: on every commit,
[we run gitlint as part of our CI checks](https://github.com/jorisroovers/gitlint/blob/2a77afd845832c1a00a65e210f9339344dd6f114/.github/workflows/ci.yml#L90-L92).
This will cause the build to fail when we submit a bad commit message.

Alternatively, gitlint will also lint any commit message that you feed it via stdin like so:
```sh
# lint the last commit message
git log -1 --pretty=%B | gitlint # (1)
# lint a specific commit: 62c0519
git log -1 --pretty=%B 62c0519 | gitlint
```

1. Gitlint requires that you specify `--pretty=%B` (=only print the log message, not the metadata),
   future versions of gitlint might fix this and not require the `--pretty` argument.

It's also possible to [lint more than one commit at once](linting_specific_commits.md).