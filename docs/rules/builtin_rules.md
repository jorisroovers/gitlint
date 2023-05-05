The page documents all of gitlint's built-in rules and their options.

**All built-in rules are enabled by default**. It's possible to [ignore specific rules through configuration](../configuration/general_options.md#ignore).

## T1: title-max-length
[:octicons-tag-24: v0.1.0][v0.1.0] · **ID**: T1 · **Name**: title-max-length

Title length must be &lt;= 72 chars.

### Options

| Name          | Type           | Default       | gitlint version                    | Description                   |
| ------------- | -------------- | ------------- | ---------------------------------- | ----------------------------- |
| `line-length` | `#!python int` | `#!python 72` | [:octicons-tag-24: v0.2.0][v0.2.0] | Maximum allowed title length. |


=== ":octicons-file-code-16:  .gitlint"

    ```ini
    # It's the 21st century, titles can be 120 chars long!
    [title-max-length]
    line-length=120
    ```

## T2: title-trailing-whitespace
[:octicons-tag-24: v0.1.0][v0.1.0] · **ID**: T2 · **Name**: title-trailing-whitespace

Title cannot have trailing whitespace (space or tab).

## T3: title-trailing-punctuation

[:octicons-tag-24: v0.1.0][v0.1.0] · **ID**: T3 · **Name**: title-trailing-punctuation

Title cannot have trailing punctuation `(?:!.,;)`.

## T4: title-hard-tab
[:octicons-tag-24: v0.1.0][v0.1.0] · **ID**: T4 · **Name**: title-hard-tab

Title cannot contain hard tab character (`\t`).

## T5: title-must-not-contain-word
[:octicons-tag-24: v0.1.0][v0.1.0] · **ID**: T5 · **Name**: title-must-not-contain-word

Title cannot contain certain words.

### Options

| Name    | Type           | Default          | gitlint version                    | Description                                                                                                                                                                                   |
| ------- | -------------- | ---------------- | ---------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `words` | `#!python str` | `#!python "WIP"` | [:octicons-tag-24: v0.3.0][v0.3.0] | Comma-separated list of words that should not be used in the title. Matching is case insensitive. Keywords occuring as part of a larger word are not matched (so `#!python "WIPING"` is allowed). |

=== ":octicons-file-code-16:  .gitlint"

    ```ini
    # Ensure the title doesn't contain swear words
    [title-must-not-contain-word]
    words=crap,darn,damn
    ```

## T6: title-leading-whitespace
[:octicons-tag-24: v0.4.0][v0.4.0] · **ID**: T6 · **Name**: title-leading-whitespace

Title cannot have leading whitespace (space or tab).

## T7: title-match-regex
[:octicons-tag-24: v0.5.0][v0.5.0] · **ID**: T7 · **Name**: title-match-regex

Title must match a given regex (default: `.*`).

### Options

