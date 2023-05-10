import copy
import logging
import os
import platform
import stat
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import click

import gitlint
from gitlint import hooks
from gitlint.config import (
    LintConfig,
    LintConfigBuilder,
    LintConfigError,
    LintConfigGenerator,
)
from gitlint.deprecation import DEPRECATED_LOG_FORMAT
from gitlint.deprecation import LOG as DEPRECATED_LOG
from gitlint.exception import GitlintError
from gitlint.git import GitContext, GitContextError, git_version
from gitlint.lint import GitLinter
from gitlint.shell import shell
from gitlint.utils import LOG_FORMAT

# Error codes
GITLINT_SUCCESS = 0
MAX_VIOLATION_ERROR_CODE = 252
USAGE_ERROR_CODE = 253
GIT_CONTEXT_ERROR_CODE = 254
CONFIG_ERROR_CODE = 255

DEFAULT_CONFIG_FILE = ".gitlint"
# -n: disable swap files. This fixes a vim error on windows (E303: Unable to open swap file for <path>)
DEFAULT_COMMIT_MSG_EDITOR = "vim -n"

# Since we use the return code to denote the amount of errors, we need to change the default click usage error code
click.UsageError.exit_code = USAGE_ERROR_CODE

# We don't use logging.getLogger(__main__) here because that will cause DEBUG output to be lost
# when invoking gitlint as a python module (python -m gitlint.cli)
LOG = logging.getLogger("gitlint.cli")


class GitLintUsageError(GitlintError):
    """Exception indicating there is an issue with how gitlint is used."""


def setup_logging() -> None:
    """Setup gitlint logging"""

    # Root log, mostly used for debug
    root_log = logging.getLogger("gitlint")
    root_log.propagate = False  # Don't propagate to child loggers, the gitlint root logger handles everything
    root_log.setLevel(logging.WARN)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(LOG_FORMAT)
    handler.setFormatter(formatter)
    root_log.addHandler(handler)

    # Deprecated log, to log deprecation warnings
    DEPRECATED_LOG.propagate = False  # Don't propagate to child logger
    DEPRECATED_LOG.setLevel(logging.WARNING)
    deprecated_log_handler = logging.StreamHandler()
    deprecated_log_handler.setFormatter(logging.Formatter(DEPRECATED_LOG_FORMAT))
    DEPRECATED_LOG.addHandler(deprecated_log_handler)


def log_system_info():
    LOG.debug("Platform: %s", platform.platform())
    LOG.debug("Python version: %s", sys.version)
    LOG.debug("Git version: %s", git_version())
    LOG.debug("Gitlint version: %s", gitlint.__version__)
    LOG.debug("TERMINAL_ENCODING: %s", gitlint.utils.TERMINAL_ENCODING)
    LOG.debug("FILE_ENCODING: %s", gitlint.utils.FILE_ENCODING)


def build_config(
    target,
    config_path,
    c,
    extra_path,
    ignore,
    contrib,
    ignore_stdin,
    staged,
    fail_without_commits,
    verbose,
    silent,
    debug,
):
    """Creates a LintConfig object based on a set of commandline parameters."""
    config_builder = LintConfigBuilder()
    # Config precedence:
    # First, load default config or config from configfile
    if config_path:
        config_builder.set_from_config_file(config_path)
    elif os.path.exists(DEFAULT_CONFIG_FILE):
        config_builder.set_from_config_file(DEFAULT_CONFIG_FILE)

    # Then process any commandline configuration flags
    config_builder.set_config_from_string_list(c)

    # Finally, overwrite with any convenience commandline flags
    if ignore:
        config_builder.set_option("general", "ignore", ignore)

    if contrib:
        config_builder.set_option("general", "contrib", contrib)

    if ignore_stdin:
        config_builder.set_option("general", "ignore-stdin", ignore_stdin)

    if silent:
        config_builder.set_option("general", "verbosity", 0)
    elif verbose > 0:
        config_builder.set_option("general", "verbosity", verbose)

    if extra_path:
        config_builder.set_option("general", "extra-path", extra_path)

    if target:
        config_builder.set_option("general", "target", target)

    if debug:
        config_builder.set_option("general", "debug", debug)

    if staged:
        config_builder.set_option("general", "staged", staged)

    if fail_without_commits:
        config_builder.set_option("general", "fail-without-commits", fail_without_commits)

    config = config_builder.build()

    return config, config_builder


