# -*- coding: utf-8 -*-
from gitlint.tests.base import BaseTestCase
from gitlint.rules import AuthorValidEmail, RuleViolation


class MetaRuleTests(BaseTestCase):
    def test_author_valid_email_rule(self):
        rule = AuthorValidEmail()

        # valid email addresses
        valid_email_addresses = ["föo@bar.com", "Jöhn.Doe@bar.com", "jöhn+doe@bar.com", "jöhn/doe@bar.com",
                                 "jöhn.doe@subdomain.bar.com"]
        for email in valid_email_addresses:
            commit = self.gitcommit("", author_email=email)
            violations = rule.validate(commit)
            self.assertIsNone(violations)

        # No email address (=allowed for now, as gitlint also lints messages passed via stdin that don't have an
        # email address)
        commit = self.gitcommit("")
        violations = rule.validate(commit)
        self.assertIsNone(violations)

        # Invalid email addresses: no TLD, no domain, no @, space anywhere (=valid but not allowed by gitlint)
        invalid_email_addresses = ["föo@bar", "JöhnDoe", "Jöhn Doe", "Jöhn Doe@foo.com", " JöhnDoe@foo.com",
                                   "JöhnDoe@ foo.com", "JöhnDoe@foo. com", "JöhnDoe@foo. com", "@bår.com",
                                   "föo@.com"]
        for email in invalid_email_addresses:
            commit = self.gitcommit("", author_email=email)
            violations = rule.validate(commit)
            self.assertListEqual(violations,
                                 [RuleViolation("M1", "Author email for commit is invalid", email)])

    def test_author_valid_email_rule_custom_regex(self):
        # regex=None -> the rule isn't applied
        rule = AuthorValidEmail()
        rule.options['regex'].set(None)
        emailadresses = ["föo", None, "hür dür"]
        for email in emailadresses:
            commit = self.gitcommit("", author_email=email)
            violations = rule.validate(commit)
            self.assertIsNone(violations)

        # Custom domain
        rule = AuthorValidEmail({'regex': "[^@]+@bår.com"})
        valid_email_addresses = [
            "föo@bår.com", "Jöhn.Doe@bår.com", "jöhn+doe@bår.com", "jöhn/doe@bår.com"]
        for email in valid_email_addresses:
            commit = self.gitcommit("", author_email=email)
            violations = rule.validate(commit)
            self.assertIsNone(violations)

        # Invalid email addresses
        invalid_email_addresses = ["föo@hur.com"]
        for email in invalid_email_addresses:
            commit = self.gitcommit("", author_email=email)
            violations = rule.validate(commit)
            self.assertListEqual(violations,
                                 [RuleViolation("M1", "Author email for commit is invalid", email)])
