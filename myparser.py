from constants import *
from tokenizer import Tokenizer
from exceptions import ParserException, ParserSemanticException

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