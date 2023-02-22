import sys

if sys.version_info >= (3, 8):
    from importlib import metadata  # pragma: nocover
else:
    import importlib_metadata as metadata  # pragma: nocover

__version__ = metadata.version("gitlint-core")
