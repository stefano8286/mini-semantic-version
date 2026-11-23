"""mini-semantic-version: a small SemVer 2.0 parser.

Only the standard library is used. The public API is intentionally tiny:
``parse`` and the ``Version`` data class it returns.
"""

from .core import Version, parse

__all__ = ["Version", "parse"]
