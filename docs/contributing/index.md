---
title: Contributing
---

# Contributing

We'd love for you to contribute to gitlint. Thanks for your interest!
The [source-code and issue tracker](https://github.com/jorisroovers/gitlint) are hosted on Github.

!!! note
    Often it takes a while for us (well, actually just [me](https://github.com/jorisroovers)) to get back to you
    (sometimes up to a few months, this is a hobby project), but rest assured that we read your message and appreciate
    your interest!
    We maintain a [loose project plan on github projects](https://github.com/users/jorisroovers/projects/1/), but
    that's open to a lot of change and input.

## Overall Guidelines

When contributing code, please consider all the parts that are typically required:

- [Unit tests](https://github.com/jorisroovers/gitlint/tree/main/gitlint-core/gitlint/tests) (automatically
  [enforced by CI](https://github.com/jorisroovers/gitlint/actions)). Please consider writing
  new ones for your functionality, not only updating existing ones to make the build pass.
- [Integration tests](https://github.com/jorisroovers/gitlint/tree/main/qa) (also automatically
  [enforced by CI](https://github.com/jorisroovers/gitlint/actions)). Again, please consider writing new ones
  for your functionality, not only updating existing ones to make the build pass.
- Code style checks: linting, formatting, type-checking
- [Documentation](https://github.com/jorisroovers/gitlint/tree/main/docs)

Since we want to maintain a high standard of quality, all of these things will have to be done regardless before code
can make it as part of a release. **Gitlint commits and pull requests are gated on all of our tests and checks as well as
code-review**. If you can already include them as part of your PR, it's a huge timesaver for us
and it's likely that your PR will be merged and released a lot sooner. 

!!! tip
    It's a good idea to open an issue before submitting a PR for non-trivial changes, so we can discuss what you have
    in mind before you spend the effort. Thanks!
