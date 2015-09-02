import gitlint
from gitlint.lint import GitLinter
from gitlint.config import LintConfig
import os
import click

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
@click.argument('path', type=click.Path(exists=True))
@click.version_option(version=gitlint.__version__)
def cli(list_files, config, ignore, path):
    """ Git lint tool, checks your git commit messages for styling issues """

    lint_config = get_lint_config(config)
    lint_config.apply_on_csv_string(ignore, lint_config.disable_rule)

    linter = GitLinter(lint_config)
    # error_count = linter.lint(files)
    # exit(error_count)


if __name__ == "__main__":
    cli()
