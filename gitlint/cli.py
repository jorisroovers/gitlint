import gitlint
from gitlint.lint import GitLinter
from gitlint.config import LintConfig, LintConfigError
import os
import click
import sys
import sh

DEFAULT_CONFIG_FILE = ".gitlint"
CONFIG_ERROR_CODE = 10000


def get_lint_config(config_path=None):
    """ Tries loading the config from the given path. If no path is specified, the default config path
    is tried, and if that is not specified, we the default config is returned. """
    # config path specified
    config = None
    try:
        if config_path:
            config = LintConfig.load_from_file(config_path)
        elif os.path.exists(DEFAULT_CONFIG_FILE):
            config = LintConfig.load_from_file(DEFAULT_CONFIG_FILE)

    except LintConfigError as e:
        click.echo("Error during config file parsing: {0}".format(e.message))
        exit(CONFIG_ERROR_CODE)  # return 10000 on config error

    # no config file
    if config:
        click.echo("Using config from {0}".format(config.config_path))
    else:
        config = LintConfig()

    return config


@click.command()
@click.option('-C', '--config', type=click.Path(exists=True),
              help="Config file location (default: {0}).".format(DEFAULT_CONFIG_FILE))
@click.option('-c', multiple=True)
@click.option('--ignore', default="", help="Ignore rules (comma-separated by id or name).")
@click.option('-v', '--verbose', count=True, default=0,
              help="Verbosity, more v's for more verbose output (e.g.: -v, -vv, -vvv). Default: -vvv", )
@click.option('-s', '--silent', help="Silent mode (no output). Takes precedence over -v, -vv, -vvv.", is_flag=True)
@click.version_option(version=gitlint.__version__)
def cli(config, c, ignore, verbose, silent):
    """ Git lint tool, checks your git commit messages for styling issues """

    try:
        # Config precedence:
        # First, load default config or config from configfile
        lint_config = get_lint_config(config)
        # Then process any commandline configuration flags
        try:
            lint_config.apply_config_options(c)
        except LintConfigError as e:
            click.echo("Config Error: '-c {0}' is invalid. Use '-c <rule>.<option>=<value>'.".format(e.message))
            exit(CONFIG_ERROR_CODE)

        # Finally, overwrite with any convenience commandline flags
        lint_config.apply_on_csv_string(ignore, lint_config.disable_rule)
        if silent:
            lint_config.verbosity = 0
        elif verbose > 0:
            lint_config.verbosity = verbose
    except LintConfigError as e:
        click.echo("Config Error: {0}".format(e.message))
        exit(CONFIG_ERROR_CODE)  # return 10000 on config error

    linter = GitLinter(lint_config)
    if sys.stdin.isatty():
        # Use _tty_out = False to disable git color output
        commit_msg = repr(sh.git.log("-1", "--pretty=%B", _tty_out=False))
    else:
        commit_msg = sys.stdin.read()
    violations = linter.lint_commit_message(commit_msg)
    linter.print_violations(violations)
    exit(len(violations))


if __name__ == "__main__":
    cli()