def get_stdin_data():
    """Helper function that returns data sent to stdin or False if nothing is sent"""
    # STDIN can only be 3 different types of things ("modes")
    #  1. An interactive terminal device (i.e. a TTY -> sys.stdin.isatty() or stat.S_ISCHR)
    #  2. A (named) pipe (stat.S_ISFIFO)
    #  3. A regular file (stat.S_ISREG)
    # Technically, STDIN can also be other device type like a named unix socket (stat.S_ISSOCK), but we don't
    # support that in gitlint (at least not today).
    #
    # Now, the behavior that we want is the following:
    # If someone sends something directly to gitlint via a pipe or a regular file, read it. If not, read from the
    # local repository.
    # Note that we don't care about whether STDIN is a TTY or not, we only care whether data is via a pipe or regular
    # file.
    # However, in case STDIN is not a TTY, it HAS to be one of the 2 other things (pipe or regular file), even if
    # no-one is actually sending anything to gitlint over them. In this case, we still want to read from the local
    # repository.
    # To support this use-case (which is common in CI runners such as Jenkins and Gitlab), we need to actually attempt
    # to read from STDIN in case it's a pipe or regular file. In case that fails, then we'll fall back to reading
    # from the local repo.

    mode = os.fstat(sys.stdin.fileno()).st_mode
    stdin_is_pipe_or_file = stat.S_ISFIFO(mode) or stat.S_ISREG(mode)
    if stdin_is_pipe_or_file:
        input_data = sys.stdin.read()
        # Only return the input data if there's actually something passed
        # i.e. don't consider empty piped data
        if input_data:
            return str(input_data)
    return False


def build_git_context(lint_config, msg_filename, commit_hash, refspec):
    """Builds a git context based on passed parameters and order of precedence"""

    # Determine which GitContext method to use if a custom message is passed
    from_commit_msg = GitContext.from_commit_msg
    if lint_config.staged:
        LOG.debug("Fetching additional meta-data from staged commit")

        def from_commit_msg(message):
            return GitContext.from_staged_commit(message, lint_config.target)

    # Order of precedence:
    # 1. Any data specified via --msg-filename
    if msg_filename:
        LOG.debug("Using --msg-filename.")
        with msg_filename.open(encoding=gitlint.utils.FILE_ENCODING) as msg_file:
            return from_commit_msg(str(msg_file.read()))

    # 2. Any data sent to stdin (unless stdin is being ignored)
    if not lint_config.ignore_stdin:
        stdin_input = get_stdin_data()
        if stdin_input:
            LOG.debug("Stdin data: '%s'", stdin_input)
            LOG.debug("Stdin detected and not ignored. Using as input.")
            return from_commit_msg(stdin_input)

    if lint_config.staged:
        raise GitLintUsageError(
            "The 'staged' option (--staged) can only be used when using '--msg-filename' or "
            "when piping data to gitlint via stdin."
        )

    # 3. Fallback to reading from local repository
    LOG.debug("No --msg-filename flag, no or empty data passed to stdin. Using the local repo.")

    if commit_hash and refspec:
        raise GitLintUsageError("--commit and --commits are mutually exclusive, use one or the other.")

    # 3.1 Linting a range of commits
    if refspec:
        # 3.1.1 Not real refspec, but comma-separated list of commit hashes
        if "," in refspec:
            commit_hashes = [hash.strip() for hash in refspec.split(",") if hash]
            return GitContext.from_local_repository(lint_config.target, commit_hashes=commit_hashes)
        # 3.1.2 Real refspec
        return GitContext.from_local_repository(lint_config.target, refspec=refspec)

    # 3.2 Linting a specific commit
    if commit_hash:
        return GitContext.from_local_repository(lint_config.target, commit_hashes=[commit_hash])

    # 3.3 Fallback to linting the current HEAD
    return GitContext.from_local_repository(lint_config.target)


