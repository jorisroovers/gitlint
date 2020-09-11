# Overview #

The table below shows an overview of all gitlint's built-in rules.
Note that you can also [write your own user-defined rule](user_defined_rules.md) in case you don't find
what you're looking for.
The rest of this page contains details on the available configuration options for each built-in rule.

ID    | Name                        | gitlint version   | Description
------|-----------------------------|-------------------|-------------------------------------------
T1    | title-max-length            | >= 0.1.0          | Title length must be &lt; 72 chars.
T2    | title-trailing-whitespace   | >= 0.1.0          | Title cannot have trailing whitespace (space or tab)
T3    | title-trailing-punctuation  | >= 0.1.0          | Title cannot have trailing punctuation (?:!.,;)
T4    | title-hard-tab              | >= 0.1.0          | Title cannot contain hard tab characters (\t)
T5    | title-must-not-contain-word | >= 0.1.0          | Title cannot contain certain words (default: "WIP")
T6    | title-leading-whitespace    | >= 0.4.0          | Title cannot have leading whitespace (space or tab)
T7    | title-match-regex           | >= 0.5.0          | Title must match a given regex (default: .*)
B1    | body-max-line-length        | >= 0.1.0          | Lines in the body must be &lt; 80 chars
B2    | body-trailing-whitespace    | >= 0.1.0          | Body cannot have trailing whitespace (space or tab)
B3    | body-hard-tab               | >= 0.1.0          | Body cannot contain hard tab characters (\t)
B4    | body-first-line-empty       | >= 0.1.0          | First line of the body (second line of commit message) must be empty
B5    | body-min-length             | >= 0.4.0          | Body length must be at least 20 characters
B6    | body-is-missing             | >= 0.4.0          | Body message must be specified
B7    | body-changed-file-mention   | >= 0.4.0          | Body must contain references to certain files if those files are changed in the last commit
M1    | author-valid-email          | >= 0.9.0          | Author email address must be a valid email address
I1    | ignore-by-title             | >= 0.10.0         | Ignore a commit based on matching its title
I2    | ignore-by-body              | >= 0.10.0         | Ignore a commit based on matching its body
I3    | ignore-body-lines           | >= 0.14.0         | Ignore certain lines in a commit body that match a regex


## T1: title-max-length ##

ID    | Name                        | gitlint version | Description
------|-----------------------------|-----------------|-------------------------------------------
T1    | title-max-length            | >= 0.1          | Title length must be &lt; 72 chars.

### Options ###

Name           | gitlint version | Default | Description
---------------|-----------------|---------|----------------------------------
line-length    | >= 0.2          | 72      |  Maximum allowed title length

## T2: title-trailing-whitespace ##

ID    | Name                        | gitlint version | Description
------|-----------------------------|-----------------|-------------------------------------------
T2    | title-trailing-whitespace   | >= 0.1          | Title cannot have trailing whitespace (space or tab)


## T3: title-trailing-punctuation ##

ID    | Name                        | gitlint version | Description
------|-----------------------------|-----------------|-------------------------------------------
T3    | title-trailing-punctuation  | >= 0.1          | Title cannot have trailing punctuation (?:!.,;)


## T4: title-hard-tab    ##

ID    | Name                        | gitlint version | Description
------|-----------------------------|-----------------|-------------------------------------------
T4    | title-hard-tab              | >= 0.1          | Title cannot contain hard tab characters (\t)


## T5: title-must-not-contain-word   ##

ID    | Name                        | gitlint version | Description
------|-----------------------------|-----------------|-------------------------------------------
T5    | title-must-not-contain-word | >= 0.1          | Title cannot contain certain words (default: "WIP")

### Options ###

Name           | gitlint version | Default | Description
---------------|-----------------|---------|----------------------------------
words          | >= 0.3          | WIP     | Comma-separated list of words that should not be used in the title. Matching is case insensitive

## T6: title-leading-whitespace   ##

