## Overview ##

ID    | Name                        | Description
------|-----------------------------|----------------------------------------------------
T1    | title-max-length            | Title length must be &lt; 72 chars.
T2    | title-trailing-whitespace   | Title cannot have trailing whitespace (space or tab)
T3    | title-trailing-punctuation  | Title cannot have trailing punctuation (?:!.,;)
T4    | title-hard-tab              | Title cannot contain hard tab characters (\t)
T5    | title-must-not-contain-word | Title cannot contain certain words (default: "WIP")
T6    | title-leading-whitespace    | Title cannot have leading whitespace (space or tab)
T7    | title-match-regex           | Title must match a given regex (default: .*)
B1    | body-max-line-length        | Lines in the body must be &lt; 80 chars
B2    | body-trailing-whitespace    | Body cannot have trailing whitespace (space or tab)
B3    | body-hard-tab               | Body cannot contain hard tab characters (\t)
B4    | body-first-line-empty       | First line of the body (second line of commit message) must be empty
B5    | body-min-length             | Body length must be at least 20 characters
B6    | body-is-missing             | Body message must be specified
B7    | body-changed-file-mention   | Body must contain references to certain files if those files are changed in the last commit
