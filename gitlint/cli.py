# pylint: disable=bad-option-value,wrong-import-position
# We need to disable the import position checks because of the windows check that we need to do below
import copy
import logging
import os
import platform
import stat
import sys
import click

# Error codes
MAX_VIOLATION_ERROR_CODE = 252  # noqa
USAGE_ERROR_CODE = 253  # noqa
GIT_CONTEXT_ERROR_CODE = 254  # noqa
CONFIG_ERROR_CODE = 255  # noqa

import gitlint
from gitlint.lint import GitLinter
from gitlint.config import LintConfigBuilder, LintConfigError, LintConfigGenerator
from gitlint.git import GitContext, GitContextError, git_version
from gitlint import hooks
from gitlint.shell import shell
from gitlint.utils import ustr, LOG_FORMAT, IS_PY2

DEFAULT_CONFIG_FILE = ".gitlint"
# -n: disable swap files. This fixes a vim error on windows (E303: Unable to open swap file for <path>)
DEFAULT_COMMIT_MSG_EDITOR = "vim -n"

# Since we use the return code to denote the amount of errors, we need to change the default click usage error code
click.UsageError.exit_code = USAGE_ERROR_CODE

# We don't use logging.getLogger(__main__) here because that will cause DEBUG output to be lost
# when invoking gitlint as a python module (python -m gitlint.cli)
LOG = logging.getLogger("gitlint.cli")


class GitLintUsageError(Exception):
    """ Exception indicating there is an issue with how gitlint is used. """
    pass


def setup_logging():
    """ Setup gitlint logging """
    root_log = logging.getLogger("gitlint")
    root_log.propagate = False  # Don't propagate to child loggers, the gitlint root logger handles everything
    handler = logging.StreamHandler()
    formatter = logging.Formatter(LOG_FORMAT)
    handler.setFormatter(formatter)
    root_log.addHandler(handler)
    root_log.setLevel(logging.ERROR)


def log_system_info():
    LOG.debug("Platform: %s", platform.platform())
    LOG.debug("Python version: %s", sys.version)
    LOG.debug("Git version: %s", git_version())
    LOG.debug("Gitlint version: %s", gitlint.__version__)
    LOG.debug("GITLINT_USE_SH_LIB: %s", os.environ.get("GITLINT_USE_SH_LIB", "[NOT SET]"))
    LOG.debug("DEFAULT_ENCODING: %s", gitlint.utils.DEFAULT_ENCODING)


def build_config(  # pylint: disable=too-many-arguments
        target, config_path, c, extra_path, ignore, contrib, ignore_stdin, staged, verbose, silent, debug
):
    """ Creates a LintConfig object based on a set of commandline parameters. """
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
        config_builder.set_option('general', 'ignore', ignore)

    if contrib:
        config_builder.set_option('general', 'contrib', contrib)

    if ignore_stdin:
        config_builder.set_option('general', 'ignore-stdin', ignore_stdin)

    if silent:
        config_builder.set_option('general', 'verbosity', 0)
    elif verbose > 0:
        config_builder.set_option('general', 'verbosity', verbose)

    if extra_path:
        config_builder.set_option('general', 'extra-path', extra_path)

    if target:
        config_builder.set_option('general', 'target', target)

    if debug:
        config_builder.set_option('general', 'debug', debug)

    if staged:
        config_builder.set_option('general', 'staged', staged)

    config = config_builder.build()

    return config, config_builder


def get_stdin_data():
    """ Helper function that returns data send to stdin or False if nothing is send """
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
            return ustr(input_data)
    return False


def build_git_context(lint_config, msg_filename, refspec):
    """ Builds a git context based on passed parameters and order of precedence """

    # Determine which GitContext method to use if a custom message is passed
    from_commit_msg = GitContext.from_commit_msg
    if lint_config.staged:
        LOG.debug("Fetching additional meta-data from staged commit")
        from_commit_msg = lambda message: GitContext.from_staged_commit(message, lint_config.target)  # noqa

    # Order of precedence:
    # 1. Any data specified via --msg-filename
    if msg_filename:
        LOG.debug("Using --msg-filename.")
        return from_commit_msg(ustr(msg_filename.read()))

    # 2. Any data sent to stdin (unless stdin is being ignored)
    if not lint_config.ignore_stdin:
        stdin_input = get_stdin_data()
        if stdin_input:
            LOG.debug("Stdin data: '%s'", stdin_input)
            LOG.debug("Stdin detected and not ignored. Using as input.")
            return from_commit_msg(stdin_input)

    if lint_config.staged:
        raise GitLintUsageError(u"The 'staged' option (--staged) can only be used when using '--msg-filename' or "
                                u"when piping data to gitlint via stdin.")

    # 3. Fallback to reading from local repository
    LOG.debug("No --msg-filename flag, no or empty data passed to stdin. Using the local repo.")
    return GitContext.from_local_repository(lint_config.target, refspec)


