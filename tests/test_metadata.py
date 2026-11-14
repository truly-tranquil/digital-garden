import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.metadata import parse_markdown_file

class TestMetadata(unittest.TestCase):
    def test_parse_markdown_file(self):
        test_file = os.path.join("tests", "temp_test_note.md")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("---\ntitle: Test Note\nstage: seedling\ntags: [test]\n---\n# Content")

        meta, content = parse_markdown_file(test_file)
        self.assertEqual(meta["title"], "Test Note")
        self.assertEqual(meta["stage"], "seedling")
        self.assertEqual(content.strip(), "# Content")

        if os.path.exists(test_file):
            os.remove(test_file)

if __name__ == '__main__':
    unittest.main()