def handle_gitlint_error(ctx, exc):
    """Helper function to handle exceptions"""
    if isinstance(exc, GitContextError):
        click.echo(exc)
        ctx.exit(GIT_CONTEXT_ERROR_CODE)
    elif isinstance(exc, GitLintUsageError):
        click.echo(f"Error: {exc}")
        ctx.exit(USAGE_ERROR_CODE)
    elif isinstance(exc, LintConfigError):
        click.echo(f"Config Error: {exc}")
        ctx.exit(CONFIG_ERROR_CODE)


@dataclass
class ContextObj:
    """Simple class to hold data that is passed between Click commands via the Click context."""

    config: LintConfig
    config_builder: LintConfigBuilder
    commit_hash: str
    refspec: str
    msg_filename: Optional[Path] = None
    gitcontext: Optional[GitContext] = None


# fmt: off
@click.group(invoke_without_command=True, context_settings={"max_content_width": 120},
             epilog="When no COMMAND is specified, gitlint defaults to 'gitlint lint'.")
@click.option("--target", envvar="GITLINT_TARGET",
              type=click.Path(exists=True, resolve_path=True, file_okay=False, readable=True),
              help="Path of the target git repository. [default: current working directory]")
@click.option("-C", "--config", envvar="GITLINT_CONFIG",
              type=click.Path(exists=True, dir_okay=False, readable=True, resolve_path=True),
              help=f"Config file location [default: {DEFAULT_CONFIG_FILE}]")
@click.option("-c", multiple=True,
              help="Config flags in format <rule>.<option>=<value> (e.g.: -c T1.line-length=80). " +
                   "Flag can be used multiple times to set multiple config values.")
@click.option("--commit", envvar="GITLINT_COMMIT", default=None, help="Hash (SHA) of specific commit to lint.")
@click.option("--commits", envvar="GITLINT_COMMITS", default=None,
              help="The range of commits (refspec or comma-separated hashes) to lint. [default: HEAD]")
@click.option("-e", "--extra-path", envvar="GITLINT_EXTRA_PATH",
              help="Path to a directory or python module with extra user-defined rules",
              type=click.Path(exists=True, resolve_path=True, readable=True))
@click.option("--ignore", envvar="GITLINT_IGNORE", default="", help="Ignore rules (comma-separated by id or name).")
@click.option("--contrib", envvar="GITLINT_CONTRIB", default="",
              help="Contrib rules to enable (comma-separated by id or name).")
@click.option("--msg-filename", type=click.Path(exists=True, dir_okay=False, path_type=Path),
              help="Path to a file containing a commit-msg.")
@click.option("--ignore-stdin", envvar="GITLINT_IGNORE_STDIN", is_flag=True,
              help="Ignore any stdin data. Useful for running in CI server.")
@click.option("--staged", envvar="GITLINT_STAGED", is_flag=True,
              help="Attempt smart guesses about meta info (like author name, email, branch, changed files, etc) " +
                   "for staged commits.")
@click.option("--fail-without-commits", envvar="GITLINT_FAIL_WITHOUT_COMMITS", is_flag=True,
              help="Hard fail when the target commit range is empty.")
@click.option("-v", "--verbose", envvar="GITLINT_VERBOSITY", count=True, default=0,
              help="Verbosity, use multiple times for more verbose output (e.g.: -v, -vv, -vvv). [default: -vvv]", )
@click.option("-s", "--silent", envvar="GITLINT_SILENT", is_flag=True,
              help="Silent mode (no output). Takes precedence over -v, -vv, -vvv.")
