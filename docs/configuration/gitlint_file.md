# The .gitlint file
You can modify gitlint's behavior by adding a `.gitlint` file to your git repository.

Generate a default `.gitlint` config file by running:
```sh
gitlint generate-config
```
You can also use a different config file like so:

```sh
gitlint --config myconfigfile.ini
```

# Example `.gitlint`

```{ .ini .copy title=".gitlint"}
### GENERAL CONFIG  ### (1)
[general]
# Ignore rules, reference them by id or name (comma-separated)
ignore=title-trailing-punctuation, T3

# verbosity should be a value between 1 and 3
verbosity = 2

# Enable debug mode (prints more output). Disabled by default.
debug=true

# By default gitlint will ignore certain commits
ignore-merge-commits=true
ignore-revert-commits=true
ignore-fixup-commits=true
ignore-fixup-amend-commits=true
ignore-squash-commits=true

# Ignore any data sent to gitlint via stdin
ignore-stdin=true

# Fetch additional meta-data from the local repository when manually passing a
# commit message to gitlint via stdin or --commit-msg. Disabled by default.
staged=true

# Hard fail when the target commit range is empty. 
fail-without-commits=true # (2)

# Whether to use Python `search` instead of `match` semantics in rules (3)
regex-style-search=true

# Enable community contributed rules
contrib=contrib-title-conventional-commits,CC1 # (4)

# Set the extra-path where gitlint will search for user defined rules # (5)
extra-path=examples/


### RULE CONFIGURATION ### (6)
[title-max-length] 
line-length=80

[title-min-length]
min-length=5

[title-must-not-contain-word]
# Comma-separated list of words that should not occur in
# the commit message title (case-insensitive).
words=wip

[title-match-regex]
regex=^US[0-9]* # (7)

[body-max-line-length]
line-length=120

[body-min-length]
min-length=5

[body-is-missing]
# Ignore this rule on merge commits (default=true) # (8)
ignore-merge-commits=false

[body-changed-file-mention]
# Files that need to be explicitly mentioned in the body when they change
files=gitlint-core/gitlint/rules.py,README.md # (9)

[body-match-regex]
regex=My-Commit-Tag: foo$ # (10)

[author-valid-email]
# E.g.: Only allow email addresses from foo.com
regex=[^@]+@foo.com # (11)


### NAMED RULES ### (20)
[title-must-not-contain-word:Additional-Words]
words=foo,bar


### CONTRIB RULES ### (12)
[contrib-title-conventional-commits]
types = bugfix,user-story,epic


### USER DEFINED RULES ### (19)
[body-max-line-count]
max-line-count = 5


### IGNORE RULES CONFIGURATION ### (13)
[ignore-by-title]
# Ignore rules for commits of which the title matches a regex
regex=^Release(.*) # (14)
ignore=T1,body-min-length # (15)

[ignore-by-body]
# Ignore rules for commits of which the body has a line that matches a regex
regex=(.*)release(.*) # (16)
ignore=T1,body-min-length

[ignore-body-lines]
regex=^Co-Authored-By # (17)

[ignore-by-author-name]
regex=(.*)dependabot(.*) # (18)
ignore=T1,body-min-length

```

1. This section of the `.gitlint` file sets overall gitlint behavior. Details about all available `[general]` options can be found in [General Options](general_options.md).
2. Gitlint will fail by default on invalid commit ranges. This option is specifically to tell gitlint to fail
   on *valid but empty* commit ranges. Disabled by default.
3. Disabled by default, but will be enabled by default in the future. [More information](general_options.md#regex-style-search).
4. See [Contrib Rules](../rules/contrib_rules.md).
5. See [User Defined Rules](../rules/user_defined_rules.md).
6. All sections below sets rule specific behavior. <br/>
   Rules and sections can be referenced by their full name or by id. For example, this rule
   `[title-max-length]` could also be referenced as `[T1]`.
   ```ini
   [T1]
   line-length=80
   ```
7. [Python style regex](https://docs.python.org/3/library/re.html) that the commit-msg title must be matched to.
   Note that the regex can contradict with other rules if not used correctly (e.g. `title-must-not-contain-word`).
8. Merge commits often don't have a body, so by default gitlint will ignore this rule for merge commits to avoid
   unncessary violations.
9. This is useful for when developers often erroneously edit certain files or git submodules. 
   By specifying this rule, developers can only change the file when they explicitly reference it in the commit message.
10. [Python style regex](https://docs.python.org/3/library/re.html) that the commit-msg body must match. In this case
    the commit message body must end in <br> `My-Commit-Tag: foo`
11. [Python style regex](https://docs.python.org/3/library/re.html) that the commit author email address should be
    matched to.
12. [Community **Contrib**uted rules](../rules/contrib_rules.md) are disabled by default. You need to explicitly enable
    them one-by-one by adding them to the `contrib` option under `[general]` section.
    You can then just configure their options like any other rule.
    ```ini
    [general]
    # Enable contrib rules (comma-separated list)
    contrib=contrib-title-conventional-commits

    # Configure contrib rule
    [contrib-title-conventional-commits]
    types = bugfix,user-story,epic
    ```
13. You can configure gitlint to ignore specific commits or parts of a commit.
14. [Python style regex](https://docs.python.org/3/library/re.html). This example matches commit titles that start
    with "Release".
15. Which rules to ignore (reference by id or name). Use `all` to ignore all rules.
16. [Python style regex](https://docs.python.org/3/library/re.html). This example matches bodies that have a line
    that contains `release`.
17. [Python style regex](https://docs.python.org/3/library/re.html). This example will make gitlint ignores all lines
    that start with `Co-Authored-By`.
18. [Python style regex](https://docs.python.org/3/library/re.html). This example will make gitlint ignore all commits
    made by `dependabot`.
19. [User-Defined rules](../rules/user_defined_rules.md) can be written in python to tailor gitlint to your specific needs. 
20. Named Rules allow you to specify multiple instances of the same rule by given them an extra name of your
    choosing after the colon sign `:`. <br><br> In the example below we're configuring another instances of the
    `title-must-not-contain-word` rule (the existing one will remain active as well) and naming it `Additional-Words`.