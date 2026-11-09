"""
@file tokenizer.py

This file implements the tokenizer for the Device Tree Source (DTS)
grammar. It contains the @ref Tokenizer, @ref Token, @ref TokenType classes as well
as various helper functions and types.
"""



from .dt_error import logError
from enum import Enum




"""
Returns whether the given character is a whitespace character (space, tab, newline)

@param nextChar Character to check if whitespace
@return True if whitespace, False otherwise
"""
def isWhiteSpace(nextChar: str):
    return nextChar.isspace()



"""
Checks whether the character is a valid decimal character.
The valid decimal characters are [0-9] which is a subset of
the valid hexadecimal characters (with no '0x' prefix).

@param nextChar Character to check
@return True if decimal, False otherwise
"""
def isValidDecimalCharacter(nextChar: str) -> bool:
    if len(nextChar) != 1:
        raise ValueError(f"isValidDecimalCharacter passed parameter: {nextChar} which is not a single character")

    return (nextChar >= "0") and (nextChar <= "9")


"""
Checks whether the character is a valid hexadecimal character.
The valid hex characters are a subset of valid label characters, so
this must be checked first or it will never be called.

@param nextChar Character to check.
@return True if hex, False if not.
"""
def isValidHexadecimalCharacter(nextChar: str) -> bool:
    if len(nextChar) != 1:
        raise ValueError(f"isValidHexadecimalCharacter passed parameter: {nextChar} which is not a single character")

    return isValidDecimalCharacter(nextChar) or ( (nextChar >= "a") and (nextChar <= "f") ) or ( (nextChar >= "A") and (nextChar <= "F") )


"""
Checks whether the next character to be processed is a valid
character for a node label. This is a strict subset of the
valid characters for a node name.

@param nextChar Character to check.
@return True if valid node label character, False if not.
"""
def isValidLabelCharacter(nextChar: str) -> bool:
    if len(nextChar) != 1:
        raise ValueError(f"isValidLabelCharacter passed parameter: {nextChar} which is not a single character")

    return nextChar.isalnum() or (nextChar == "_")


"""
Checks whether the next character to be processed is a valid
character for a node or property name.

@important The valid character set for node names and property names is the
same and does not include the '.' ',' '+' or '?' characters. The '#' character
is not considered to be part of the name, and is its own token. This contradicts
the strictest reading of the [Device Tree Specification](https://app.readthedocs.org/projects/devicetree-specification/downloads/pdf/latest/)

@note In all device tree files used in miniOS, the characters ',' '+'
and '.' are not used for node or property names. This is useful for the ',' and '+'
characters which are there own tokens, which could lead to ambiguous lexing.
Furthermore, the '#' character is given its own separate token and is not
considered to be part of the name. The '?' character is also excluded from consideration
from property names and is not used. Originally it was used to denote
boolean properties, but in modern device tree boolean properties are denoted
by a property name and no value, thus it is not necessary.

@param nextChar Character to check.
@return True if valid node name character, False if not.
"""
def isValidNodeNameOrPropertyCharacter(nextChar: str) -> bool:
    if len(nextChar) != 1:
        raise ValueError(f"isValidNodeNameCharacter passed parameter: {nextChar} which is not a single character")
    
    return isValidLabelCharacter(nextChar) or (nextChar == "-")



"""
Returns whether the next character is a valid character to be
the first character in a name. Names must start with an upper
or lowercase letter but after that can have numbers, etc. This
is different from @ref isValidNameCharacter, which checks if a
character is valid anywhere in the name.

@param nextChar Character to check.
@return True if valid first character for name, False otherwise.
"""
def isValidFirstNameCharacter(nextChar: str):
    return nextChar.isalpha()


"""
@class TokenType

Enum which defines the type or class of the token. This
is different than the actual text in the token: for example
the token (LEFT_CURLY_BRACE, '{') has a type "LEFT_CURLY_BRACE"
and a value of '{'. This is just the type. The whole token
itself is represented by the @ref Token class.

@important You may notice that three of the members are the logical OR
of multiple different types of tokens (HEX_NUMBER_NO_PREFIX_OR_LABEL_OR_NODE_OR_PROPERTY,
LABEL_OR_NODE_OR_PROPERTY_NAME, NODE_OR_PROPERTY_NAME). This occurs because the
valid syntax for hexadecimal numbers (without the explicit '0x' prefix) is a subset
of the valid syntax for node labels, which is a subset of the valid syntax for
node and property names. Hexadecimal numbers with no prefix can start with [a-f] or [A-F] and
contain the characters [a-f], [A-F], or [0-9]. Node labels can start with [a-z] or [A-Z] and
contain the characters [a-z], [A-Z], [0-9], or '_'. Thus, a valid hex number like deadbeef101
could also be a node label. Similarly, the node label uart_1 can also be interpreted as a node
name or a property name. The solution is to create multiple ambiguous token classes where a given
output token may be in one of several different true token classes and to leave the decision
about what the true class is to the parser based on the context in which the token is used. For example,
if the token (LABEL_OR_NODE_OR_PROPERTY_NAME, "uart_1") is followed by the token (COLON, ":"), then
the only valid way to parse this is as a label rather than a node or property name.
"""
class TokenType(Enum):
    NONE = 0                        ## No token type
    LEFT_CURLY_BRACE = 1            ## '{'
    RIGHT_CURLY_BRACE = 2           ## '}'
    COLON = 3                       ## ':'
    HEXADECIMAL_NUMBER = 4          ## Hexadecimal number with the '0x' prefix. Numbers without this prefix are described below.
    STRING = 5                      ## String literal
    HASHTAG = 6                     ## '#'
    AT_SYMBOL = 7                   ## '@'
    SEMICOLON = 8                   ## ';'
    LEFT_ANGLE_BRACKET = 9          ## '<'
    RIGHT_ANGLE_BRACKET = 10        ## '>'
    AMPERSAND = 11                  ## '&'
    EQUALS = 12                     ## '='
    DECIMAL_NUMBER = 13             ## Decimal number
    HEX_NUMBER_NO_PREFIX_OR_LABEL_OR_NODE_OR_PROPERTY = 14  ## Ambiguous class where token may either be a hex number, label, node name, or property name
    LABEL_OR_NODE_OR_PROPERTY_NAME = 15     ## Ambiguous class where token may either be a label or a node name or a property name
    NODE_OR_PROPERTY_NAME = 16      ## Ambiguous class where token may either be a node name or a property name
    COMMA = 18                      ## ','
    END_OF_FILE = 19                ## Denotes the end of the file
    FORWARD_SLASH = 20              ## '/'
    NEWLINE = 21                    ## Newline character
    LEFT_SQUARE_BRACKET = 22        ## '['
    RIGHT_SQUARE_BRACKET = 23       ## ']'
    EXCLAMATION_POINT = 24          ## '!'
    QUESTION_MARK = 25              ## '?'
    MULTIPLY = 26                   ## '*'
    XOR = 27                        ## '^'
    MODULUS = 28                    ## '%'
    BITWISE_NOT = 29                ## '~'
    LEFT_SHIFT = 30                 ## '<<'
    RIGHT_SHIFT = 31                ## '>>'
    LOGICAL_AND = 32                ## '&&'
    LOGICAL_OR = 33                 ## '||'
    LESS_EQ = 34                    ## '<='
    GREATER_EQ = 35                 ## '>='
    PLUS = 36                       ## '+'
    MINUS = 37                      ## '-'
    BITWISE_OR = 38                 ## '|'
    DOUBLE_EQUALS = 39              ## '=='
    NOT_EQUALS = 40                 ## '!='
    LEFT_PARENTHESIS = 41           ## '('
    RIGHT_PARENTHESIS = 42          ## ')'


"""
@class Token

Class representing a parsed token. The two main components
of a parsed token are the token class (type of the token),
represented by the 'type' member, and the value which is represented
by the 'value'. The value is always a string and the type is
of type @ref TokenType. There are also members for the line and
column numbers (used extensively for debugging and error messages),
and an ID number member and a next ID number class member (mostly unused).
"""
class Token:

    # for keeping track of token numbers
    nextIDNumber = 0

    @classmethod
    def incrementID(cls):
        cls.nextIDNumber += 1


    def __init__(self, type: TokenType, value: str, lineNumber: int = 1, columnNumber: int = 1):
        self.type = type
        self.value = value
        self.lineNumber = lineNumber
        self.columnNumber = columnNumber
        self.id = self.nextIDNumber
        Token.incrementID()

    def __str__(self):
        return f"Type: {self.type}, Value: {self.value}."
    
    def __eq__(self, other) -> bool:
        return (self.type == other.type) and (self.value == other.value)

    def appendText(self, newChar: str):
        self.value = self.value + newChar



