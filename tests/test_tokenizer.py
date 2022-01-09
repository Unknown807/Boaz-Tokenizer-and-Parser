import io
import sys
sys.path.append("..")

from tokenizer import Tokenizer
from exceptions import TokenizeException
from pathlib import Path
import unittest

BOAZ_DIR = Path(__file__).parent
BOAZ_DIR = BOAZ_DIR.parent / "boazfiles"

class TestTokenizer(unittest.TestCase):

    def read_boaz_file_and_set_tokenizer_code(self, filename):
        with open(BOAZ_DIR / (filename+".boaz")) as f:
            self.tokenizer.CODE = f.read()

    def setUp(self):
        self.tokenizer = Tokenizer
        self.tokenizer.CODE = None
        self.tokenizer.TOKENS = []
        self.tokenizer.CURRENT_TOKEN = 0

    def test_error_when_incorrect_int_const(self):

        self.read_boaz_file_and_set_tokenizer_code("incorrect_int_const")
        self.assertRaises(TokenizeException, self.tokenizer.tokenize)

    def test_error_when_incorrect_char_const(self):

        self.read_boaz_file_and_set_tokenizer_code("incorrect_char_const")
        self.assertRaises(TokenizeException, self.tokenizer.tokenize)

    def test_error_when_untokenizable_char(self):

        self.read_boaz_file_and_set_tokenizer_code("untokenizable")
        self.assertRaises(TokenizeException, self.tokenizer.tokenize)

    def test_success_tokenizing_empty_file(self):
        
        self.read_boaz_file_and_set_tokenizer_code("empty")
        self.assertEqual(self.tokenizer.TOKENS, [])

    def test_sucess_tokenizing_simple_file(self):
        
        self.read_boaz_file_and_set_tokenizer_code("simple")
        self.tokenizer.tokenize()
        self.assertEqual(len(self.tokenizer.TOKENS), 4)

    def test_success_tokenizing_all_legal_syntax(self):

        self.read_boaz_file_and_set_tokenizer_code("all_legal_syntax")
        self.tokenizer.tokenize()
        self.assertGreaterEqual(len(self.tokenizer.TOKENS), 1)

if __name__ == "__main__":
    unittest.main()