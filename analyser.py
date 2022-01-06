import os
import sys

# LETTERS = "abcdefghijklmnopqrstuvwxyz"
# LETTERS += LETTERS.upper()
# DIGITS = "0123456789"

class Tokenizer:

    CODE = None
    TOKENS = []

    @staticmethod
    def is_literal(line):
        return line in (
            ":=", "!=", "<=", ">=",
            ",", ";", "+", "-",
            "*", "/", "&", "|",
            "=", "<", ">", "!",
            "(", ")"
        )

    @staticmethod
    def is_keyword(line):
        return line in (
            "begin", "char", "do", "else",
            "end", "fi", "if", "int", "od",
            "print", "program", "then", "while"
        )

    @staticmethod
    def gather_chars(i, char, end):
        token_str = char
        i+=1
        while ( i < end ):
            if ((Tokenizer.CODE[i]+" ").isspace() or Tokenizer.CODE[i] in (",", ";")):
                break

            token_str += Tokenizer.CODE[i]
            i+=1
        i=i-1 # to tokenize the possible ',' or ';' next iter

        return (token_str, i)

    @staticmethod
    def tokenize():
        i = 0
        end = len(Tokenizer.CODE)

        while (i < end):
            char = Tokenizer.CODE[i]
            
            # check if character is empty or whitespace
            if ( (char+" ").isspace() ):
                i+=1
                continue

            # check if character is alphabetic or and _
            if ( char.isalpha() or char == "_" ):
                token_str, i = Tokenizer.gather_chars(i, char, end)

                if (Tokenizer.is_keyword(token_str)):
                    Tokenizer.TOKENS.append( ("KEYWORD", token_str) )
                else:
                    Tokenizer.TOKENS.append( ("IDENTIFIER", token_str) )
            
            # check if character is a digit
            elif ( char.isdigit() ):
                token_str, i = Tokenizer.gather_chars(i, char, end)
                Tokenizer.TOKENS.append( ("INT_CONST", token_str) )

            # check if character is a single character enclosed with "
            elif ( char == '"' ):
                if ( Tokenizer.CODE[i+1] != '"' and Tokenizer.CODE[i+2] == '"' ):
                    token_str = char+Tokenizer.CODE[i+1]+Tokenizer.CODE[i+2]
                    Tokenizer.TOKENS.append( ("CHAR_CONST", token_str))
                    i+=2

            # the rest are symbols, 1 or 2 character literals
            else:
                # check for 2 character literals
                token_str = Tokenizer.CODE[i]+Tokenizer.CODE[i+1]
                if (Tokenizer.is_literal(token_str)):
                    Tokenizer.TOKENS.append( ("SYMBOL", token_str))
                    i+=1
                else: # check for 1 character literals
                    token_str = Tokenizer.CODE[i];
                    if (Tokenizer.is_literal(token_str)):
                        Tokenizer.TOKENS.append( ("SYMBOL", token_str))
                    else:
                        # can't be tokenised, most likely error
                        print("error")
                        sys.exit()
            i+=1

    @staticmethod
    def get_next_token():
        pass

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
Tokenizer.CODE = code
Tokenizer.tokenize()

# for token in Tokenizer.TOKENS:
#     print(token)
