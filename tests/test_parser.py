import sys
sys.path.append("..")

import myparser
from exceptions import ParserException, ParserSemanticException
from pathlib import Path

import unittest
from unittest.mock import patch

BOAZ_DIR = Path(__file__).parent
BOAZ_DIR = BOAZ_DIR.parent / "boazfiles"

class MockTokenizer:
    CURRENT_PARSE_TEST = -1
    CURRENT_TOKEN = 0

    @classmethod
    def get_next_token(cls):
        return (cls.CURRENT_PARSE_TEST, cls.CURRENT_TOKEN)
        

class TestParser(unittest.TestCase):
    '''
    Tests as exhaustively as possible the parser against the
    different grammar and semantic structures in the boaz
    language
    '''

    test1list = [("KEYWORD", "program")]

    def read_boaz_file_and_set_tokenizer_code(self, filename):
        with open(BOAZ_DIR / (filename+".boaz")) as f:
            self.tokenizer.CODE = f.read()

    def setUp(self):
        self.parser = myparser.Parser
        self.parser.SYMBOL_TABLE = {}

        MockTokenizer
        MockTokenizer.CURRENT_TOKEN = 0
        MockTokenizer.CURRENT_PARSE_TEST+=1
    

    @patch.object(myparser.Tokenizer, "get_next_token", side_effect=MockTokenizer.get_next_token)
    def test_parser_mock(self, _):
        self.parser.parse()
        