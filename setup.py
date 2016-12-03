#!/usr/bin/env python
from setuptools import setup, find_packages
import re
import os

# There is an issue with building python packages in a shared vagrant directory because of how setuptools works
# in python < 2.7.9. We solve this by deleting the filesystem hardlinking capability during build.
# See: http://stackoverflow.com/a/22147112/381010
del os.link

description = "Git commit message linter written in python, checks your commit messages for style."
long_description = """
Great for use as a commit-msg git hook or as part of your gating script in a CI/CD pipeline (e.g. jenkins).
Many of the gitlint validations are based on `well-known`_ community_ `standards`_, others are based on checks that
we've found useful throughout the years. Gitlint has sane defaults, but you can also easily customize it to your
own liking.

Demo and full documentation on `jorisroovers.github.io/gitlint`_.
To see what's new in the latest release, visit the CHANGELOG_.

Source code on `github.com/jorisroovers/gitlint`_.

.. _well-known: http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html
.. _community: http://addamhardy.com/blog/2013/06/05/good-commit-messages-and-enforcing-them-with-git-hooks/
.. _standards: http://chris.beams.io/posts/git-commit/
.. _jorisroovers.github.io/gitlint: https://jorisroovers.github.io/gitlint
.. _CHANGELOG: https://github.com/jorisroovers/gitlint/blob/master/CHANGELOG.md
.. _github.com/jorisroovers/gitlint: https://github.com/jorisroovers/gitlint
"""


# shamelessly stolen from mkdocs' setup.py: https://github.com/mkdocs/mkdocs/blob/master/setup.py
def get_version(package):
    """Return package version as listed in `__version__` in `init.py`."""
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


setup(
    name="gitlint",
    version=get_version("gitlint"),
    description=description,
    long_description=long_description,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License"
    ],
    install_requires=[
        'Click==6.6',
        'sh==1.11',
        'arrow==0.10.0',
        'ordereddict==1.1',
    ],
    extras_require={
        ':python_version == "2.6"': [
            'importlib==1.0.3',
        ],
    },
    keywords='gitlint git lint',
    author='Joris Roovers',
    url='https://github.com/jorisroovers/gitlint',
    license='MIT',
    package_data={
        'gitlint': ['files/*']
    },
    packages=find_packages(exclude=["examples"]),
    entry_points={
        "console_scripts": [
            "gitlint = gitlint.cli:cli",
        ],
    },
)
