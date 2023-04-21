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
```sh
# Find latest dev build on https://pypi.org/project/gitlint/#history
pip install gitlint=="0.19.0.dev68"
```
