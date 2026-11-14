import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.backlinks import build_backlink_graph

class TestBacklinks(unittest.TestCase):
    def test_backlink_graph(self):
        os.makedirs("tests/temp_docs", exist_ok=True)
        with open("tests/temp_docs/A.md", "w", encoding="utf-8") as f:
            f.write("Linking to [[B]]")
        with open("tests/temp_docs/B.md", "w", encoding="utf-8") as f:
            f.write("Note B content")

        graph = build_backlink_graph("tests/temp_docs")
        self.assertIn("A", graph["B"])

        os.remove("tests/temp_docs/A.md")
        os.remove("tests/temp_docs/B.md")
        os.rmdir("tests/temp_docs")

if __name__ == '__main__':
    unittest.main()