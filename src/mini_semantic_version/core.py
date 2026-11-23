"""Core SemVer 2.0 parsing logic.

SemVer 2.0 is specified at https://semver.org. This module implements the
parser described there without pulling in any third-party dependency.

The grammar is small enough that a single compiled regular expression is
both faster and easier to audit than a hand-written state machine. The
regex is anchored with ``\\A`` and ``\\Z`` so that trailing newlines or
other junk cannot slip through ``re.match``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional, Tuple


# SemVer 2.0 grammar. The numeric identifiers forbid leading zeroes, which
# is the rule most naive parsers miss (``01`` is not a valid major version,
# but ``0`` is).
_SEMVER_RE = re.compile(
    r"\A"
    r"(?P<major>0|[1-9]\d*)"
    r"\."
    r"(?P<minor>0|[1-9]\d*)"
    r"\."
    r"(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*))?"
    r"(?:\+(?P<build>[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"\Z"
)


@dataclass(frozen=True)
class Version:
    """A parsed SemVer 2.0 version.

    ``prerelease`` and ``build`` are tuples of the dot-separated identifiers
    rather than the raw strings. Splitting once at parse time means callers
    that need to compare or inspect identifiers do not have to re-split and
    risk subtle mistakes (for example, treating ``""`` as one identifier).
    """

    major: int
    minor: int
    patch: int
    prerelease: Tuple[str, ...] = ()
    build: Tuple[str, ...] = ()

    @property
    def prerelease_string(self) -> Optional[str]:
        """The prerelease joined back into its canonical dotted form.

        Returns ``None`` when there is no prerelease, which is distinct from
        the empty string: ``1.0.0-`` is not a valid version, so an empty
        string could only ever be a caller error.
        """
        if not self.prerelease:
            return None
        return ".".join(self.prerelease)

    @property
    def build_string(self) -> Optional[str]:
        """The build metadata joined back into its canonical dotted form."""
        if not self.build:
            return None
        return ".".join(self.build)

    def __str__(self) -> str:
        """Render back to a SemVer 2.0 string.

        This is not round-trip identical for inputs with leading zeroes in
        prerelease identifiers, because those are rejected at parse time.
        """
        out = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            out += "-" + ".".join(self.prerelease)
        if self.build:
            out += "+" + ".".join(self.build)
        return out


def parse(text: str) -> Version:
    """Parse a SemVer 2.0 version string into a :class:`Version`.

    Raises :class:`ValueError` if ``text`` is not a valid SemVer 2.0 string.
    The error message names the offending input so callers can surface it
    without reaching into the exception's arguments.
    """
    if not isinstance(text, str):
        raise TypeError(f"expected str, got {type(text).__name__}")

    match = _SEMVER_RE.match(text)
    if match is None:
        raise ValueError(f"invalid semantic version: {text!r}")

    prerelease_raw = match.group("prerelease")
    build_raw = match.group("build")

    return Version(
        major=int(match.group("major")),
        minor=int(match.group("minor")),
        patch=int(match.group("patch")),
        prerelease=tuple(prerelease_raw.split(".")) if prerelease_raw else (),
        build=tuple(build_raw.split(".")) if build_raw else (),
    )