@click.option("-d", "--debug", envvar="GITLINT_DEBUG", help="Enable debugging output.", is_flag=True)
@click.version_option(version=gitlint.__version__)
@click.pass_context
def cli(
        ctx, target, config, c, commit, commits, extra_path, ignore, contrib,
        msg_filename, ignore_stdin, staged, fail_without_commits, verbose,
        silent, debug,
):
    """ Git lint tool, checks your git commit messages for styling issues

        Documentation: https://jorisroovers.github.io/gitlint
    """
    try:
        if debug:
            logging.getLogger("gitlint").setLevel(logging.DEBUG)
            DEPRECATED_LOG.setLevel(logging.DEBUG)
        LOG.debug("To report issues, please visit https://github.com/jorisroovers/gitlint/issues")

        log_system_info()

        # Get the lint config from the commandline parameters and
        # store it in the context (click allows storing an arbitrary object in ctx.obj).
        config, config_builder = build_config(target, config, c, extra_path, ignore, contrib, ignore_stdin,
                                              staged, fail_without_commits, verbose, silent, debug)
        LOG.debug("Configuration\n%s", config)

        ctx.obj = ContextObj(config, config_builder, commit, commits, msg_filename)

        # If no subcommand is specified, then just lint
        if ctx.invoked_subcommand is None:
            ctx.invoke(lint)

    except GitlintError as e:
        handle_gitlint_error(ctx, e)
# fmt: on


@cli.command("lint")
@click.pass_context
def lint(ctx):
    """Lints a git repository [default command]"""
    lint_config = ctx.obj.config
    refspec = ctx.obj.refspec
    commit_hash = ctx.obj.commit_hash
    msg_filename = ctx.obj.msg_filename

    gitcontext = build_git_context(lint_config, msg_filename, commit_hash, refspec)
    # Set gitcontext in the click context, so we can use it in command that are ran after this
    # in particular, this is used by run-hook
    ctx.obj.gitcontext = gitcontext

    number_of_commits = len(gitcontext.commits)
    # Exit if we don't have commits in the specified range. Use a 0 exit code, since a popular use-case is one
    # where users are using --commits in a check job to check the commit messages inside a CI job. By returning 0, we
    # ensure that these jobs don't fail if for whatever reason the specified commit range is empty.
    # This behavior can be overridden by using the --fail-without-commits flag.
    if number_of_commits == 0:
        LOG.debug('No commits in range "%s"', refspec)
        if lint_config.fail_without_commits:
            raise GitLintUsageError(f'No commits in range "{refspec}"')
        ctx.exit(GITLINT_SUCCESS)

    LOG.debug("Linting %d commit(s)", number_of_commits)
    general_config_builder = ctx.obj.config_builder
    last_commit = gitcontext.commits[-1]

    # Let's get linting!
    first_violation = True
    exit_code = GITLINT_SUCCESS
    for commit in gitcontext.commits:
        # Build a config_builder taking into account the commit specific config (if any)
        config_builder = general_config_builder.clone()
        config_builder.set_config_from_commit(commit)

        # Create a deepcopy from the original config, so we have a unique config object per commit
        # This is important for configuration rules to be able to modifying the config on a per commit basis
        commit_config = config_builder.build(copy.deepcopy(lint_config))

        # Actually do the linting
        linter = GitLinter(commit_config)
        violations = linter.lint(commit)
        # exit code equals the total number of violations in all commits
        exit_code += len(violations)
        if violations:
            # Display the commit hash & new lines intelligently
            if number_of_commits > 1 and commit.sha:
                commit_separator = "\n" if not first_violation or commit is last_commit else ""
                linter.display.e(f"{commit_separator}Commit {commit.sha[:10]}:")
            linter.print_violations(violations)
            first_violation = False

    # cap actual max exit code because bash doesn't like exit codes larger than 255:
    # http://tldp.org/LDP/abs/html/exitcodes.html
    exit_code = min(MAX_VIOLATION_ERROR_CODE, exit_code)
    LOG.debug("Exit Code = %s", exit_code)
    ctx.exit(exit_code)


@cli.command("install-hook")
@click.pass_context
def install_hook(ctx):
    """Install gitlint as a git commit-msg hook."""
    try:
        hooks.GitHookInstaller.install_commit_msg_hook(ctx.obj.config)
        hook_path = hooks.GitHookInstaller.commit_msg_hook_path(ctx.obj.config)
        click.echo(f"Successfully installed gitlint commit-msg hook in {hook_path}")
        ctx.exit(GITLINT_SUCCESS)
    except hooks.GitHookInstallerError as e:
        click.echo(e, err=True)
        ctx.exit(GIT_CONTEXT_ERROR_CODE)


