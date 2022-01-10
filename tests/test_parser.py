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

    # missing 'program' keyword
    SYN1 = [('IDENTIFIER', 'example'), ('KEYWORD', 'char'), ('IDENTIFIER', 'ch'), ('SYMBOL', ';'), ('KEYWORD', 'begin'), ('KEYWORD', 'end')]

    # missing identifier after program
    SYN2 = [('KEYWORD', 'program'), ('KEYWORD', 'char'), ('IDENTIFIER', 'ch'), ('SYMBOL', ';'), ('KEYWORD', 'begin'), ('KEYWORD', 'end')]

    # missing 'end' keyword
    SYN3 = [('KEYWORD', 'program'), ('IDENTIFIER', 'example'), ('KEYWORD', 'char'), ('IDENTIFIER', 'ch'), ('SYMBOL', ';'),('KEYWORD', 'begin')]

    # missing 'begin' keyword
    SYN4 = [('KEYWORD', 'program'), ('IDENTIFIER', 'example'), ('KEYWORD', 'char'), ('IDENTIFIER', 'ch'), ('SYMBOL', ';'), ('KEYWORD', 'end')]

    # incorrect vardec type (not int or char)
    SYN5 = [('KEYWORD', 'program'), ('IDENTIFIER', 'example'), ('IDENTIFIER', 'charr'), ('IDENTIFIER', 'ch'), ('SYMBOL', ';'), ('KEYWORD', 'begin'), ('KEYWORD', 'end')]

    # single and multiple vardecs
    SYN6 = [('KEYWORD', 'program'), ('IDENTIFIER', 'example'), ('KEYWORD', 'char'), ('IDENTIFIER', 'chr'), ('SYMBOL', ';'), ('KEYWORD', 'int'), ('IDENTIFIER', 'num'), ('SYMBOL', ';'), ('KEYWORD', 'int'), ('IDENTIFIER', 'n1'), ('SYMBOL', ','), ('IDENTIFIER', 'n2'), ('SYMBOL', ','), ('IDENTIFIER', 'n3'), ('SYMBOL', ','), ('IDENTIFIER', 'n4'), ('SYMBOL', ','), ('IDENTIFIER', 'n5'), ('SYMBOL', ','), ('IDENTIFIER', 'n6'), ('SYMBOL', ';'), ('KEYWORD', 'char'), ('IDENTIFIER', 'ch1'), ('SYMBOL', ','), ('IDENTIFIER', 'ch2'), ('SYMBOL', ';'), ('KEYWORD', 'begin'), ('KEYWORD', 'end')]

    # incorrect var dec syntax
    SYN7 = [('KEYWORD', 'program'), ('IDENTIFIER', 'example'), ('KEYWORD', 'char'), ('IDENTIFIER', 'chr'), ('SYMBOL', ';'), ('KEYWORD', 'int'), ('IDENTIFIER', 'num'), ('SYMBOL', ';'), ('KEYWORD', 'int'), ('IDENTIFIER', 'n1'), ('SYMBOL', ','), ('IDENTIFIER', 'n2'), ('SYMBOL', ','), ('IDENTIFIER', 'n3'), ('SYMBOL', ','), ('INT_CONST', '100'), ('SYMBOL', ','), ('IDENTIFIER', 'n5'), ('SYMBOL', ','), ('IDENTIFIER', 'n6'), ('SYMBOL', ';'), ('KEYWORD', 'char'), ('IDENTIFIER', 'ch1'), ('SYMBOL', ','), ('IDENTIFIER', 'ch2'), ('SYMBOL', ';'), ('KEYWORD', 'begin'), ('KEYWORD', 'end')]

    # incorrect symbol instead of ':=' in assignment
    SYN8 = [('KEYWORD', 'program'), ('IDENTIFIER', 'example'), ('KEYWORD', 'char'), ('IDENTIFIER', 'chr'), ('SYMBOL', ';'), ('KEYWORD', 'begin'), ('IDENTIFIER', 'chr'), ('SYMBOL', ':='), ('SYMBOL', '='), ('CHAR_CONST', '"a"'), ('SYMBOL', ';'), ('KEYWORD', 'end')]

    # really long expression in assignment, no spaces
    SYN9 = [('KEYWORD', 'program'), ('IDENTIFIER', 'example'), ('KEYWORD', 'int'), ('IDENTIFIER', 'num'), ('SYMBOL', ';'), ('KEYWORD', 'begin'), ('IDENTIFIER', 'num'), ('SYMBOL', ':='), ('SYMBOL', '('), ('IDENTIFIER', 'num'), ('SYMBOL', '+'), ('IDENTIFIER', 'num'), ('SYMBOL', ')'), ('SYMBOL', '*'), ('INT_CONST', '2'), ('SYMBOL', '/'), ('INT_CONST', '4'), ('SYMBOL', '*'), ('INT_CONST', '0'), ('SYMBOL', '*'), ('INT_CONST', '0'), ('SYMBOL', '*'), ('IDENTIFIER', 'num'), ('SYMBOL', '-'), ('IDENTIFIER', 'num'), ('SYMBOL', '-'), ('IDENTIFIER', 'num'), ('SYMBOL', '-'), ('SYMBOL', '-'), ('SYMBOL', '-'), ('INT_CONST', '3'), ('SYMBOL', ';'), ('KEYWORD', 'end')]

    # random comma in an expression
    SYN10 = [('KEYWORD', 'program'), ('IDENTIFIER', 'example'), ('KEYWORD', 'int'), ('IDENTIFIER', 'num'), ('SYMBOL', ';'), ('KEYWORD', 'begin'), ('IDENTIFIER', 'num'), ('SYMBOL', ':='), ('SYMBOL', '('), ('IDENTIFIER', 'num'), ('SYMBOL', '+'), ('IDENTIFIER', 'num'), ('SYMBOL', ')'), ('SYMBOL', '*'), ('INT_CONST', '2'), ('SYMBOL', '/'), ('INT_CONST', '4'), ('SYMBOL', '*'), ('INT_CONST', '0'), ('SYMBOL', '*'), ('INT_CONST', '0'), ('SYMBOL', '*'), ('IDENTIFIER', 'num'), ('SYMBOL', '-'), ('IDENTIFIER', 'num'), ('SYMBOL', '-'), ('IDENTIFIER', 'num'), ('SYMBOL', '-'), ('SYMBOL', ','), ('SYMBOL', '-'), ('SYMBOL', '-'), ('INT_CONST', '3'), ('SYMBOL', ';'), ('KEYWORD', 'end')]

    # multiple unary operators followed by term, no spaces
    SYN11 = [('KEYWORD', 'program'), ('IDENTIFIER', 'example'), ('KEYWORD', 'int'), ('IDENTIFIER', 'num'), ('SYMBOL', ';'), ('KEYWORD', 'begin'), ('IDENTIFIER', 'num'), ('SYMBOL', ':='), ('IDENTIFIER', 'num'), ('SYMBOL', '-'), ('SYMBOL', '-'), ('SYMBOL', '-'), ('SYMBOL', '-'), ('SYMBOL', '-'), ('SYMBOL', '-'), ('SYMBOL', '-'), ('SYMBOL', '-'), ('SYMBOL', '-'), ('INT_CONST', '10'), ('SYMBOL', ';'), ('KEYWORD', 'end')]

    # really long expression in while, no spaces
    SYN12 = [('KEYWORD', 'program'), ('IDENTIFIER', 'example'), ('KEYWORD', 'int'), ('IDENTIFIER', 'num'), ('SYMBOL', ';'), ('KEYWORD', 'begin'), ('KEYWORD', 'while'), ('IDENTIFIER', 'num'), ('SYMBOL', '-'), ('SYMBOL', '-'), ('SYMBOL', '-'), ('SYMBOL', '-'), ('SYMBOL', '-'), ('SYMBOL', '-'), ('SYMBOL', '-'), ('SYMBOL', '-'), ('SYMBOL', '-'), ('SYMBOL', '-'), ('SYMBOL', '!'), ('SYMBOL', '!'), ('SYMBOL', '!'), ('SYMBOL', '!'), ('SYMBOL', '!'), ('SYMBOL', '!'), ('SYMBOL', '!'), ('SYMBOL', '!'), ('SYMBOL', '-'), ('SYMBOL', '-'), ('SYMBOL', '-'), ('SYMBOL', '-'), ('SYMBOL', '-'), ('SYMBOL', '-'), ('SYMBOL', '-'), ('SYMBOL', '!'), ('SYMBOL', '!'), ('SYMBOL', '!'), ('SYMBOL', '!'), ('SYMBOL', '!'), ('INT_CONST', '10'), ('SYMBOL', '+'), ('INT_CONST', '100'), ('SYMBOL', '/'), ('SYMBOL', '('), ('IDENTIFIER', 'num'), ('SYMBOL', '&'), ('INT_CONST', '6'), ('SYMBOL', ')'), ('KEYWORD', 'do'), ('KEYWORD', 'od'), ('SYMBOL', ';'), ('KEYWORD', 'end')]

    # really long expression in if, no spaces
    SYN13 = [('KEYWORD', 'program'), ('IDENTIFIER', 'example'), ('KEYWORD', 'int'), ('IDENTIFIER', 'num'), ('SYMBOL', ';'), ('KEYWORD', 'begin'), ('KEYWORD', 'if'), ('IDENTIFIER', 'num'), ('SYMBOL', '-'), ('SYMBOL', '-'), ('SYMBOL', '-'), ('SYMBOL', '-'), ('SYMBOL', '-'), ('SYMBOL', '-'), ('SYMBOL', '-'), ('SYMBOL', '-'), ('SYMBOL', '!'), ('INT_CONST', '5'), ('SYMBOL', '|'), ('SYMBOL', '!'), ('INT_CONST', '4'), ('SYMBOL', '-'), ('SYMBOL', '-'), ('SYMBOL', '-'), ('SYMBOL', '-'), ('SYMBOL', '-'), ('SYMBOL', '-'), ('SYMBOL', '-'), ('SYMBOL', '-'), ('INT_CONST', '10'), ('SYMBOL', '+'), ('INT_CONST', '100'), ('SYMBOL', '/'), ('SYMBOL', '('), ('IDENTIFIER', 'num'), ('SYMBOL', '&'), ('INT_CONST', '6'), ('SYMBOL', ')'), ('KEYWORD', 'then'), ('KEYWORD', 'fi'), ('SYMBOL', ';'), ('KEYWORD', 'end')]

    # binary operation missing second operand
    SYN14 = [('KEYWORD', 'program'), ('IDENTIFIER', 'example'), ('KEYWORD', 'int'), ('IDENTIFIER', 'num'), ('SYMBOL', ';'), ('KEYWORD', 'begin'), ('IDENTIFIER', 'num'), ('SYMBOL', ':='), ('INT_CONST', '4'), ('SYMBOL', '+'), ('SYMBOL', ';'), ('KEYWORD', 'end')]

    # multiple binary operations followed by missing second operand
    SYN15 = [('KEYWORD', 'program'), ('IDENTIFIER', 'example'), ('KEYWORD', 'int'), ('IDENTIFIER', 'num'), ('SYMBOL', ';'), ('KEYWORD', 'begin'), ('IDENTIFIER', 'num'), ('SYMBOL', ':='), ('INT_CONST', '4'), ('SYMBOL', '+'), ('SYMBOL', '+'), ('SYMBOL', '+'), ('SYMBOL', '+'), ('SYMBOL', '+'), ('SYMBOL', '+'), ('SYMBOL', '+'), ('SYMBOL', '+'), ('SYMBOL', ';'), ('KEYWORD', 'end')]

    # expression missing semicolon at the end
    SYN16 = [('KEYWORD', 'program'), ('IDENTIFIER', 'example'), ('KEYWORD', 'int'), ('IDENTIFIER', 'num'), ('SYMBOL', ';'), ('KEYWORD', 'begin'), ('IDENTIFIER', 'num'), ('SYMBOL', ':='), ('INT_CONST', '4'), ('SYMBOL', '/'), ('INT_CONST', '5'), ('KEYWORD', 'end')]

    # empty while statement
    SYN17 = [('KEYWORD', 'program'), ('IDENTIFIER', 'example'), ('KEYWORD', 'begin'), ('KEYWORD', 'while'), ('INT_CONST', '1'), ('SYMBOL', '<'), ('INT_CONST', '1'), ('KEYWORD', 'do'), ('KEYWORD', 'od'), ('SYMBOL', ';'), ('KEYWORD', 'end')]

    # empty if statement, no else
    SYN18 = [('KEYWORD', 'program'), ('IDENTIFIER', 'example'), ('KEYWORD', 'begin'), ('KEYWORD', 'if'), ('INT_CONST', '1'), ('SYMBOL', '<'), ('INT_CONST', '1'), ('KEYWORD', 'then'), ('KEYWORD', 'fi'), ('SYMBOL', ';'), ('KEYWORD', 'end')]

    # empty if statement, with else
    SYN19 = [('KEYWORD', 'program'), ('IDENTIFIER', 'example'), ('KEYWORD', 'begin'), ('KEYWORD', 'if'), ('INT_CONST', '1'), ('SYMBOL', '<'), ('INT_CONST', '1'), ('KEYWORD', 'then'), ('KEYWORD', 'else'), ('KEYWORD', 'fi'), ('SYMBOL', ';'), ('KEYWORD', 'end')]

    # while statement missing do
    SYN20 = [('KEYWORD', 'program'), ('IDENTIFIER', 'example'), ('KEYWORD', 'begin'), ('KEYWORD', 'while'), ('INT_CONST', '1'), ('SYMBOL', '<'), ('INT_CONST', '1'), ('KEYWORD', 'od'), ('SYMBOL', ';'), ('KEYWORD', 'end')]

    # while statement missing od
    SYN21 = [('KEYWORD', 'program'), ('IDENTIFIER', 'example'), ('KEYWORD', 'begin'), ('KEYWORD', 'while'), ('INT_CONST', '1'), ('SYMBOL', '<'), ('INT_CONST', '1'), ('KEYWORD', 'do'), ('KEYWORD', 'end')]

    # if statement missing then
    SYN22 = [('KEYWORD', 'program'), ('IDENTIFIER', 'example'), ('KEYWORD', 'begin'), ('KEYWORD', 'if'), ('INT_CONST', '1'), ('SYMBOL', '<'), ('INT_CONST', '1'), ('KEYWORD', 'fi'), ('SYMBOL', ';'), ('KEYWORD', 'end')]

    # if statement missing fi
    SYN23 = [('KEYWORD', 'program'), ('IDENTIFIER', 'example'), ('KEYWORD', 'begin'), ('KEYWORD', 'if'), ('INT_CONST', '1'), ('SYMBOL', '<'), ('INT_CONST', '1'), ('KEYWORD', 'then'), ('KEYWORD', 'end')]

    # missing term for unary operator
    SYN24 = [('KEYWORD', 'program'), ('IDENTIFIER', 'example'), ('KEYWORD', 'begin'), ('KEYWORD', 'print'), ('SYMBOL', '!'), ('SYMBOL', ';'), ('KEYWORD', 'end')]

    # print statement missing expression
    SYN25 = [('KEYWORD', 'program'), ('IDENTIFIER', 'example'), ('KEYWORD', 'begin'), ('KEYWORD', 'print'), ('SYMBOL', ';'), ('KEYWORD', 'end')]

    # print statement with really long expression
    SYN26 = [('KEYWORD', 'program'), ('IDENTIFIER', 'example'), ('KEYWORD', 'begin'), ('KEYWORD', 'print'), ('INT_CONST', '1'), ('SYMBOL', '+'), ('INT_CONST', '1'), ('SYMBOL', '<'), ('SYMBOL', '('), ('INT_CONST', '1'), ('SYMBOL', '*'), ('INT_CONST', '7'), ('SYMBOL', '-'), ('SYMBOL', '('), ('INT_CONST', '1'), ('SYMBOL', '+'), ('INT_CONST', '1'), ('SYMBOL', ')'), ('SYMBOL', '/'), ('CHAR_CONST', '"a"'), ('SYMBOL', ')'), ('SYMBOL', '-'), ('CHAR_CONST', '"b"'), ('SYMBOL', '+'), ('CHAR_CONST', '"d"'), ('SYMBOL', '+'), ('CHAR_CONST', '"e"'), ('SYMBOL', ';'), ('KEYWORD', 'end')]

    # deep nested whiles and ifs
    SYN27 = [('KEYWORD', 'program'), ('IDENTIFIER', 'example'), ('KEYWORD', 'int'), ('IDENTIFIER', 'num'), ('SYMBOL', ','), ('IDENTIFIER', 'sum'), ('SYMBOL', ';'), ('KEYWORD', 'char'), ('IDENTIFIER', 'ch'), ('SYMBOL', ';'), ('KEYWORD', 'begin'), ('IDENTIFIER', 'sum'), ('SYMBOL', ':='), ('INT_CONST', '0'), ('SYMBOL', ';'), ('IDENTIFIER', 'num'), ('SYMBOL', ':='), ('INT_CONST', '1'), ('SYMBOL', ';'), ('IDENTIFIER', 'ch'), ('SYMBOL', ':='), ('CHAR_CONST', '"a"'), ('SYMBOL', ';'), ('KEYWORD', 'while'), ('IDENTIFIER', 'ch'), ('SYMBOL', '<'), ('CHAR_CONST', '"z"'), ('KEYWORD', 'do'), ('KEYWORD', 'if'), ('IDENTIFIER', 'num'), ('SYMBOL', '/'), ('INT_CONST', '3'), ('SYMBOL', '!='), ('INT_CONST', '0'), ('SYMBOL', '&'), ('IDENTIFIER', 'ch'), ('SYMBOL', '!='), ('CHAR_CONST', '"y"'), ('KEYWORD', 'then'), ('KEYWORD', 'if'), ('IDENTIFIER', 'num'), ('SYMBOL', '/'), ('INT_CONST', '3'), ('SYMBOL', '!='), ('INT_CONST', '0'), ('SYMBOL', '&'), ('IDENTIFIER', 'ch'), ('SYMBOL', '!='), ('CHAR_CONST', '"y"'), ('KEYWORD', 'then'), ('IDENTIFIER', 'sum'), ('SYMBOL', ':='), ('IDENTIFIER', 'sum'), ('SYMBOL', '+'), ('IDENTIFIER', 'num'), ('SYMBOL', '*'), ('INT_CONST', '2'), ('SYMBOL', ';'), ('IDENTIFIER', 'ch'), ('SYMBOL', ':='), ('IDENTIFIER', 'ch'), ('SYMBOL', '+'), ('INT_CONST', '1'), ('SYMBOL', ';'), ('KEYWORD', 'while'), ('CHAR_CONST', '"z"'), ('SYMBOL', '>'), ('IDENTIFIER', 'ch'), ('KEYWORD', 'do'), ('KEYWORD', 'print'), ('CHAR_CONST', '"a"'), ('SYMBOL', ';'), ('KEYWORD', 'if'), ('IDENTIFIER', 'num'), ('SYMBOL', '/'), ('INT_CONST', '3'), ('SYMBOL', '!='), ('INT_CONST', '0'), ('SYMBOL', '&'), ('IDENTIFIER', 'ch'), ('SYMBOL', '!='), ('CHAR_CONST', '"y"'), ('KEYWORD', 'then'), ('IDENTIFIER', 'ch'), ('SYMBOL', ':='), ('IDENTIFIER', 'ch'), ('SYMBOL', '+'), ('INT_CONST', '1'), ('SYMBOL', ';'), ('KEYWORD', 'fi'), ('SYMBOL', ';'), ('KEYWORD', 'if'), ('IDENTIFIER', 'num'), ('SYMBOL', '/'), ('INT_CONST', '3'), ('SYMBOL', '!='), ('INT_CONST', '0'), ('SYMBOL', '&'), ('IDENTIFIER', 'ch'), ('SYMBOL', '!='), ('CHAR_CONST', '"y"'), ('KEYWORD', 'then'), ('IDENTIFIER', 'ch'), ('SYMBOL', ':='), ('IDENTIFIER', 'ch'), ('SYMBOL', '+'), ('INT_CONST', '1'), ('SYMBOL', ';'), ('KEYWORD', 'fi'), ('SYMBOL', ';'), ('KEYWORD', 'od'), ('SYMBOL', ';'), ('KEYWORD', 'else'), ('IDENTIFIER', 'sum'), ('SYMBOL', ':='), ('IDENTIFIER', 'sum'), ('SYMBOL', '-'), ('IDENTIFIER', 'num'), ('SYMBOL', ';'), ('IDENTIFIER', 'ch'), ('SYMBOL', ':='), ('CHAR_CONST', '"m"'), ('SYMBOL', ';'), ('KEYWORD', 'while'), ('SYMBOL', '!'), ('CHAR_CONST', '"a"'), ('KEYWORD', 'do'), ('IDENTIFIER', 'num'), ('SYMBOL', ':='), ('INT_CONST', '1'), ('SYMBOL', ';'), ('KEYWORD', 'od'), ('SYMBOL', ';'), ('KEYWORD', 'fi'), ('SYMBOL', ';'), ('IDENTIFIER', 'sum'), ('SYMBOL', ':='), ('IDENTIFIER', 'sum'), ('SYMBOL', '+'), ('IDENTIFIER', 'num'), ('SYMBOL', '*'), ('INT_CONST', '2'), ('SYMBOL', ';'), ('IDENTIFIER', 'ch'), ('SYMBOL', ':='), ('IDENTIFIER', 'ch'), ('SYMBOL', '+'), ('INT_CONST', '1'), ('SYMBOL', ';'), ('KEYWORD', 'else'), ('IDENTIFIER', 'sum'), ('SYMBOL', ':='), ('IDENTIFIER', 'sum'), ('SYMBOL', '-'), ('IDENTIFIER', 'num'), ('SYMBOL', ';'), ('IDENTIFIER', 'ch'), ('SYMBOL', ':='), ('CHAR_CONST', '"m"'), ('SYMBOL', ';'), ('KEYWORD', 'fi'), ('SYMBOL', ';'), ('IDENTIFIER', 'num'), ('SYMBOL', ':='), ('IDENTIFIER', 'num'), ('SYMBOL', '+'), ('INT_CONST', '1'), ('SYMBOL', ';'), ('KEYWORD', 'od'), ('SYMBOL', ';'), ('KEYWORD', 'print'), ('IDENTIFIER', 'sum'), ('SYMBOL', ';'), ('KEYWORD', 'print'), ('IDENTIFIER', 'ch'), ('SYMBOL', ';'), ('KEYWORD', 'end')]

    # deep nested whiles and ifs, using no declared vars
    SYN28 = [('KEYWORD', 'program'), ('IDENTIFIER', 'example'), ('KEYWORD', 'begin'), ('KEYWORD', 'while'), ('INT_CONST', '1'), ('SYMBOL', '<'), ('CHAR_CONST', '"z"'), ('KEYWORD', 'do'), ('KEYWORD', 'if'), ('INT_CONST', '123'), ('SYMBOL', '/'), ('INT_CONST', '3'), ('SYMBOL', '!='), ('INT_CONST', '0'), ('SYMBOL', '&'), ('CHAR_CONST', '"b"'), ('SYMBOL', '!='), ('CHAR_CONST', '"y"'), ('KEYWORD', 'then'), ('KEYWORD', 'if'), ('INT_CONST', '123'), ('SYMBOL', '/'), ('INT_CONST', '3'), ('SYMBOL', '!='), ('INT_CONST', '0'), ('SYMBOL', '&'), ('CHAR_CONST', '"b"'), ('SYMBOL', '!='), ('CHAR_CONST', '"y"'), ('KEYWORD', 'then'), ('KEYWORD', 'while'), ('CHAR_CONST', '"z"'), ('SYMBOL', '>'), ('CHAR_CONST', '"b"'), ('KEYWORD', 'do'), ('KEYWORD', 'print'), ('CHAR_CONST', '"a"'), ('SYMBOL', ';'), ('KEYWORD', 'if'), ('SYMBOL', '-'), ('INT_CONST', '123'), ('SYMBOL', '/'), ('SYMBOL', '-'), ('INT_CONST', '3'), ('SYMBOL', '!='), ('INT_CONST', '0'), ('SYMBOL', '&'), ('CHAR_CONST', '"b"'), ('SYMBOL', '!='), ('CHAR_CONST', '"y"'), ('KEYWORD', 'then'), ('KEYWORD', 'fi'), ('SYMBOL', ';'), ('KEYWORD', 'if'), ('SYMBOL', '-'), ('INT_CONST', '123'), ('SYMBOL', '/'), ('SYMBOL', '-'), ('INT_CONST', '3'), ('SYMBOL', '!='), ('INT_CONST', '0'), ('SYMBOL', '&'), ('CHAR_CONST', '"b"'), ('SYMBOL', '!='), ('CHAR_CONST', '"y"'), ('KEYWORD', 'then'), ('KEYWORD', 'fi'), ('SYMBOL', ';'), ('KEYWORD', 'od'), ('SYMBOL', ';'), ('KEYWORD', 'else'), ('KEYWORD', 'while'), ('SYMBOL', '!'), ('CHAR_CONST', '"a"'), ('KEYWORD', 'do'), ('KEYWORD', 'od'), ('SYMBOL', ';'), ('KEYWORD', 'fi'), ('SYMBOL', ';'), ('KEYWORD', 'else'), ('KEYWORD', 'print'), ('SYMBOL', '-'), ('INT_CONST', '123'), ('SYMBOL', '-'), ('INT_CONST', '4'), ('SYMBOL', ';'), ('KEYWORD', 'fi'), ('SYMBOL', ';'), ('KEYWORD', 'od'), ('SYMBOL', ';'), ('KEYWORD', 'print'), ('SYMBOL', '-'), ('INT_CONST', '321'), ('SYMBOL', ';'), ('KEYWORD', 'print'), ('CHAR_CONST', '"b"'), ('SYMBOL', ';'), ('KEYWORD', 'end')]

    # one huge file with no spaces or newlines
    SYN29 = [('KEYWORD', 'program'), ('IDENTIFIER', 'example'), ('KEYWORD', 'int'), ('IDENTIFIER', 'num'), ('SYMBOL', ','), ('IDENTIFIER', 'sum'), ('SYMBOL', ';'), ('KEYWORD', 'char'), ('IDENTIFIER', 'ch'), ('SYMBOL', ';'), ('KEYWORD', 'begin'), ('IDENTIFIER', 'sum'), ('SYMBOL', ':='), ('INT_CONST', '0'), ('SYMBOL', ';'), ('IDENTIFIER', 'num'), ('SYMBOL', ':='), ('INT_CONST', '1'), ('SYMBOL', ';'), ('IDENTIFIER', 'ch'), ('SYMBOL', ':='), ('CHAR_CONST', '"a"'), ('SYMBOL', ';'), ('KEYWORD', 'while'), ('IDENTIFIER', 'ch'), ('SYMBOL', '<'), ('CHAR_CONST', '"z"'), ('KEYWORD', 'do'), ('KEYWORD', 'if'), ('IDENTIFIER', 'num'), ('SYMBOL', '/'), ('INT_CONST', '3'), ('SYMBOL', '!='), ('INT_CONST', '0'), ('SYMBOL', '&'), ('IDENTIFIER', 'ch'), ('SYMBOL', '!='), ('CHAR_CONST', '"y"'), ('KEYWORD', 'then'), ('KEYWORD', 'if'), ('IDENTIFIER', 'num'), ('SYMBOL', '/'), ('INT_CONST', '3'), ('SYMBOL', '!='), ('INT_CONST', '0'), ('SYMBOL', '&'), ('IDENTIFIER', 'ch'), ('SYMBOL', '!='), ('CHAR_CONST', '"y"'), ('KEYWORD', 'then'), ('IDENTIFIER', 'sum'), ('SYMBOL', ':='), ('IDENTIFIER', 'sum'), ('SYMBOL', '+'), ('IDENTIFIER', 'num'), ('SYMBOL', '*'), ('INT_CONST', '2'), ('SYMBOL', ';'), ('IDENTIFIER', 'ch'), ('SYMBOL', ':='), ('IDENTIFIER', 'ch'), ('SYMBOL', '+'), ('INT_CONST', '1'), ('SYMBOL', ';'), ('KEYWORD', 'while'), ('CHAR_CONST', '"z"'), ('SYMBOL', '>'), ('IDENTIFIER', 'ch'), ('KEYWORD', 'do'), ('KEYWORD', 'print'), ('CHAR_CONST', '"a"'), ('SYMBOL', ';'), ('KEYWORD', 'if'), ('IDENTIFIER', 'num'), ('SYMBOL', '/'), ('INT_CONST', '3'), ('SYMBOL', '!='), ('INT_CONST', '0'), ('SYMBOL', '&'), ('IDENTIFIER', 'ch'), ('SYMBOL', '!='), ('CHAR_CONST', '"y"'), ('KEYWORD', 'then'), ('IDENTIFIER', 'ch'), ('SYMBOL', ':='), ('IDENTIFIER', 'ch'), ('SYMBOL', '+'), ('INT_CONST', '1'), ('SYMBOL', ';'), ('KEYWORD', 'fi'), ('SYMBOL', ';'), ('KEYWORD', 'if'), ('IDENTIFIER', 'num'), ('SYMBOL', '/'), ('INT_CONST', '3'), ('SYMBOL', '!='), ('INT_CONST', '0'), ('SYMBOL', '&'), ('IDENTIFIER', 'ch'), ('SYMBOL', '!='), ('CHAR_CONST', '"y"'), ('KEYWORD', 'then'), ('IDENTIFIER', 'ch'), ('SYMBOL', ':='), ('IDENTIFIER', 'ch'), ('SYMBOL', '+'), ('INT_CONST', '1'), ('SYMBOL', ';'), ('KEYWORD', 'fi'), ('SYMBOL', ';'), ('KEYWORD', 'od'), ('SYMBOL', ';'), ('KEYWORD', 'else'), ('IDENTIFIER', 'sum'), ('SYMBOL', ':='), ('IDENTIFIER', 'sum'), ('SYMBOL', '-'), ('IDENTIFIER', 'num'), ('SYMBOL', ';'), ('IDENTIFIER', 'ch'), ('SYMBOL', ':='), ('CHAR_CONST', '"m"'), ('SYMBOL', ';'), ('KEYWORD', 'while'), ('SYMBOL', '!'), ('CHAR_CONST', '"a"'), ('KEYWORD', 'do'), ('IDENTIFIER', 'num'), ('SYMBOL', ':='), ('INT_CONST', '1'), ('SYMBOL', ';'), ('KEYWORD', 'od'), ('SYMBOL', ';'), ('KEYWORD', 'fi'), ('SYMBOL', ';'), ('IDENTIFIER', 'sum'), ('SYMBOL', ':='), ('IDENTIFIER', 'sum'), ('SYMBOL', '+'), ('IDENTIFIER', 'num'), ('SYMBOL', '*'), ('INT_CONST', '2'), ('SYMBOL', ';'), ('IDENTIFIER', 'ch'), ('SYMBOL', ':='), ('IDENTIFIER', 'ch'), ('SYMBOL', '+'), ('INT_CONST', '1'), ('SYMBOL', ';'), ('KEYWORD', 'else'), ('IDENTIFIER', 'sum'), ('SYMBOL', ':='), ('IDENTIFIER', 'sum'), ('SYMBOL', '-'), ('IDENTIFIER', 'num'), ('SYMBOL', ';'), ('IDENTIFIER', 'ch'), ('SYMBOL', ':='), ('CHAR_CONST', '"m"'), ('SYMBOL', ';'), ('KEYWORD', 'fi'), ('SYMBOL', ';'), ('IDENTIFIER', 'num'), ('SYMBOL', ':='), ('IDENTIFIER', 'num'), ('SYMBOL', '+'), ('INT_CONST', '1'), ('SYMBOL', ';'), ('KEYWORD', 'od'), ('SYMBOL', ';'), ('KEYWORD', 'print'), ('IDENTIFIER', 'sum'), ('SYMBOL', ';'), ('KEYWORD', 'print'), ('IDENTIFIER', 'ch'), ('SYMBOL', ';'), ('KEYWORD', 'end')]

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

    # random semicolon in an expression causes cut off var
    SEM8 = [('KEYWORD', 'program'), ('IDENTIFIER', 'example'), ('KEYWORD', 'int'), ('IDENTIFIER', 'num'), ('SYMBOL', ';'), ('KEYWORD', 'begin'), ('IDENTIFIER', 'num'), ('SYMBOL', ':='), ('SYMBOL', '('), ('IDENTIFIER', 'num'), ('SYMBOL', '+'), ('IDENTIFIER', 'num'), ('SYMBOL', ')'), ('SYMBOL', '*'), ('INT_CONST', '2'), ('SYMBOL', '/'), ('INT_CONST', '4'), ('SYMBOL', '*'), ('INT_CONST', '0'), ('SYMBOL', '*'), ('INT_CONST', '0'), ('SYMBOL', '*'), ('IDENTIFIER', 'num'), ('SYMBOL', '-'), ('IDENTIFIER', 'nu'), ('SYMBOL', ';'), ('IDENTIFIER', 'm'), ('SYMBOL', '-'), ('IDENTIFIER', 'num'), ('SYMBOL', '-'), ('SYMBOL', '-'), ('SYMBOL', '-'), ('INT_CONST', '3'), ('SYMBOL', ';'), ('KEYWORD', 'end')]

    ALL_TOKENS = [
        SEM1, SEM2, SEM3, SEM4, SEM5, SEM6, SEM7, SEM8, SYN1, SYN2, SYN3,
        SYN4, SYN5, SYN6, SYN7, SYN8, SYN9, SYN10, SYN11, SYN12,
        SYN13, SYN14, SYN15, SYN16, SYN17, SYN18, SYN19, SYN20,
        SYN21, SYN22, SYN23, SYN24, SYN25, SYN26, SYN27, SYN28,
        SYN29
    ]

    @classmethod
    def get_next_token(cls):
        cls.CURRENT_TOKEN += 1
        try:
            return cls.ALL_TOKENS[cls.CURRENT_PARSE_TEST][cls.CURRENT_TOKEN]
        except:
            # normally the tokenizer handles an eof error when trying
            # to get the next token 
            raise ParserException("MISSING", "MISSING")
        
