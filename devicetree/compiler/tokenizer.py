
from enum import Enum



'''
@class TokenType

Enum which defines the type or class of the token
'''
class TokenType(Enum):
    TOKEN_TYPE_NONE = 0
    TOKEN_TYPE_LEFT_CURLY_BRACE = 1
    TOKEN_TYPE_RIGHT_CURLY_BRACE = 2
    TOKEN_TYPE_COLON = 3
    TOKEN_TYPE_HEXADECIMAL_NUMBER = 4
    TOKEN_TYPE_DECIMAL_NUMBER = 5
    TOKEN_TYPE_STRING = 6
    TOKEN_TYPE_HASHTAG = 7
    TOKEN_TYPE_AT_SYMBOL = 8
    TOKEN_TYPE_SEMICOLON = 9
    TOKEN_TYPE_LEFT_ANGLE_BRACKET = 10
    TOKEN_TYPE_RIGHT_ANGLE_BRACKET = 11
    TOKEN_TYPE_PHANDLE_REFERENCE = 12
    TOKEN_TYPE_EQUALS = 13
    TOKEN_TYPE_NAME = 14                     # Name of a node or a property or a node label
    TOKEN_TYPE_COMMA = 15
    TOKEN_TYPE_END_OF_FILE = 16
    TOKEN_TYPE_FORWARD_SLASH = 17
    TOKEN_TYPE_NEWLINE = 18



'''
@class Token

Class representing a parsed token. The token class (type) and
value are stored here.
'''
class Token:

    # for keeping track of token numbers
    nextIDNumber = 0

    @classmethod
    def incrementID(cls):
        cls.nextIDNumber += 1


    def __init__(self, type: TokenType, value: str):
        self.type = type
        self.value = value
        self.id = self.nextIDNumber
        Token.incrementID()

    def __str__(self):
        return f"Type: {self.type}, Value: {self.value}."

    def appendText(self, newChar: str):
        self.value = self.value + newChar



'''
@class TokenizerState

Enum representing the state of the tokenizer state machine. It should be noted here
that "hex numbers" and "decimal numbers" do not have their typical meaning. In the
device tree files, any number can be a hex number, but only some are explicitly
marked as hex with the "0x" prefix. These are processed as hex numbers and any number
that is not marked with "0x" prefix is processed as decimal. This is all syntactically
speaking; the interpretation of the semantic value of the numbers is not considered
in the tokenizer.
'''
class TokenizerState(Enum):
    TOKENIZER_STATE_DEFAULT = 0
    TOKENIZER_STATE_PROCESSING_NAME = 1
    TOKENIZER_STATE_PROCESSING_DECIMAL_NUMBER = 2
    TOKENIZER_STATE_UNSURE_WHETHER_DECIMAL_OR_HEXADECIMAL = 3
    TOKENIZER_STATE_PROCESSING_HEXADECIMAL_NUMBER = 4
    TOKENIZER_STATE_PROCESSING_STRING = 5
    TOKENIZER_STATE_PROCESSING_PHANDLE_REFERENCE = 6



'''
Returns whether the given character is a whitespace character (space, tab, newline)

@param nextChar Character to check if whitespace
@return True if whitespace, False otherwise
'''
def isWhiteSpace(nextChar: str):
    return nextChar.isspace()




'''
Returns whether the next character is a valid name character. Since the
character set for node names and labels is a subset of the character
set for property names (property names can have # and ?), the larger
set is taken as a general name class and then later the proper name
format checking is done.

@param nextChar Character to check.
@return True if name character, False otherwise.
'''
def isValidNameCharacter(nextChar: str):
    return nextChar.isalnum() or nextChar == "," or nextChar == "." \
        or nextChar == "_" or nextChar == "+" or nextChar == "?" \
        or nextChar == "#" or nextChar == "-"




'''
Returns whether the next character is a valid character to be
the first character in a name. Names must start with an upper
or lowercase letter but after that can have numbers, etc. This
is different from @ref isValidNameCharacter, which checks if a
character is valid anywhere in the name.

@param nextChar Character to check.
@return True if valid first character for name, False otherwise.
'''
def isValidFirstNameCharacter(nextChar: str):
    return nextChar.isalpha()



