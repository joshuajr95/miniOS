
from enum import Enum


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
    TOKEN_TYPE_WHITESPACE = 13
    TOKEN_TYPE_EQUALS = 14
    TOKEN_TYPE_NAME = 15                     # Name of a node or a property or a node label
    TOKEN_TYPE_COMMA = 16
    TOKEN_TYPE_END_OF_FILE = 17
    TOKEN_TYPE_FORWARD_SLASH = 18
    TOKEN_TYPE_NEWLINE = 19


class Token:
    def __init__(self, type: TokenType, value: str):
        self.type = type
        self.value = value
    
    def __str__(self):
        return f"Type: {self.type}, Value: {self.value}."
    
    def appendText(self, newChar: str):
        self.value = self.value + newChar



class TokenizerState(Enum):
    TOKENIZER_STATE_DEFAULT = 0
    TOKENIZER_STATE_PROCESSING_NAME = 1
    TOKENIZER_STATE_PROCESSING_DECIMAL_NUMBER = 2
    TOKENIZER_STATE_UNSURE_WHETHER_DECIMAL_OR_HEXADECIMAL = 3
    TOKENIZER_STATE_PROCESSING_HEXADECIMAL_NUMBER = 4
    TOKENIZER_STATE_PROCESSING_STRING = 5
    TOKENIZER_STATE_PROCESSING_PHANDLE_REFERENCE = 6



def isWhiteSpace(nextChar: str):
    return nextChar.isspace()

def isValidNameCharacter(nextChar: str):
    return nextChar.isalnum() or nextChar == "," or nextChar == "." \
        or nextChar == "_" or nextChar == "+" or nextChar == "?" \
        or nextChar == "#" or nextChar == "-"

'''
The difference between this and the above function is
that a name must start with a upper or lowercase letter
but can have any of the other characters after that. This
distinguishes it from numbers which start with digits.
'''
def isValidFirstNameCharacter(nextChar: str):
    return nextChar.isalpha()


def isValidHexadecimalCharacter(nextChar: str):
    return nextChar.isdigit() or (nextChar >= 'a' and nextChar <= 'f') or (nextChar >= 'A' and nextChar <= 'F')


class TokenizerStateMachine:


    def __init__(self, stringToTokenize: str):
        self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
        self.stringToTokenize = stringToTokenize
        self.currentStringIndex = 0
        self.currentLine = 1

        self.stateNames = {
            TokenizerState.TOKENIZER_STATE_DEFAULT : "TOKENIZER_STATE_DEFAULT",
            TokenizerState.TOKENIZER_STATE_PROCESSING_NAME : "TOKENIZER_STATE_PROCESSING_IDENTIFIER",
            TokenizerState.TOKENIZER_STATE_PROCESSING_DECIMAL_NUMBER : "TOKENIZER_STATE_PROCESSING_DECIMAL_NUMBER",
            TokenizerState.TOKENIZER_STATE_UNSURE_WHETHER_DECIMAL_OR_HEXADECIMAL : "TOKENIZER_STATE_UNSURE_WHETHER_DECIMAL_OR_HEXADECIMAL",
            TokenizerState.TOKENIZER_STATE_PROCESSING_HEXADECIMAL_NUMBER : "TOKENIZER_STATE_PROCESSING_HEXADECIMAL_NUMBER",
            TokenizerState.TOKENIZER_STATE_PROCESSING_STRING : "TOKENIZER_STATE_PROCESSING_STRING",
            TokenizerState.TOKENIZER_STATE_PROCESSING_PHANDLE_REFERENCE : "TOKENIZER_STATE_PROCESSING_PHANDLE_REFERENCE"
        }

        # stores the current token
        self.currentToken = None

        # sometimes one token will be terminated by a character
        # that is an entire token in itself, so the getNextToken
        # function should technically return two tokens at once.
        # This breaks the API for that function, so the extra token
        # is stored in the self.currentToken member and this flag
        # is set.
        self.hasExtraToken = False


    def getNextChar(self) -> str:
        nextChar: str = None

        if self.currentStringIndex < len(self.stringToTokenize):
            nextChar = self.stringToTokenize[self.currentStringIndex]
            self.currentStringIndex += 1
        
        return nextChar



    '''
    Callback function for processing the TOKENIZER_STATE_DEFAULT state.
    '''
    def handleStateDefault(self) -> Token:
        nextChar: str = self.getNextChar()

        if nextChar is None:
            newToken: Token = Token(TokenType.TOKEN_TYPE_END_OF_FILE, None)
            return newToken
        elif nextChar == "\n":
            newToken: Token = Token(TokenType.TOKEN_TYPE_NEWLINE, "\n")
            self.currentLine += 1
            return newToken
        elif isWhiteSpace(nextChar):
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
        elif nextChar == "0":
            self.currentToken = Token(TokenType.TOKEN_TYPE_NONE, "0")
            self.state = TokenizerState.TOKENIZER_STATE_UNSURE_WHETHER_DECIMAL_OR_HEXADECIMAL       # need either 'x' or another digit to be sure
            return None
        elif isValidHexadecimalCharacter(nextChar):
            self.currentToken = Token(TokenType.TOKEN_TYPE_DECIMAL_NUMBER, nextChar)
            self.state = TokenizerState.TOKENIZER_STATE_PROCESSING_DECIMAL_NUMBER
            return None
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
            raise ValueError(f"Character: \"{nextChar}\" at line {self.currentLine} is not a valid character for devicetree file.")

        

    def handleStateProcessingName(self) -> Token:
        nextChar: str = self.getNextChar()

        if nextChar is None:
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_END_OF_FILE, None)
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken
        
        elif nextChar == "\n":
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_NEWLINE, "\n")
            self.currentLine += 1
            self.hasExtraToken = True
            return newToken

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
            raise ValueError(f"Error occurred during tokenization. Unexpected character: {nextChar} at line {self.currentLine} should not appear in device tree name.")

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
            raise ValueError(f"Character: \"{nextChar}\" at line {self.currentLine} is not a valid character for devicetree file.")



