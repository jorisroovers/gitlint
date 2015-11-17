import gitlint
from gitlint.lint import GitLinter
from gitlint.config import LintConfig, LintConfigError, LintConfigGenerator
from gitlint.git import GitContext, GitContextError
from gitlint import hooks
import os
import click
import sys

DEFAULT_CONFIG_FILE = ".gitlint"

# Error codes
MAX_VIOLATION_ERROR_CODE = 252
USAGE_ERROR_CODE = 253
GIT_CONTEXT_ERROR_CODE = 254
CONFIG_ERROR_CODE = 255
# Since we use the return code to denote the amount of errors, we need to change the default click usage error code
click.UsageError.exit_code = USAGE_ERROR_CODE


def load_config_from_path(ctx, config_path=None):
    """ Tries loading the config from the given path. If no path is specified, the default config path
    is tried, and if no file exists at the that location, None is returned. """
    config = None
    try:
        if config_path:
            config = LintConfig.load_from_file(config_path)
        elif os.path.exists(DEFAULT_CONFIG_FILE):
            config = LintConfig.load_from_file(DEFAULT_CONFIG_FILE)

    except LintConfigError as e:
        click.echo("Error during config file parsing: {0}".format(str(e)))
        ctx.exit(CONFIG_ERROR_CODE)

    return config


def get_config(ctx, target, config_path, c, ignore, verbose, silent):
    """ Creates a LintConfig object based on a set of commandline parameters. """
    try:
        # Config precedence:
        # First, load default config or config from configfile
        lint_config = load_config_from_path(ctx, config_path)
        # default to default configuration when no config file was loaded
        if lint_config:
            click.echo("Using config from {0}".format(lint_config.config_path))
        else:
            lint_config = LintConfig()

        # Then process any commandline configuration flags
        lint_config.apply_config_options(c)

        # Finally, overwrite with any convenience commandline flags
        lint_config.apply_on_csv_string(ignore, lint_config.disable_rule)
        if silent:
            lint_config.verbosity = 0
        elif verbose > 0:
            lint_config.verbosity = verbose

        # Set target
        lint_config.target = target
        return lint_config
    except LintConfigError as e:
        click.echo("Config Error: {0}".format(str(e)))
    ctx.exit(CONFIG_ERROR_CODE)  # return CONFIG_ERROR_CODE on config error


@click.group(invoke_without_command=True, epilog="When no COMMAND is specified, gitlint defaults to 'gitlint lint'.")
@click.option('--target', type=click.Path(exists=True, resolve_path=True, file_okay=False, readable=True),
              default=os.getcwd(), help="Path of the target git repository. [default: current working directory]")
@click.option('-C', '--config', type=click.Path(exists=True, dir_okay=False, readable=True, resolve_path=True),
              help="Config file location [default: {}]".format(DEFAULT_CONFIG_FILE))
@click.option('-c', multiple=True,
              help="Config flags in format <rule>.<option>=<value> (e.g.: -c T1.line-length=80). " +
                   "Flag can be used multiple times to set multiple config values.")
@click.option('--ignore', default="", help="Ignore rules (comma-separated by id or name).")
@click.option('-v', '--verbose', count=True, default=0,
              help="Verbosity, more v's for more verbose output (e.g.: -v, -vv, -vvv). [default: -vvv]", )
@click.option('-s', '--silent', help="Silent mode (no output). Takes precedence over -v, -vv, -vvv.", is_flag=True)
@click.version_option(version=gitlint.__version__)
@click.pass_context
def cli(ctx, target, config, c, ignore, verbose, silent):
    """ Git lint tool, checks your git commit messages for styling issues """

    # Get the lint config from the commandline parameters and
    # store it in the context (click allows storing an arbitrary object in ctx.obj).
    lint_config = get_config(ctx, target, config, c, ignore, verbose, silent)
    ctx.obj = lint_config

    # If no subcommand is specified, then just lint
    if ctx.invoked_subcommand is None:
        ctx.invoke(lint)


@cli.command("lint")
@click.pass_context
def lint(ctx):
    """ Lints a git repository [default command] """
    lint_config = ctx.obj
    try:
        if sys.stdin.isatty():
            gitcontext = GitContext.from_local_repository(lint_config.target)
        else:
            gitcontext = GitContext()
            gitcontext.set_commit_msg(sys.stdin.read())
    except GitContextError as e:
        click.echo(str(e))
        ctx.exit(GIT_CONTEXT_ERROR_CODE)

    # Apply an additional config that is specified in the gitcontext (= commit message)
    lint_config.apply_config_from_gitcontext(gitcontext)

    # Let's get linting!
    linter = GitLinter(lint_config)
    violations = linter.lint(gitcontext)
    linter.print_violations(violations)
    exit_code = min(MAX_VIOLATION_ERROR_CODE, len(violations))
    ctx.exit(exit_code)


@cli.command("install-hook")
@click.pass_context
def install_hook(ctx):
    """ Install gitlint as a git commit-msg hook. """
    try:
        lint_config = ctx.obj
        hooks.GitHookInstaller.install_commit_msg_hook(lint_config)
        # declare victory :-)
        hook_path = hooks.GitHookInstaller.commit_msg_hook_path(lint_config)
        click.echo("Successfully installed gitlint commit-msg hook in {0}".format(hook_path))
        ctx.exit(0)
    except hooks.GitHookInstallerError as e:
        click.echo(str(e), err=True)
        ctx.exit(GIT_CONTEXT_ERROR_CODE)


@cli.command("uninstall-hook")
@click.pass_context
def uninstall_hook(ctx):
    """ Uninstall gitlint commit-msg hook. """
    try:
        lint_config = ctx.obj
        hooks.GitHookInstaller.uninstall_commit_msg_hook(lint_config)
        # declare victory :-)
        hook_path = hooks.GitHookInstaller.commit_msg_hook_path(lint_config)
        click.echo("Successfully uninstalled gitlint commit-msg hook from {0}".format(hook_path))
        ctx.exit(0)
    except hooks.GitHookInstallerError as e:
        click.echo(str(e), err=True)
        ctx.exit(GIT_CONTEXT_ERROR_CODE)


@cli.command("generate-config")
@click.pass_context
def generate_config(ctx):
    """ Generates a sample gitlint config file. """
    path = click.prompt('Please specify a location for the sample gitlint config file', default=DEFAULT_CONFIG_FILE)
    path = os.path.abspath(path)
    dir_name = os.path.dirname(path)
    if not os.path.exists(dir_name):
        click.echo("Error: Directory '{}' does not exist.".format(dir_name), err=True)
        ctx.exit(USAGE_ERROR_CODE)
    elif os.path.exists(path):
        click.echo("Error: File \"{}\" already exists.".format(path), err=True)
        ctx.exit(USAGE_ERROR_CODE)

    LintConfigGenerator.generate_config(path)
    click.echo("Successfully generated {}".format(path))
    ctx.exit(0)


if __name__ == "__main__":
    cli()