"""
@class TokenizerState

Enum representing the state of the tokenizer state machine. It should be noted here
that "hex numbers" and "decimal numbers" do not have their typical meaning. In the
device tree files, any number can be a hex number, but only some are explicitly
marked as hex with the "0x" prefix. These are processed as hex numbers and any number
that is not marked with "0x" prefix is processed as decimal. This is all syntactically
speaking; the interpretation of the semantic value of the numbers is not considered
in the tokenizer.

@note The usage/conditions for entry and exit of the various states are documented in @ref Tokenizer
"""
class TokenizerState(Enum):
    DEFAULT = 0
    PROCESSING_HEX_NUMBER_NO_PREFIX_OR_LABEL_OR_NAME_OR_PROPERTY = 1
    PROCESSING_LABEL_OR_NAME_OR_PROPERTY = 2
    PROCESSING_NAME_OR_PROPERTY = 3
    PROCESSING_DECIMAL_NUMBER = 4
    UNSURE_WHETHER_DECIMAL_OR_HEXADECIMAL = 5
    PROCESSING_HEXADECIMAL_NUMBER = 6
    PROCESSING_STRING = 7
    PROCESSING_LEFT_ANGLE_BRACKET = 8
    PROCESSING_RIGHT_ANGLE_BRACKET = 9
    PROCESSING_AMPERSAND = 10
    PROCESSING_OR = 11
    PROCESSING_EQUALS = 12
    PROCESSING_NOT = 13




