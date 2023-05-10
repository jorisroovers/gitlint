[:octicons-tag-24: v0.14.0][v0.14.0] 

Named rules allow you to have multiple of the same rules active at the same time, which allows you to
enforce the same rule multiple times but with different options. 

Named rules are so-called because they require an
additional unique identifier (i.e. the rule *name*) during configuration.

!!! warning

    Named rules is an advanced topic. It's easy to make mistakes by defining conflicting instances of the same rule.
    For example, by defining 2 `body-max-line-length` rules with different `line-length` options, you obviously create
    a conflicting situation. Gitlint does not do any resolution of such conflicts, it's up to you to make sure
    any configuration is non-conflicting. So caution advised!

Defining a named rule is easy:

=== ":octicons-file-code-16:  .gitlint"

    ```ini
    # By adding the following section, you will add a second instance of the
    # title-must-not-contain-word (T5) rule, with the name 'extra-words' (1).
    [title-must-not-contain-word:extra-words]
    words=foo,bar

    # Another example, referencing the rule type by id (2)
    [T5:more-words]
    words=hur,dur

    # You can add as many additional rules and you can name them whatever you want (3)
    [title-must-not-contain-word:This-Can_Be*Whatever$YouWant]
    words=wonderwoman,batman,power ranger
    ```

    1. This rule is enabled in addition to the one that is enabled by default
    2. The generic form is
       ```ini
       [<rule-id-or-name>:<your-chosen-name>]
       <option1>=<value>
       <option2>=<value>
       ```
    3. The only requirement is that names cannot contain whitespace or colons (:).

When executing gitlint, you will see the violations from the default `title-must-not-contain-word (T5)` rule, as well as
the violations caused by the additional Named Rules.

```
$ gitlint
1: T5 Title contains the word 'WIP' (case-insensitive): "WIP: foo wonderwoman hur bar"
1: T5:This-Can_Be*Whatever$YouWant Title contains the word 'wonderwoman' (case-insensitive): "WIP: foo wonderwoman hur bar"
1: T5:extra-words Title contains the word 'foo' (case-insensitive): "WIP: foo wonderwoman hur bar"
1: T5:extra-words Title contains the word 'bar' (case-insensitive): "WIP: foo wonderwoman hur bar"
1: T5:more-words Title contains the word 'hur' (case-insensitive): "WIP: foo wonderwoman hur bar"
```

Named rules are further treated identical to all other rules in gitlint:

- You can reference them by their full name, when e.g. adding them to your `ignore` configuration

    === ":octicons-file-code-16:  .gitlint"

        ```ini
        [general]
        ignore=T5:more-words,title-must-not-contain-word:extra-words
        ```

    === ":octicons-terminal-16:  CLI"

        ```sh
        gitlint --ignore="T5:more-words,title-must-not-contain-word:extra-words"
        ```

    === ":material-application-variable-outline: Env var"

        ```sh
        GITLINT_IGNORE="T5:more-words,title-must-not-contain-word:extra-words" gitlint
        ```

- You can use them to instantiate multiple of the same [user-defined rule](user_defined_rules/index.md)
- You can configure them using [any of the ways you can configure regular gitlint rules](../configuration/index.md)
