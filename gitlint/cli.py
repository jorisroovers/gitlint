import gitlint
from gitlint.lint import GitLinter
from gitlint.config import LintConfig, LintConfigError
import os
import click
import sys
import sh

DEFAULT_CONFIG_FILE = ".gitlint"


def get_lint_config(config_path=None):
    """ Tries loading the config from the given path. If no path is specified, the default config path
    is tried, and if that is not specified, we the default config is returned. """
    # config path specified
    if config_path:
        config = LintConfig.load_from_file(config_path)
        click.echo("Using config from {0}".format(config_path))
    # default config path
    elif os.path.exists(DEFAULT_CONFIG_FILE):
        config = LintConfig.load_from_file(DEFAULT_CONFIG_FILE)
        click.echo("Using config from {0}".format(DEFAULT_CONFIG_FILE))
    # no config file
    else:
        config = LintConfig()

    return config


@click.command()
@click.option('--config', type=click.Path(exists=True),
              help="Config file location (default: {0}).".format(DEFAULT_CONFIG_FILE))
@click.option('--ignore', default="", help="Ignore rules (comma-separated by id or name).")
@click.option('-v', '--verbose', count=True, default=3,
              help="Verbosity, more v's for more verbose output (e.g.: -v, -vv, -vvv). Default: -vvv", )
@click.option('-s', '--silent', help="Silent mode (no output).", is_flag=True)
@click.version_option(version=gitlint.__version__)
def cli(config, ignore, verbose, silent):
    """ Git lint tool, checks your git commit messages for styling issues """
    try:
        lint_config = get_lint_config(config)
        lint_config.apply_on_csv_string(ignore, lint_config.disable_rule)
        if silent:
            lint_config.verbosity = 0
        else:
            lint_config.verbosity = verbose
    except LintConfigError as e:
        click.echo("Lint Config Error: {0}".format(e.message))
        exit(10000)  # return 10000 on config error

    linter = GitLinter(lint_config)
    if sys.stdin.isatty():
        # Use _tty_out = False to disable git color output
        commit_msg = repr(sh.git.log("-1", "--pretty=%B", _tty_out=False))
    else:
        commit_msg = sys.stdin.read()
    error_count = linter.lint_commit_message(commit_msg)
    exit(error_count)


if __name__ == "__main__":
    cli()
