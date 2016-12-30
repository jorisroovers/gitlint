import os
import sys

import click

import gitlint
from gitlint.lint import GitLinter
from gitlint.config import LintConfigBuilder, LintConfigError, LintConfigGenerator
from gitlint.git import GitContext, GitContextError
from gitlint import hooks
from gitlint.utils import ustr

DEFAULT_CONFIG_FILE = ".gitlint"

# Error codes
MAX_VIOLATION_ERROR_CODE = 252
USAGE_ERROR_CODE = 253
GIT_CONTEXT_ERROR_CODE = 254
CONFIG_ERROR_CODE = 255
# Since we use the return code to denote the amount of errors, we need to change the default click usage error code
click.UsageError.exit_code = USAGE_ERROR_CODE


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
        if debug:
            click.echo(ustr(config), nl=True)

        return config, config_builder
    except LintConfigError as e:
        click.echo(u"Config Error: {0}".format(ustr(e)))
    ctx.exit(CONFIG_ERROR_CODE)  # return CONFIG_ERROR_CODE on config error


@click.group(invoke_without_command=True, epilog="When no COMMAND is specified, gitlint defaults to 'gitlint lint'.")
@click.option('--target', type=click.Path(exists=True, resolve_path=True, file_okay=False, readable=True),
              help="Path of the target git repository. [default: current working directory]")
@click.option('-C', '--config', type=click.Path(exists=True, dir_okay=False, readable=True, resolve_path=True),
              help="Config file location [default: {0}]".format(DEFAULT_CONFIG_FILE))
@click.option('-c', multiple=True,
              help="Config flags in format <rule>.<option>=<value> (e.g.: -c T1.line-length=80). " +
                   "Flag can be used multiple times to set multiple config values.")  # pylint: disable=bad-continuation
@click.option('-e', '--extra-path', help="Path to a directory with extra user-defined rules",
              type=click.Path(exists=True, resolve_path=True, file_okay=False, readable=True))
@click.option('--ignore', default="", help="Ignore rules (comma-separated by id or name).")
@click.option('-v', '--verbose', count=True, default=0,
              help="Verbosity, more v's for more verbose output (e.g.: -v, -vv, -vvv). [default: -vvv]", )
@click.option('-s', '--silent', help="Silent mode (no output). Takes precedence over -v, -vv, -vvv.", is_flag=True)
@click.option('-d', '--debug', help="Enable debugging output.", is_flag=True)
@click.version_option(version=gitlint.__version__)
@click.pass_context
def cli(ctx, target, config, c, extra_path, ignore, verbose, silent, debug):
    """ Git lint tool, checks your git commit messages for styling issues """

    # Get the lint config from the commandline parameters and
    # store it in the context (click allows storing an arbitrary object in ctx.obj).
    config, config_builder = build_config(ctx, target, config, c, extra_path, ignore, verbose, silent, debug)

    ctx.obj = (config, config_builder)

    # If no subcommand is specified, then just lint
    if ctx.invoked_subcommand is None:
        ctx.invoke(lint)


@cli.command("lint")
@click.pass_context
def lint(ctx):
    """ Lints a git repository [default command] """
    lint_config = ctx.obj[0]
    try:
        if sys.stdin.isatty():
            # If target has not been set explicitly before, fallback to the current directory
            gitcontext = GitContext.from_local_repository(lint_config.target)
        else:
            stdin_str = ustr(sys.stdin.read())
            gitcontext = GitContext.from_commit_msg(stdin_str)
    except GitContextError as e:
        click.echo(ustr(e))
        ctx.exit(GIT_CONTEXT_ERROR_CODE)

    config_builder = ctx.obj[1]
    last_commit = gitcontext.commits[-1]
    # Apply an additional config that is specified in the last commit message
    config_builder.set_config_from_commit(last_commit)
    lint_config = config_builder.build(lint_config)

    # Let's get linting!
    linter = GitLinter(lint_config)
    violations = linter.lint(last_commit)
    linter.print_violations(violations)
    exit_code = min(MAX_VIOLATION_ERROR_CODE, len(violations))
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


if __name__ == "__main__":
    cli()  # pragma: no cover, # pylint: disable=no-value-for-parameter
