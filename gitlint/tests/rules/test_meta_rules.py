# -*- coding: utf-8 -*-
from gitlint.tests.base import BaseTestCase
from gitlint.rules import AuthorValidEmail, RuleViolation


class MetaRuleTests(BaseTestCase):
    def test_author_valid_email_rule(self):
        rule = AuthorValidEmail()

        # valid email addresses
        valid_email_addresses = [u"föo@bar.com", u"Jöhn.Doe@bar.com", u"jöhn+doe@bar.com", u"jöhn/doe@bar.com",
                                 u"jöhn.doe@subdomain.bar.com"]
        for email in valid_email_addresses:
            commit = self.gitcommit(u"", author_email=email)
            violations = rule.validate(commit)
            self.assertIsNone(violations)

        # No email address (=allowed for now, as gitlint also lints messages passed via stdin that don't have an
        # email address)
        commit = self.gitcommit(u"")
        violations = rule.validate(commit)
        self.assertIsNone(violations)

        # Invalid email addresses: no TLD, no domain, no @, space anywhere (=valid but not allowed by gitlint)
        invalid_email_addresses = [u"föo@bar", u"JöhnDoe", u"Jöhn Doe", u"Jöhn Doe@foo.com", u" JöhnDoe@foo.com",
                                   u"JöhnDoe@ foo.com", u"JöhnDoe@foo. com", u"JöhnDoe@foo. com", u"@bår.com",
                                   u"föo@.com"]
        for email in invalid_email_addresses:
            commit = self.gitcommit(u"", author_email=email)
            violations = rule.validate(commit)
            self.assertListEqual(violations,
                                 [RuleViolation("M1", "Author email for commit is invalid", email)])

    def test_author_valid_email_rule_custom_regex(self):
        # regex=None -> the rule isn't applied
        rule = AuthorValidEmail()
        rule.options['regex'].set(None)
        emailadresses = [u"föo", None, u"hür dür"]
        for email in emailadresses:
            commit = self.gitcommit(u"", author_email=email)
            violations = rule.validate(commit)
            self.assertIsNone(violations)

        # Custom domain
        rule = AuthorValidEmail({'regex': u"[^@]+@bår.com"})
        valid_email_addresses = [
            u"föo@bår.com", u"Jöhn.Doe@bår.com", u"jöhn+doe@bår.com", u"jöhn/doe@bår.com"]
        for email in valid_email_addresses:
            commit = self.gitcommit(u"", author_email=email)
            violations = rule.validate(commit)
            self.assertIsNone(violations)

        # Invalid email addresses
        invalid_email_addresses = [u"föo@hur.com"]
        for email in invalid_email_addresses:
            commit = self.gitcommit(u"", author_email=email)
            violations = rule.validate(commit)
            self.assertListEqual(violations,
                                 [RuleViolation("M1", "Author email for commit is invalid", email)])
