import unittest

from mini_semantic_version import Version, parse


class ParseTests(unittest.TestCase):
    def test_plain_version(self):
        v = parse("1.2.3")
        self.assertEqual((v.major, v.minor, v.patch), (1, 2, 3))
        self.assertEqual(v.prerelease, ())
        self.assertEqual(v.build, ())
        self.assertIsNone(v.prerelease_string)
        self.assertIsNone(v.build_string)

    def test_zero_components(self):
        v = parse("0.0.0")
        self.assertEqual((v.major, v.minor, v.patch), (0, 0, 0))

    def test_large_numbers(self):
        v = parse("1234567890.0.42")
        self.assertEqual(v.major, 1234567890)
        self.assertEqual(v.patch, 42)

    def test_prerelease_only(self):
        v = parse("1.0.0-alpha.1")
        self.assertEqual(v.prerelease, ("alpha", "1"))
        self.assertEqual(v.build, ())
        self.assertEqual(v.prerelease_string, "alpha.1")

    def test_build_only(self):
        v = parse("1.0.0+build.5")
        self.assertEqual(v.prerelease, ())
        self.assertEqual(v.build, ("build", "5"))
        self.assertEqual(v.build_string, "build.5")

    def test_prerelease_and_build(self):
        v = parse("1.0.0-rc.1+exp.sha.5114f85")
        self.assertEqual(v.prerelease, ("rc", "1"))
        self.assertEqual(v.build, ("exp", "sha", "5114f85"))

    def test_hyphenated_prerelease(self):
        v = parse("1.0.0-x-y-z.--")
        self.assertEqual(v.prerelease, ("x-y-z", "--"))

    def test_numeric_prerelease_identifier(self):
        v = parse("1.0.0-0")
        self.assertEqual(v.prerelease, ("0",))

    def test_leading_zero_in_prerelease_numeric_is_rejected(self):
        with self.assertRaises(ValueError):
            parse("1.0.0-01")

    def test_alphanumeric_prerelease_with_leading_zero_is_allowed(self):
        # "01a" contains a letter, so it is an alphanumeric identifier and
        # the leading-zero rule does not apply.
        v = parse("1.0.0-01a")
        self.assertEqual(v.prerelease, ("01a",))

    def test_str_round_trip(self):
        for text in ("1.2.3", "1.0.0-alpha.1", "1.0.0+build.5", "1.0.0-rc.1+exp.sha.5114f85"):
            self.assertEqual(str(parse(text)), text)


class RejectionTests(unittest.TestCase):
    def test_missing_patch(self):
        with self.assertRaises(ValueError):
            parse("1.2")

    def test_leading_zero_in_major(self):
        with self.assertRaises(ValueError):
            parse("01.2.3")

    def test_leading_zero_in_minor(self):
        with self.assertRaises(ValueError):
            parse("1.02.3")

    def test_leading_zero_in_patch(self):
        with self.assertRaises(ValueError):
            parse("1.2.03")

    def test_empty_prerelease(self):
        with self.assertRaises(ValueError):
            parse("1.0.0-")

    def test_empty_build(self):
        with self.assertRaises(ValueError):
            parse("1.0.0+")

    def test_empty_prerelease_identifier(self):
        with self.assertRaises(ValueError):
            parse("1.0.0-alpha..1")

    def test_empty_build_identifier(self):
        with self.assertRaises(ValueError):
            parse("1.0.0+build..5")

    def test_trailing_newline(self):
        with self.assertRaises(ValueError):
            parse("1.2.3\n")

    def test_non_string_input_raises_type_error(self):
        with self.assertRaises(TypeError):
            parse(123)  # type: ignore[arg-type]


class EqualityTests(unittest.TestCase):
    def test_equal_versions_compare_equal(self):
        self.assertEqual(parse("1.2.3-alpha+build"), parse("1.2.3-alpha+build"))

    def test_build_metadata_participates_in_equality(self):
        # The dataclass is frozen and compares every field. SemVer 2.0 says
        # build metadata is ignored for precedence, but this library does
        # not implement precedence; equality is structural.
        self.assertNotEqual(parse("1.2.3+a"), parse("1.2.3+b"))

    def test_version_is_hashable(self):
        s = {parse("1.2.3"), parse("1.2.3")}
        self.assertEqual(len(s), 1)


if __name__ == "__main__":
    unittest.main()
