# -*- coding: utf-8 -*-
from gitlint.tests.base import BaseTestCase
from gitlint.rules import AuthorValidEmail, AuthorFromFile, RuleViolation

import tempfile


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

    def test_author_from_list_rule(self):
        authors_file = tempfile.NamedTemporaryFile(mode='wb')
        valid_authors = [
            (u'Foo Bar', u'foo@bar.com'),
            (u'Jöhn Doe', u'jöhndoe@bar.com')
        ]
        invalid_authors = [
            (u'Föo', u'fäo@bar.com'),
            (u'Jöhn Doe', u'jöhndoe@doe.com')
        ]
        for author in valid_authors:
            line = u'{0} <{1}>\n'.format(*author)
            authors_file.write(line.encode('utf-8'))
            authors_file.flush()
        rule = AuthorFromFile({'file': authors_file.name, 'validate-authors': True, 'validate-committers': False})
        for author in valid_authors:
            commit = self.gitcommit(u"", author_name=author[0], author_email=author[1],)
            violations = rule.validate(commit)
            self.assertIsNone(violations)
        for author in invalid_authors:
            commit = self.gitcommit(u"", author_name=author[0],
                                    author_email=author[1])
            violations = rule.validate(commit)
            self.assertListEqual(
                violations,
                [RuleViolation("M2", u"Author information does not match", u"{} <{}>".format(author[0], author[1]))])

    def test_committer_from_list_rule(self):
        authors_file = tempfile.NamedTemporaryFile(mode='wb')
        valid_authors = [
            (u'Foo Bar', u'foo@bar.com'),
            (u'Jöhn Doe', u'jöhndoe@bar.com')
        ]
        invalid_authors = [
            (u'Föo', u'fäo@bar.com'),
            (u'Jöhn Doe', u'jöhndoe@doe.com')
        ]
        for author in valid_authors:
            line = u'{0} <{1}>\n'.format(*author)
            authors_file.write(line.encode('utf-8'))
            authors_file.flush()
        rule = AuthorFromFile({'file': authors_file.name, 'validate-authors': False, 'validate-committers': True})
        for author in valid_authors:
            commit = self.gitcommit(u"", committer_name=author[0], committer_email=author[1],)
            violations = rule.validate(commit)
            self.assertIsNone(violations)
        for author in invalid_authors:
            commit = self.gitcommit(u"", author_name=author[0],
                                    author_email=author[1])
            violations = rule.validate(commit)
            self.assertListEqual(
                violations,
                [RuleViolation("M2", u"Committer information does not match", u"{} <{}>".format(author[0], author[1]))])
