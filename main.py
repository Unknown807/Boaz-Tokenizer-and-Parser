import os
import sys
from exceptions import TokenizeException, ParserException, ParserSemanticException
from tokenizer import Tokenizer
from myparser import Parser

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
    code = f.read()

if (len(code) == 0):
    print("error")
    sys.exit()

#------------------------------------------------------------------------

# lexical analysis, generate tokens from source code
try:
    Tokenizer.CODE = code
    Tokenizer.tokenize()
except TokenizeException:
    print("error")
    sys.exit()

# syntax + simple semantic analysis, check tokens against grammar of Boaz language
try:
    Parser.parse()
except (ParserException, ParserSemanticException):
    print("error")
    sys.exit()

print("ok")