from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from orbit_notes import parse_note


class ParserTests(unittest.TestCase):
    def test_parses_synthetic_note(self) -> None:
        self.assertEqual(
            parse_note("Launch: verify the fictional fixture"),
            {"title": "Launch", "body": "verify the fictional fixture", "word_count": 4},
        )

    def test_rejects_missing_separator(self) -> None:
        with self.assertRaises(ValueError):
            parse_note("not a structured note")


if __name__ == "__main__":
    unittest.main()
