# pylint: disable=bad-option-value,wrong-import-position
# We need to disable the import position checks because of the windows check that we need to do below
import logging
import os
import platform
import select
import sys

import click

# Error codes
MAX_VIOLATION_ERROR_CODE = 252  # noqa
USAGE_ERROR_CODE = 253  # noqa
GIT_CONTEXT_ERROR_CODE = 254  # noqa
CONFIG_ERROR_CODE = 255  # noqa

# We need to make sure we're not on Windows before importing other gitlint modules, as some of these modules use sh
# which will raise an exception when imported on Windows.
if "windows" in platform.system().lower():  # noqa
    click.echo("Gitlint currently does not support Windows. Check out "  # noqa
               "https://github.com/jorisroovers/gitlint/issues/20 for details.", err=True)  # noqa
    exit(USAGE_ERROR_CODE)  # noqa

import gitlint
from gitlint.lint import GitLinter
from gitlint.config import LintConfigBuilder, LintConfigError, LintConfigGenerator
from gitlint.git import GitContext, GitContextError, git_version
from gitlint import hooks
from gitlint.utils import ustr, LOG_FORMAT

DEFAULT_CONFIG_FILE = ".gitlint"

# Since we use the return code to denote the amount of errors, we need to change the default click usage error code
click.UsageError.exit_code = USAGE_ERROR_CODE

LOG = logging.getLogger(__name__)


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


def build_config(ctx, target, config_path, c, extra_path, ignore, verbose, silent, debug):
    """ Creates a LintConfig object based on a set of commandline parameters. """
    config_builder = LintConfigBuilder()
    try:
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

        config = config_builder.build()

        return config, config_builder
    except LintConfigError as e:
        click.echo(u"Config Error: {0}".format(ustr(e)))
    ctx.exit(CONFIG_ERROR_CODE)  # return CONFIG_ERROR_CODE on config error


def stdin_has_data():
    """ Helper function that indicates whether the stdin has data incoming or not """
    # This code was taken from:
    # https://stackoverflow.com/questions/3762881/how-do-i-check-if-stdin-has-some-data

    # Caveat, this probably doesn't work on Windows because the code is dependent on the unix SELECT syscall.
    # Details: https://docs.python.org/2/library/select.html#select.select
    # This isn't a real problem now, because gitlint as a whole doesn't support Windows (see #20).
    # If we ever do, we probably want to fall back to the old detection mechanism of reading from the local git repo
    # in case there's no TTY connected to STDIN.
    return select.select([sys.stdin, ], [], [], 0.0)[0]


@click.group(invoke_without_command=True, epilog="When no COMMAND is specified, gitlint defaults to 'gitlint lint'.")
@click.option('--target', type=click.Path(exists=True, resolve_path=True, file_okay=False, readable=True),
              help="Path of the target git repository. [default: current working directory]")
@click.option('-C', '--config', type=click.Path(exists=True, dir_okay=False, readable=True, resolve_path=True),
              help="Config file location [default: {0}]".format(DEFAULT_CONFIG_FILE))
@click.option('-c', multiple=True,
              help="Config flags in format <rule>.<option>=<value> (e.g.: -c T1.line-length=80). " +
                   "Flag can be used multiple times to set multiple config values.")  # pylint: disable=bad-continuation
@click.option('--commits', default=None, help="The range of commits to lint. [default: HEAD]")
@click.option('-e', '--extra-path', help="Path to a directory or python module with extra user-defined rules",
              type=click.Path(exists=True, resolve_path=True, readable=True))
@click.option('--ignore', default="", help="Ignore rules (comma-separated by id or name).")
@click.option('-v', '--verbose', count=True, default=0,
              help="Verbosity, more v's for more verbose output (e.g.: -v, -vv, -vvv). [default: -vvv]", )
@click.option('-s', '--silent', help="Silent mode (no output). Takes precedence over -v, -vv, -vvv.", is_flag=True)
@click.option('-d', '--debug', help="Enable debugging output.", is_flag=True)
@click.version_option(version=gitlint.__version__)
@click.pass_context
def cli(ctx, target, config, c, commits, extra_path, ignore, verbose, silent, debug):
    """ Git lint tool, checks your git commit messages for styling issues """

    try:
        if debug:
            logging.getLogger("gitlint").setLevel(logging.DEBUG)

        log_system_info()

        # Get the lint config from the commandline parameters and
        # store it in the context (click allows storing an arbitrary object in ctx.obj).
        config, config_builder = build_config(ctx, target, config, c, extra_path, ignore, verbose, silent, debug)

        LOG.debug(u"Configuration\n%s", ustr(config))

        ctx.obj = (config, config_builder, commits)

        # If no subcommand is specified, then just lint
        if ctx.invoked_subcommand is None:
            ctx.invoke(lint)

    except GitContextError as e:
        click.echo(ustr(e))
        ctx.exit(GIT_CONTEXT_ERROR_CODE)


@cli.command("lint")
@click.pass_context
def lint(ctx):
    """ Lints a git repository [default command] """
    lint_config = ctx.obj[0]

    # If we get data via stdin, then let's consider that our commit message, otherwise parse it from the local git repo.
    if stdin_has_data():
        stdin_str = ustr(sys.stdin.read())
        gitcontext = GitContext.from_commit_msg(stdin_str)
    else:
        gitcontext = GitContext.from_local_repository(lint_config.target, ctx.obj[2])

    number_of_commits = len(gitcontext.commits)
    # Exit if we don't have commits in the specified range. Use a 0 exit code, since a popular use-case is one
    # where users are using --commits in a check job to check the commit messages inside a CI job. By returning 0, we
    # ensure that these jobs don't fail if for whatever reason the specified commit range is empty.
    if number_of_commits == 0:
        click.echo(u'No commits in range "{0}".'.format(ctx.obj[2]))
        ctx.exit(0)

    general_config_builder = ctx.obj[1]
    last_commit = gitcontext.commits[-1]

    # Let's get linting!
    first_violation = True
    exit_code = 0
    for commit in gitcontext.commits:
        # Build a config_builder and linter taking into account the commit specific config (if any)
        config_builder = general_config_builder.clone()
        config_builder.set_config_from_commit(commit)
        lint_config = config_builder.build(lint_config)
        linter = GitLinter(lint_config)

        # Actually do the linting
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
        lint_config = ctx.obj[0]
        hooks.GitHookInstaller.install_commit_msg_hook(lint_config)
        # declare victory :-)
        hook_path = hooks.GitHookInstaller.commit_msg_hook_path(lint_config)
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
        lint_config = ctx.obj[0]
        hooks.GitHookInstaller.uninstall_commit_msg_hook(lint_config)
        # declare victory :-)
        hook_path = hooks.GitHookInstaller.commit_msg_hook_path(lint_config)
        click.echo(u"Successfully uninstalled gitlint commit-msg hook from {0}".format(hook_path))
        ctx.exit(0)
    except hooks.GitHookInstallerError as e:
        click.echo(ustr(e), err=True)
        ctx.exit(GIT_CONTEXT_ERROR_CODE)


@cli.command("generate-config")
@click.pass_context
def generate_config(ctx):
    """ Generates a sample gitlint config file. """
    path = click.prompt('Please specify a location for the sample gitlint config file', default=DEFAULT_CONFIG_FILE)
    path = os.path.abspath(path)
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
    cli()  # pragma: no cover, # pylint: disable=no-value-for-parameter
