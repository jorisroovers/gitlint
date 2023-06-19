Gitlint releases typically go out when there's either enough new features and fixes
to make it worthwhile or when there's a critical fix for a bug that fundamentally breaks gitlint.

While the amount of overhead of doing a release isn't huge, it's also not zero. In practice this means that it might
take weeks or months before merged code actually gets released - we know that can be frustrating but please
understand it's a well-considered trade-off based on available time.

### Dev Builds
While final releases are usually months apart, we do dev builds on every commit to `main`:

- **gitlint**: [https://pypi.org/project/gitlint/#history](https://pypi.org/project/gitlint/#history)
- **gitlint-core**:  [https://pypi.org/project/gitlint-core/#history](https://pypi.org/project/gitlint-core/#history)

It usually takes about 5 min after merging a PR to `main` for new dev builds to show up. Note that the installation
of a recently published version can still fail for a few minutes after a new version shows up on PyPI while the package
is replicated to all download mirrors.

To install a dev build of gitlint:
```{.sh .copy}
# Find latest dev build on https://pypi.org/project/gitlint/#history
pip install gitlint=="0.19.0.dev68"
```

### Git archive installs
You can also install directly from GitHub source Git archive URLs.
This can even be done for unmerged commits (pending PRs). It will work as long as you have a commit hash.

```{.sh .copy}
# Set commit hash to install
export COMMIT_HASH="345414171baea56c5b2b8290f17a2a13a685274c"

# Install using pinned dependencies
pip install "gitlint-core [trusted-deps] @ https://github.com/jorisroovers/gitlint/archive/$COMMIT_HASH.tar.gz#subdirectory=gitlint-core"

# Install using looser dependencies
pip install "https://github.com/jorisroovers/gitlint/archive/$COMMIT_HASH.tar.gz#subdirectory=gitlint-core"
```