"""
@class Tokenizer

@brief Represents the tokenizer for Device Tree Source grammar.

The tokenizer class contains multiple parts which are important to understand.

The first is the finite state machine (FSM) implementation which actually does
the tokenization. The FSM is implemented by the self.state variable, which stores
the current state of the FSM, one callback method per state (defined below) which
implements the processing for that state as well as transitions to other states, and a
callback method table which is indexed by the current state to invoke the callback
corresponding to that state.

The self.stringToTokenize member variable stores the text of the string to be
tokenized. In most cases this will be the entire text of the device tree file.

The self.currentStringIndex variable keeps track of the index of the next character
to inspect in the stringToTokenize. This is incremented on each invocation of a
state callback method.

The self.currentLineNumber keeps track of the current line number to be able to
report it when the tokenizer encounters an error. Incremented each time a newline
character is encountered. This is passed on to each token when a new one is created
so that the parser may also report the line number accurately for errors.

The self.currentColumnNumber keeps track of the current column number in a similar
way to self.currentLineNumber. It is incremented each time getNextChar is called,
and reset to 1 each time a newline is encountered (except when processing a string
token in which case newline causes an error since strings must be terminated by a
double quote on the same line).

The self.currentToken variable stores the current token while it is being processed.
For example, when processing a name token, the tokenizer changes to the state
TOKENIZER_STATE_PROCESSING_NAME when the first name character is encountered,
creates a new token object with the first character, and assigns that token object
to the self.currentToken variable. After that, for every invocation of the state
machine until a terminating character is encountered, the tokenizer simply appends
the next character to the current token's value.

The self.hasExtraToken variable is due to the fact that some
tokens are terminated by a single-character token. For example, in the node declaration
uart@bf806000, the uart part is terminated by the symbol "@", which is an entire token itself
(AT_SYMBOL). Thus, when this is encountered, the function would either return
2 tokens at once, which kinda breaks the intended API for the tokenizer, or it can
store the token in the self.currentToken variable and set the self.hasExtraToken flag. The
getNextToken method then checks this flag to see if there is a token ready for it and
if so returns it and resets the flag.

The various states of the state machine also bear some explaining. The "default" state is
represented by DEFAULT. This occurs when the tokenizer is not in the middle
of processing something such as a name, number, etc. The tokenizer starts in this state and
returns to this state at the end of processing any token. The method that implements the
processing for this state is @ref handleStateDefault. If the tokenizer encounters any character
that is an entire token by itself, it will emit this token without changing state. However,
it will change states when processing tokens larger than a single character. If the tokenizer
encounters a double quote (") character, it will switch to processing a string token (the
entire string including opening and closing double quotes are considered a single token) which
is defined by PROCESSING_STRING. Upon reaching the ending double quote it will
switch back to DEFAULT. If the tokenizer encounters a valid decimal character
while in DEFAULT, it will switch to PROCESSING_DECIMAL_NUMBER
and begin processing the decimal number. If there are only the characters 0-9 in the number
it will continue until it hits the end of the token and then switch back to DEFAULT.
However, in device tree hexadecimal number may not always be marked with a preceding '0x' and
thus a hex number could appear as '80bc0000'. In order for this to not throw an error, the
tokenizer will switch to PROCESSING_HEXADECIMAL_NUMBER if it encounters one
of the characters a-f or A-F. The existence of hexadecimal numbers further complicates processing
because even if they do start with '0x', '0' is a valid decimal character which means that by
default the tokenizer would switch to PROCESSING_DECIMAL_NUMBER. However, since
'x' is not valid hexadecimal, the tokenizer would end up throwing an error. To fix this, a new
state UNSURE_WHETHER_DECIMAL_OR_HEXADECIMAL is entered when the tokenizer
encounters '0' while in DEFAULT. In this state, the tokenizer will check the
next character and if it is 'x' or another valid hexadecimal character, it will transition
to PROCESSING_HEXADECIMAL_NUMBER. Otherwise, if it is another valid decimal
character, it will transition to PROCESSING_DECIMAL_NUMBER. In either case, it
will change the token type as well to reflect the transition. Processing becomes even more
complex when labels, node names, and property names are added to the mix. Neither labels,
node names, nor property names can start with 0-9, so they are not in conflict with decimal
numbers, but they must start with a-z or A-Z, and since hexadecimal numbers may not have the
'0x' prefix, they can start with any of the letter a-f or A-F which are a subset of a-z and A-Z.
Furthermore, node names and property names may contain ',', '.', '+', or '-' in addition to
alphanumeric characters and '_' while labels may only have alphanumeric characters and '_'.
In order to deal with these nested character classes, in DEFAULT the tokenizer
will move into PROCESSING_HEX_NUMBER_NO_PREFIX_OR_LABEL_OR_NAME_OR_PROPERTY if
it detects a-f or A-F. Otherwise, if the character is alphabetic it will move to 
PROCESSING_LABEL_OR_NAME_OR_PROPERTY. Since a label, node name, or property name
may start with a-f or A-F, the tokenizer may find the character g-z, G-Z, '_', '+', '-', '.', or
',' in the token. If it encounters g-z, G-Z or '_', it will switch to the state
PROCESSING_LABEL_OR_NAME_OR_PROPERTY since this token is definitely not a hexadecimal
number and if it encounters '+'. '-', '.' or ',' it will switch to
PROCESSING_NAME_OR_PROPERTY since it is neither a hex number or a label. Similarly,
while in the state PROCESSING_LABEL_OR_NAME_OR_PROPERTY, if it encounters any of the
characters '+', '-', '.', ',' it will switch to PROCESSING_LABEL_OR_NAME_OR_PROPERTY
since this token cannot be a label. This does leave some ambiguity, since 'uart_0' is a valid node
name or property name in addition to a label and 'deadbeef' is a valid hex number, label, node name,
or property name. These ambiguities are left to the parser and semantic analyzer to figure out. For
example, in the node definition 'uart1: uart@bfc04000 { ... }', the hex number 'bfc04000' will result
in a token that can be either a hex number with no prefix, a label, a node name, or a property name.
However, since nothing besides a hex number makes sense here, the parser will interpret it as a hex
number.

When interacting with the tokenizer, the user calls the getNextToken API method to get the next
token. This will return an actual token or the dummy end-of-file token if it has reached the end
of the input string. The getNextToken method first checks if there is an extra token and if so, it
returns that without running the state machine. Extra tokens occur when a character both signals
the end of the previous token and is an entire token itself ({, }, <, >, etc.). The state machine is
supposed to process a single character at a time and not move backward, and the getNextToken method
is only supposed to return a single token at a time, so it is not possible to either move the state
machine back one character or to return two tokens at once. Thus, the extra token is stored until the
next call to getNextToken. If there is no extra token, the tokenizer runs the state machine until it
returns a token rather than None. The state machine will only return a token when it has finished
processing the current token.
"""
class Tokenizer:

    # map for single character tokens to token types
    # does not include characters that can be part of multi-character tokens
    # like <, >, &, and | since those need special processing (see below map).
    # This is used to get the token type as part of token construction upon
    # tokenizer encountering one of these characters
    singleCharacterTokenTypeMap = {
        "{" : TokenType.LEFT_CURLY_BRACE,
        "}" : TokenType.RIGHT_CURLY_BRACE,
        ":" : TokenType.COLON,
        "#" : TokenType.HASHTAG,
        "@" : TokenType.AT_SYMBOL,
        ";" : TokenType.SEMICOLON,
        "," : TokenType.COMMA,
        "/" : TokenType.FORWARD_SLASH,
        "[" : TokenType.LEFT_SQUARE_BRACKET,
        "]" : TokenType.RIGHT_SQUARE_BRACKET,
        "?" : TokenType.QUESTION_MARK,
        "*" : TokenType.MULTIPLY,
        "^" : TokenType.XOR,
        "%" : TokenType.MODULUS,
        "~" : TokenType.BITWISE_NOT,
        "+" : TokenType.PLUS,
        "-" : TokenType.MINUS,
        "(" : TokenType.LEFT_PARENTHESIS,
        ")" : TokenType.RIGHT_PARENTHESIS
    }


    # All of these characters can either be single tokens or
    # can be part of multi-character tokens. For example,
    # the '<' character can be part of the '<', '<<', or '<='
    # tokens. This map gives the next processing state in which
    # the tokenizer figures out based on the next character
    # what token this character is part of
    multiCharacterTokenNextStateMap = {
        "<" : TokenizerState.PROCESSING_LEFT_ANGLE_BRACKET,
        ">" : TokenizerState.PROCESSING_RIGHT_ANGLE_BRACKET,
        "&" : TokenizerState.PROCESSING_AMPERSAND,
        "|" : TokenizerState.PROCESSING_OR,
        "=" : TokenizerState.PROCESSING_EQUALS,
        "!" : TokenizerState.PROCESSING_NOT
    }


    def __init__(self, stringToTokenize: str = ""):
        self.state = TokenizerState.DEFAULT
        self.stringToTokenize = stringToTokenize
        self.currentStringIndex = 0
        self.currentLineNumber = 1
        self.currentColumnNumber = 1
        self.currentToken = None
        self.hasExtraToken = False



    """
    Returns the text of the current line (defined by the current line number).

    @return The current line.
    """
    def getCurrentLine(self) -> str:
        return self.stringToTokenize.split("\n")[self.currentLineNumber-1]


    """
    Returns the number of the current line but not the text of it.

    @return The current line number.
    """
    def getCurrentLineNumber(self) -> int:
        return self.currentLineNumber



    """
    Gets the next character from the string to tokenize (the text of the
    device tree file).

    @return The next character in the string.
    """
    def getNextChar(self) -> str | None:
        nextChar = None

        if self.currentStringIndex < len(self.stringToTokenize):
            nextChar = self.stringToTokenize[self.currentStringIndex]
            self.currentStringIndex += 1
            self.currentColumnNumber += 1

        return nextChar



    ####################################################
    # The next section contains the callback methods 
    # for implementing each state in the state machine.
    ####################################################


    """
    Callback function for processing the DEFAULT state.

    @return Next token or None if needs more processing.
    """
    def handleStateDefault(self) -> Token | None:
        nextChar = self.getNextChar()

        if nextChar is None:
            newToken = Token(TokenType.END_OF_FILE, "", self.currentLineNumber, self.currentColumnNumber-1)
            return newToken

        # this has to go before the next elif since \n is whitespace
        elif nextChar == "\n":
            self.currentLineNumber += 1
            self.currentColumnNumber = 1
            return None
        elif isWhiteSpace(nextChar):
            return None
        elif nextChar == "0":
            self.currentToken = Token(TokenType.NONE, "0", self.currentLineNumber, self.currentColumnNumber-1)
            self.state = TokenizerState.UNSURE_WHETHER_DECIMAL_OR_HEXADECIMAL       # need either 'x' or another digit to be sure
            return None

        # since decimal characters are a subset of hexadecimal characters, this elif must come before
        # the next one for hexadecimal, otherwise all decimal character (0-9) would fall through
        # into the next elif
        elif isValidDecimalCharacter(nextChar):
            self.currentToken = Token(TokenType.DECIMAL_NUMBER, nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.state = TokenizerState.PROCESSING_DECIMAL_NUMBER                   
            return None

        # hexadecimal numbers can start with a-f which would otherwise be interpreted
        # as a name, thus this elif must go before the next one. This elif will not be
        # entered if the character is 0-9 since the previous elif handles those. The state handling the
        # processing of hexadecimal characters must check if the next character is valid
        # hexadecimal, and if not but it is valid name character, change state to
        # processing name
        elif isValidHexadecimalCharacter(nextChar):
            self.currentToken = Token(TokenType.HEX_NUMBER_NO_PREFIX_OR_LABEL_OR_NODE_OR_PROPERTY, nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.state = TokenizerState.PROCESSING_HEX_NUMBER_NO_PREFIX_OR_LABEL_OR_NAME_OR_PROPERTY
            return None

        # the characters that occur at the beginning of a name are different than those
        # that can occur in the middle of one. For example, the numeral 0-9 can occur
        # in a name as well as underscores or dashes, but just not at the beginning
        elif isValidFirstNameCharacter(nextChar):
            self.currentToken = Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.state = TokenizerState.PROCESSING_LABEL_OR_NAME_OR_PROPERTY
            return None

        elif nextChar == "\"":
            self.currentToken = Token(TokenType.STRING, "", self.currentLineNumber, self.currentColumnNumber-1)
            self.state = TokenizerState.PROCESSING_STRING
            return None
        
        elif nextChar in Tokenizer.singleCharacterTokenTypeMap.keys():
            newToken: Token = Token(Tokenizer.singleCharacterTokenTypeMap[nextChar], nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            return newToken

        elif nextChar in Tokenizer.multiCharacterTokenNextStateMap.keys():
            self.currentToken = Token(TokenType.NONE, nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.state = Tokenizer.multiCharacterTokenNextStateMap[nextChar]

        else:
            logError(f"Character: \"{nextChar}\" at line {self.currentLineNumber} is not a valid character for devicetree file.")



    """
    Callback function for processing the PROCESSING_HEX_NUMBER_NO_PREFIX_OR_LABEL_OR_NAME_OR_PROPERTY state.

    @return Next token or None if needs more processing.
    """
    def handleStateProcessingHexNumberOrLabelOrNameOrProperty(self) -> Token | None:
        nextChar = self.getNextChar()

        if nextChar is None:
            newToken = self.currentToken
            self.currentToken = Token(TokenType.END_OF_FILE, "", self.currentLineNumber, self.currentColumnNumber-1)
            self.hasExtraToken = True
            self.state = TokenizerState.DEFAULT
            return newToken

        elif nextChar == "\n":
            self.state = TokenizerState.DEFAULT
            self.currentLineNumber += 1
            self.currentColumnNumber = 1
            return self.currentToken

        elif isWhiteSpace(nextChar):
            self.state = TokenizerState.DEFAULT
            return self.currentToken

        elif isValidNodeNameOrPropertyCharacter(nextChar) and not isValidLabelCharacter(nextChar):
            self.state = TokenizerState.PROCESSING_NAME_OR_PROPERTY
            self.currentToken.type = TokenType.NODE_OR_PROPERTY_NAME
            self.currentToken.appendText(nextChar)
            return None

        elif isValidLabelCharacter(nextChar) and not isValidHexadecimalCharacter(nextChar):
            self.state = TokenizerState.PROCESSING_LABEL_OR_NAME_OR_PROPERTY
            self.currentToken.type = TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME
            self.currentToken.appendText(nextChar)
            return None

        elif isValidHexadecimalCharacter(nextChar):
            self.currentToken.appendText(nextChar)
            return None

        elif nextChar in Tokenizer.singleCharacterTokenTypeMap.keys():
            newToken: Token = self.currentToken
            self.currentToken = Token(Tokenizer.singleCharacterTokenTypeMap[nextChar], nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.hasExtraToken = True
            self.state = TokenizerState.DEFAULT
            return newToken

        elif nextChar in Tokenizer.multiCharacterTokenNextStateMap.keys():
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.NONE, nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.state = Tokenizer.multiCharacterTokenNextStateMap[nextChar]
            return newToken

        elif nextChar == "\"":
            logError(f"Error occurred during tokenization. Unexpected character: {nextChar} at line {self.currentLineNumber} should not appear in device tree name.")

        else:
            logError(f"Character: \"{nextChar}\" at line {self.currentLineNumber} is not a valid character for devicetree file.")



    """
    Callback function for processing the PROCESSING_LABEL_OR_NAME_OR_PROPERTY state.

    @return Next token or None if needs more processing.
    """
    def handleStateProcessingLabelOrNameOrProperty(self) -> Token | None:
        nextChar = self.getNextChar()

        if nextChar is None:
            newToken = self.currentToken
            self.currentToken = Token(TokenType.END_OF_FILE, "", self.currentLineNumber, self.currentColumnNumber-1)
            self.hasExtraToken = True
            self.state = TokenizerState.DEFAULT
            return newToken

        elif nextChar == "\n":
            self.state = TokenizerState.DEFAULT
            self.currentLineNumber += 1
            self.currentColumnNumber = 1
            return self.currentToken

        elif isWhiteSpace(nextChar):
            self.state = TokenizerState.DEFAULT
            return self.currentToken

        elif isValidNodeNameOrPropertyCharacter(nextChar) and not isValidLabelCharacter(nextChar):
            self.state = TokenizerState.PROCESSING_NAME_OR_PROPERTY
            self.currentToken.type = TokenType.NODE_OR_PROPERTY_NAME
            self.currentToken.appendText(nextChar)
            return None

        elif isValidLabelCharacter(nextChar):
            self.currentToken.appendText(nextChar)
            return None

        elif nextChar in Tokenizer.singleCharacterTokenTypeMap.keys():
            newToken: Token = self.currentToken
            self.currentToken = Token(Tokenizer.singleCharacterTokenTypeMap[nextChar], nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.hasExtraToken = True
            self.state = TokenizerState.DEFAULT
            return newToken

        elif nextChar in Tokenizer.multiCharacterTokenNextStateMap.keys():
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.NONE, nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.state = Tokenizer.multiCharacterTokenNextStateMap[nextChar]
            return newToken

        elif nextChar == "\"":
            logError(f"Error occurred during tokenization. Unexpected character: {nextChar} at line {self.currentLineNumber} should not appear in device tree name.")

        else:
            logError(f"Character: \"{nextChar}\" at line {self.currentLineNumber} is not a valid character for devicetree file.")



    """
    Callback function for processing the PROCESSING_NAME_OR_PROPERTY state.

    @return Next token or None if needs more processing.
    """
    def handleStateProcessingNameOrProperty(self) -> Token | None:
        nextChar = self.getNextChar()

        if nextChar is None:
            newToken = self.currentToken
            self.currentToken = Token(TokenType.END_OF_FILE, "", self.currentLineNumber, self.currentColumnNumber-1)
            self.hasExtraToken = True
            self.state = TokenizerState.DEFAULT
            return newToken

        elif nextChar == "\n":
            self.state = TokenizerState.DEFAULT
            self.currentLineNumber += 1
            self.currentColumnNumber = 1
            return self.currentToken

        elif isWhiteSpace(nextChar):
            self.state = TokenizerState.DEFAULT
            return self.currentToken
        

        elif isValidNodeNameOrPropertyCharacter(nextChar):
            self.currentToken.appendText(nextChar)
            return None

        elif nextChar in Tokenizer.singleCharacterTokenTypeMap.keys():
            newToken: Token = self.currentToken
            self.currentToken = Token(Tokenizer.singleCharacterTokenTypeMap[nextChar], nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.hasExtraToken = True
            self.state = TokenizerState.DEFAULT
            return newToken

        elif nextChar in Tokenizer.multiCharacterTokenNextStateMap.keys():
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.NONE, nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.state = Tokenizer.multiCharacterTokenNextStateMap[nextChar]
            return newToken

        elif nextChar == "\"":
            logError(f"Error occurred during tokenization. Unexpected character: {nextChar} at line {self.currentLineNumber} should not appear in device tree name.")

        else:
            logError(f"Character: \"{nextChar}\" at line {self.currentLineNumber} is not a valid character for devicetree file.")


    
    
    """
    Callback function for processing the PROCESSING_LEFT_ANGLE_BRACKET state.

    @return Next token or None if needs more processing.
    """
    def handleStateProcessingLeftAngleBracket(self) -> Token | None:
        nextChar = self.getNextChar()

        if nextChar is None:
            self.state = TokenizerState.DEFAULT
            self.currentToken.type = TokenType.LEFT_ANGLE_BRACKET
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.END_OF_FILE, "", self.currentLineNumber, self.currentColumnNumber-1)
            self.hasExtraToken = True
            return newToken

        elif nextChar == "\n":
            self.state = TokenizerState.DEFAULT
            self.currentToken.type = TokenType.LEFT_ANGLE_BRACKET
            newToken: Token = self.currentToken
            self.currentLineNumber += 1
            self.currentColumnNumber = 1
            return newToken

        elif isWhiteSpace(nextChar):
            self.state = TokenizerState.DEFAULT
            self.currentToken.type = TokenType.LEFT_ANGLE_BRACKET
            newToken: Token = self.currentToken
            return newToken

        elif nextChar in Tokenizer.singleCharacterTokenTypeMap.keys():
            self.state = TokenizerState.DEFAULT
            self.currentToken.type = TokenType.LEFT_ANGLE_BRACKET
            newToken: Token = self.currentToken
            self.currentToken = Token(Tokenizer.singleCharacterTokenTypeMap[nextChar], nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.hasExtraToken = True
            return newToken

        elif nextChar == "<":
            self.state = TokenizerState.DEFAULT
            self.currentToken = None
            newToken: Token = Token(TokenType.LEFT_SHIFT, "<<", self.currentLineNumber, self.currentColumnNumber-1)
            return newToken

        elif nextChar == "=":
            self.state = TokenizerState.DEFAULT
            self.currentToken = None
            newToken: Token = Token(TokenType.LESS_EQ, "<=", self.currentLineNumber, self.currentColumnNumber-1)
            return newToken

        elif nextChar in Tokenizer.multiCharacterTokenNextStateMap.keys():
            newToken: Token = Token(TokenType.LEFT_ANGLE_BRACKET, "<", self.currentLineNumber, self.currentColumnNumber-1)
            self.currentToken = Token(TokenType.NONE, nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.state = Tokenizer.multiCharacterTokenNextStateMap[nextChar]
            return newToken

        elif nextChar == "0":
            newToken: Token = Token(TokenType.LEFT_ANGLE_BRACKET, "<", self.currentLineNumber, self.currentColumnNumber-1)
            self.currentToken = Token(TokenType.NONE, "0", self.currentLineNumber, self.currentColumnNumber-1)
            self.state = TokenizerState.UNSURE_WHETHER_DECIMAL_OR_HEXADECIMAL       # need either 'x' or another digit to be sure
            return newToken

        # since decimal characters are a subset of hexadecimal characters, this elif must come before
        # the next one for hexadecimal, otherwise all decimal character (0-9) would fall through
        # into the next elif
        elif isValidDecimalCharacter(nextChar):
            newToken: Token = Token(TokenType.LEFT_ANGLE_BRACKET, "<", self.currentLineNumber, self.currentColumnNumber-1)
            self.currentToken = Token(TokenType.DECIMAL_NUMBER, nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.state = TokenizerState.PROCESSING_DECIMAL_NUMBER                   
            return newToken

        # hexadecimal numbers can start with a-f which would otherwise be interpreted
        # as a name, thus this elif must go before the next one. This elif will not be
        # entered if the character is 0-9 since the previous elif handles those. The state handling the
        # processing of hexadecimal characters must check if the next character is valid
        # hexadecimal, and if not but it is valid name character, change state to
        # processing name
        elif isValidHexadecimalCharacter(nextChar):
            newToken: Token = Token(TokenType.LEFT_ANGLE_BRACKET, "<", self.currentLineNumber, self.currentColumnNumber-1)
            self.currentToken = Token(TokenType.HEX_NUMBER_NO_PREFIX_OR_LABEL_OR_NODE_OR_PROPERTY, nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.state = TokenizerState.PROCESSING_HEX_NUMBER_NO_PREFIX_OR_LABEL_OR_NAME_OR_PROPERTY
            return newToken

        # the characters that occur at the beginning of a name are different than those
        # that can occur in the middle of one. For example, the numeral 0-9 can occur
        # in a name as well as underscores or dashes, but just not at the beginning
        elif isValidFirstNameCharacter(nextChar):
            newToken: Token = Token(TokenType.LEFT_ANGLE_BRACKET, "<", self.currentLineNumber, self.currentColumnNumber-1)
            self.currentToken = Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.state = TokenizerState.PROCESSING_LABEL_OR_NAME_OR_PROPERTY
            return newToken

        elif nextChar == "\"":
            newToken: Token = Token(TokenType.LEFT_ANGLE_BRACKET, "<", self.currentLineNumber, self.currentColumnNumber-1)
            self.currentToken = Token(TokenType.STRING, "", self.currentLineNumber, self.currentColumnNumber-1)
            self.state = TokenizerState.PROCESSING_STRING
            return newToken

        else:
            logError(f"Character: \"{nextChar}\" at line {self.currentLineNumber} is not a valid character for devicetree file.")




    """
    Callback function for processing the PROCESSING_RIGHT_ANGLE_BRACKET state.

    @return Next token or None if needs more processing.
    """
    def handleStateProcessingRightAngleBracket(self) -> Token | None:
        nextChar = self.getNextChar()

        if nextChar is None:
            self.state = TokenizerState.DEFAULT
            self.currentToken.type = TokenType.RIGHT_ANGLE_BRACKET
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.END_OF_FILE, "", self.currentLineNumber, self.currentColumnNumber-1)
            self.hasExtraToken = True
            return newToken

        elif nextChar == "\n":
            self.state = TokenizerState.DEFAULT
            self.currentToken.type = TokenType.RIGHT_ANGLE_BRACKET
            newToken: Token = self.currentToken
            self.currentLineNumber += 1
            self.currentColumnNumber = 1
            return newToken

        elif isWhiteSpace(nextChar):
            self.state = TokenizerState.DEFAULT
            self.currentToken.type = TokenType.RIGHT_ANGLE_BRACKET
            newToken: Token = self.currentToken
            return newToken

        elif nextChar in Tokenizer.singleCharacterTokenTypeMap.keys():
            self.state = TokenizerState.DEFAULT
            self.currentToken.type = TokenType.RIGHT_ANGLE_BRACKET
            newToken: Token = self.currentToken
            self.currentToken = Token(Tokenizer.singleCharacterTokenTypeMap[nextChar], nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.hasExtraToken = True
            return newToken

        elif nextChar == ">":
            self.state = TokenizerState.DEFAULT
            self.currentToken = None
            newToken: Token = Token(TokenType.RIGHT_SHIFT, ">>", self.currentLineNumber, self.currentColumnNumber-1)
            return newToken

        elif nextChar == "=":
            self.state = TokenizerState.DEFAULT
            self.currentToken = None
            newToken: Token = Token(TokenType.GREATER_EQ, ">=", self.currentLineNumber, self.currentColumnNumber-1)
            return newToken

        elif nextChar in Tokenizer.multiCharacterTokenNextStateMap.keys():
            newToken: Token = Token(TokenType.RIGHT_ANGLE_BRACKET, ">", self.currentLineNumber, self.currentColumnNumber-1)
            self.currentToken = Token(TokenType.NONE, nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.state = Tokenizer.multiCharacterTokenNextStateMap[nextChar]
            return newToken

        elif nextChar == "0":
            newToken: Token = Token(TokenType.RIGHT_ANGLE_BRACKET, ">", self.currentLineNumber, self.currentColumnNumber-1)
            self.currentToken = Token(TokenType.NONE, "0", self.currentLineNumber, self.currentColumnNumber-1)
            self.state = TokenizerState.UNSURE_WHETHER_DECIMAL_OR_HEXADECIMAL       # need either 'x' or another digit to be sure
            return newToken

        # since decimal characters are a subset of hexadecimal characters, this elif must come before
        # the next one for hexadecimal, otherwise all decimal character (0-9) would fall through
        # into the next elif
        elif isValidDecimalCharacter(nextChar):
            newToken: Token = Token(TokenType.RIGHT_ANGLE_BRACKET, ">", self.currentLineNumber, self.currentColumnNumber-1)
            self.currentToken = Token(TokenType.DECIMAL_NUMBER, nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.state = TokenizerState.PROCESSING_DECIMAL_NUMBER                   
            return newToken

        # hexadecimal numbers can start with a-f which would otherwise be interpreted
        # as a name, thus this elif must go before the next one. This elif will not be
        # entered if the character is 0-9 since the previous elif handles those. The state handling the
        # processing of hexadecimal characters must check if the next character is valid
        # hexadecimal, and if not but it is valid name character, change state to
        # processing name
        elif isValidHexadecimalCharacter(nextChar):
            newToken: Token = Token(TokenType.RIGHT_ANGLE_BRACKET, ">", self.currentLineNumber, self.currentColumnNumber-1)
            self.currentToken = Token(TokenType.HEX_NUMBER_NO_PREFIX_OR_LABEL_OR_NODE_OR_PROPERTY, nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.state = TokenizerState.PROCESSING_HEX_NUMBER_NO_PREFIX_OR_LABEL_OR_NAME_OR_PROPERTY
            return newToken

        # the characters that occur at the beginning of a name are different than those
        # that can occur in the middle of one. For example, the numeral 0-9 can occur
        # in a name as well as underscores or dashes, but just not at the beginning
        elif isValidFirstNameCharacter(nextChar):
            newToken: Token = Token(TokenType.RIGHT_ANGLE_BRACKET, ">", self.currentLineNumber, self.currentColumnNumber-1)
            self.currentToken = Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.state = TokenizerState.PROCESSING_LABEL_OR_NAME_OR_PROPERTY
            return newToken

        elif nextChar == "\"":
            newToken: Token = Token(TokenType.RIGHT_ANGLE_BRACKET, ">", self.currentLineNumber, self.currentColumnNumber-1)
            self.currentToken = Token(TokenType.STRING, "", self.currentLineNumber, self.currentColumnNumber-1)
            self.state = TokenizerState.PROCESSING_STRING
            return newToken

        else:
            logError(f"Character: \"{nextChar}\" at line {self.currentLineNumber} is not a valid character for devicetree file.")




    """
    Callback function for processing the PROCESSING_AMPERSAND state.

    @return Next token or None if needs more processing.
    """
    def handleStateProcessingAmpersand(self) -> Token | None:
        nextChar = self.getNextChar()

        if nextChar is None:
            self.state = TokenizerState.DEFAULT
            self.currentToken.type = TokenType.AMPERSAND
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.END_OF_FILE, "", self.currentLineNumber, self.currentColumnNumber-1)
            self.hasExtraToken = True
            return newToken

        elif nextChar == "\n":
            self.state = TokenizerState.DEFAULT
            self.currentToken.type = TokenType.AMPERSAND
            newToken: Token = self.currentToken
            self.currentLineNumber += 1
            self.currentColumnNumber = 1
            return newToken

        elif isWhiteSpace(nextChar):
            self.state = TokenizerState.DEFAULT
            self.currentToken.type = TokenType.AMPERSAND
            newToken: Token = self.currentToken
            return newToken

        elif nextChar in Tokenizer.singleCharacterTokenTypeMap.keys():
            self.state = TokenizerState.DEFAULT
            self.currentToken.type = TokenType.AMPERSAND
            newToken: Token = self.currentToken
            self.currentToken = Token(Tokenizer.singleCharacterTokenTypeMap[nextChar], nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.hasExtraToken = True
            return newToken

        elif nextChar == "&":
            self.state = TokenizerState.DEFAULT
            self.currentToken = None
            newToken: Token = Token(TokenType.LOGICAL_AND, "&&", self.currentLineNumber, self.currentColumnNumber-1)
            return newToken

        elif nextChar in Tokenizer.multiCharacterTokenNextStateMap.keys():
            newToken: Token = Token(TokenType.AMPERSAND, "&", self.currentLineNumber, self.currentColumnNumber-1)
            self.currentToken = Token(TokenType.NONE, nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.state = Tokenizer.multiCharacterTokenNextStateMap[nextChar]
            return newToken

        elif nextChar == "0":
            newToken: Token = Token(TokenType.AMPERSAND, "&", self.currentLineNumber, self.currentColumnNumber-1)
            self.currentToken = Token(TokenType.NONE, "0", self.currentLineNumber, self.currentColumnNumber-1)
            self.state = TokenizerState.UNSURE_WHETHER_DECIMAL_OR_HEXADECIMAL       # need either 'x' or another digit to be sure
            return newToken

        # since decimal characters are a subset of hexadecimal characters, this elif must come before
        # the next one for hexadecimal, otherwise all decimal character (0-9) would fall through
        # into the next elif
        elif isValidDecimalCharacter(nextChar):
            newToken: Token = Token(TokenType.AMPERSAND, "&", self.currentLineNumber, self.currentColumnNumber-1)
            self.currentToken = Token(TokenType.DECIMAL_NUMBER, nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.state = TokenizerState.PROCESSING_DECIMAL_NUMBER                   
            return newToken

        # hexadecimal numbers can start with a-f which would otherwise be interpreted
        # as a name, thus this elif must go before the next one. This elif will not be
        # entered if the character is 0-9 since the previous elif handles those. The state handling the
        # processing of hexadecimal characters must check if the next character is valid
        # hexadecimal, and if not but it is valid name character, change state to
        # processing name
        elif isValidHexadecimalCharacter(nextChar):
            newToken: Token = Token(TokenType.AMPERSAND, "&", self.currentLineNumber, self.currentColumnNumber-1)
            self.currentToken = Token(TokenType.HEX_NUMBER_NO_PREFIX_OR_LABEL_OR_NODE_OR_PROPERTY, nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.state = TokenizerState.PROCESSING_HEX_NUMBER_NO_PREFIX_OR_LABEL_OR_NAME_OR_PROPERTY
            return newToken

        # the characters that occur at the beginning of a name are different than those
        # that can occur in the middle of one. For example, the numeral 0-9 can occur
        # in a name as well as underscores or dashes, but just not at the beginning
        elif isValidFirstNameCharacter(nextChar):
            newToken: Token = Token(TokenType.AMPERSAND, "&", self.currentLineNumber, self.currentColumnNumber-1)
            self.currentToken = Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.state = TokenizerState.PROCESSING_LABEL_OR_NAME_OR_PROPERTY
            return newToken

        elif nextChar == "\"":
            newToken: Token = Token(TokenType.AMPERSAND, "&", self.currentLineNumber, self.currentColumnNumber-1)
            self.currentToken = Token(TokenType.STRING, "", self.currentLineNumber, self.currentColumnNumber-1)
            self.state = TokenizerState.PROCESSING_STRING
            return newToken

        else:
            logError(f"Character: \"{nextChar}\" at line {self.currentLineNumber} is not a valid character for devicetree file.")



    """
    Callback method for the state PROCESSING_OR.

    @return Next token or None if needs more processing.
    """
    def handleStateProcessingOr(self) -> Token | None:
        nextChar = self.getNextChar()

        if nextChar is None:
            self.state = TokenizerState.DEFAULT
            self.currentToken.type = TokenType.BITWISE_OR
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.END_OF_FILE, "", self.currentLineNumber, self.currentColumnNumber-1)
            self.hasExtraToken = True
            return newToken

        elif nextChar == "\n":
            self.state = TokenizerState.DEFAULT
            self.currentToken.type = TokenType.BITWISE_OR
            newToken: Token = self.currentToken
            self.currentLineNumber += 1
            self.currentColumnNumber = 1
            return newToken

        elif isWhiteSpace(nextChar):
            self.state = TokenizerState.DEFAULT
            self.currentToken.type = TokenType.BITWISE_OR
            newToken: Token = self.currentToken
            return newToken

        elif nextChar in Tokenizer.singleCharacterTokenTypeMap.keys():
            self.state = TokenizerState.DEFAULT
            self.currentToken.type = TokenType.BITWISE_OR
            newToken: Token = self.currentToken
            self.currentToken = Token(Tokenizer.singleCharacterTokenTypeMap[nextChar], nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.hasExtraToken = True
            return newToken

        elif nextChar == "|":
            self.state = TokenizerState.DEFAULT
            self.currentToken = None
            newToken: Token = Token(TokenType.LOGICAL_OR, "||", self.currentLineNumber, self.currentColumnNumber-1)
            return newToken

        elif nextChar in Tokenizer.multiCharacterTokenNextStateMap.keys():
            newToken: Token = Token(TokenType.BITWISE_OR, "|", self.currentLineNumber, self.currentColumnNumber-1)
            self.currentToken = Token(TokenType.NONE, nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.state = Tokenizer.multiCharacterTokenNextStateMap[nextChar]
            return newToken

        elif nextChar == "0":
            newToken: Token = Token(TokenType.BITWISE_OR, "|", self.currentLineNumber, self.currentColumnNumber-1)
            self.currentToken = Token(TokenType.NONE, "0", self.currentLineNumber, self.currentColumnNumber-1)
            self.state = TokenizerState.UNSURE_WHETHER_DECIMAL_OR_HEXADECIMAL       # need either 'x' or another digit to be sure
            return newToken

        # since decimal characters are a subset of hexadecimal characters, this elif must come before
        # the next one for hexadecimal, otherwise all decimal character (0-9) would fall through
        # into the next elif
        elif isValidDecimalCharacter(nextChar):
            newToken: Token = Token(TokenType.BITWISE_OR, "|", self.currentLineNumber, self.currentColumnNumber-1)
            self.currentToken = Token(TokenType.DECIMAL_NUMBER, nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.state = TokenizerState.PROCESSING_DECIMAL_NUMBER                   
            return newToken

        # hexadecimal numbers can start with a-f which would otherwise be interpreted
        # as a name, thus this elif must go before the next one. This elif will not be
        # entered if the character is 0-9 since the previous elif handles those. The state handling the
        # processing of hexadecimal characters must check if the next character is valid
        # hexadecimal, and if not but it is valid name character, change state to
        # processing name
        elif isValidHexadecimalCharacter(nextChar):
            newToken: Token = Token(TokenType.BITWISE_OR, "|", self.currentLineNumber, self.currentColumnNumber-1)
            self.currentToken = Token(TokenType.HEX_NUMBER_NO_PREFIX_OR_LABEL_OR_NODE_OR_PROPERTY, nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.state = TokenizerState.PROCESSING_HEX_NUMBER_NO_PREFIX_OR_LABEL_OR_NAME_OR_PROPERTY
            return newToken

        # the characters that occur at the beginning of a name are different than those
        # that can occur in the middle of one. For example, the numeral 0-9 can occur
        # in a name as well as underscores or dashes, but just not at the beginning
        elif isValidFirstNameCharacter(nextChar):
            newToken: Token = Token(TokenType.BITWISE_OR, "|", self.currentLineNumber, self.currentColumnNumber-1)
            self.currentToken = Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.state = TokenizerState.PROCESSING_LABEL_OR_NAME_OR_PROPERTY
            return newToken

        elif nextChar == "\"":
            newToken: Token = Token(TokenType.BITWISE_OR, "|", self.currentLineNumber, self.currentColumnNumber-1)
            self.currentToken = Token(TokenType.STRING, "", self.currentLineNumber, self.currentColumnNumber-1)
            self.state = TokenizerState.PROCESSING_STRING
            return newToken

        else:
            logError(f"Character: \"{nextChar}\" at line {self.currentLineNumber} is not a valid character for devicetree file.")



    """
    Callback method for the state PROCESSING_EQUALS.

    @return Next token or None if needs more processing.
    """
    def handleStateProcessingEquals(self) -> Token | None:
        nextChar = self.getNextChar()

        if nextChar is None:
            self.state = TokenizerState.DEFAULT
            self.currentToken.type = TokenType.EQUALS
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.END_OF_FILE, "", self.currentLineNumber, self.currentColumnNumber-1)
            self.hasExtraToken = True
            return newToken

        elif nextChar == "\n":
            self.state = TokenizerState.DEFAULT
            self.currentToken.type = TokenType.EQUALS
            newToken: Token = self.currentToken
            self.currentLineNumber += 1
            self.currentColumnNumber = 1
            return newToken

        elif isWhiteSpace(nextChar):
            self.state = TokenizerState.DEFAULT
            self.currentToken.type = TokenType.EQUALS
            newToken: Token = self.currentToken
            return newToken

        elif nextChar in Tokenizer.singleCharacterTokenTypeMap.keys():
            self.state = TokenizerState.DEFAULT
            self.currentToken.type = TokenType.EQUALS
            newToken: Token = self.currentToken
            self.currentToken = Token(Tokenizer.singleCharacterTokenTypeMap[nextChar], nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.hasExtraToken = True
            return newToken

        elif nextChar == "=":
            self.state = TokenizerState.DEFAULT
            self.currentToken = None
            newToken: Token = Token(TokenType.DOUBLE_EQUALS, "==", self.currentLineNumber, self.currentColumnNumber-1)
            return newToken

        elif nextChar in Tokenizer.multiCharacterTokenNextStateMap.keys():
            newToken: Token = Token(TokenType.EQUALS, "=", self.currentLineNumber, self.currentColumnNumber-1)
            self.currentToken = Token(TokenType.NONE, nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.state = Tokenizer.multiCharacterTokenNextStateMap[nextChar]
            return newToken

        elif nextChar == "0":
            newToken: Token = Token(TokenType.EQUALS, "=", self.currentLineNumber, self.currentColumnNumber-1)
            self.currentToken = Token(TokenType.NONE, "0", self.currentLineNumber, self.currentColumnNumber-1)
            self.state = TokenizerState.UNSURE_WHETHER_DECIMAL_OR_HEXADECIMAL       # need either 'x' or another digit to be sure
            return newToken

        # since decimal characters are a subset of hexadecimal characters, this elif must come before
        # the next one for hexadecimal, otherwise all decimal character (0-9) would fall through
        # into the next elif
        elif isValidDecimalCharacter(nextChar):
            newToken: Token = Token(TokenType.EQUALS, "=", self.currentLineNumber, self.currentColumnNumber-1)
            self.currentToken = Token(TokenType.DECIMAL_NUMBER, nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.state = TokenizerState.PROCESSING_DECIMAL_NUMBER                   
            return newToken

        # hexadecimal numbers can start with a-f which would otherwise be interpreted
        # as a name, thus this elif must go before the next one. This elif will not be
        # entered if the character is 0-9 since the previous elif handles those. The state handling the
        # processing of hexadecimal characters must check if the next character is valid
        # hexadecimal, and if not but it is valid name character, change state to
        # processing name
        elif isValidHexadecimalCharacter(nextChar):
            newToken: Token = Token(TokenType.EQUALS, "=", self.currentLineNumber, self.currentColumnNumber-1)
            self.currentToken = Token(TokenType.HEX_NUMBER_NO_PREFIX_OR_LABEL_OR_NODE_OR_PROPERTY, nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.state = TokenizerState.PROCESSING_HEX_NUMBER_NO_PREFIX_OR_LABEL_OR_NAME_OR_PROPERTY
            return newToken

        # the characters that occur at the beginning of a name are different than those
        # that can occur in the middle of one. For example, the numeral 0-9 can occur
        # in a name as well as underscores or dashes, but just not at the beginning
        elif isValidFirstNameCharacter(nextChar):
            newToken: Token = Token(TokenType.EQUALS, "=", self.currentLineNumber, self.currentColumnNumber-1)
            self.currentToken = Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.state = TokenizerState.PROCESSING_LABEL_OR_NAME_OR_PROPERTY
            return newToken

        elif nextChar == "\"":
            newToken: Token = Token(TokenType.EQUALS, "=", self.currentLineNumber, self.currentColumnNumber-1)
            self.currentToken = Token(TokenType.STRING, "", self.currentLineNumber, self.currentColumnNumber-1)
            self.state = TokenizerState.PROCESSING_STRING
            return newToken

        else:
            logError(f"Character: \"{nextChar}\" at line {self.currentLineNumber} is not a valid character for devicetree file.")



    """
    Callback method for the state PROCESSING_NOT.

    @return Next token or None if needs more processing.
    """
    def handleStateProcessingNot(self) -> Token | None:
        nextChar = self.getNextChar()

        if nextChar is None:
            self.state = TokenizerState.DEFAULT
            self.currentToken.type = TokenType.EXCLAMATION_POINT
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.END_OF_FILE, "", self.currentLineNumber, self.currentColumnNumber-1)
            self.hasExtraToken = True
            return newToken

        elif nextChar == "\n":
            self.state = TokenizerState.DEFAULT
            self.currentToken.type = TokenType.EXCLAMATION_POINT
            newToken: Token = self.currentToken
            self.currentLineNumber += 1
            self.currentColumnNumber = 1
            return newToken

        elif isWhiteSpace(nextChar):
            self.state = TokenizerState.DEFAULT
            self.currentToken.type = TokenType.EXCLAMATION_POINT
            newToken: Token = self.currentToken
            return newToken

        elif nextChar in Tokenizer.singleCharacterTokenTypeMap.keys():
            self.state = TokenizerState.DEFAULT
            self.currentToken.type = TokenType.EXCLAMATION_POINT
            newToken: Token = self.currentToken
            self.currentToken = Token(Tokenizer.singleCharacterTokenTypeMap[nextChar], nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.hasExtraToken = True
            return newToken

        elif nextChar == "=":
            self.state = TokenizerState.DEFAULT
            self.currentToken = None
            newToken: Token = Token(TokenType.NOT_EQUALS, "!=", self.currentLineNumber, self.currentColumnNumber-1)
            return newToken

        elif nextChar in Tokenizer.multiCharacterTokenNextStateMap.keys():
            newToken: Token = Token(TokenType.EXCLAMATION_POINT, "!", self.currentLineNumber, self.currentColumnNumber-1)
            self.currentToken = Token(TokenType.NONE, nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.state = Tokenizer.multiCharacterTokenNextStateMap[nextChar]
            return newToken

        elif nextChar == "0":
            newToken: Token = Token(TokenType.EXCLAMATION_POINT, "!", self.currentLineNumber, self.currentColumnNumber-1)
            self.currentToken = Token(TokenType.NONE, "0", self.currentLineNumber, self.currentColumnNumber-1)
            self.state = TokenizerState.UNSURE_WHETHER_DECIMAL_OR_HEXADECIMAL       # need either 'x' or another digit to be sure
            return newToken

        # since decimal characters are a subset of hexadecimal characters, this elif must come before
        # the next one for hexadecimal, otherwise all decimal character (0-9) would fall through
        # into the next elif
        elif isValidDecimalCharacter(nextChar):
            newToken: Token = Token(TokenType.EXCLAMATION_POINT, "!", self.currentLineNumber, self.currentColumnNumber-1)
            self.currentToken = Token(TokenType.DECIMAL_NUMBER, nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.state = TokenizerState.PROCESSING_DECIMAL_NUMBER                   
            return newToken

        # hexadecimal numbers can start with a-f which would otherwise be interpreted
        # as a name, thus this elif must go before the next one. This elif will not be
        # entered if the character is 0-9 since the previous elif handles those. The state handling the
        # processing of hexadecimal characters must check if the next character is valid
        # hexadecimal, and if not but it is valid name character, change state to
        # processing name
        elif isValidHexadecimalCharacter(nextChar):
            newToken: Token = Token(TokenType.EXCLAMATION_POINT, "!", self.currentLineNumber, self.currentColumnNumber-1)
            self.currentToken = Token(TokenType.HEX_NUMBER_NO_PREFIX_OR_LABEL_OR_NODE_OR_PROPERTY, nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.state = TokenizerState.PROCESSING_HEX_NUMBER_NO_PREFIX_OR_LABEL_OR_NAME_OR_PROPERTY
            return newToken

        # the characters that occur at the beginning of a name are different than those
        # that can occur in the middle of one. For example, the numeral 0-9 can occur
        # in a name as well as underscores or dashes, but just not at the beginning
        elif isValidFirstNameCharacter(nextChar):
            newToken: Token = Token(TokenType.EXCLAMATION_POINT, "!", self.currentLineNumber, self.currentColumnNumber-1)
            self.currentToken = Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.state = TokenizerState.PROCESSING_LABEL_OR_NAME_OR_PROPERTY
            return newToken

        elif nextChar == "\"":
            newToken: Token = Token(TokenType.EXCLAMATION_POINT, "!", self.currentLineNumber, self.currentColumnNumber-1)
            self.currentToken = Token(TokenType.STRING, "", self.currentLineNumber, self.currentColumnNumber-1)
            self.state = TokenizerState.PROCESSING_STRING
            return newToken

        else:
            logError(f"Character: \"{nextChar}\" at line {self.currentLineNumber} is not a valid character for devicetree file.")


    """
    Callback method for the state PROCESSING_DECIMAL_NUMBER.

    @return Next token or None if needs more processing.
    """
    def handleStateProcessingDecimalNumber(self) -> Token | None:
        nextChar = self.getNextChar()

        if nextChar is None:
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.END_OF_FILE, "", self.currentLineNumber, self.currentColumnNumber-1)
            self.hasExtraToken = True
            self.state = TokenizerState.DEFAULT
            return newToken

        elif nextChar == "\n":
            self.state = TokenizerState.DEFAULT
            self.currentLineNumber += 1
            self.currentColumnNumber = 1
            return self.currentToken

        elif isWhiteSpace(nextChar):
            self.state = TokenizerState.DEFAULT
            return self.currentToken

        elif isValidDecimalCharacter(nextChar):
            self.currentToken.appendText(nextChar)
            return None

        elif isValidHexadecimalCharacter(nextChar):
            self.currentToken.type = TokenType.HEXADECIMAL_NUMBER
            self.state = TokenizerState.PROCESSING_HEXADECIMAL_NUMBER
            self.currentToken.appendText(nextChar)
            return None

        elif nextChar in Tokenizer.singleCharacterTokenTypeMap.keys():
            newToken: Token = self.currentToken
            self.state = TokenizerState.DEFAULT
            self.currentToken = Token(Tokenizer.singleCharacterTokenTypeMap[nextChar], nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.hasExtraToken = True
            return newToken

        elif nextChar in Tokenizer.multiCharacterTokenNextStateMap.keys():
            newToken: Token = self.currentToken
            self.state = Tokenizer.multiCharacterTokenNextStateMap[nextChar]
            self.currentToken = Token(TokenType.NONE, nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            return newToken

        # largest subset: decimal < hexadecimal < label < node name, property name
        # if character is any of '_', '-', '+', ',', '.' then raise error. Should
        # not get here if syntactically correct
        elif isValidNodeNameOrPropertyCharacter(nextChar):
            logError(f"Syntax error at line {self.currentLineNumber}, column {self.currentColumnNumber}.\
                              Expected characters [0-9], [a-f], or [A-F]. Encountered: {nextChar}.")

        elif nextChar == "\"":
            logError(f"Error occurred during tokenization. Unexpected character: {nextChar} at line {self.currentLineNumber} should not appear in device tree name.")

        else:
            logError(f"Character: \"{nextChar}\" at line {self.currentLineNumber} is not a valid character for devicetree file.")



    """
    Callback method for the state UNSURE_WHETHER_DECIMAL_OR_HEXADECIMAL.
    This state occurs at the beginning of a number

    @return Next token or None if needs more processing.
    """
    def handleStateUnsureWhetherDecimalOrHexadecimal(self) -> Token | None:
        nextChar = self.getNextChar()

        if nextChar is None:
            self.currentToken.type = TokenType.DECIMAL_NUMBER
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.END_OF_FILE, "", self.currentLineNumber, self.currentColumnNumber-1)
            self.hasExtraToken = True
            self.state = TokenizerState.DEFAULT
            return newToken

        elif nextChar == "\n":
            self.currentToken.type = TokenType.DECIMAL_NUMBER
            self.state = TokenizerState.DEFAULT
            self.currentLineNumber += 1
            self.currentColumnNumber = 1
            return self.currentToken

        elif isWhiteSpace(nextChar):
            self.currentToken.type = TokenType.DECIMAL_NUMBER
            self.state = TokenizerState.DEFAULT
            return self.currentToken

        elif isValidDecimalCharacter(nextChar):
            self.state = TokenizerState.PROCESSING_DECIMAL_NUMBER
            self.currentToken.type = TokenType.DECIMAL_NUMBER
            self.currentToken.appendText(nextChar)
            return None

        elif isValidHexadecimalCharacter(nextChar):
            self.state = TokenizerState.PROCESSING_HEXADECIMAL_NUMBER
            self.currentToken.type = TokenType.HEXADECIMAL_NUMBER
            self.currentToken.appendText(nextChar)
            return None

        elif nextChar == "x":
            self.currentToken.type = TokenType.HEXADECIMAL_NUMBER
            self.currentToken.appendText(nextChar)
            self.state = TokenizerState.PROCESSING_HEXADECIMAL_NUMBER
            return None

        elif nextChar in Tokenizer.singleCharacterTokenTypeMap.keys():
            self.currentToken.type = TokenType.DECIMAL_NUMBER
            newToken: Token = self.currentToken
            self.currentToken = Token(Tokenizer.singleCharacterTokenTypeMap[nextChar], nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.hasExtraToken = True
            self.state = TokenizerState.DEFAULT
            return newToken

        elif nextChar in Tokenizer.multiCharacterTokenNextStateMap.keys():
            self.currentToken.type = TokenType.DECIMAL_NUMBER
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.NONE, nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.state = Tokenizer.multiCharacterTokenNextStateMap[nextChar]
            return newToken

        # largest subset of valid characters. decimal < hexadecimal < node label < node name, property name
        elif isValidNodeNameOrPropertyCharacter(nextChar):
            logError(f"Error occurred during tokenization. Unexpected character: {nextChar} at line {self.currentLineNumber} should not appear in device tree number.")

        elif nextChar == "\"":
            logError(f"Error occurred during tokenization. Unexpected character: {nextChar} at line {self.currentLineNumber} should not appear in device tree name.")

        else:
            logError(f"Character: \"{nextChar}\" at line {self.currentLineNumber} is not a valid character for devicetree file.")



    """
    Callback method for the state PROCESSING_HEXADECIMAL_NUMBER.
    This state occurs when the tokenizer is processing a hexadecimal number.

    @return Next token or None if needs more processing.
    """
    def handleStateProcessingHexadecimalNumber(self) -> Token | None:
        nextChar = self.getNextChar()

        if nextChar is None:
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.END_OF_FILE, "", self.currentLineNumber, self.currentColumnNumber-1)
            self.hasExtraToken = True
            self.state = TokenizerState.DEFAULT
            return newToken
        
        elif nextChar == "\n":
            self.state = TokenizerState.DEFAULT
            self.currentLineNumber += 1
            self.currentColumnNumber = 1
            return self.currentToken

        elif isWhiteSpace(nextChar):
            self.state = TokenizerState.DEFAULT
            return self.currentToken

        elif isValidHexadecimalCharacter(nextChar):
            self.currentToken.appendText(nextChar)
            return None

        elif nextChar in Tokenizer.singleCharacterTokenTypeMap.keys():
            self.currentToken.type = TokenType.HEXADECIMAL_NUMBER
            newToken: Token = self.currentToken
            self.currentToken = Token(Tokenizer.singleCharacterTokenTypeMap[nextChar], nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.hasExtraToken = True
            self.state = TokenizerState.DEFAULT
            return newToken

        elif nextChar in Tokenizer.multiCharacterTokenNextStateMap.keys():
            self.currentToken.type = TokenType.HEXADECIMAL_NUMBER
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.NONE, nextChar, self.currentLineNumber, self.currentColumnNumber-1)
            self.state = Tokenizer.multiCharacterTokenNextStateMap[nextChar]
            return newToken

        elif isValidNodeNameOrPropertyCharacter(nextChar):
            logError(f"Error occurred during tokenization. Unexpected character: {nextChar} at line {self.currentLineNumber} should not appear in device tree number.")

        elif nextChar == "\"":
            logError(f"Error occurred during tokenization. Unexpected character: {nextChar} at line {self.currentLineNumber} should not appear in device tree name.")

        else:
            logError(f"Character: \"{nextChar}\" at line {self.currentLineNumber} is not a valid character for devicetree file.")




    """
    Callback method for the state PROCESSING_STRING. This
    state occurs when the tokenizer is in the middle of processing a string
    (i.e. it has encountered one " character but not the second).

    @return Next token or None if needs more processing.
    """
    def handleStateProcessingString(self) -> Token | None:
        nextChar = self.getNextChar()

        if nextChar is None:
            logError(f"Error occurred during tokenization at line {self.currentLineNumber}. No matching \" for string: {self.currentToken.value}.")

        elif nextChar == "\n":
            logError(f"Error occurred during tokenization at line {self.currentLineNumber}. Cannot have newline in middle of string.")

        elif nextChar == "\"":
            self.state = TokenizerState.DEFAULT
            return self.currentToken

        else:
            self.currentToken.appendText(nextChar)
            return None




    # This is the callback table for the methods that implement each state
    stateCallbacks = {
        TokenizerState.DEFAULT : handleStateDefault,
        TokenizerState.PROCESSING_HEX_NUMBER_NO_PREFIX_OR_LABEL_OR_NAME_OR_PROPERTY : handleStateProcessingHexNumberOrLabelOrNameOrProperty,
        TokenizerState.PROCESSING_LABEL_OR_NAME_OR_PROPERTY : handleStateProcessingLabelOrNameOrProperty,
        TokenizerState.PROCESSING_NAME_OR_PROPERTY : handleStateProcessingNameOrProperty,
        TokenizerState.PROCESSING_DECIMAL_NUMBER : handleStateProcessingDecimalNumber,
        TokenizerState.UNSURE_WHETHER_DECIMAL_OR_HEXADECIMAL : handleStateUnsureWhetherDecimalOrHexadecimal,
        TokenizerState.PROCESSING_HEXADECIMAL_NUMBER : handleStateProcessingHexadecimalNumber,
        TokenizerState.PROCESSING_STRING : handleStateProcessingString,
        TokenizerState.PROCESSING_AMPERSAND : handleStateProcessingAmpersand,
        TokenizerState.PROCESSING_LEFT_ANGLE_BRACKET : handleStateProcessingLeftAngleBracket,
        TokenizerState.PROCESSING_RIGHT_ANGLE_BRACKET : handleStateProcessingRightAngleBracket,
        TokenizerState.PROCESSING_OR : handleStateProcessingOr,
        TokenizerState.PROCESSING_EQUALS : handleStateProcessingEquals,
        TokenizerState.PROCESSING_NOT : handleStateProcessingNot
    }


    """
    Resets the tokenization process to the beginning. Sets state
    to DEFAULT, sets current index into string back to 0. 
    """
    def resetTokenization(self, newStringToTokenize=None):
        self.state = TokenizerState.DEFAULT
        self.currentStringIndex = 0
        self.currentToken = None
        self.hasExtraToken = False
        self.currentColumnNumber = 1
        self.currentLineNumber = 1

        if newStringToTokenize is not None:
            self.stringToTokenize = newStringToTokenize


    """
    Sets a new string to tokenize.

    @param newStringToTokenize string to perform tokenization on
    """
    def setStringToTokenize(self, newStringToTokenize: str):
        self.state = TokenizerState.DEFAULT
        self.currentStringIndex = 0
        self.currentToken = None
        self.hasExtraToken = False
        self.currentColumnNumber = 1
        self.currentLineNumber = 1
        
        if newStringToTokenize is not None:
            self.stringToTokenize = newStringToTokenize
        else:
            self.stringToTokenize = ""


    """
    Returns the next token from the string (text of device tree file).

    @return Next token.
    """
    def getNextToken(self) -> Token:

        if self.hasExtraToken:
            newToken = self.currentToken
            self.currentToken = None
            self.hasExtraToken = False
            return newToken


        nextToken = self.stateCallbacks[self.state](self)

        while nextToken is None:
            nextToken = self.stateCallbacks[self.state](self)

        return nextToken




