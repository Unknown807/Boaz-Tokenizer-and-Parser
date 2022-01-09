from constants import *
from exceptions import TokenizeException

class Tokenizer:
    CODE = None
    TOKENS = []
    CURRENT_TOKEN = 0

    LITERALS = (
        ":=", ",", ";", ")", "("
    ) + ARITHMETIC_OP + BOOLEAN_OP + RELATIONAL_OP + UNARY_OP

    KEYWORDS = (
        "begin", "char", "do", "else",
        "end", "fi", "if", "int", "od",
        "print", "program", "then", "while"
    )

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
            if ((cls.CODE[i]+" ").isspace() or cls.CODE[i] in cls.LITERALS+(":",)):
                break

            token_str += cls.CODE[i]
            i+=1
        i=i-1 # to tokenize the possible ',' or ';' or ')' next iter

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
                    raise TokenizeException(token_str)

                cls.TOKENS.append( ("INT_CONST", token_str) )

            # check if character is a single character enclosed with "
            elif ( char == '"' ):
                token_str = char+cls.CODE[i+1]+cls.CODE[i+2]
                if ( cls.CODE[i+1] != '"' and cls.CODE[i+2] == '"' ):
                    cls.TOKENS.append( ("CHAR_CONST", token_str))
                    i+=2
                else:
                    raise TokenizeException(token_str)

            # the rest are symbols, 1 or 2 character literals
            else:
                # check for 2 character literals
                token_str = cls.CODE[i]+cls.CODE[i+1]
                if (cls.is_literal(token_str)):
                    cls.TOKENS.append( ("SYMBOL", token_str))
                    i+=1
                else: # check for 1 character literals
                    token_str = cls.CODE[i]
                    if (cls.is_literal(token_str)):
                        cls.TOKENS.append( ("SYMBOL", token_str))
                    else:
                        # can't be tokenised, most likely error
                        raise TokenizeException(token_str)
            i+=1

    @classmethod
    def get_next_token(cls):
        token = cls.TOKENS[cls.CURRENT_TOKEN]
        cls.CURRENT_TOKEN += 1
        return token
