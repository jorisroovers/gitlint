#!/bin/sh

brew install asdf

# Install multiple pythons
asdf plugin add python
asdf install python 3.6.15
asdf install python 3.7.15
asdf install python 3.8.15
asdf install python 3.9.15
asdf install python 3.10.8
asdf install python 3.11.0
asdf install python pypy3.9-7.3.9

asdf global python 3.11.0