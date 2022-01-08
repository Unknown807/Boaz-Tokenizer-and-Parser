import os
import sys
from typing import BinaryIO

#------------------------------------------------------------------------

ARITHMETIC_OP = ("+", "-", "*", "/")
BOOLEAN_OP = ("&", "|")
RELATIONAL_OP = ("=", "!=", "<", ">", "<=", ">=")
UNARY_OP = ("-", "!")

#------------------------------------------------------------------------

class ParserException(Exception):
    pass

class TokenizeException(Exception):
    pass

#------------------------------------------------------------------------

class Tokenizer:
    CODE = None
    TOKENS = []

    LITERALS = (
        ":=", ",", ";", ")", "("
    ) + ARITHMETIC_OP + BOOLEAN_OP + RELATIONAL_OP + UNARY_OP

    KEYWORDS = (
        "begin", "char", "do", "else",
        "end", "fi", "if", "int", "od",
        "print", "program", "then", "while"
    )

    CURRENT_TOKEN = 0

    @classmethod
    def is_literal(cls, line):
        return line in cls.LITERALS

    @classmethod
    def is_keyword(cls, line):
        return line in cls.KEYWORDS

    @classmethod
    def gather_chars(cls, i, char, end):
        token_str = char
        i+=1
        while ( i < end ):
            if ((cls.CODE[i]+" ").isspace() or cls.CODE[i] in (",", ";")):
                break

            token_str += cls.CODE[i]
            i+=1
        i=i-1 # to tokenize the possible ',' or ';' next iter

        return (token_str, i)

    @classmethod
    def tokenize(cls):
        i = 0
        end = len(cls.CODE)

        while (i < end):
            char = cls.CODE[i]
            
            # check if character is empty or whitespace
            if ( (char+" ").isspace() ):
                i+=1
                continue

            # check if character is alphabetic or and _
            if ( char.isalpha() or char == "_" ):
                token_str, i = cls.gather_chars(i, char, end)

                if (cls.is_keyword(token_str)):
                    cls.TOKENS.append( ("KEYWORD", token_str) )
                else:
                    cls.TOKENS.append( ("IDENTIFIER", token_str) )
            
            # check if character is a digit
            elif ( char.isdigit() ):
                token_str, i = cls.gather_chars(i, char, end)
                if (not token_str.isdigit()):
                    raise TokenizeException

                cls.TOKENS.append( ("INT_CONST", token_str) )

            # check if character is a single character enclosed with "
            elif ( char == '"' ):
                if ( cls.CODE[i+1] != '"' and cls.CODE[i+2] == '"' ):
                    token_str = char+cls.CODE[i+1]+cls.CODE[i+2]
                    cls.TOKENS.append( ("CHAR_CONST", token_str))
                    i+=2
                else:
                    raise TokenizeException

            # the rest are symbols, 1 or 2 character literals
            else:
                # check for 2 character literals
                token_str = cls.CODE[i]+cls.CODE[i+1]
                if (cls.is_literal(token_str)):
                    cls.TOKENS.append( ("SYMBOL", token_str))
                    i+=1
                else: # check for 1 character literals
                    token_str = cls.CODE[i];
                    if (cls.is_literal(token_str)):
                        cls.TOKENS.append( ("SYMBOL", token_str))
                    else:
                        # can't be tokenised, most likely error
                        raise TokenizeException
            i+=1

    @classmethod
    def get_next_token(cls):
        token = cls.TOKENS[cls.CURRENT_TOKEN]
        cls.CURRENT_TOKEN += 1
        return token

    @classmethod
    def backtrack(cls):
        cls.CURRENT_TOKEN -= 1

#------------------------------------------------------------------------

