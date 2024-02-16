## Introduction
[:octicons-tag-24: v0.12.0][v0.12.0] 


Contrib rules are community-**contrib**uted rules that are disabled by default, but can be enabled through configuration.

Contrib rules are meant to augment default gitlint behavior by providing users with rules for common use-cases without
forcing these rules on all gitlint users. This also means that users don't have to
re-implement these commonly used rules themselves as [user-defined](user_defined_rules/index.md) rules.

Example:

```sh
$ gitlint
1: CC1 Body does not contain a 'Signed-off-by' line
1: CL1 Title does not start with one of fix, feat, chore, docs, style, refactor, perf, test: "WIP: This is the title of a commit message."
```


To enable contrib rules:

=== ":octicons-file-code-16:  .gitlint"
   
    ```ini
    [general]
    # You HAVE to add the rule to [general] to enable it
    # Only configuring (such as below) does NOT enable it.
    contrib = contrib-title-conventional-commits,CC1

    # Setting contrib rule options is identical to configuring other rules 
    [contrib-title-conventional-commits]
    types = bugfix,user-story,epic
    ```

=== ":octicons-terminal-16:  CLI"

    ```sh
    $ gitlint --contrib contrib-title-conventional-commits,CC1
    ```

=== ":material-application-variable-outline: Env var"

    ```sh
    GITLINT_CONTRIB=contrib-title-conventional-commits,CC1 gitlint
    ```

## Available contrib rules
### CT1: contrib-title-conventional-commits
[:octicons-tag-24: v0.12.0][v0.12.0] · **ID**: CT1 · **Name**: contrib-title-conventional-commits

Enforces [Conventional Commits](https://www.conventionalcommits.org/) commit message style on the title.

#### Options

| Name       | Type           | Default                                                        | gitlint version                      | Description                                      |
|------------| -------------- |----------------------------------------------------------------|--------------------------------------|--------------------------------------------------|
| `types`    | `#!python str` | `fix,feat,chore,docs,style,refactor,perf,test,revert,ci,build` | [:octicons-tag-24: v0.12.0][v0.12.0] | Comma separated list of allowed commit types.    |
| `scopes`   | `#!python str` |                                                                | [:octicons-tag-24: v0.12.0][v0.12.0] | Optional comma separated list of allowed scopes. |


=== ":octicons-file-code-16:  .gitlint"

    ```ini
    [contrib-title-conventional-commits]
    types=bugfix,user-story,epic
    ```


### CC1: contrib-body-requires-signed-off-by ##
[:octicons-tag-24: v0.12.0][v0.12.0] · **ID**: CC1 · **Name**: contrib-body-requires-signed-off-by

Commit body must contain a line that starts with `Signed-off-by`.

### CC2: contrib-disallow-cleanup-commits
[:octicons-tag-24: v0.18.0][v0.18.0] · **ID**: CC2 · **Name**: contrib-disallow-cleanup-commits

Commit title must not contain `fixup!`, `squash!` or `amend!`. This means `git commit --fixup` and `git commit --squash` commits are not allowed.

### CC3: contrib-allowed-authors
[:octicons-tag-24: v0.18.0][v0.18.0] · **ID**: CC3 · **Name**: contrib-allowed-authors

The commit author must be listed in an `AUTHORS` (or `AUTHORS.txt` or `AUTHORS.md`) file to be allowed to commit.

## Contributing Contrib rules

We'd love for you to contribute new Contrib rules to gitlint or improve existing ones! Please visit the [Contributing](../contributing/contrib_rules.md) page on how to get started.
