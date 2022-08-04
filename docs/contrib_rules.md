# Using Contrib Rules
_Introduced in gitlint v0.12.0_

Contrib rules are community-**contrib**uted rules that are disabled by default, but can be enabled through configuration.

Contrib rules are meant to augment default gitlint behavior by providing users with rules for common use-cases without
forcing these rules on all gitlint users. This also means that users don't have to
re-implement these commonly used rules themselves as [user-defined](user_defined_rules) rules.

To enable certain contrib rules, you can use the `--contrib` flag.
```sh
$ cat examples/commit-message-1 | gitlint --contrib contrib-title-conventional-commits,CC1
1: CC1 Body does not contain a 'Signed-off-by' line
1: CL1 Title does not start with one of fix, feat, chore, docs, style, refactor, perf, test: "WIP: This is the title of a commit message."

# These are the default violations
1: T3 Title has trailing punctuation (.): "WIP: This is the title of a commit message."
1: T5 Title contains the word 'WIP' (case-insensitive): "WIP: This is the title of a commit message."
2: B4 Second line is not empty: "The second line should typically be empty"
3: B1 Line exceeds max length (123>80): "Lines typically need to have a max length, meaning that they can't exceed a preset number of characters, usually 80 or 120."
```

Same thing using a `.gitlint` file:

```ini
[general]
# You HAVE to add the rule here to enable it, only configuring (such as below)
# does NOT enable it.
contrib=contrib-title-conventional-commits,CC1


[contrib-title-conventional-commits]
# Specify allowed commit types. For details see: https://www.conventionalcommits.org/
types = bugfix,user-story,epic
```

You can also configure contrib rules using [any of the other ways to configure gitlint](configuration.md).

## Available Contrib Rules

ID    | Name                                | gitlint version   | Description
------|-------------------------------------|------------------ |-------------------------------------------
CT1   | contrib-title-conventional-commits  | >= 0.12.0         | Enforces [Conventional Commits](https://www.conventionalcommits.org/) commit message style on the title.
CC1   | contrib-body-requires-signed-off-by | >= 0.12.0         | Commit body must contain a `Signed-off-by` line.
CC2   | contrib-disallow-cleanup-commits    | >= 0.18.0         | Commit title must not contain `fixup!`, `squash!`, `amend!`.

## CT1: contrib-title-conventional-commits ##

ID    | Name                                  | gitlint version    | Description
------|---------------------------------------|--------------------|-------------------------------------------
CT1   | contrib-title-conventional-commits    | >= 0.12.0          | Enforces [Conventional Commits](https://www.conventionalcommits.org/) commit message style on the title.

### Options ###

Name           | gitlint version    | Default      | Description
---------------|--------------------|--------------|----------------------------------
types          | >= 0.12.0          | `fix,feat,chore,docs,style,refactor,perf,test,revert,ci,build` | Comma separated list of allowed commit types.


## CC1: contrib-body-requires-signed-off-by ##

ID    | Name                                  | gitlint version    | Description
------|---------------------------------------|--------------------|-------------------------------------------
CC1   | contrib-body-requires-signed-off-by   | >= 0.12.0          | Commit body must contain a `Signed-off-by` line. This means, a line that starts with the `Signed-off-by` keyword.


## CC2: contrib-disallow-cleanup-commits ##

ID    | Name                             | gitlint version    | Description
------|----------------------------------|--------------------|-------------------------------------------
CC2   | contrib-disallow-cleanup-commits | >= 0.18.0          | Commit title must not contain `fixup!`, `squash!` or `amend!`. This means `git commit --fixup` and `git commit --squash` commits are not allowed.

## Contributing Contrib rules
We'd love for you to contribute new Contrib rules to gitlint or improve existing ones! Please visit the [Contributing](contributing) page on how to get started.
