#!/usr/bin/env python
from __future__ import print_function
from setuptools import setup

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


version = "0.17.0"

setup(
    name="gitlint",
    version=version,
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
        'gitlint-core[trusted-deps]==' + version,
    ],
    keywords='gitlint git lint',
    author='Joris Roovers',
    url='https://jorisroovers.github.io/gitlint',
    project_urls={
        'Documentation': 'https://jorisroovers.github.io/gitlint',
        'Source': 'https://github.com/jorisroovers/gitlint',
    },
    license='MIT',
)
