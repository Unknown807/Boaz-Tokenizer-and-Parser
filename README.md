# Boaz-Tokenizer-and-Parser

# Description

My final assignment for my 'Computer Systems' module. The purpose of this assignment was to write a lexical analyser and recursive-descent parser for a high-level language called Boaz, including limited semantic analysis. The program outputs 'ok' if the parsing is a success and 'error' if any issues are encountered, with no error recovery.

# How It Works
(Taken from the brief)

### Definitions of terminal symbols - lexical analysis:
- The following are all keywords of the language: begin, char, do, else, end, fi,
if, int, od, print, program, then, while. They are case-sensitive and must
be all lower-case in the source. These are represented in the grammar by upper-case
versions.
- All symbols within a pair of single quote characters in the grammar are onecharacter
or two-character literals that will be found in the source code; e.g. , '!='.
- IDENTIFIER: A sequence of one or more alphabetic, digit or underscore characters, of
which the first must be alphabetic. E.g., Ng1_f3 is valid but 1e4 is not. It is not
permitted to define a variable that is the same as a keyword.
- INT_CONST: A sequence of one or more digits (0-9).
- CHAR_CONST: A single character enclosed within a pair of double-quote characters.
E.g., "!", "a", etc. Multi-character character constants are not permitted.

### Limited type checking:
- If the expression contains at least one relationalOp, booleanOp or unary
boolean negation operator (!) then its type is boolean.
- If the expression is not boolean and it contains at least one CHAR_CONST or an
IDENTIFIER of type CHAR then its type is char.
- If the expression is neither boolean nor char then its type is int.

### The following results in a failed parse:

- Use of an IDENTIFIER either on the left-hand side of an assignStatement or
in a term that has not been declared within a varDec.
- Assignment of an expression of one type to a variable of a different type in an
assignStatement. It is only legal to assign a char expression to a variable of type
char, and an int expression to a variable of type int. It is not permitted to assign a
boolean expression to any variable.
- Use of an expression of type int or char in the expression (condition) of either an
ifStatement or whileStatement. All condition expressions must be of type
boolean.

### Process

![](/diagram.png)
