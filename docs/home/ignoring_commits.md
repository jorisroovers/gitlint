
## Ignoring commits

You can configure gitlint to ignore specific commits or parts of a commit.

One way to do this, is by [adding a gitlint-ignore line to your commit message](../configuration/commit_config.md).

If you have a case where you want to ignore a certain type of commits all-together, you can
use gitlint's **ignore** rules.
Here's a few examples:

=== ":octicons-file-code-16:  .gitlint"

    ```ini
    [ignore-by-title]
    # Match commit titles starting with "Release"
    regex=^Release(.*)
    ignore=title-max-length,body-min-length # (1)

    [ignore-by-body]
    # Match commits message bodies that have a line that contains 'release'
    regex=(.*)release(.*)
    ignore=all

    [ignore-by-author-name]
    # Match commits by author name (e.g. ignore dependabot commits)
    regex=dependabot
    ignore=all
    ```

    1. Ignore all rules by setting `ignore` to 'all'. 
    ```ini
    [ignore-by-title]
    regex=^Release(.*)
    ignore=all
    ```

If you just want to ignore certain lines in a commit but still lint the other
ones,  you can do that using the
[ignore-body-lines](../rules/builtin_rules.md#i3-ignore-body-lines) rule.

=== ":octicons-file-code-16:  .gitlint"

    ```ini
    # Ignore all lines that start with 'Co-Authored-By'
    [ignore-body-lines]
    regex=^Co-Authored-By
    ```

!!! warning

    When ignoring specific lines, gitlint will no longer be aware of them while applying other rules.
    This can sometimes be confusing for end-users, especially as line numbers of violations will typically no longer
    match line numbers in the original commit message. Make sure to educate your users accordingly.

!!! tip

    If you want to implement more complex ignore rules according to your own logic, you can do so using
    [user-defined configuration rules](../rules/user_defined_rules/configuration_rules.md).

## Merge, fixup, squash and revert commits

[:octicons-tag-24: v0.7.0][v0.7.0] _(merge)_ ·
[:octicons-tag-24: v0.9.0][v0.9.0] _(fixup, squash)_ ·
[:octicons-tag-24: v0.13.0][v0.13.0] _(revert)_ ·
[:octicons-tag-24: v0.18.0][v0.18.0] _(fixup=amend)_

**Gitlint ignores merge, revert, fixup, and squash commits by default.**

For merge and revert commits, the rationale for ignoring them is
that most users keep git's default messages for these commits (i.e *Merge/Revert "[original commit message]"*).
Often times these commit messages are also auto-generated through tools like github.
These default/auto-generated commit messages tend to cause gitlint violations.
For example, a common case is that *"Merge:"* being auto-prepended triggers a
[title-max-length](../rules/builtin_rules.md#t1-title-max-length) violation. Most users don't want this, so we disable linting
on Merge and Revert commits by default.

For [squash](https://git-scm.com/docs/git-commit#Documentation/git-commit.txt---squashltcommitgt) and [fixup](https://git-scm.com/docs/git-commit#Documentation/git-commit.txt---fixupamendrewordltcommitgt) (including [fixup=amend](https://git-scm.com/docs/git-commit#Documentation/git-commit.txt---fixupamendrewordltcommitgt)) commits, the rationale is that these are temporary
commits that will be squashed into a different commit, and hence the commit messages for these commits are very
short-lived and not intended to make it into the final commit history. In addition, by prepending *"fixup!"*,
*"amend!"* or *"squash!"* to your commit message, certain gitlint rules might be violated
(e.g. [title-max-length](../rules/builtin_rules.md#t1-title-max-length)) which is often undesirable.

In case you *do* want to lint these commit messages, you can disable this behavior by setting the
general `ignore-merge-commits`, `ignore-revert-commits`,  `ignore-fixup-commits`, `ignore-fixup-amend-commits` or
`ignore-squash-commits` option to `false`
[using one of the various ways to configure gitlint](../../configuration).