import logging
from typing import ClassVar, Optional, Set

LOG = logging.getLogger("gitlint.deprecated")
DEPRECATED_LOG_FORMAT = "%(levelname)s: %(message)s"


class Deprecation:
    """Singleton class that handles deprecation warnings and behavior."""

    # LintConfig class that is used to determine deprecation behavior
    config: ClassVar[Optional[object]] = None

    # Set of warning messages that have already been logged, to prevent duplicate warnings
    warning_msgs: ClassVar[Set[str]] = set()

    @classmethod
    def get_regex_method(cls, rule, regex_option):
        """Returns the regex method to be used for a given rule based on general.regex-style-search option.
        Logs a warning if the deprecated re.match method is returned."""

        # if general.regex-style-search is set, just return re.search
        if cls.config.regex_style_search:
            return regex_option.value.search

        warning_msg = (
            f"{rule.id} - {rule.name}: gitlint will be switching from using Python regex 'match' (match beginning) to "
            "'search' (match anywhere) semantics. "
            f"Please review your {rule.name}.regex option accordingly. "
            "To remove this warning, set general.regex-style-search=True. "
            "More details: https://jorisroovers.github.io/gitlint/configuration/#regex-style-search"
        )

        # Only log warnings once
        if warning_msg not in cls.warning_msgs:
            log = logging.getLogger("gitlint.deprecated.regex_style_search")
            log.warning(warning_msg)
        cls.warning_msgs.add(warning_msg)

        return regex_option.value.match
