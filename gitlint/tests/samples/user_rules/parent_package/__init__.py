# -*- coding: utf-8 -*-
# This file is meant to test that we can also load rules from __init__.py files, this was an issue with pypy before.

from gitlint.rules import CommitRule


class InitFileRule(CommitRule):
    name = u"my-init-cömmit-rule"
    id = "UC1"
    options_spec = []

    def validate(self, _commit):
        return []
