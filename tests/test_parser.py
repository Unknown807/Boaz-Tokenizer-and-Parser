import sys
sys.path.append("..")

import myparser
from exceptions import ParserException, ParserSemanticException

import unittest
from unittest.mock import patch

class MockTokenizer:
    CURRENT_PARSE_TEST = -1
    CURRENT_TOKEN = -1

    # syntax test tokens

    # semantic test tokens

    # undeclared left var in assign
    SEM1 = [('KEYWORD', 'program'), ('IDENTIFIER', 'example'),('KEYWORD', 'begin'), ('IDENTIFIER', 'sum'),('SYMBOL', ':='), ('INT_CONST', '0'),('SYMBOL', ';'), ('KEYWORD', 'end')]

    # undeclared right var inassign
    SEM2 = [('KEYWORD', 'program'), ('IDENTIFIER', 'example'), ('KEYWORD', 'int'), ('IDENTIFIER', 'sum'), ('SYMBOL', ';'), ('KEYWORD', 'begin'), ('IDENTIFIER', 'sum'), ('SYMBOL', ':='), ('IDENTIFIER', 'num'), ('SYMBOL', ';'), ('KEYWORD', 'end')]

    # boolean assignment error
    SEM3 = [('KEYWORD', 'program'), ('IDENTIFIER', 'example'), ('KEYWORD', 'int'), ('IDENTIFIER', 'sum'), ('SYMBOL', ';'), ('KEYWORD', 'begin'), ('IDENTIFIER', 'sum'), ('SYMBOL', ':='), ('IDENTIFIER', 'sum'), ('SYMBOL', '<'), ('INT_CONST', '2'), ('SYMBOL', ';'), ('KEYWORD', 'end')]

    # char in while statement
    SEM4 = [('KEYWORD', 'program'), ('IDENTIFIER', 'example'), ('KEYWORD', 'char'), ('IDENTIFIER', 'ch'), ('SYMBOL', ';'), ('KEYWORD', 'begin'), ('KEYWORD', 'while'), ('IDENTIFIER', 'ch'), ('SYMBOL', '+'), ('CHAR_CONST', '"z"'), ('KEYWORD', 'do'), ('KEYWORD', 'od'), ('SYMBOL', ';'), ('KEYWORD', 'end')]

    # char in if statement
    SEM5 = [('KEYWORD', 'program'), ('IDENTIFIER', 'example'), ('KEYWORD', 'char'), ('IDENTIFIER', 'ch'), ('SYMBOL', ';'), ('KEYWORD', 'begin'), ('KEYWORD', 'if'), ('IDENTIFIER', 'ch'), ('SYMBOL', '+'), ('CHAR_CONST', '"c"'), ('KEYWORD', 'then'), ('KEYWORD', 'else'), ('KEYWORD', 'fi'), ('SYMBOL', ';'), ('KEYWORD', 'end')]

    # int in while statement
    SEM6 = [('KEYWORD', 'program'), ('IDENTIFIER', 'example'),('KEYWORD', 'int'), ('IDENTIFIER', 'num'),('SYMBOL', ';'), ('KEYWORD', 'begin'), ('KEYWORD', 'while'), ('IDENTIFIER', 'num'), ('SYMBOL', '/'), ('INT_CONST', '2'), ('KEYWORD', 'do'), ('KEYWORD', 'od'), ('SYMBOL', ';'), ('KEYWORD', 'end')]

    # int in if statement
    SEM7 = [('KEYWORD', 'program'), ('IDENTIFIER', 'example'), ('KEYWORD', 'int'), ('IDENTIFIER', 'num'), ('SYMBOL', ';'), ('KEYWORD', 'begin'), ('KEYWORD', 'if'), ('IDENTIFIER', 'num'), ('SYMBOL', '*'), ('INT_CONST', '2'), ('KEYWORD', 'then'), ('KEYWORD', 'else'), ('KEYWORD', 'fi'), ('SYMBOL', ';'), ('KEYWORD', 'end')]

    ALL_TOKENS = [
        SEM1, SEM2, SEM3, SEM4, SEM5,
        SEM6, SEM7
    ]

    @classmethod
    def get_next_token(cls):
        cls.CURRENT_TOKEN += 1
        return cls.ALL_TOKENS[cls.CURRENT_PARSE_TEST][cls.CURRENT_TOKEN]
        
class TestParser(unittest.TestCase):
    '''
    Tests as exhaustively as possible the parser against the
    different grammar and semantic structures in the boaz
    language
    '''

    test1list = [("KEYWORD", "program")]

    def setUp(self):
        self.parser = myparser.Parser
        self.parser.SYMBOL_TABLE = {}
        MockTokenizer.CURRENT_TOKEN = -1

    #tests for semantic analysis

    @patch.object(myparser.Tokenizer, "get_next_token", side_effect=MockTokenizer.get_next_token)
    def test_semantics_undeclared_left_var_assign(self, _):
        MockTokenizer.CURRENT_PARSE_TEST = 0
        self.assertRaises(ParserSemanticException, self.parser.parse)
    
    @patch.object(myparser.Tokenizer, "get_next_token", side_effect=MockTokenizer.get_next_token)
    def test_semantics_undeclared_right_var_assign(self, _):
        MockTokenizer.CURRENT_PARSE_TEST = 1
        self.assertRaises(ParserSemanticException, self.parser.parse)
    
    @patch.object(myparser.Tokenizer, "get_next_token", side_effect=MockTokenizer.get_next_token)
    def test_semantics_boolean_assignment(self, _):
        MockTokenizer.CURRENT_PARSE_TEST = 2
        self.assertRaises(ParserSemanticException, self.parser.parse)

    @patch.object(myparser.Tokenizer, "get_next_token", side_effect=MockTokenizer.get_next_token)
    def test_semantics_char_type_in_while(self, _):
        MockTokenizer.CURRENT_PARSE_TEST = 3
        self.assertRaises(ParserSemanticException, self.parser.parse)
    
    @patch.object(myparser.Tokenizer, "get_next_token", side_effect=MockTokenizer.get_next_token)
    def test_semantics_char_type_in_if(self, _):
        MockTokenizer.CURRENT_PARSE_TEST = 4
        self.assertRaises(ParserSemanticException, self.parser.parse)

    @patch.object(myparser.Tokenizer, "get_next_token", side_effect=MockTokenizer.get_next_token)
    def test_semantics_int_type_in_while(self, _):
        MockTokenizer.CURRENT_PARSE_TEST = 5
        self.assertRaises(ParserSemanticException, self.parser.parse)
    
    @patch.object(myparser.Tokenizer, "get_next_token", side_effect=MockTokenizer.get_next_token)
    def test_semantics_int_type_in_if(self, _):
        MockTokenizer.CURRENT_PARSE_TEST = 6
        self.assertRaises(ParserSemanticException, self.parser.parse)
    
    #tests for syntax analysis