Gitlint uses the exit code as a simple way to indicate the number of violations found.
Some exit codes are used to indicate special errors as indicated in the table below.

Because of these special error codes and the fact that
[bash only supports exit codes between 0 and 255](http://tldp.org/LDP/abs/html/exitcodes.html), the maximum number
of violations counted by the exit code is 252. Note that gitlint does not have a limit on the number of violations
it can detect, it will just always return with exit code 252 when the number of violations is greater than or equal
to 252.

| Exit Code | Description                                |
| --------- | ------------------------------------------ |
| 253       | Wrong invocation of the `gitlint` command. |
| 254       | Something went wrong when invoking git.    |
| 255       | Invalid gitlint configuration              |
