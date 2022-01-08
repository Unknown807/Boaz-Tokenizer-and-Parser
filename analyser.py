import os
import sys

#------------------------------------------------------------------------

ARITHMETIC_OP = ("+", "-", "*", "/")
BOOLEAN_OP = ("&", "|")
RELATIONAL_OP = ("=", "!=", "<", ">", "<=", ">=")
UNARY_OP = ("-", "!")

#------------------------------------------------------------------------

class ParserException(Exception):
    def __init__(self, _type, token):
        self.type = _type
        self.token = token
    
    def __str__(self):
        return "Something wrong with the last token or its type - TYPE:{}, TOKEN:{}".format(self.type, self.token)
    
class ParserSemanticException(Exception):
    def __init__(self, message):
        self.message = message
    
    def __str__(self):
        return self.message

class TokenizeException(Exception):
    def __init__(self, token):
        self.token = token

    def __str__(self):
        return "Error trying to create a token from the character/string: {}".format(self.token)

#------------------------------------------------------------------------

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
                    token_str = cls.CODE[i];
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

#------------------------------------------------------------------------

class Parser:
    
    SYMBOL_TABLE = {}

    @classmethod
    def is_identifier_declared(cls, token):
        if token not in cls.SYMBOL_TABLE.keys():
            raise ParserSemanticException("Identifier: {}, has not been declared".format(token))
        
        return True

    @classmethod
    def is_valid_identifier(cls, token):
        '''
        starts with a letter and is alphanumeric + any
        underscores
        '''
        if ( token[0].isalpha() ):
            if (token.replace("_", "").isalnum()):
                return True
        
        return False

    @classmethod
    def check_matching_types(cls, intended_type, expression):
        # it contains any boolean related operators
        for char in RELATIONAL_OP+BOOLEAN_OP+("!",):
            if char in expression:
                return intended_type == "bool"
        
        # it contains a character constant or identifier
        if '"' in expression or "char" in expression:
            return intended_type == "char"

        return intended_type == "int"

    @classmethod
    def parse(cls):
        _, program_token = Tokenizer.get_next_token()
        _type, id_token = Tokenizer.get_next_token()

        if (program_token != "program" or _type != "IDENTIFIER" or not cls.is_valid_identifier(id_token)):
            raise ParserException(_type, program_token+"or "+id_token)

        cls.parse_var_decs()
        cls.parse_statements()

    @classmethod
    def parse_var_decs(cls):
        _type, token = Tokenizer.get_next_token()
        if (token == "begin"):
            return
        elif (token in ("int", "char")):
            cls.parse_var_list(token)
            cls.parse_var_decs()
        else:
            raise ParserException(_type, token)
    
    @classmethod
    def parse_var_list(cls, var_type):
        '''
        Each variable declaration starts with an identifier after a type
        declaration, then its followed by either a ',' or ends with a ';'
        '''

        _type, token = Tokenizer.get_next_token()

        if (_type != "IDENTIFIER"):
            raise ParserException(_type,  token)

        if (not cls.is_valid_identifier(token)):
            raise ParserException(_type, token)

        cls.SYMBOL_TABLE[token] = var_type

        _type, token = Tokenizer.get_next_token()
        if (token == ";"):
            return
        elif (token == ","):
            cls.parse_var_list(var_type)
        else:
            raise ParserException(_type, token)

    @classmethod
    def parse_statements(cls):
        '''
        Only possible statements are:
        - assign statement
        - if statement (+ else clause)
        - print statement
        - while statement
        '''

        _type, token = Tokenizer.get_next_token()

        if (token in ("end", "od", "fi")):
            return
        elif (token == "else"):
            cls.parse_statements()
            return
        elif (token == "while"):
            cls.parse_while()
        elif (token == "if"):
            cls.parse_if()
        elif (token == "print"):
            cls.parse_expression()
        elif (cls.is_valid_identifier(token) and cls.is_identifier_declared(token)):
            # assignment statement starts with a valid identifier
            # otherwise it is incorrect
            cls.parse_assign(cls.SYMBOL_TABLE[token])
        else:
            raise ParserException(_type, token)
        
        cls.parse_statements()

    @classmethod
    def parse_if(cls):
        line = cls.parse_expression()
        if (not cls.check_matching_types("bool", line)):
            raise ParserSemanticException("If statement condition has to evaluate to a BOOLEAN")
        cls.parse_statements()

        _type, token = Tokenizer.get_next_token()
        if (token != ";"):
            raise ParserException(_type, token)

    @classmethod
    def parse_assign(cls, assignment_type):
        _type, token = Tokenizer.get_next_token()
        
        if (token == ":="):
            line = cls.parse_expression()
            if (not cls.check_matching_types(assignment_type, line)):
                raise ParserSemanticException("Wrong type assignment to identifier of type: {}".format(assignment_type))
        else:
            raise ParserException(_type, token)

    @classmethod
    def parse_while(cls):
        line = cls.parse_expression()
        if (not cls.check_matching_types("bool", line)):
            raise ParserSemanticException("While statement condition has to evaluate to a BOOLEAN")
        cls.parse_statements()
        
        _type, token = Tokenizer.get_next_token()
        if (token != ";"):
            raise ParserException(_type, token)

    @classmethod
    def parse_expression(cls, expression=""):
        expression+=cls.parse_term()

        _type, token = Tokenizer.get_next_token()

        if (token in (";", "then", "do", ")")):
            return expression
        elif (token in ARITHMETIC_OP+BOOLEAN_OP+RELATIONAL_OP):
            expression += token
            expression += cls.parse_expression()
        else:
            raise ParserException(_type, token)

        return expression

    @classmethod
    def parse_term(cls, expression=""):
        _type, token = Tokenizer.get_next_token()

        if (_type != "INT_CONST" and _type != "CHAR_CONST"):
            if (token == "("):
                expression+=cls.parse_expression()
            elif (token in UNARY_OP):
                expression+=cls.parse_term()
            elif (cls.is_valid_identifier(token) and cls.is_identifier_declared(token)):
                expression += cls.SYMBOL_TABLE[token]
                return expression
            else:
                raise ParserException(_type, token)

        expression+=token
        return expression

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
# try:
#     Tokenizer.CODE = code
#     Tokenizer.tokenize()
# except TokenizeException:
#     print("error")
#     sys.exit()

Tokenizer.CODE = code
Tokenizer.tokenize()

# print("token done")
# for x in range(100):
#     print(Tokenizer.get_next_token())


# syntax analysis, check tokens against grammar of Boaz language
# try:
#     Parser.parse()
# except ParserException, ParserSemanticException:
#     print("error")
#     sys.exit()

Parser.parse()