class ContextObj(object):
    """ Simple class to hold data that is passed between Click commands via the Click context. """

    def __init__(self, config, config_builder, refspec, msg_filename, gitcontext=None):
        self.config = config
        self.config_builder = config_builder
        self.refspec = refspec
        self.msg_filename = msg_filename
        self.gitcontext = gitcontext


@click.group(invoke_without_command=True, context_settings={'max_content_width': 120},
             epilog="When no COMMAND is specified, gitlint defaults to 'gitlint lint'.")
@click.option('--target', envvar='GITLINT_TARGET',
              type=click.Path(exists=True, resolve_path=True, file_okay=False, readable=True),
              help="Path of the target git repository. [default: current working directory]")
@click.option('-C', '--config', type=click.Path(exists=True, dir_okay=False, readable=True, resolve_path=True),
              help="Config file location [default: {0}]".format(DEFAULT_CONFIG_FILE))
@click.option('-c', multiple=True,
              help="Config flags in format <rule>.<option>=<value> (e.g.: -c T1.line-length=80). " +
                   "Flag can be used multiple times to set multiple config values.")  # pylint: disable=bad-continuation
@click.option('--commits', envvar='GITLINT_COMMITS', default=None, help="The range of commits to lint. [default: HEAD]")
@click.option('-e', '--extra-path', envvar='GITLINT_EXTRA_PATH',
              help="Path to a directory or python module with extra user-defined rules",
              type=click.Path(exists=True, resolve_path=True, readable=True))
@click.option('--ignore', envvar='GITLINT_IGNORE', default="", help="Ignore rules (comma-separated by id or name).")
@click.option('--contrib', envvar='GITLINT_CONTRIB', default="",
              help="Contrib rules to enable (comma-separated by id or name).")
@click.option('--msg-filename', type=click.File(), help="Path to a file containing a commit-msg.")
@click.option('--ignore-stdin', envvar='GITLINT_IGNORE_STDIN', is_flag=True,
              help="Ignore any stdin data. Useful for running in CI server.")
@click.option('--staged', envvar='GITLINT_STAGED', is_flag=True,
              help="Read staged commit meta-info from the local repository.")
@click.option('-v', '--verbose', envvar='GITLINT_VERBOSITY', count=True, default=0,
              help="Verbosity, more v's for more verbose output (e.g.: -v, -vv, -vvv). [default: -vvv]", )
@click.option('-s', '--silent', envvar='GITLINT_SILENT', is_flag=True,
              help="Silent mode (no output). Takes precedence over -v, -vv, -vvv.")
@click.option('-d', '--debug', envvar='GITLINT_DEBUG', help="Enable debugging output.", is_flag=True)
@click.version_option(version=gitlint.__version__)
@click.pass_context
def cli(  # pylint: disable=too-many-arguments
        ctx, target, config, c, commits, extra_path, ignore, contrib,
        msg_filename, ignore_stdin, staged, verbose, silent, debug,
):
    """ Git lint tool, checks your git commit messages for styling issues

        Documentation: http://jorisroovers.github.io/gitlint
    """

    try:
        if debug:
            logging.getLogger("gitlint").setLevel(logging.DEBUG)
        LOG.debug("To report issues, please visit https://github.com/jorisroovers/gitlint/issues")

        log_system_info()

        # Get the lint config from the commandline parameters and
        # store it in the context (click allows storing an arbitrary object in ctx.obj).
        config, config_builder = build_config(target, config, c, extra_path, ignore, contrib,
                                              ignore_stdin, staged, verbose, silent, debug)
        LOG.debug(u"Configuration\n%s", ustr(config))

        ctx.obj = ContextObj(config, config_builder, commits, msg_filename)

        # If no subcommand is specified, then just lint
        if ctx.invoked_subcommand is None:
            ctx.invoke(lint)

    except GitContextError as e:
        click.echo(ustr(e))
        ctx.exit(GIT_CONTEXT_ERROR_CODE)
    except GitLintUsageError as e:
        click.echo(u"Error: {0}".format(ustr(e)))
        ctx.exit(USAGE_ERROR_CODE)
    except LintConfigError as e:
        click.echo(u"Config Error: {0}".format(ustr(e)))
        ctx.exit(CONFIG_ERROR_CODE)


