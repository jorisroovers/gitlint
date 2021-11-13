#!/usr/bin/env python
from __future__ import print_function
from setuptools import setup, find_packages
import io
import re
import os
import platform
import sys


description = "Git commit message linter written in python, checks your commit messages for style."
long_description = """
Great for use as a commit-msg git hook or as part of your gating script in a CI pipeline (e.g. jenkins, github actions).
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
.. _CHANGELOG: https://github.com/jorisroovers/gitlint/blob/main/CHANGELOG.md
.. _github.com/jorisroovers/gitlint: https://github.com/jorisroovers/gitlint
"""


# shamelessly stolen from mkdocs' setup.py: https://github.com/mkdocs/mkdocs/blob/master/setup.py
def get_version(package):
    """Return package version as listed in `__version__` in `init.py`."""
    init_py = io.open(os.path.join(package, '__init__.py'), encoding="UTF-8").read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


setup(
    name="gitlint-core",
    version=get_version("gitlint"),
    description=description,
    long_description=long_description,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires=">=3.6",
    install_requires=[
        'Click>=8',
        'arrow>=1',
        'sh>=1.13.0 ; sys_platform != "win32"',
    ],
    extras_require={
        'trusted-deps': [
            'Click==8.0.3',
            'arrow==1.2.1',
            'sh==1.14.2 ; sys_platform != "win32"',
        ],
    },
    keywords='gitlint git lint',
    author='Joris Roovers',
    url='https://jorisroovers.github.io/gitlint',
    project_urls={
        'Documentation': 'https://jorisroovers.github.io/gitlint',
        'Source': 'https://github.com/jorisroovers/gitlint',
    },
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

# Print a red deprecation warning for python < 3.6 users
if sys.version_info[:2] < (3, 6):
    msg = "\033[31mDEPRECATION: You're using a python version that has reached end-of-life. " + \
          "Gitlint does not support Python < 3.6" + \
          "Please upgrade your Python to 3.6 or above.\033[0m"
    print(msg)

# Print a warning message for Windows users
PLATFORM_IS_WINDOWS = "windows" in platform.system().lower()
if PLATFORM_IS_WINDOWS:
    msg = "\n\n\n\n\n****************\n" + \
          "WARNING: Gitlint support for Windows is still experimental and there are some known issues: " + \
          "https://github.com/jorisroovers/gitlint/issues?q=is%3Aissue+is%3Aopen+label%3Awindows " + \
          "\n*******************"
    print(msg)