| Name    | Type           | Default       | gitlint version                    | Description                                                                          |
| ------- | -------------- | ------------- | ---------------------------------- | ------------------------------------------------------------------------------------ |
| `regex` | `#!python str` | `#!python .*` | [:octicons-tag-24: v0.5.0][v0.5.0] | [Python regex](https://docs.python.org/library/re.html) the title should match. |

=== ":octicons-file-code-16:  .gitlint"

    ```ini
    # Ensure every title starts with a user-story identifier like US123
    [title-match-regex]
    regex=^US[1-9][0-9]*
    ```


## T8: title-min-length ##
[:octicons-tag-24: v0.14.0][v0.14.0] · **ID**: T8 · **Name**: title-min-length

Title length must be &gt;= 5 chars.

### Options

| Name         | Type           | Default      | gitlint version                      | Description                   |
| ------------ | -------------- | ------------ | ------------------------------------ | ----------------------------- |
| `min-length` | `#!python int` | `#!python 5` | [:octicons-tag-24: v0.14.0][v0.14.0] | Minimum required title length |


=== ":octicons-file-code-16:  .gitlint"

    ```ini
    # Titles should be min 3 chars
    [title-min-length]
    min-length=3
    ```

## B1: body-max-line-length
[:octicons-tag-24: v0.1.0][v0.1.0] · **ID**: B1 · **Name**: body-max-line-length

Lines in the body must be &lt;= 80 chars.

### Options

| Name          | Type           | Default       | gitlint version                    | Description                                             |
| ------------- | -------------- | ------------- | ---------------------------------- | ------------------------------------------------------- |
| `line-length` | `#!python int` | `#!python 80` | [:octicons-tag-24: v0.2.0][v0.2.0] | Maximum allowed line length in the commit message body. |


=== ":octicons-file-code-16:  .gitlint"

    ```ini
    # It's the 21st century, lines can be 120 chars long
    [body-max-line-length]
    line-length=120
    ```

## B2: body-trailing-whitespace
[:octicons-tag-24: v0.1.0][v0.1.0] · **ID**: B2 · **Name**: body-trailing-whitespace

Body cannot have trailing whitespace (space or tab).

## B3: body-hard-tab
[:octicons-tag-24: v0.1.0][v0.1.0] · **ID**: B3 · **Name**: body-hard-tab

Body cannot contain hard tab characters (`\t`).

## B4: body-first-line-empty
[:octicons-tag-24: v0.1.0][v0.1.0] · **ID**: B4 · **Name**: body-first-line-empty

First line of the body (second line of commit message) must be empty.

## B5: body-min-length
[:octicons-tag-24: v0.4.0][v0.4.0] · **ID**: B5 · **Name**: body-min-length

Body length must be at least 20 characters. Gitlint will not count newline characters towards this limit.

### Options ###

| Name         | Type           | Default       | gitlint version                    | Description                                    |
| ------------ | -------------- | ------------- | ---------------------------------- | ---------------------------------------------- |
| `min-length` | `#!python int` | `#!python 20` | [:octicons-tag-24: v0.4.0][v0.4.0] | Minimum number of required characters in body. |


=== ":octicons-file-code-16:  .gitlint"

    ```ini
    # You want *something* in every commit body, but doesn't have to be as long as 20 chars.
    [body-min-length]
    min-length=5

    # You want a more elaborate message in every commit body
    [body-min-length]
    min-length=100
    ```

## B6: body-is-missing
[:octicons-tag-24: v0.4.0][v0.4.0] · **ID**: B6 · **Name**: body-is-missing

Body message must be specified.

### Options

| Name                   | Type            | Default         | gitlint version                    | Description                                                                           |
| ---------------------- | --------------- | --------------- | ---------------------------------- | ------------------------------------------------------------------------------------- |
| `ignore-merge-commits` | `#!python bool` | `#!python true` | [:octicons-tag-24: v0.4.0][v0.4.0] | Whether this rule should be ignored during merge commits. Allowed values: true,false. |


=== ":octicons-file-code-16:  .gitlint"

    ```ini
    # You want gitlint to check enforce this rule for merge commits as well
    [body-is-missing]
    ignore-merge-commits=false

    # This also needs to be enabled at the general gitlint level # (1)
    [general]
    ignore-merge-commits=false 
    ```

    1. By default, [gitlint will ignore merge commits all-together](../home/ignoring_commits.md#merge-fixup-squash-and-revert-commits).

## B7: body-changed-file-mention
[:octicons-tag-24: v0.4.0][v0.4.0] · **ID**: B7 · **Name**: body-changed-file-mention

Body must contain references to certain files if those files are changed in the last commit.

### Options

| Name    | Type           | Default | gitlint version                    | Description                                                                                                    |
| ------- | -------------- | ------- | ---------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| `files` | `#!python str` | `empty` | [:octicons-tag-24: v0.4.0][v0.4.0] | Comma-separated list of files that need to an explicit mention in the commit message in case they are changed. |

=== ":octicons-file-code-16:  .gitlint"

    ```ini
    # Prevent that certain files are committed by mistake by forcing
    # users to mention them explicitly when they're deliberately changing them
    [body-changed-file-mention]
    files=generated.xml,secrets.txt,private-key.pem
    ```

## B8: body-match-regex
[:octicons-tag-24: v0.14.0][v0.14.0] · **ID**: B8 · **Name**: body-match-regex

Body must match a given regex.

### Options

| Name    | Type           | Default | gitlint version                      | Description                                                                         |
| ------- | -------------- | ------- | ------------------------------------ | ----------------------------------------------------------------------------------- |
| `regex` | `#!python str` | `empty` | [:octicons-tag-24: v0.14.0][v0.14.0] | [Python regex](https://docs.python.org/library/re.html) the body should match. |

=== ":octicons-file-code-16:  .gitlint"

    ```ini
    # Ensure the body ends with Reviewed-By: <some value>
    [body-match-regex]
    regex=Reviewed-By:(.*)$

    # Ensure body contains the word "Foo" somewhere
    [body-match-regex]
    regex=(*.)Foo(.*)
    ```

## M1: author-valid-email
[:octicons-tag-24: v0.9.0][v0.9.0] · **ID**: M1 · **Name**: author-valid-email

Author email address must be a valid email address.

!!! note
    Email addresses are [notoriously hard to validate and the official email valid spec is often too loose for any real world application](http://stackoverflow.com/a/201378/381010).
    Gitlint by default takes a pragmatic approach and requires users to enter email addresses that contain a name, domain and tld and has no spaces.


### Options

| Name    | Type           | Default                                  | gitlint version                    | Description                                                                                                |
| ------- | -------------- | ---------------------------------------- | ---------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `regex` | `#!python str` | **[^@&nbsp;]+@[^@&nbsp;]+\.[^@&nbsp;]+** | [:octicons-tag-24: v0.9.0][v0.9.0] | [Python regex](https://docs.python.org/library/re.html) the commit author email address is matched against |


=== ":octicons-file-code-16:  .gitlint"

    ```ini
    # Only allow email addresses from a foo.com domain
    [author-valid-email]
    regex=[^@]+@foo.com
    ```

## I1: ignore-by-title
[:octicons-tag-24: v0.10.0][v0.10.0] · **ID**: I1 · **Name**: ignore-by-title

Ignore a commit based on matching its title.

### Options

| Name     | Type           | Default          | gitlint version                      | Description                                                                                                                  |
| -------- | -------------- | ---------------- | ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------- |
| `regex`  | `#!python str` | `empty`          | [:octicons-tag-24: v0.10.0][v0.10.0] | [Python regex](https://docs.python.org/library/re.html) to match against commit title. On match, the commit will be ignored. |
| `ignore` | `#!python str` | `#!python "all"` | [:octicons-tag-24: v0.10.0][v0.10.0] | Comma-separated list of rule names or ids to ignore when this rule is matched.                                               |

=== ":octicons-file-code-16:  .gitlint"

    ```ini
    # Match commit titles starting with Release
    # For those commits, ignore title-max-length and body-min-length rules
    [ignore-by-title]
    regex=^Release(.*)
    ignore=title-max-length,body-min-length,B6 # (1)

    # Ignore all rules by setting ignore to 'all'
    [ignore-by-title]
    regex=^Release(.*)
    ignore=all
    ```

     1. You can use both names as well as ids to refer to other rules.

## I2: ignore-by-body
[:octicons-tag-24: v0.10.0][v0.10.0] · **ID**: I2 · **Name**: ignore-by-body

Ignore a commit based on matching its body.

### Options

| Name     | Type           | Default          | gitlint version                      | Description                                                                                                                 |
| -------- | -------------- | ---------------- | ------------------------------------ | --------------------------------------------------------------------------------------------------------------------------- |
| `regex`  | `#!python str` | `empty`          | [:octicons-tag-24: v0.10.0][v0.10.0] | [Python regex](https://docs.python.org/library/re.html) to match against commit body. On match, the commit will be ignored. |
| `ignore` | `#!python str` | `#!python "all"` | [:octicons-tag-24: v0.10.0][v0.10.0] | Comma-separated list of rule names or ids to ignore when this rule is matched.                                              |


=== ":octicons-file-code-16:  .gitlint"

    ```ini
    # Ignore all commits with a commit message body with a line that contains 'release'
    # For matching commits, only ignore rules T1, body-min-length, B6.
    [ignore-by-body]
    regex=(.*)release(.*)
    ignore=T1,body-min-length,B6 # (1)

    # Ignore all rules by setting ignore to 'all'
    [ignore-by-body]
    regex=(.*)release(.*)
    ignore=all
    ```

    1. You can use both names as well as ids to refer to other rules.

## I3: ignore-body-lines
[:octicons-tag-24: v0.14.0][v0.14.0] · **ID**: I3 · **Name**: ignore-body-lines

Ignore certain lines in a commit body that match a regex.

### Options


| Name    | Type           | Default | gitlint version                      | Description                                                                                                                                                                                 |
| ------- | -------------- | ------- | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `regex` | `#!python str` | `empty` | [:octicons-tag-24: v0.14.0][v0.14.0] | [Python regex](https://docs.python.org/library/re.html) to match against each line of the body. On match, that line will be ignored by gitlint (the rest of the body will still be linted). |

=== ":octicons-file-code-16:  .gitlint"

    ```ini
    # Ignore all lines that start with 'Co-Authored-By'
    [ignore-body-lines]
    regex=^Co-Authored-By

    # Ignore lines that start with 'Co-Authored-By' or with 'Signed-off-by'
    [ignore-body-lines]
    regex=(^Co-Authored-By)|(^Signed-off-by)

    # Ignore lines that contain 'foobar'
    [ignore-body-lines]
    regex=(.*)foobar(.*)
    ```

## I4: ignore-by-author-name
[:octicons-tag-24: v0.16.0][v0.16.0] · **ID**: I4 · **Name**: ignore-by-author-name

Ignore a commit based on matching its author name.

### Options


| Name     | Type           | Default          | gitlint version                      | Description                                                                                                                            |
| -------- | -------------- | ---------------- | ------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------- |
| `regex`  | `#!python str` | `empty`          | [:octicons-tag-24: v0.16.0][v0.16.0] | [Python regex](https://docs.python.org/library/re.html) to match against the commit author name. On match, the commit will be ignored. |
| `ignore` | `#!python str` | `#!python "all"` | [:octicons-tag-24: v0.16.0][v0.16.0] | Comma-separated list of rule names or ids to ignore when this rule is matched.                                                         |


=== ":octicons-file-code-16:  .gitlint"

    ```ini
    # Ignore all commits authored by dependabot
    [ignore-by-author-name]
    regex=dependabot

    # For commits made by authors with "[bot]" in their name, ignore specific rules
    [ignore-by-author-name]
    regex=(.*)\[bot\](.*)
    ignore=T1,body-min-length,B6 # (1)
    ```

    1. You can use both names as well as ids to refer to other rules.
