Gitlint can lint specific commits using `--commit`:
```sh
gitlint --commit 019cf40580a471a3958d3c346aa8bfd265fe5e16
gitlint --commit 019cf40  # short SHAs work too
gitlint --commit HEAD~2   # as do special references
gitlint --commit mybranch # lint latest commit on a branch 
```

You can also lint multiple commits using `--commits` (plural):

```sh
# Lint a specific commit range
gitlint --commits "019cf40...d6bc75a"
# Lint all commits on a branch
gitlint --commits mybranch
# Lint all commits that are different between a branch and your main branch
gitlint --commits "main..mybranch"
# Use git's special references
gitlint --commits "origin/main..HEAD"

# You can also pass multiple, comma separated commit hashes
gitlint --commits 019cf40,c50eb150,d6bc75a
# These can include special references as well
gitlint --commits HEAD~1,mybranch-name,origin/main,d6bc75a
# You can also lint a single commit by adding a trailing comma
gitlint --commits 019cf40,
```

The `--commits` flag takes a **single** refspec argument or commit range. Basically, any range that is understood
by [git rev-list](https://git-scm.com/docs/git-rev-list) as a single argument will work.

Alternatively, you can pass `--commits` a comma-separated list of commit hashes (both short and full-length SHAs work,
as well as special references such as `HEAD` and branch names).
Gitlint will treat these as pointers to **single** commits and lint these in the order you passed.
`--commits` also accepts a single commit SHA with a trailing comma. 

For cases where the `--commits` option doesn't provide the flexibility you need, you can always use a simple shell
script to lint an arbitrary set of commits, like shown in the example below.

```sh
#!/bin/sh

for commit in $(git rev-list my-branch); do
    echo "Commit $commit"
    gitlint --commit $commit
    echo "--------"
done
```

!!! note
    One downside to this approach is that you invoke gitlint once per commit vs. once per set of commits.
    This means you'll incur the gitlint startup time once per commit, making it rather slow if you want to
    lint a large set of commits. Always use `--commits` if you can to avoid this performance penalty.