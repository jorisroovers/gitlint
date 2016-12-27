# pylint: disable=bad-option-value,unidiomatic-typecheck,undefined-variable
import sys


def ustr(obj):
    """ Python 2 and 3 utility method that converts an obj to unicode in python 2 and to a str object in python 3"""
    if sys.version_info[0] == 2:
        # If we are getting a string, then do an explicit decode
        # else, just call the unicode method of the object
        if type(obj) in [str, basestring]:  # noqa
            return unicode(obj, 'utf-8')  # noqa
        else:
            return unicode(obj)  # noqa
    else:
        return str(obj)
