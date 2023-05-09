In order to make your own rules configurable, you can add an optional `options_spec` attribute to your rule class.

```{ .python .copy title="examples/my_commit_rules.py" linenums="1" hl_lines="12-19"}
from gitlint.rules import CommitRule, RuleViolation
from gitlint.options import IntOption

class BodyMaxLineCount(CommitRule):
    # A rule MUST have a human friendly name
    name = "body-max-line-count"

    # A rule MUST have a *unique* id
    # we recommend starting with UC (for User-defined Commit-rule).
    id = "UC1"

    # A rule MAY have an option_spec if its behavior is configurable.
    options_spec = [
        IntOption(
            "max-line-count",  # option name
            3,  # default value
            "Maximum body line count",  # description
        )
    ]

    def validate(self, commit):
        line_count = len(commit.message.body)
        max_count = self.options["max-line-count"].value
        if line_count > max_count:
            msg = f"Body has too many lines ({line_count} > {max_count})"
            return [RuleViolation(self.id, msg, line_nr=1)]
```


By using `options_spec`, gitlint automatically takes care of the parsing and input validation. 

You can configure your option like so:

=== ":octicons-file-code-16:  .gitlint"

    ```ini
    [body-max-line-count]
    max-line-count=1
    ```

=== ":octicons-terminal-16:  CLI"

    ```sh
    gitlint -c body-max-line-count.max-line-count=1
    ```

Because `options_spec` is a list, you can have multiple options per rule.

```python
options_spec = [
    IntOption("max-lint-count", 3, "Maximum body line count"),
    BoolOption("count-signoff-by", True, "Include 'Sign-off By' lines in count"),
    # etc
]
```

## Option Types
Gitlint supports a variety of different option types, all can be imported from `gitlint.options`:

| Option Class  | Use for                                                                                                                                |
| ------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `StrOption `  | Strings                                                                                                                                |
| `IntOption`   | Integers. `IntOption` takes an optional `allow_negative` parameter if you want to allow negative integers.                             |
| `BoolOption`  | Booleans. Valid values: `true`, `false`. Case-insensitive.                                                                             |
| `ListOption`  | List of strings. Comma separated.                                                                                                      |
| `PathOption`  | Directory or file path. Takes an optional `type` parameter for specifying path type (`file`, `dir` (=default) or `both`).              |
| `RegexOption` | String representing a [Python-style regex](https://docs.python.org/library/re.html) - compiled and validated before rules are applied. |

!!! note
    Gitlint currently does not support options for all possible types (e.g. float, list of int, etc).
    [We could use a hand getting those implemented](../../../contributing)!



### Examples

```python
options_spec = [
    StrOption("my-str-option", "default", "Fancy string option"),
    IntOption("my-int-option", 3, "Fancy integer option", allow_negative=True),
    BoolOption("my-bool-option", False, "Fancy boolean option"),
    ListOption("my-list-option"), ["foo", "bar"], "Fancy list option"
    PathOption("my-regex-option", "/foo/bar", "Fancy path option", type="dir"),
    RegexOption("my-regex-option", "^(foo|bar)", "Fancy regex option"),
]
```