@cli.command("lint")
@click.pass_context
def lint(ctx):
    """ Lints a git repository [default command] """
    lint_config = ctx.obj.config
    refspec = ctx.obj.refspec
    msg_filename = ctx.obj.msg_filename

    gitcontext = build_git_context(lint_config, msg_filename, refspec)
    # Set gitcontext in the click context, so we can use it in command that are ran after this
    # in particular, this is used by run-hook
    ctx.obj.gitcontext = gitcontext

    number_of_commits = len(gitcontext.commits)
    # Exit if we don't have commits in the specified range. Use a 0 exit code, since a popular use-case is one
    # where users are using --commits in a check job to check the commit messages inside a CI job. By returning 0, we
    # ensure that these jobs don't fail if for whatever reason the specified commit range is empty.
    if number_of_commits == 0:
        LOG.debug(u'No commits in range "%s"', refspec)
        ctx.exit(0)

    LOG.debug(u'Linting %d commit(s)', number_of_commits)
    general_config_builder = ctx.obj.config_builder
    last_commit = gitcontext.commits[-1]

    # Let's get linting!
    first_violation = True
    exit_code = 0
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
                linter.display.e(u"{0}Commit {1}:".format(
                    "\n" if not first_violation or commit is last_commit else "",
                    commit.sha[:10]
                ))
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
    """ Install gitlint as a git commit-msg hook. """
    try:
        hooks.GitHookInstaller.install_commit_msg_hook(ctx.obj.config)
        hook_path = hooks.GitHookInstaller.commit_msg_hook_path(ctx.obj.config)
        click.echo(u"Successfully installed gitlint commit-msg hook in {0}".format(hook_path))
        ctx.exit(0)
    except hooks.GitHookInstallerError as e:
        click.echo(ustr(e), err=True)
        ctx.exit(GIT_CONTEXT_ERROR_CODE)


@cli.command("uninstall-hook")
@click.pass_context
def uninstall_hook(ctx):
    """ Uninstall gitlint commit-msg hook. """
    try:
        hooks.GitHookInstaller.uninstall_commit_msg_hook(ctx.obj.config)
        hook_path = hooks.GitHookInstaller.commit_msg_hook_path(ctx.obj.config)
        click.echo(u"Successfully uninstalled gitlint commit-msg hook from {0}".format(hook_path))
        ctx.exit(0)
    except hooks.GitHookInstallerError as e:
        click.echo(ustr(e), err=True)
        ctx.exit(GIT_CONTEXT_ERROR_CODE)


@cli.command("run-hook")
@click.pass_context
def run_hook(ctx):
    """ Runs the gitlint commit-msg hook. """

    exit_code = 1
    while exit_code > 0:
        try:
            click.echo(u"gitlint: checking commit message...")
            ctx.invoke(lint)
        except click.exceptions.Exit as e:
            # Flush stderr andstdout, this resolves an issue with output ordering in Cygwin
            sys.stderr.flush()
            sys.stdout.flush()

            exit_code = e.exit_code
            if exit_code == 0:
                click.echo(u"gitlint: " + click.style("OK", fg='green') + u" (no violations in commit message)")
                continue

            click.echo(u"-----------------------------------------------")
            click.echo(u"gitlint: " + click.style("Your commit message contains the above violations.", fg='red'))

            value = None
            while value not in ["y", "n", "e"]:
                click.echo("Continue with commit anyways (this keeps the current commit message)? "
                           "[y(es)/n(no)/e(dit)] ", nl=False)

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
                #
                # We also need a to use raw_input() in Python2 as input() is unsafe (and raw_input() doesn't exist in
                # Python3). See https://stackoverflow.com/a/4960216/381010
                input_func = input
                if IS_PY2:
                    input_func = raw_input  # noqa pylint: disable=undefined-variable

                value = input_func()

            if value == "y":
                LOG.debug("run-hook: commit message accepted")
                exit_code = 0
            elif value == "e":
                LOG.debug("run-hook: editing commit message")
                msg_filename = ctx.obj.msg_filename
                if msg_filename:
                    msg_filename.seek(0)
                    editor = os.environ.get("EDITOR", DEFAULT_COMMIT_MSG_EDITOR)
                    msg_filename_path = os.path.realpath(msg_filename.name)
                    LOG.debug("run-hook: %s %s", editor, msg_filename_path)
                    shell(editor + " " + msg_filename_path)
                else:
                    click.echo(u"Editing only possible when --msg-filename is specified.")
                    ctx.exit(exit_code)
            elif value == "n":
                LOG.debug("run-hook: commit message declined")
                click.echo(u"Commit aborted.")
                click.echo(u"Your commit message: ")
                click.echo(u"-----------------------------------------------")
                click.echo(ctx.obj.gitcontext.commits[0].message.full)
                click.echo(u"-----------------------------------------------")
                ctx.exit(exit_code)

    ctx.exit(exit_code)


@cli.command("generate-config")
@click.pass_context
def generate_config(ctx):
    """ Generates a sample gitlint config file. """
    path = click.prompt('Please specify a location for the sample gitlint config file', default=DEFAULT_CONFIG_FILE)
    path = os.path.realpath(path)
    dir_name = os.path.dirname(path)
    if not os.path.exists(dir_name):
        click.echo(u"Error: Directory '{0}' does not exist.".format(dir_name), err=True)
        ctx.exit(USAGE_ERROR_CODE)
    elif os.path.exists(path):
        click.echo(u"Error: File \"{0}\" already exists.".format(path), err=True)
        ctx.exit(USAGE_ERROR_CODE)

    LintConfigGenerator.generate_config(path)
    click.echo(u"Successfully generated {0}".format(path))
    ctx.exit(0)


# Let's Party!
setup_logging()
if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    cli()  # pragma: no cover
