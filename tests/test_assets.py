import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.assets import copy_static_assets

class TestAssets(unittest.TestCase):
    def test_copy_assets(self):
        os.makedirs("tests/temp_src", exist_ok=True)
        with open("tests/temp_src/test.png", "w") as f:
            f.write("img")

        result = copy_static_assets("tests/temp_src", "tests/temp_dist")
        self.assertTrue(result)
        self.assertTrue(os.path.exists("tests/temp_dist/test.png"))

        os.remove("tests/temp_src/test.png")
        os.remove("tests/temp_dist/test.png")
        os.rmdir("tests/temp_src")
        os.rmdir("tests/temp_dist")

if __name__ == '__main__':
    unittest.main()