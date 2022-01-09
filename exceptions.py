class TokenizeException(Exception):
    def __init__(self, token):
        self.token = token

    def __str__(self):
        return "Error trying to create a token from the character/string: {}".format(self.token)

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