'''
Checks whether the character is a valid hexadecimal character.
The valid hex characters are a subset of valid name characters, so
this must be checked first or it will never be called.

@param nextChar Character to check.
@return True if hex, False if not.
'''
def isValidHexadecimalCharacter(nextChar: str):
    return nextChar.isdigit() or (nextChar >= 'a' and nextChar <= 'f') or (nextChar >= 'A' and nextChar <= 'F')




'''
@class Tokenizer

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
character is encountered.

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
(TOKEN_TYPE_AT_SYMBOL). Thus, when this is encountered, the function would either return
2 tokens at once, which kinda breaks the intended API for the tokenizer, or it can
store the token in the self.currentToken variable and set the self.hasExtraToken flag. The
getNextToken method then checks this flag to see if there is a token ready for it and
if so returns it and resets the flag.

The various states of the state machine also bear some explaining. The "default" state is
represented by TOKENIZER_STATE_DEFAULT. This occurs when the tokenizer is not in the middle
of processing something such as a name, number, etc. The tokenizer starts in this state and
returns to this state at the end of processing any token. The method that implements the
processing for this state is @ref handleStateDefault. If the tokenizer encounters a valid
character to start a device tree name (node or property), it changes to the state
TOKENIZER_STATE_PROCESSING_NAME, which is implemented by the @ref handleStateProcessingName
method. It will remain in that state until a valid terminating character is encountered at
which point it will move back to the default state. The same is true for the states
TOKENIZER_STATE_PROCESSING_STRING and TOKENIZER_STATE_PROCESSING_PHANDLE_REFERENCE, except
that the former is entered when processing string literals, and the latter is entered when
processing so-called phandle references, i.e. &node-name (often used to override properties
created in previous node definitions). There is a bit of trickiness with the states
TOKENIZER_STATE_PROCESSING_DECIMAL_NUMBER and TOKENIZER_STATE_PROCESSING_HEXADECIMAL_NUMBER
since hex numbers begin with 0x, and thus the tokenizer would see the first character as a
"0" and move to the TOKENIZER_STATE_PROCESSING_DECIMAL_NUMBER state, and then see an "x" and
raise an error. To avoid this, the tokenizer will move into the state
TOKENIZER_STATE_UNSURE_WHETHER_DECIMAL_OR_HEXADECIMAL and then move to either 
TOKENIZER_STATE_PROCESSING_DECIMAL_NUMBER if more digits are encountered or to
TOKENIZER_STATE_PROCESSING_HEXADECIMAL_NUMBER if an "x" is encountered.

TODO: Some other issues with state machine processing include that it is common practice in device
tree files to omit the "0x" prefix on hex numbers in the node declaration. For example,
in the declaration "uart1: uart@bfc04000", the "0x" prefix has been omitted from the hex 
number "bfc04000". The tokenizer would otherwise process this as a name and then the parser
would raise an error since a name cannot appear there in the grammar. To fix this (partially),
the state processing for TOKENIZER_STATE_PROCESSING_NAME will move to the state
TOKENIZER_STATE_PROCESSING_DECIMAL_NUMBER if a digit is encountered. This leaves two problems.
First, a name that starts with valid hex characters and ends with numbers will never be
interpreted as a name. For example "feed123" cannot be used as a name since the tokenizer will
see the "123" and lex it as a decimal number. Second, valid hex numbers may still be interpreted
as names when the "0x" prefix is left off since for example "0xcafebabe" or "0xdeadbeef" become
"cafebabe" and "deadbeef" when the "0x" prefix is removed, both of which are valid names.
'''
class Tokenizer:




    def __init__(self, stringToTokenize: str):
        self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
        self.stringToTokenize = stringToTokenize
        self.currentStringIndex = 0
        self.currentLineNumber = 1


        # stores the current token
        self.currentToken = None

        # sometimes one token will be terminated by a character
        # that is an entire token in itself, so the getNextToken
        # function should technically return two tokens at once.
        # This breaks the API for that function, so the extra token
        # is stored in the self.currentToken member and this flag
        # is set.
        self.hasExtraToken = False



    '''
    Returns the text of the current line (defined by the current line number).

    @return The current line.
    '''
    def getCurrentLine(self) -> str:
        return self.stringToTokenize.split("\n")[self.currentLineNumber-1]


    '''
    Returns the number of the current line but not the text of it.

    @return The current line number.
    '''
    def getCurrentLineNumber(self) -> int:
        return self.currentLineNumber



    '''
    Gets the next character from the string to tokenize (the text of the
    device tree file).

    @return The next character in the string.
    '''
    def getNextChar(self) -> str:
        nextChar: str = None

        if self.currentStringIndex < len(self.stringToTokenize):
            nextChar = self.stringToTokenize[self.currentStringIndex]
            self.currentStringIndex += 1

        return nextChar



    ####################################################
    # The next section contains the callback methods 
    # for implementing each state in the state machine.
    ####################################################


    '''
    Callback function for processing the TOKENIZER_STATE_DEFAULT state.

    @return Next token or None if needs more processing.
    '''
    def handleStateDefault(self) -> Token:
        nextChar: str = self.getNextChar()

        if nextChar is None:
            newToken: Token = Token(TokenType.TOKEN_TYPE_END_OF_FILE, None)
            return newToken

        # this has to go before the next elif since \n is whitespace
        elif nextChar == "\n":
            self.currentLineNumber += 1
            return None
        elif isWhiteSpace(nextChar):
            return None
        elif nextChar == "0":
            self.currentToken = Token(TokenType.TOKEN_TYPE_NONE, "0")
            self.state = TokenizerState.TOKENIZER_STATE_UNSURE_WHETHER_DECIMAL_OR_HEXADECIMAL       # need either 'x' or another digit to be sure
            return None

        # hexadecimal numbers can start with a-f which would otherwise be interpreted
        # as a name, thus this elif must go before the next one. The state handling the
        # processing of hexadecimal characters must check if the next character is valid
        # hexadecimal, and if not but it is valid name character, change state to
        # processing name
        elif isValidHexadecimalCharacter(nextChar):
            self.currentToken = Token(TokenType.TOKEN_TYPE_DECIMAL_NUMBER, nextChar)
            self.state = TokenizerState.TOKENIZER_STATE_PROCESSING_DECIMAL_NUMBER                   
            return None
        elif isValidFirstNameCharacter(nextChar):
            self.currentToken = Token(TokenType.TOKEN_TYPE_NAME, nextChar)
            self.state = TokenizerState.TOKENIZER_STATE_PROCESSING_NAME
            return None
        elif nextChar == "{":
            newToken: Token = Token(TokenType.TOKEN_TYPE_LEFT_CURLY_BRACE, "{")
            return newToken
        elif nextChar == "}":
            newToken: Token = Token(TokenType.TOKEN_TYPE_RIGHT_CURLY_BRACE, "}")
            return newToken
        elif nextChar == ":":
            newToken: Token = Token(TokenType.TOKEN_TYPE_COLON, ":")
            return newToken
        elif nextChar == "/":
            newToken: Token = Token(TokenType.TOKEN_TYPE_FORWARD_SLASH, "/")
            return newToken
        elif nextChar == "\"":
            self.currentToken = Token(TokenType.TOKEN_TYPE_STRING, "")
            self.state = TokenizerState.TOKENIZER_STATE_PROCESSING_STRING
            return None
        elif nextChar == "#":
            newToken: Token = Token(TokenType.TOKEN_TYPE_HASHTAG, "#")
            return newToken
        elif nextChar == "@":
            newToken: Token = Token(TokenType.TOKEN_TYPE_AT_SYMBOL, "@")
            return newToken
        elif nextChar == ";":
            newToken: Token = Token(TokenType.TOKEN_TYPE_SEMICOLON, ";")
            return newToken
        elif nextChar == "<":
            newToken: Token = Token(TokenType.TOKEN_TYPE_LEFT_ANGLE_BRACKET, "<")
            return newToken
        elif nextChar == ">":
            newToken: Token = Token(TokenType.TOKEN_TYPE_RIGHT_ANGLE_BRACKET, ">")
            return newToken
        elif nextChar == "&":
            self.currentToken = Token(TokenType.TOKEN_TYPE_PHANDLE_REFERENCE, "&")
            self.state = TokenizerState.TOKENIZER_STATE_PROCESSING_PHANDLE_REFERENCE
            return None
        elif nextChar == "=":
            newToken: Token = Token(TokenType.TOKEN_TYPE_EQUALS, "=")
            return newToken
        elif nextChar == ",":
            newToken: Token = Token(TokenType.TOKEN_TYPE_COMMA, ",")
            return newToken
        else:
            raise ValueError(f"Character: \"{nextChar}\" at line {self.currentLineNumber} is not a valid character for devicetree file.")



    '''
    Callback method for the state TOKENIZER_STATE_PROCESSING_NAME.

    @return Next token or None if needs more processing.
    '''
    def handleStateProcessingName(self) -> Token:
        nextChar: str = self.getNextChar()

        if nextChar is None:
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_END_OF_FILE, None)
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == "\n":
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            self.currentLineNumber += 1
            return self.currentToken

        elif isWhiteSpace(nextChar):
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return self.currentToken

        elif isValidNameCharacter(nextChar):
            self.currentToken.appendText(nextChar)
            return None

        elif nextChar == "{":
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_LEFT_CURLY_BRACE, "{")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == "}":
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_RIGHT_CURLY_BRACE, "}")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == ":":
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_COLON, ":")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == "\"":
            raise ValueError(f"Error occurred during tokenization. Unexpected character: {nextChar} at line {self.currentLineNumber} should not appear in device tree name.")

        elif nextChar == "@":
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_AT_SYMBOL, "@")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == ";":
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_SEMICOLON, ";")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == "<":
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_LEFT_ANGLE_BRACKET, "<")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == ">":
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_RIGHT_ANGLE_BRACKET, ">")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == "&":
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_PHANDLE_REFERENCE, "&")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == "=":
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_EQUALS, "=")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == ",":
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_COMMA, ",")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        else:
            raise ValueError(f"Character: \"{nextChar}\" at line {self.currentLineNumber} is not a valid character for devicetree file.")




    '''
    Callback method for the state TOKENIZER_STATE_PROCESSING_DECIMAL_NUMBER.

    @return Next token or None if needs more processing.
    '''
    def handleStateProcessingDecimalNumber(self) -> Token:
        nextChar: str = self.getNextChar()

        if nextChar is None:
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_END_OF_FILE, None)
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == "\n":
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            self.currentLineNumber += 1
            return self.currentToken

        elif isWhiteSpace(nextChar):
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return self.currentToken

        elif isValidHexadecimalCharacter(nextChar):
            self.currentToken.appendText(nextChar)
            return None

        elif isValidNameCharacter(nextChar):
            self.currentToken.appendText(nextChar)
            self.currentToken.type = TokenType.TOKEN_TYPE_NAME
            self.state = TokenizerState.TOKENIZER_STATE_PROCESSING_NAME
            return None

        elif nextChar == "{":
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_LEFT_CURLY_BRACE, "{")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == "}":
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_RIGHT_CURLY_BRACE, "}")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == ":":
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_COLON, ":")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == "\"":
            raise ValueError(f"Error occurred during tokenization. Unexpected character: {nextChar} at line {self.currentLineNumber} should not appear in device tree name.")

        elif nextChar == "@":
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_AT_SYMBOL, "@")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == ";":
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_SEMICOLON, ";")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == "<":
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_LEFT_ANGLE_BRACKET, "<")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == ">":
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_RIGHT_ANGLE_BRACKET, ">")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == "&":
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_PHANDLE_REFERENCE, "&")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == "=":
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_EQUALS, "=")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == ",":
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_COMMA, ",")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        else:
            raise ValueError(f"Character: \"{nextChar}\" at line {self.currentLineNumber} is not a valid character for devicetree file.")



    '''
    Callback method for the state TOKENIZER_STATE_UNSURE_WHETHER_DECIMAL_OR_HEXADECIMAL.
    This state occurs at the beginning of a number

    @return Next token or None if needs more processing.
    '''
    def handleStateUnsureWhetherDecimalOrHexadecimal(self) -> Token:
        nextChar: str = self.getNextChar()

        if nextChar is None:
            self.currentToken.type = TokenType.TOKEN_TYPE_DECIMAL_NUMBER
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_END_OF_FILE, None)
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken
        
        elif nextChar == "\n":
            self.currentToken.type = TokenType.TOKEN_TYPE_DECIMAL_NUMBER
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            self.currentLineNumber += 1
            return self.currentToken

        elif isWhiteSpace(nextChar):
            self.currentToken.type = TokenType.TOKEN_TYPE_DECIMAL_NUMBER
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return self.currentToken
        
        elif isValidHexadecimalCharacter(nextChar):
            self.currentToken.type = TokenType.TOKEN_TYPE_DECIMAL_NUMBER
            self.currentToken.appendText(nextChar)
            return None

        elif nextChar == "x":
            self.currentToken.type = TokenType.TOKEN_TYPE_HEXADECIMAL_NUMBER
            self.currentToken.appendText(nextChar)
            self.state = TokenizerState.TOKENIZER_STATE_PROCESSING_HEXADECIMAL_NUMBER
            return None

        elif isValidNameCharacter(nextChar):
            raise ValueError(f"Error occurred during tokenization. Unexpected character: {nextChar} at line {self.currentLineNumber} should not appear in device tree number.")
        
        elif nextChar == "{":
            self.currentToken.type = TokenType.TOKEN_TYPE_DECIMAL_NUMBER
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_LEFT_CURLY_BRACE, "{")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == "}":
            self.currentToken.type = TokenType.TOKEN_TYPE_DECIMAL_NUMBER
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_RIGHT_CURLY_BRACE, "}")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == ":":
            self.currentToken.type = TokenType.TOKEN_TYPE_DECIMAL_NUMBER
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_COLON, ":")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == "\"":
            raise ValueError(f"Error occurred during tokenization. Unexpected character: {nextChar} at line {self.currentLineNumber} should not appear in device tree name.")

        elif nextChar == "@":
            self.currentToken.type = TokenType.TOKEN_TYPE_DECIMAL_NUMBER
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_AT_SYMBOL, "@")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == ";":
            self.currentToken.type = TokenType.TOKEN_TYPE_DECIMAL_NUMBER
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_SEMICOLON, ";")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == "<":
            self.currentToken.type = TokenType.TOKEN_TYPE_DECIMAL_NUMBER
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_LEFT_ANGLE_BRACKET, "<")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == ">":
            self.currentToken.type = TokenType.TOKEN_TYPE_DECIMAL_NUMBER
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_RIGHT_ANGLE_BRACKET, ">")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == "&":
            self.currentToken.type = TokenType.TOKEN_TYPE_DECIMAL_NUMBER
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_PHANDLE_REFERENCE, "&")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == "=":
            self.currentToken.type = TokenType.TOKEN_TYPE_DECIMAL_NUMBER
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_EQUALS, "=")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == ",":
            self.currentToken.type = TokenType.TOKEN_TYPE_DECIMAL_NUMBER
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_COMMA, ",")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        else:
            raise ValueError(f"Character: \"{nextChar}\" at line {self.currentLineNumber} is not a valid character for devicetree file.")




    '''
    Callback method for the state TOKENIZER_STATE_PROCESSING_HEXADECIMAL_NUMBER.
    This state occurs when the tokenizer is processing a hexadecimal number.

    @return Next token or None if needs more processing.
    '''
    def handleStateProcessingHexadecimalNumber(self) -> Token:
        nextChar: str = self.getNextChar()

        if nextChar is None:
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_END_OF_FILE, None)
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken
        
        elif nextChar == "\n":
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            self.currentLineNumber += 1
            return self.currentToken
        
        elif isWhiteSpace(nextChar):
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return self.currentToken
        
        elif isValidHexadecimalCharacter(nextChar):
            self.currentToken.appendText(nextChar)
            return None

        elif isValidNameCharacter(nextChar):
            raise ValueError(f"Error occurred during tokenization. Unexpected character: {nextChar} at line {self.currentLineNumber} should not appear in device tree number.")

        elif nextChar == "{":
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_LEFT_CURLY_BRACE, "{")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == "}":
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_RIGHT_CURLY_BRACE, "}")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == ":":
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_COLON, ":")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == "\"":
            raise ValueError(f"Error occurred during tokenization. Unexpected character: {nextChar} at line {self.currentLineNumber} should not appear in device tree name.")

        elif nextChar == "@":
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_AT_SYMBOL, "@")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == ";":
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_SEMICOLON, ";")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == "<":
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_LEFT_ANGLE_BRACKET, "<")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == ">":
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_RIGHT_ANGLE_BRACKET, ">")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == "&":
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_PHANDLE_REFERENCE, "&")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == "=":
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_EQUALS, "=")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == ",":
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_COMMA, ",")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        else:
            raise ValueError(f"Character: \"{nextChar}\" at line {self.currentLineNumber} is not a valid character for devicetree file.")




    '''
    Callback method for the state TOKENIZER_STATE_PROCESSING_STRING. This
    state occurs when the tokenizer is in the middle of processing a string
    (i.e. it has encountered one " character but not the second).

    @return Next token or None if needs more processing.
    '''
    def handleStateProcessingString(self) -> Token:
        nextChar: str = self.getNextChar()

        if nextChar is None:
            raise ValueError(f"Error occurred during tokenization at line {self.currentLineNumber}. No matching \" for string: {self.currentToken.value}.")

        elif nextChar == "\n":
            raise ValueError(f"Error occurred during tokenization at line {self.currentLineNumber}. Cannot have newline in middle of string.")


        elif nextChar == "\"":
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return self.currentToken

        else:
            self.currentToken.appendText(nextChar)
            return None



    '''
    Callback method for the state TOKENIZER_STATE_PROCESSING_PHANDLE_REFERENCE.
    This state occurs when the tokenizer is in the middle of processing a phandle
    reference. A phandle reference is a name of the form: &label1 or &path/to/node.

    @return Next token or None if needs more processing.
    '''
    def handleStateProcessingPhandleReference(self) -> Token:
        nextChar: str = self.getNextChar()

        if nextChar is None:
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_END_OF_FILE, None)
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken
        
        elif nextChar == "\n":
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            self.currentLineNumber += 1
            return self.currentToken
        
        elif isWhiteSpace(nextChar):
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return self.currentToken

        elif isValidNameCharacter(nextChar):
            self.currentToken.appendText(nextChar)
            return None

        elif nextChar == "{":
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_LEFT_CURLY_BRACE, "{")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == "}":
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_RIGHT_CURLY_BRACE, "}")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == ":":
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_COLON, ":")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == "\"":
            raise ValueError(f"Error occurred during tokenization. Unexpected character: {nextChar} at line {self.currentLineNumber} should not appear in device tree name.")

        elif nextChar == "@":
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_AT_SYMBOL, "@")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == ";":
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_SEMICOLON, ";")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == "<":
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_LEFT_ANGLE_BRACKET, "<")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == ">":
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_RIGHT_ANGLE_BRACKET, ">")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == "&":
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_PHANDLE_REFERENCE, "&")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == "=":
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_EQUALS, "=")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == ",":
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_COMMA, ",")
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken

        elif nextChar == "/":
            self.currentToken.appendText(nextChar)
            return None

        else:
            raise ValueError(f"Character: \"{nextChar}\" at line {self.currentLineNumber} is not a valid character for devicetree file.")



    # This is the callback table for the methods that implement each state
    stateCallbacks = {
        TokenizerState.TOKENIZER_STATE_DEFAULT : handleStateDefault,
        TokenizerState.TOKENIZER_STATE_PROCESSING_NAME : handleStateProcessingName,
        TokenizerState.TOKENIZER_STATE_PROCESSING_DECIMAL_NUMBER : handleStateProcessingDecimalNumber,
        TokenizerState.TOKENIZER_STATE_UNSURE_WHETHER_DECIMAL_OR_HEXADECIMAL : handleStateUnsureWhetherDecimalOrHexadecimal,
        TokenizerState.TOKENIZER_STATE_PROCESSING_HEXADECIMAL_NUMBER : handleStateProcessingHexadecimalNumber,
        TokenizerState.TOKENIZER_STATE_PROCESSING_STRING : handleStateProcessingString,
        TokenizerState.TOKENIZER_STATE_PROCESSING_PHANDLE_REFERENCE : handleStateProcessingPhandleReference
    }



    '''
    Resets the tokenization process to the beginning.
    '''
    def resetTokenization(self):
        self.state =TokenizerState.TOKENIZER_STATE_DEFAULT
        self.currentStringIndex = 0
        self.currentToken = None
        self.hasExtraToken = False



    '''
    Returns the next token from the string (text of device tree file).

    @return Next token.
    '''
    def getNextToken(self) -> Token:

        if self.hasExtraToken:
            newToken: Token = self.currentToken
            self.currentToken = None
            self.hasExtraToken = False
            return newToken


        nextToken: Token = self.stateCallbacks[self.state](self)

        while nextToken == None:
            nextToken = self.stateCallbacks[self.state](self)
        

        return nextToken

    


