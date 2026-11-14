import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.wikilinks import transform_wikilinks

class TestWikilinks(unittest.TestCase):
    def test_standard_wikilink(self):
        self.assertEqual(transform_wikilinks('[[My Note]]'), '[My Note](My Note.md)')

    def test_aliased_wikilink(self):
        self.assertEqual(transform_wikilinks('[[My Note|Custom Label]]'), '[Custom Label](My Note.md)')

    def test_image_embed(self):
        self.assertEqual(transform_wikilinks('![[photo.png]]'), '![photo.png](photo.png)')

if __name__ == '__main__':
    unittest.main()

