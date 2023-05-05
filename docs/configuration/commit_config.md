You can configure gitlint by adding specific lines to your commit message.

For now, we only support ignoring commits by adding `gitlint-ignore: all` to the commit
message like so:

```
WIP: This is my commit message

I want gitlint to ignore this entire commit message.
gitlint-ignore: all
```

`gitlint-ignore: all` can occur on any line, as long as it is at the start of the line.

You can also specify specific rules to be ignored as follows:
```
WIP: This is my commit message

I want gitlint to only ignore certain rules specified below.
gitlint-ignore: T1, body-hard-tab
```
