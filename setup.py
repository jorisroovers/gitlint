#!/usr/bin/env python
from setuptools import setup, find_packages
import re
import os

# There is an issue with building python packages in a shared vagrant directory because of how setuptools works
# in python < 2.7.9. We solve this by deleting the filesystem hardlinking capability during build.
# See: http://stackoverflow.com/a/22147112/381010
del os.link

long_description = (
    "Linter for git repositories. Under active development."
    "Source code: https://github.com/jorisroovers/gitlint"
)

# shamelessly stolen from mkdocs' setup.py: https://github.com/mkdocs/mkdocs/blob/master/setup.py
def get_version(package):
    """Return package version as listed in `__version__` in `init.py`."""
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


setup(
    name="gitlint",
    version=get_version("gitlint"),
    description="Linter for git repositories. Under active development.",
    long_description=long_description,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License"
    ],
    install_requires=[
        'Click==4.1',
        'sh==1.11'
    ],
    keywords='gitlint git lint',
    author='Joris Roovers',
    url='https://github.com/jorisroovers/gitlint',
    license='MIT',
    packages=find_packages(exclude=["examples"]),
    entry_points={
        "console_scripts": [
            "gitlint = gitlint.cli:cli",
        ],
    },
)