ID    | Name                        | gitlint version | Description
------|-----------------------------|-----------------|-------------------------------------------
T6    | title-leading-whitespace    | >= 0.4          | Title cannot have leading whitespace (space or tab)

## T7: title-match-regex   ##

ID    | Name                        | gitlint version | Description
------|-----------------------------|-----------------|-------------------------------------------
T7    | title-match-regex           | >= 0.5          | Title must match a given regex (default: .*)


### Options ###

Name           | gitlint version | Default | Description
---------------|-----------------|---------|----------------------------------
regex          | >= 0.5          | .*      | [Python regex](https://docs.python.org/library/re.html) that the title should match.

## B1: body-max-line-length   ##

ID    | Name                        | gitlint version | Description
------|-----------------------------|-----------------|-------------------------------------------
B1    | body-max-line-length        | >= 0.1          | Lines in the body must be &lt; 80 chars

### Options ###

Name           | gitlint version | Default | Description
---------------|-----------------|---------|----------------------------------
line-length    | >= 0.2          | 80      |  Maximum allowed line length in the commit message body

## B2: body-trailing-whitespace   ##

ID    | Name                        | gitlint version | Description
------|-----------------------------|-----------------|-------------------------------------------
B2    | body-trailing-whitespace    | >= 0.1          | Body cannot have trailing whitespace (space or tab)


## B3: body-hard-tab   ##

ID    | Name                        | gitlint version | Description
------|-----------------------------|-----------------|-------------------------------------------
B3    | body-hard-tab               | >= 0.1          | Body cannot contain hard tab characters (\t)


## B4: body-first-line-empty    ##

ID    | Name                        | gitlint version | Description
------|-----------------------------|-----------------|-------------------------------------------
B4    | body-first-line-empty       | >= 0.1          | First line of the body (second line of commit message) must be empty

## B5: body-min-length    ##

ID    | Name                        | gitlint version | Description
------|-----------------------------|-----------------|-------------------------------------------
B5    | body-min-length             | >= 0.4          | Body length must be at least 20 characters. In versions >= 0.8.0, gitlint will not count newline characters.

### Options ###

Name           | gitlint version | Default | Description
---------------|-----------------|---------|----------------------------------
min-length     | >= 0.4          | 20      |  Minimum number of required characters in body

## B6: body-is-missing   ##

ID    | Name                        | gitlint version | Description
------|-----------------------------|-----------------|-------------------------------------------
B6    | body-is-missing             | >= 0.4          | Body message must be specified


### Options ###

Name                  | gitlint version | Default   | Description
----------------------|-----------------|-----------|----------------------------------
ignore-merge-commits  | >= 0.4          | true      |  Whether this rule should be ignored during merge commits. Allowed values: true,false.

## B7: body-changed-file-mention   ##

ID    | Name                        | gitlint version | Description
------|-----------------------------|-----------------|-------------------------------------------
B7    | body-changed-file-mention   | >= 0.4          | Body must contain references to certain files if those files are changed in the last commit

### Options ###

Name                  | gitlint version | Default      | Description
----------------------|-----------------|--------------|----------------------------------
files                 | >= 0.4          | (empty)      |  Comma-separated list of files that need to an explicit mention in the commit message in case they are changed.


## B8: body-match-regex   ##

ID    | Name                        | gitlint version | Description
------|-----------------------------|-----------------|-------------------------------------------
B8    | body-match-regex            | >= 0.14         | Body must match a given regex

### Options ###

Name                  | gitlint version | Default      | Description
----------------------|-----------------|--------------|----------------------------------
regex                 | >= 0.14         | None         |  [Python regex](https://docs.python.org/library/re.html) that the title should match.

### Examples

#### .gitlint

```ini
# Ensure the body ends with Reviewed-By: <some value>
[body-match-regex]
regex=Reviewed-By:(.*)$

# Ensure body contains the word "Foo" somewhere
[body-match-regex]
regex=(*.)Foo(.*)
```

## M1: author-valid-email   ##

ID    | Name                        | gitlint version | Description
------|-----------------------------|-----------------|-------------------------------------------
M1    |  author-valid-email         | >= 0.8.3        | Author email address must be a valid email address

!!! note
    Email addresses are [notoriously hard to validate and the official email valid spec is often too loose for any real world application](http://stackoverflow.com/a/201378/381010).
    Gitlint by default takes a pragmatic approach and requires users to enter email addresses that contain a name, domain and tld and has no spaces.



### Options ###

Name                  | gitlint version   | Default                      | Description
----------------------|-------------------|------------------------------|----------------------------------
regex                 | >= 0.9.0          | ```[^@ ]+@[^@ ]+\.[^@ ]+```  |  [Python regex](https://docs.python.org/library/re.html) the commit author email address is matched against


!!! note
    An often recurring use-case is to only allow email addresses from a certain domain. The following regular expression achieves this: ```[^@]+@foo.com```


## I1: ignore-by-title ##

ID    | Name                        | gitlint version | Description
------|-----------------------------|-----------------|-------------------------------------------
I1    |  ignore-by-title            | >= 0.10.0       | Ignore a commit based on matching its title.


### Options ###

Name                  | gitlint version   | Default                      | Description
----------------------|-------------------|------------------------------|----------------------------------
regex                 | >= 0.10.0         | None                         |  [Python regex](https://docs.python.org/library/re.html) to match against commit title. On match, the commit will be ignored.
ignore                | >= 0.10.0         | all                          |  Comma-separated list of rule names or ids to ignore when this rule is matched.

### Examples

#### .gitlint

```ini
# Match commit titles starting with Release
# For those commits, ignore title-max-length and body-min-length rules
[ignore-by-title]
regex=^Release(.*)
ignore=title-max-length,body-min-length
# ignore all rules by setting ignore to 'all'
# ignore=all
```

## I2: ignore-by-body ##

ID    | Name                        | gitlint version | Description
------|-----------------------------|-----------------|-------------------------------------------
I2    |  ignore-by-body             | >= 0.10.0       | Ignore a commit based on matching its body.


### Options ###

Name                  | gitlint version   | Default                      | Description
----------------------|-------------------|------------------------------|----------------------------------
regex                 | >= 0.10.0         | None                         |  [Python regex](https://docs.python.org/library/re.html) to match against each line of the body. On match, the commit will be ignored.
ignore                | >= 0.10.0         | all                          |  Comma-separated list of rule names or ids to ignore when this rule is matched.

### Examples

#### .gitlint

```ini
# Ignore all commits with a commit message body with a line that contains 'release'
[ignore-by-body]
regex=(.*)release(.*)
ignore=all

# For matching commits, only ignore rules T1, body-min-length, B6.
# You can use both names as well as ids to refer to other rules.
[ignore-by-body]
regex=(.*)release(.*)
ignore=T1,body-min-length,B6
```

## I3: ignore-body-lines

ID    | Name                        | gitlint version | Description
------|-----------------------------|-----------------|-------------------------------------------
I3    |  ignore-body-lines          | >= 0.14.0    | Ignore certain lines in a commit body that match a regex.


### Options

Name                  | gitlint version   | Default                      | Description
----------------------|-------------------|------------------------------|----------------------------------
regex                 | >= 0.14.0         | None                         |  [Python regex](https://docs.python.org/library/re.html) to match against each line of the body. On match, that line will be ignored by gitlint (the rest of the body will still be linted).

### Examples

#### .gitlint

```ini
# Ignore all lines that start with 'Co-Authored-By'
[ignore-body-lines]
regex=^Co-Authored-By

# Ignore lines that start with 'Co-Authored-By' or with 'Signed-Off-By'
[ignore-body-lines]
regex=(^Co-Authored-By)|(^Signed-Off-By)

# Ignore lines that contain 'foobar'
[ignore-body-lines]
regex=(.*)foobar(.*)
```