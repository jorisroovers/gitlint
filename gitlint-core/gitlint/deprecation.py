import logging


LOG = logging.getLogger("gitlint.deprecated")
DEPRECATED_LOG_FORMAT = "%(levelname)s: %(message)s"


class Deprecation:
    """Singleton class that handles deprecation warnings and behavior."""

    config = None

    warning_msgs = set()

    @classmethod
    def get_regex_method(cls, rule, regex_option):
        if cls.config.regex_style_search:
            return regex_option.value.search

        warning_msg = (
            f"{rule.id} - {rule.name}: gitlint will be switching from using Python regex 'match' (match beginning) to "
            "'search' (match anywhere) semantics. "
            f"Please review your {rule.name}.regex option accordingly. "
            "To remove this warning, set general.regex-style-search=True. "
            "More details: TODO"
        )

        # Only log warnings once
        if warning_msg not in cls.warning_msgs:
            log = logging.getLogger("gitlint.deprecated.regex_style_search")
            log.warning(warning_msg)
        cls.warning_msgs.add(warning_msg)

        return regex_option.value.match