class TestParser(unittest.TestCase):
    '''
    Tests as exhaustively as possible the parser against the
    different grammar and semantic structures in the boaz
    language
    '''

    def setUp(self):
        self.parser = myparser.Parser
        self.parser.SYMBOL_TABLE = {}

        self.patcher = patch.object(myparser.Tokenizer, "get_next_token", side_effect=MockTokenizer.get_next_token)
        self.patcher.start()
        MockTokenizer.CURRENT_TOKEN = -1

    def tearDown(self):
        self.patcher.stop()

    #tests for semantic analysis

    def test_semantics_undeclared_left_var_assign(self):
        MockTokenizer.CURRENT_PARSE_TEST = 0
        self.assertRaises(ParserSemanticException, self.parser.parse)
    
    def test_semantics_undeclared_right_var_assign(self):
        MockTokenizer.CURRENT_PARSE_TEST = 1
        self.assertRaises(ParserSemanticException, self.parser.parse)
    
    def test_semantics_boolean_assignment(self):
        MockTokenizer.CURRENT_PARSE_TEST = 2
        self.assertRaises(ParserSemanticException, self.parser.parse)

    def test_semantics_char_type_in_while(self):
        MockTokenizer.CURRENT_PARSE_TEST = 3
        self.assertRaises(ParserSemanticException, self.parser.parse)
    
    def test_semantics_char_type_in_if(self):
        MockTokenizer.CURRENT_PARSE_TEST = 4
        self.assertRaises(ParserSemanticException, self.parser.parse)

    def test_semantics_int_type_in_while(self):
        MockTokenizer.CURRENT_PARSE_TEST = 5
        self.assertRaises(ParserSemanticException, self.parser.parse)
    
    def test_semantics_int_type_in_if(self):
        MockTokenizer.CURRENT_PARSE_TEST = 6
        self.assertRaises(ParserSemanticException, self.parser.parse)
    
    def test_misplaced_semicolon_symbol(self):
        MockTokenizer.CURRENT_PARSE_TEST = 7
        self.assertRaises(ParserSemanticException, self.parser.parse)

    #tests for syntax analysis

    def test_missing_program_keyword(self):
        MockTokenizer.CURRENT_PARSE_TEST = 8
        self.assertRaises(ParserException, self.parser.parse)
    
    def test_missing_identifier_after_program(self):
        MockTokenizer.CURRENT_PARSE_TEST = 9
        self.assertRaises(ParserException, self.parser.parse)

    def test_missing_end_keyword(self):
        MockTokenizer.CURRENT_PARSE_TEST = 10
        self.assertRaises(ParserException, self.parser.parse)
    
    def test_missing_begin_keyword(self):
        MockTokenizer.CURRENT_PARSE_TEST = 11
        self.assertRaises(ParserException, self.parser.parse)

    def test_incorrect_var_declaration_type(self):
        MockTokenizer.CURRENT_PARSE_TEST = 12
        self.assertRaises(ParserException, self.parser.parse)
    
    def test_single_and_multiple_var_declaration(self):
        MockTokenizer.CURRENT_PARSE_TEST = 13
        self.parser.parse()
    
    def test_incorrect_var_declaration_syntax(self):
        MockTokenizer.CURRENT_PARSE_TEST = 14
        self.assertRaises(ParserException, self.parser.parse)
    
    def test_missing_assignment_symbol_in_assignment(self):
        MockTokenizer.CURRENT_PARSE_TEST = 15
        self.assertRaises(ParserException, self.parser.parse)

    def test_long_assignment_expression(self):
        MockTokenizer.CURRENT_PARSE_TEST = 16
        self.parser.parse()
    
    def test_misplaced_comma_symbol(self):
        MockTokenizer.CURRENT_PARSE_TEST = 17
        self.assertRaises(ParserException, self.parser.parse)

    def test_mutliple_unary_operators(self):
        MockTokenizer.CURRENT_PARSE_TEST = 18
        self.parser.parse()
    
    def test_long_while_expression(self):
        MockTokenizer.CURRENT_PARSE_TEST = 19
        self.parser.parse()
    
    def test_long_if_expression(self):
        MockTokenizer.CURRENT_PARSE_TEST = 20
        self.parser.parse()

    def test_binary_operation_missing_second_operand(self):
        MockTokenizer.CURRENT_PARSE_TEST = 21
        self.assertRaises(ParserException, self.parser.parse)

    def test_mutliple_binary_operations_missing_second_operand(self):
        MockTokenizer.CURRENT_PARSE_TEST = 22
        self.assertRaises(ParserException, self.parser.parse)

    def test_expression_missing_semicolon(self):
        MockTokenizer.CURRENT_PARSE_TEST = 23
        self.assertRaises(ParserException, self.parser.parse)

    def test_empty_while_statement(self):
        MockTokenizer.CURRENT_PARSE_TEST = 24
        self.parser.parse()

    def test_empty_if_statment_no_else(self):
        MockTokenizer.CURRENT_PARSE_TEST = 25
        self.parser.parse()

    def test_empty_if_statment_with_else(self):
        MockTokenizer.CURRENT_PARSE_TEST = 26
        self.parser.parse()
    
    def test_while_missing_do(self):
        MockTokenizer.CURRENT_PARSE_TEST = 27
        self.assertRaises(ParserException, self.parser.parse)

    def test_while_missing_od(self):
        MockTokenizer.CURRENT_PARSE_TEST = 28
        self.assertRaises(ParserException, self.parser.parse)

    def test_if_missing_then(self):
        MockTokenizer.CURRENT_PARSE_TEST = 29
        self.assertRaises(ParserException, self.parser.parse)

    def test_if_missing_fi(self):
        MockTokenizer.CURRENT_PARSE_TEST = 30
        self.assertRaises(ParserException, self.parser.parse)

    def test_missing_unary_operand(self):
        MockTokenizer.CURRENT_PARSE_TEST = 31
        self.assertRaises(ParserException, self.parser.parse)

    def test_print_missing_expression(self):
        MockTokenizer.CURRENT_PARSE_TEST = 32
        self.assertRaises(ParserException, self.parser.parse)

    def test_long_expression_print(self):
        MockTokenizer.CURRENT_PARSE_TEST = 33
        self.parser.parse()

    def test_deep_nested_statements(self):
        MockTokenizer.CURRENT_PARSE_TEST = 34
        self.parser.parse()

    def test_deep_nested_statements_no_vars(self):
        MockTokenizer.CURRENT_PARSE_TEST = 35
        self.parser.parse()

    def test_big_file_no_whitespaces(self):
        MockTokenizer.CURRENT_PARSE_TEST = 36
        self.parser.parse()