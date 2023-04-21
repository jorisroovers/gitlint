[:octicons-tag-24: v0.12.0][v0.12.0]

Gitlint supports [Contrib rules](contrib_rules.md): community contributed rules that are part of gitlint
itself. Thanks for considering to add a new one to gitlint!

Before starting, please read all the other documentation on this page about contributing first.
Then, we suggest taking the following approach to add a Contrib rule:

1. **Write your rule as a [user-defined rule](user_defined_rules.md)**. In terms of code, Contrib rules are identical to
   user-defined rules, they just happen to have their code sit within the gitlint codebase itself.
2. **Add your user-defined rule to gitlint**. You should put your file(s) in the [gitlint/contrib/rules](https://github.com/jorisroovers/gitlint/tree/main/gitlint-core/gitlint/contrib/rules) directory.
3. **Write unit tests**. The gitlint codebase contains [Contrib rule test files you can copy and modify](https://github.com/jorisroovers/gitlint/tree/main/gitlint-core/gitlint/tests/contrib/rules).
4. **Write documentation**. In particular, you should update the [gitlint/docs/contrib_rules.md](https://github.com/jorisroovers/gitlint/blob/main/docs/contrib_rules.md) file with details on your Contrib rule.
5. **Create a Pull Request**: code review typically requires a bit of back and forth. Thanks for your contribution!


## Contrib rule requirements
If you follow the steps above and follow the existing gitlint conventions wrt naming things, you should already be fairly close to done.

In case you're looking for a slightly more formal spec, here's what gitlint requires of Contrib rules.

- Since Contrib rules are really just user-defined rules that live within the gitlint code-base, all the [user-rule requirements](user_defined_rules.md#rule-requirements) also apply to Contrib rules.
- All contrib rules **must** have associated unit tests. We *sort of* enforce this by a unit test that verifies that there's a
  test file for each contrib file.
- All contrib rules **must** have names that start with `contrib-`. This is to easily distinguish them from default gitlint rules.
- All contrib rule ids **must** start with `CT` (for LineRules targeting the title), `CB` (for LineRules targeting the body) or `CC` (for CommitRules). Again, this is to easily distinguish them from default gitlint rules.
- All contrib rules **must** have unique names and ids.
- You **can** add multiple rule classes to the same file, but classes **should** be logically grouped together in a single file that implements related rules.
- Contrib rules **should** be meaningfully different from one another. If a behavior change or tweak can be added to an existing rule by adding options, that should be considered first. However, large [god classes](https://en.wikipedia.org/wiki/God_object) that implement multiple rules in a single class should obviously also be avoided.
- Contrib rules **should** use [options](user_defined_rules.md#options) to make rules configurable.
