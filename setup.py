#!/usr/bin/env python
from __future__ import print_function
from setuptools import setup, find_packages
import re
import os
import sys

# There is an issue with building python packages in a shared vagrant directory because of how setuptools works
# in python < 2.7.9. We solve this by deleting the filesystem hardlinking capability during build.
# See: http://stackoverflow.com/a/22147112/381010
try:
    del os.link
except:
    pass  # Not all OSes (e.g. windows) support os.link

description = "Git commit message linter written in python, checks your commit messages for style."
long_description = """
Great for use as a commit-msg git hook or as part of your gating script in a CI pipeline (e.g. jenkins, gitlab).
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
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License"
    ],
    install_requires=[
        'Click==6.6',
        'arrow==0.10.0'
    ],
    extras_require={
        ':python_version < "2.7"': [
            'importlib==1.0.3',
            'ordereddict==1.1',
        ],
        ':sys_platform != "win32"': [
            'sh==1.11',
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

# Print a red deprecation warning for python 2.6 users
if sys.version_info[0] == 2 and sys.version_info[1] <= 6:
    msg = "\033[31mDEPRECATION: Python 2.6 is no longer supported by the Python core team, please upgrade your Python. " + \
        "A future version of gitlint will drop support for Python 2.6\033[0m"
    print(msg)
