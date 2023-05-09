As long as you stick with simple rules that are similar to the sample user-defined rules (see the
[examples](https://github.com/jorisroovers/gitlint/blob/main/examples/my_commit_rules.py) directory), gitlint
should be able to discover and execute them. While clearly you can run any python code you want in your rules,
you might run into some issues if you don't follow the conventions that gitlint requires.

While the [rule finding source-code](https://github.com/jorisroovers/gitlint/blob/main/gitlint-core/gitlint/rule_finder.py) is the
ultimate source of truth, here are some of the requirements that gitlint enforces.

### Rule class requirements

- Rules **must** extend from  `LineRule`, `CommitRule` or `ConfigurationRule`
- Rule classes **must** have `id` and `name` string attributes. The `options_spec` is optional,
  but if set, it **must** be a list of gitlint Options.
- `CommitRule` and `LineRule` classes **must** have a `validate` method.
- In case of a `CommitRule`, `validate`  **must** take a single `commit` parameter.
- In case of `LineRule`, `validate` **must** take `line` and `commit` as first and second parameters.
- `ConfigurationRule` classes **must** have an `apply` method that take `config` and `commit` as first and second parameters.
- LineRule classes **must** have a `target` class attributes that is set to either `CommitMessageTitle` or `CommitMessageBody`.
- User Rule id's **cannot** start with `R`, `T`, `B`, `M` or `I` as these rule ids are reserved for gitlint itself.
- Rules **should** have a case-insensitive unique id as only one rule can exist with a given id. While gitlint does not
  enforce this, having multiple rules with the same id might lead to unexpected or undeterministic behavior.

### extra-path requirements
- If  `extra-path` is a directory, it does **not** need to be a proper python package, i.e. it doesn't require an `__init__.py` file.
- Python files containing user-defined rules must have a `.py` extension. Files with a different extension will be ignored.
- The `extra-path` will be searched non-recursively, i.e. all rule classes must be present at the top level `extra-path` directory.
- User rule classes must be defined in the modules that are part of `extra-path`, rules that are imported from outside the `extra-path` will be ignored.