class Parser:
    
    SYMBOL_TABLE = {}

    @classmethod
    def is_valid_identifier(cls, token):
        if ( token[0].isalpha() ):
            if (token.replace("_", "").isalnum()):
                return True
        
        return False

    @classmethod
    def parse(cls):
        _, program_token = Tokenizer.get_next_token()
        _type, id_token = Tokenizer.get_next_token()

        if (program_token != "program" or _type != "IDENTIFIER" or not cls.is_valid_identifier(id_token)):
            raise ParserException

        cls.parse_var_decs()
        cls.parse_statements()

    @classmethod
    def parse_var_decs(cls):
        _, token = Tokenizer.get_next_token()
        if (token == "begin"):
            return
        elif (token in ("int", "char")):
            cls.parse_var_list(token)
            cls.parse_var_decs()
        else:
            raise ParserException
    
    @classmethod
    def parse_var_list(cls, var_type):
        '''
        Each variable declaration starts with an identifier after a type
        declaration, then its followed by either a ',' or ends with a ';'
        '''

        _type, token = Tokenizer.get_next_token()

        if (_type != "IDENTIFIER"):
            raise ParserException

        if (not cls.is_valid_identifier(token)):
            raise ParserException

        # set the type of the variable for later semantic analysis
        cls.SYMBOL_TABLE[token] = var_type

        _, token = Tokenizer.get_next_token()
        if (token == ";"):
            return
        elif (token == ","):
            cls.parse_var_list(var_type)
        else:
            raise ParserException

    @classmethod
    def parse_statements(cls):
        '''
        Only possible statements are:
        - assign statement
        - if statement
        - print statement
        - while statement
        '''

        _, token = Tokenizer.get_next_token()

        if (token in ("end", "od", "fi")):
            return
        elif (token == "while"):
            cls.parse_while()
        elif (token == "if"):
            pass
        elif (token == "print"):
            cls.parse_expression()
        elif (cls.is_valid_identifier(token)):
            # assignment statement starts with a valid identifier
            # otherwise it is incorrect
            cls.parse_assign()
        else:
            raise ParserException
        
        cls.parse_statements()

    @classmethod
    def parse_assign(cls):
        _, token = Tokenizer.get_next_token()
        
        if (token == ":="):
            cls.parse_expression()
        else:
            raise ParserException

    @classmethod
    def parse_if(cls):
        pass

    @classmethod
    def parse_while(cls):
        cls.parse_expression()
        cls.parse_statements()
        _, token = Tokenizer.get_next_token()
        if (token != ";"):
            raise ParserException

    @classmethod
    def parse_expression(cls):
        cls.parse_term()

        _, token = Tokenizer.get_next_token()
        if (token in (";", "then", "do", ")")):
            return
        elif (token in ARITHMETIC_OP+BOOLEAN_OP+RELATIONAL_OP):
            cls.parse_expression()
        else:
            raise ParserException

    @classmethod
    def parse_term(cls):
        _type, token = Tokenizer.get_next_token()

        if (_type != "INT_CONST" and _type != "CHAR_CONST"):
            if (token == "("):
                cls.parse_expression()
            elif (token in UNARY_OP):
                # could add backtracking to avoid deep parse_term recursion
                cls.parse_term()
            elif (cls.is_valid_identifier(token)):
                # could add stuff here for symbol table later
                pass
            else:
                raise ParserException

#------------------------------------------------------------------------

if len(sys.argv) != 2:
    print("error")
    sys.exit()

filename = sys.argv[1]

if not filename.endswith(".boaz") or not os.path.isfile("./"+filename):
    print("error")
    sys.exit()

# read the .boaz input file 
with open(filename, "r") as f:
    code = f.read();

#------------------------------------------------------------------------

# lexical analysis, generate tokens from source code
try:
    Tokenizer.CODE = code
    Tokenizer.tokenize()
except TokenizeException:
    print("error")
    sys.exit()

# print("token done")
# for x in range(100):
#     print(Tokenizer.get_next_token())


# syntax analysis, check tokens against grammar of Boaz language
# try:
#     Parser.parse()
# except ParserException:
#     print("error")
#     sys.exit()

Parser.parse()