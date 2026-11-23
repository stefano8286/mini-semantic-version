# mini-semantic-version

Parses SemVer 2.0 version strings into major, minor, patch, prerelease, and build components.

```python
from mini_semantic_version import parse

v = parse("1.0.0-rc.1+exp.sha.5114f85")
assert v.major == 1
assert v.minor == 0
assert v.patch == 0
assert v.prerelease == ("rc", "1")
assert v.build == ("exp", "sha", "5114f85")
assert v.prerelease_string == "rc.1"
assert v.build_string == "exp.sha.5114f85"
assert str(v) == "1.0.0-rc.1+exp.sha.5114f85"
```

`parse` raises `ValueError` for anything that is not a valid SemVer 2.0 string, and `TypeError` for non-string input.

The exported names are `parse`, `Version`, `Version.prerelease_string`, and `Version.build_string`.

## Why this exists

SemVer strings show up everywhere, and most projects either hand-roll a regex that gets the leading-zero rule wrong or pull in a full version-comparison library when all they need is to read the components. This library does exactly one thing: it turns a string into the five fields the spec defines, and nothing else.

It deliberately does **not** implement precedence (the ordering rules in SemVer 2.0 §11) or range matching. Those are separate problems with their own edge cases, and mixing them into a parser is how you end up with a comparator that orders prereleases by two conflicting rules. If you need ordering, build it on top of the parsed fields.

## The awkward edge

Build metadata participates in equality here. SemVer 2.0 says build metadata is ignored when determining precedence, so `1.0.0+a` and `1.0.0+b` have the same precedence — but this library is not a precedence comparator. `Version` is a frozen dataclass, so `parse("1.0.0+a") != parse("1.0.0+b")`. If you want precedence semantics, compare the first three fields and the prerelease tuple yourself; the parser gives you those directly.

The other edge most parsers get wrong is leading zeroes. `1.2.03` is rejected, and so is `1.0.0-01`, because a purely numeric prerelease identifier may not have a leading zero. `1.0.0-01a` is accepted, because it contains a letter and is therefore an alphanumeric identifier, not a numeric one.

## Running the tests

```
PYTHONPATH=src python -m unittest discover -s tests
```