@cli.command("uninstall-hook")
@click.pass_context
def uninstall_hook(ctx):
    """Uninstall gitlint commit-msg hook."""
    try:
        hooks.GitHookInstaller.uninstall_commit_msg_hook(ctx.obj.config)
        hook_path = hooks.GitHookInstaller.commit_msg_hook_path(ctx.obj.config)
        click.echo(f"Successfully uninstalled gitlint commit-msg hook from {hook_path}")
        ctx.exit(GITLINT_SUCCESS)
    except hooks.GitHookInstallerError as e:
        click.echo(e, err=True)
        ctx.exit(GIT_CONTEXT_ERROR_CODE)


@cli.command("run-hook")
@click.pass_context
def run_hook(ctx):
    """Runs the gitlint commit-msg hook."""

    exit_code = 1
    while exit_code > 0:
        try:
            click.echo("gitlint: checking commit message...")
            ctx.invoke(lint)
        except GitlintError as e:
            handle_gitlint_error(ctx, e)
        except click.exceptions.Exit as e:
            # Flush stderr andstdout, this resolves an issue with output ordering in Cygwin
            sys.stderr.flush()
            sys.stdout.flush()

            exit_code = e.exit_code
            if exit_code == GITLINT_SUCCESS:
                click.echo("gitlint: " + click.style("OK", fg="green") + " (no violations in commit message)")
                continue

            click.echo("-----------------------------------------------")
            click.echo("gitlint: " + click.style("Your commit message contains violations.", fg="red"))

            value = None
            while value not in ["y", "n", "e"]:
                click.echo(
                    "Continue with commit anyways (this keeps the current commit message)? [y(es)/n(no)/e(dit)] ",
                    nl=False,
                )

                # Ideally, we'd want to use click.getchar() or click.prompt() to get user's input here instead of
                # input(). However, those functions currently don't support getting answers from stdin.
                # This wouldn't be a huge issue since this is unlikely to occur in the real world,
                # were it not that we use a stdin to pipe answers into gitlint in our integration tests.
                # If that ever changes, we can revisit this.
                # Related click pointers:
                # - https://github.com/pallets/click/issues/1370
                # - https://github.com/pallets/click/pull/1372
                # - From https://click.palletsprojects.com/en/7.x/utils/#getting-characters-from-terminal
                #   Note that this function will always read from the terminal, even if stdin is instead a pipe.
                value = input()

            if value == "y":
                LOG.debug("run-hook: commit message accepted")
                exit_code = GITLINT_SUCCESS
            elif value == "e":
                LOG.debug("run-hook: editing commit message")
                if ctx.obj.msg_filename:
                    editor = os.environ.get("EDITOR", DEFAULT_COMMIT_MSG_EDITOR)
                    LOG.debug("run-hook: %s %s", editor, ctx.obj.msg_filename)
                    shell(f"{editor} {ctx.obj.msg_filename}")
                else:
                    click.echo("Editing only possible when --msg-filename is specified.")
                    ctx.exit(exit_code)
            elif value == "n":
                LOG.debug("run-hook: commit message declined")
                click.echo("Commit aborted.")
                click.echo("Your commit message: ")
                click.echo("-----------------------------------------------")
                click.echo(ctx.obj.gitcontext.commits[0].message.full)
                click.echo("-----------------------------------------------")
                ctx.exit(exit_code)

    ctx.exit(exit_code)


@cli.command("generate-config")
@click.pass_context
def generate_config(ctx):
    """Generates a sample gitlint config file."""
    path = click.prompt("Please specify a location for the sample gitlint config file", default=DEFAULT_CONFIG_FILE)
    path = os.path.realpath(path)
    dir_name = os.path.dirname(path)
    if not os.path.exists(dir_name):
        click.echo(f"Error: Directory '{dir_name}' does not exist.", err=True)
        ctx.exit(USAGE_ERROR_CODE)
    elif os.path.exists(path):
        click.echo(f'Error: File "{path}" already exists.', err=True)
        ctx.exit(USAGE_ERROR_CODE)

    LintConfigGenerator.generate_config(path)
    click.echo(f"Successfully generated {path}")
    ctx.exit(GITLINT_SUCCESS)


# Let's Party!
setup_logging()
if __name__ == "__main__":
    cli()  # pragma: no cover