# here
    def handleStateProcessingDecimalNumber(self) -> Token:
        nextChar: str = self.getNextChar()

        if nextChar is None:
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_END_OF_FILE, None)
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken
        
        elif nextChar == "\n":
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_NEWLINE, "\n")
            self.currentLine += 1
            self.hasExtraToken = True
            return newToken
        
        elif isWhiteSpace(nextChar):
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return self.currentToken
        
        elif isValidHexadecimalCharacter(nextChar):
            self.currentToken.appendText(nextChar)
            return None

        elif isValidNameCharacter(nextChar):
            raise ValueError(f"Error occurred during tokenization. Unexpected character: {nextChar} at line {self.currentLine} should not appear in device tree number.")

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
            raise ValueError(f"Error occurred during tokenization. Unexpected character: {nextChar} at line {self.currentLine} should not appear in device tree name.")

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
            raise ValueError(f"Character: \"{nextChar}\" at line {self.currentLine} is not a valid character for devicetree file.")

    
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
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_NEWLINE, "\n")
            self.currentLine += 1
            self.hasExtraToken = True
            return newToken

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
            raise ValueError(f"Error occurred during tokenization. Unexpected character: {nextChar} at line {self.currentLine} should not appear in device tree number.")
        
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
            raise ValueError(f"Error occurred during tokenization. Unexpected character: {nextChar} at line {self.currentLine} should not appear in device tree name.")

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
            raise ValueError(f"Character: \"{nextChar}\" at line {self.currentLine} is not a valid character for devicetree file.")



    def handleStateProcessingHexadecimalNumber(self) -> Token:
        nextChar: str = self.getNextChar()

        if nextChar is None:
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_END_OF_FILE, None)
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken
        
        elif nextChar == "\n":
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_NEWLINE, "\n")
            self.currentLine += 1
            self.hasExtraToken = True
            return newToken
        
        elif isWhiteSpace(nextChar):
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return self.currentToken
        
        elif isValidHexadecimalCharacter(nextChar):
            self.currentToken.appendText(nextChar)
            return None

        elif isValidNameCharacter(nextChar):
            raise ValueError(f"Error occurred during tokenization. Unexpected character: {nextChar} at line {self.currentLine} should not appear in device tree number.")

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
            raise ValueError(f"Error occurred during tokenization. Unexpected character: {nextChar} at line {self.currentLine} should not appear in device tree name.")

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
            raise ValueError(f"Character: \"{nextChar}\" at line {self.currentLine} is not a valid character for devicetree file.")




    def handleStateProcessingString(self) -> Token:
        nextChar: str = self.getNextChar()

        if nextChar is None:
            raise ValueError(f"Error occurred during tokenization at line {self.currentLine}. No matching \" for string: {self.currentToken.value}.")
        
        elif nextChar == "\n":
            raise ValueError(f"Error occurred during tokenization at line {self.currentLine}. Cannot have newline in middle of string.")

        
        elif nextChar == "\"":
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return self.currentToken
        
        else:
            self.currentToken.appendText(nextChar)
            return None
        

    
    def handleStateProcessingPhandleReference(self) -> Token:
        nextChar: str = self.getNextChar()

        if nextChar is None:
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_END_OF_FILE, None)
            self.hasExtraToken = True
            self.state = TokenizerState.TOKENIZER_STATE_DEFAULT
            return newToken
        
        elif nextChar == "\n":
            newToken: Token = self.currentToken
            self.currentToken = Token(TokenType.TOKEN_TYPE_NEWLINE, "\n")
            self.currentLine += 1
            self.hasExtraToken = True
            return newToken
        
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
            raise ValueError(f"Error occurred during tokenization. Unexpected character: {nextChar} at line {self.currentLine} should not appear in device tree name.")

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
            raise ValueError(f"Character: \"{nextChar}\" at line {self.currentLine} is not a valid character for devicetree file.")


    stateCallbacks = {
        TokenizerState.TOKENIZER_STATE_DEFAULT : handleStateDefault,
        TokenizerState.TOKENIZER_STATE_PROCESSING_NAME : handleStateProcessingName,
        TokenizerState.TOKENIZER_STATE_PROCESSING_DECIMAL_NUMBER : handleStateProcessingDecimalNumber,
        TokenizerState.TOKENIZER_STATE_UNSURE_WHETHER_DECIMAL_OR_HEXADECIMAL : handleStateUnsureWhetherDecimalOrHexadecimal,
        TokenizerState.TOKENIZER_STATE_PROCESSING_HEXADECIMAL_NUMBER : handleStateProcessingHexadecimalNumber,
        TokenizerState.TOKENIZER_STATE_PROCESSING_STRING : handleStateProcessingString,
        TokenizerState.TOKENIZER_STATE_PROCESSING_PHANDLE_REFERENCE : handleStateProcessingPhandleReference
    }


    def resetTokenization(self):
        self.state =TokenizerState.TOKENIZER_STATE_DEFAULT
        self.currentStringIndex = 0
        self.currentToken = None
        self.hasExtraToken = False


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

    


