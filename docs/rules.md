# Overview #

The table below shows an overview of all gitlint's built-in rules.
Note that you can also [write your own user-defined rule](user_defined_rules.md) in case you don't find
what you're looking for.
The rest of this page contains details on the available configuration options for each built-in rule.

ID    | Name                        | gitlint version | Description
------|-----------------------------|---------------- |-------------------------------------------
T1    | title-max-length            | >= 0.1          | Title length must be &lt; 72 chars.
T2    | title-trailing-whitespace   | >= 0.1          | Title cannot have trailing whitespace (space or tab)
T3    | title-trailing-punctuation  | >= 0.1          | Title cannot have trailing punctuation (?:!.,;)
T4    | title-hard-tab              | >= 0.1          | Title cannot contain hard tab characters (\t)
T5    | title-must-not-contain-word | >= 0.1          | Title cannot contain certain words (default: "WIP")
T6    | title-leading-whitespace    | >= 0.4          | Title cannot have leading whitespace (space or tab)
T7    | title-match-regex           | >= 0.5          | Title must match a given regex (default: .*)
B1    | body-max-line-length        | >= 0.1          | Lines in the body must be &lt; 80 chars
B2    | body-trailing-whitespace    | >= 0.1          | Body cannot have trailing whitespace (space or tab)
B3    | body-hard-tab               | >= 0.1          | Body cannot contain hard tab characters (\t)
B4    | body-first-line-empty       | >= 0.1          | First line of the body (second line of commit message) must be empty
B5    | body-min-length             | >= 0.4          | Body length must be at least 20 characters
B6    | body-is-missing             | >= 0.4          | Body message must be specified
B7    | body-changed-file-mention   | >= 0.4          | Body must contain references to certain files if those files are changed in the last commit
M1    | author-valid-email          | >= 0.9          | Author email address must be a valid email address



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
regex          | >= 0.5          | .*      | [Python-style regular expression](https://docs.python.org/3.5/library/re.html) that the title should match.

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
regex                 | >= 0.8.3          | ```[^@ ]+@[^@ ]+\.[^@ ]+```  |  Regex the commit author email address is matched against


!!! note
    An often recurring use-case is to only allow email addresses from a certain domain. The following regular expression achieves this: ```[^@]+@foo.com```