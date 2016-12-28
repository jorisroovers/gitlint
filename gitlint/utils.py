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


def sstr(obj):
    """ Python 2 and 3 utility method that converts an obj to a utf-8 encoded string in python 2
    and to unicode in python 3.
    Especially useful for implementing __str__ methods in python 2: http://stackoverflow.com/a/1307210/381010"""
    if sys.version_info[0] == 2:
        return unicode(obj).encode('utf-8')
    else:
        return unicode(obj)
