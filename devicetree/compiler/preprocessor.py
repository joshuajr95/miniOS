

from enum import Enum
import os


MAX_STRING_SIZE = 1000000000
UNDEFINED_STRING_INDEX = -1
UNDEFINED_LINE_NUMBER = -1


# TODO: Document include tree invariants and structure
class IncludeTreeNode:

    '''
    Start index and start line are in the output fully preprocessed and include merged file
    '''
    def __init__(self, parent, fileName: str, startIndex: int, startLine: int, endIndex: int = UNDEFINED_STRING_INDEX, endLine: int = UNDEFINED_LINE_NUMBER):
        self.parent = parent
        self.fileName = fileName
        self.startIndex = startIndex
        self.endIndex = endIndex
        self.startLineNumber = startLine
        self.endLineNumber = endLine
        self.children: list[IncludeTreeNode] = []
        self.lineControlEntries: list[LineControlEntry] = []


    # children must be added in order
    def addChild(self, node):

        if (node.startIndex >= node.endIndex) and (node.endIndex != UNDEFINED_STRING_INDEX):
            raise Exception(f"Include tree node for {node.fileName} appears to have start index greater than end index")

        if (node.startIndex < self.startIndex) or (node.endIndex > self.endIndex):
            raise Exception(f"Include tree node for {node.fileName} could not be added to node for {self.fileName} since indices were out of range")

        if len(self.children) == 0:
            self.children.append(node)
        elif node.startIndex <= self.children[-1].endIndex:
            print(f"Previous node end: {self.children[-1].endIndex}, current node start: {node.startIndex}")
            raise Exception(f"Conflict between ranges for node for {node.fileName} and node for {self.children[-1].fileName}")
        else:
            self.children.append(node)


    def mapIndexToChild(self, index: int):

        if (index < self.startIndex) or (index > self.endIndex):
            return None

        for child in self.children:
            if (index >= child.startIndex) and (index <= child.endIndex):
                return child

        return self



class IncludeTree:

    def __init__(self, rootNode: IncludeTreeNode):
        self.root = rootNode

    
    def findNodeFromIndex(self, outputIndex: int):
        currentNode = self.root

        while currentNode is not None:
            nextNode = currentNode.mapIndexToChild(outputIndex)

            if nextNode is currentNode:
                break
            else:
                currentNode = nextNode
        
        return currentNode





class LineControlType(Enum):
    SINGLE_LINE_COMMENT = 0
    MULTILINE_COMMENT = 1
    OBJECT_LIKE_MACRO_DEFINITION = 2
    FUNCTION_LIKE_MACRO_DEFINITION = 3
    OBJECT_LIKE_MACRO_SUBSTITUTION = 4
    FUNCTION_LIKE_MACRO_SUBSTITUTION = 5
    LINE_BREAK_MERGE = 6


# get filename and string offset from total offset via IncludeTree (find node in include tree)
# get beginning line number and end line number for a file from IncludeTree
# calculate line number within file via subtract beginning from current
# iterate through line control entries until you get to outputLineNumber (after processing)
# matching or greater than current in tokenizer. Then get inputLineNumber
# from line control entry

'''
Have inputLineNumber and outputLineNumber, that way the tokenizer can iterate
through all line control entries and find the one just before where the current
line is (determined by output) and then check the inputLineNumber
'''
class LineControlEntry:

    def __init__(self, fileName: str, lineNumber: int, preprocessedLineNumber: int, numLinesAdded: int, stringOffset: int, sizeChange: int, type: LineControlType):
        self.fileName = fileName
        self.lineNumber = lineNumber
        self.preprocessedLineNumber = preprocessedLineNumber
        self.numLinesAdded = numLinesAdded
        self.stringOffset = stringOffset
        self.sizeChange = sizeChange
        self.type = type


class LineBreakMerge(LineControlEntry):

    def __init__(self, fileName: str, lineNumber: int, preprocessedLineNumber: int, numLinesAdded: int, stringOffset: int, sizeChange: int):
        super().__init__(fileName, lineNumber, preprocessedLineNumber, numLinesAdded, stringOffset, sizeChange, LineControlType.LINE_BREAK_MERGE)

class SingleLineComment(LineControlEntry):

    def __init__(self, fileName: str, lineNumber: int, preprocessedLineNumber: int, numLinesAdded: int, stringOffset: int, sizeChange: int):
        super().__init__(fileName, lineNumber, preprocessedLineNumber, numLinesAdded, stringOffset, sizeChange, LineControlType.SINGLE_LINE_COMMENT)

class MultiLineComment(LineControlEntry):

    def __init__(self, fileName: str, lineNumber: int, preprocessedLineNumber: int, numLinesAdded: int, stringOffset: int, sizeChange: int):
        super().__init__(fileName, lineNumber, preprocessedLineNumber, numLinesAdded, stringOffset, sizeChange, LineControlType.MULTILINE_COMMENT)

class FunctionLikeMacroDefine(LineControlEntry):

    def __init__(self, fileName: str, lineNumber: int, preprocessedLineNumber: int, numLinesAdded: int, stringOffset: int, sizeChange: int, macroName: str):
        super().__init__(fileName, lineNumber, preprocessedLineNumber, numLinesAdded, stringOffset, sizeChange, LineControlType.FUNCTION_LIKE_MACRO_DEFINITION)
        self.macroName = macroName          # can be used to index into the macro table

class ObjectMacroDefine(LineControlEntry):

    def __init__(self, fileName: str, lineNumber: int, preprocessedLineNumber: int, numLinesAdded: int, stringOffset: int, sizeChange: int, macroName: str):
        super().__init__(fileName, lineNumber, preprocessedLineNumber, numLinesAdded, stringOffset, sizeChange, LineControlType.OBJECT_LIKE_MACRO_DEFINITION)
        self.macroName = macroName          # can be used to index into the macro table

class ObjectMacroSubstitution(LineControlEntry):

    def __init__(self, fileName: str, lineNumber: int, preprocessedLineNumber: int, numLinesAdded: int, stringOffset: int, sizeChange: int, macroName: str):
        super().__init__(fileName, lineNumber, preprocessedLineNumber, numLinesAdded, stringOffset, sizeChange, LineControlType.OBJECT_LIKE_MACRO_SUBSTITUTION)
        self.macroName = macroName          # can be used to index into the macro table

class FunctionMacroSubstitution(LineControlEntry):

    def __init__(self, fileName: str, lineNumber: int, preprocessedLineNumber: int, numLinesAdded: int, stringOffset: int, sizeChange: int, macroName: str, *args):
        super().__init__(fileName, lineNumber, preprocessedLineNumber, numLinesAdded, stringOffset, sizeChange, LineControlType.FUNCTION_LIKE_MACRO_SUBSTITUTION)
        self.macroName = macroName          # can be used to index into the macro table
        self.macroArguments = [arg for arg in args]



# map string index to LineControl instances (string index within file and calculate based on offset from beginning of processed string)
# find IncludeTreeNode corresponding to index, calculate offset as index - start, index into dictionary to get LineControl object
# PER IncludeTreeNode, check the type and get line number. If not found in dictionary, then sorted(dictionary), and iterate through
# to find last entry that changed the line count that is less than the offset and add up the numLinesAdded for each, and then get
# that line number plus numLinesAdded plus


class PreprocessedFileEntry:

    def __init__(self, fileName):
        self.fileName = fileName
        
        with open(self.fileName, "r") as f:
            self.inputBuffer = f.read()
        
        self.currentInputIndex = 0

        # self.currentInputLineNumber is the line number as it appears in the
        # original file, whereas self.currentInputLineNumberPreprocessed is the
        # line number after preprocessing which will be different due to
        # stripped out comments, #defines being removed, macros being expanded,
        # and line breaks being merged onto one line
        self.currentInputLineNumber = 1
        self.currentInputLineNumberPreprocessed = 1
    
    def __str__(self) -> str:
        return f"File: {self.fileName}, Input index: {self.currentInputIndex}, Line Number: {self.currentInputLineNumber}"

    def nextCharacter(self) -> str:
        return self.inputBuffer[self.currentInputIndex]



class Stack:

    def __init__(self):
        self._stackInternal = []

    def empty(self) -> bool:
        return len(self._stackInternal) == 0

    def size(self) -> int:
        return len(self._stackInternal)

    def push(self, element):
        self._stackInternal.append(element)

    def pop(self):
        return self._stackInternal.pop()

    def getTop(self):
        return self._stackInternal[-1]

    def setTop(self, element):
        self._stackInternal[-1] = element



class FunctionLikeMacroEntry:

    def __init__(self, macroName: str, argumentList: list[str], macroBody: str):
        self.macroName = macroName
        self.argumentList = argumentList
        self.macroBody = macroBody
    
    def __str__(self) -> str:
        return f"Name: {self.macroName}, Args: {str(self.argumentList)}, Body: {self.macroBody}"



'''
Returns true if the buffer at the current index contains a valid
#include directive. This means that the index is not too close to
the end of the input buffer, it matches the text "#include", and
the next character must be whitespace.

@param inputBuffer: String to check for the '#include'
@param inputIndex: Index into string at which to check for '#include'

@return True if found, False otherwise
'''
def isInclude(inputBuffer: str, inputIndex: int):
    return (inputIndex + len("#include") < len(inputBuffer)) and \
    (inputBuffer[inputIndex:inputIndex+len("#include")] == "#include") and \
    ((inputBuffer[inputIndex + len("#include")] == " ") or (inputBuffer[inputIndex + len("#include")] == "\t"))



'''
Returns true if the buffer at the current index contains a valid
#define directive. This means that the index is not too close to
the end of the input buffer, it matches the text "#define", and
the next character must be whitespace.

@param inputBuffer: String to check for the '#define'
@param inputIndex: Index into string at which to check for '#define'

@return True if found, False otherwise
'''
def isDefine(inputBuffer: str, inputIndex: int):
    return (inputIndex + len("#define") < len(inputBuffer)) and \
    (inputBuffer[inputIndex:inputIndex+len("#define")] == "#define") and \
    ((inputBuffer[inputIndex + len("#define")] == " ") or (inputBuffer[inputIndex + len("#define")] == "\t"))



'''
Returns true if the buffer at the current index contains a valid
#undef directive. This means that the index is not too close to
the end of the input buffer, it matches the text "#undef", and
the next character must be whitespace.

@param inputBuffer: String to check for the '#undef'
@param inputIndex: Index into string at which to check for '#undef'

@return True if found, False otherwise
'''
def isUndef(inputBuffer: str, inputIndex: int):
    return (inputIndex + len("#undef") < len(inputBuffer)) and \
    (inputBuffer[inputIndex:inputIndex+len("#undef")] == "#undef") and \
    ((inputBuffer[inputIndex + len("#undef")] == " ") or (inputBuffer[inputIndex + len("#undef")] == "\t"))



'''
Returns true if the buffer at the current index contains a valid
#ifdef directive. This means that the index is not too close to
the end of the input buffer, it matches the text "#ifdef", and
the next character must be whitespace.

@param inputBuffer: String to check for the '#ifdef'
@param inputIndex: Index into string at which to check for '#ifdef'

@return True if found, False otherwise
'''
def isIfdef(inputBuffer: str, inputIndex: int):
    return (inputIndex + len("#ifdef") < len(inputBuffer)) and \
    (inputBuffer[inputIndex:inputIndex+len("#ifdef")] == "#ifdef") and \
    ((inputBuffer[inputIndex + len("#ifdef")] == " ") or (inputBuffer[inputIndex + len("#ifdef")] == "\t"))



'''
Returns true if the buffer at the current index contains a valid
#ifndef directive. This means that the index is not too close to
the end of the input buffer, it matches the text "#ifndef", and
the next character must be whitespace.

@param inputBuffer: String to check for the '#ifndef'
@param inputIndex: Index into string at which to check for '#ifndef'

@return True if found, False otherwise
'''
def isIfndef(inputBuffer: str, inputIndex: int):
    return (inputIndex + len("#ifndef") < len(inputBuffer)) and \
    (inputBuffer[inputIndex:inputIndex+len("#ifndef")] == "#ifndef") and \
    ((inputBuffer[inputIndex + len("#ifndef")] == " ") or (inputBuffer[inputIndex + len("#ifndef")] == "\t"))



'''
Returns true if the buffer at the current index contains a valid
#if directive. This means that the index is not too close to
the end of the input buffer, it matches the text "#if", and
the next character must be whitespace.

@param inputBuffer: String to check for the '#if'
@param inputIndex: Index into string at which to check for '#if'

@return True if found, False otherwise
'''
def isIf(inputBuffer: str, inputIndex: int):
    return (inputIndex + len("#if") < len(inputBuffer)) and \
    (inputBuffer[inputIndex:inputIndex+len("#if")] == "#if") and \
    ((inputBuffer[inputIndex + len("#if")] == " ") or (inputBuffer[inputIndex + len("#if")] == "\t"))



'''
Returns true if the buffer at the current index contains a valid
#else directive. This means that the index is not too close to
the end of the input buffer, it matches the text "#else", and
the next character must be whitespace.

@param inputBuffer: String to check for the '#else'
@param inputIndex: Index into string at which to check for '#else'

@return True if found, False otherwise
'''
def isElse(inputBuffer: str, inputIndex: int):
    return (inputIndex + len("#else") < len(inputBuffer)) and \
    (inputBuffer[inputIndex:inputIndex+len("#else")] == "#else") and \
    ((inputBuffer[inputIndex + len("#else")] == " ") or (inputBuffer[inputIndex + len("#else")] == "\t"))



'''
Returns true if the buffer at the current index contains a valid
#endif directive. This means that the index is not too close to
the end of the input buffer and it matches the text "#endif

@param inputBuffer: String to check for the '#endif'
@param inputIndex: Index into string at which to check for '#endif'

@return True if found, False otherwise
'''
def isEndif(inputBuffer: str, inputIndex: int):
    return (inputIndex + len("#endif") < len(inputBuffer)) and \
    (inputBuffer[inputIndex:inputIndex+len("#endif")] == "#endif")



'''
Returns true if the buffer at the current index contains the beginning
of a single line comment ('//').

@param inputBuffer: String to check for the comment
@param inputIndex: Index into string at which to check for comment

@return True if found, False otherwise
'''
def isSingleLineComment(inputBuffer: str, inputIndex: int):
    return (inputIndex + 1 <= len(inputBuffer)) and (inputBuffer[inputIndex:inputIndex+2] == "//")



'''
Returns true if the buffer at the current index contains the beginning
of a multi-line comment ('/*').

@param inputBuffer: String to check for the comment
@param inputIndex: Index into string at which to check for comment

@return True if found, False otherwise
'''
def isMultiLineComment(inputBuffer: str, inputIndex: int):
    return (inputIndex + 1 <= len(inputBuffer)) and (inputBuffer[inputIndex:inputIndex+2] == "/*")



'''
Returns true if the buffer at the current index contains the beginning
of a string literal. String literals begin and end with double quotes
and all other directives and comments are ignored inside of them, so it
is necessary to check for string literals to avoid errors.

@param inputBuffer: String to check for the string literal
@param inputIndex: Index into string at which to check for string literal

@return True if found, False otherwise
'''
def isString(inputBuffer: str, inputIndex: int):
    return inputBuffer[inputIndex] == "\""



def isPunctuator(char: str):

    punctuators = {
        "(",
        ")",
        ":",
        ";",
        ",",
        ".",
        "<",
        ">",
        "{",
        "}",
        "[",
        "]",
        " ",
        "\t"
    }

    return char in punctuators


def isValidPreprocessorIdentifierCharacter(char: str):
    return (len(char) == 1) and (char.isalnum() or (char == "_"))


def isValidMacroNameCharacter(char: str):
    return isValidPreprocessorIdentifierCharacter(char)

def isValidMacroArgumentCharacter(char: str):
    return isValidPreprocessorIdentifierCharacter(char)


'''
Things to consider for include calling conventions:
- Output index position before and after                Before: points to next char to be added, After: points to next char to be added
- Input index before and after                          Before: points to # in #include, After: points to char after ending " or >
- Current output line number
- Current include tree node and include tree state      Before: current points to current, After: points to current with whole subtree added
'''


# TODO: Check in default handling for file processing for macro to expand
# TODO: Handle recursive macro expansion
# TODO: Macro table format for both object-like and function-like macros
# TODO: Handle include path for creating PreprocessedFileEntry
# TODO: Handle line break merge in preprocess and preprocessFileContents
# TODO: Issue with getting original line number when line number is inside of comment or macro definition. Need more complex logic. NO. Only in macro
#       expansion since it can go from many lines to many more or fewer, but comments and definitions get stripped out, so only one line
# TODO: Create output buffer class that uses ring buffer to store output temporarily until writing it to output file
# TODO: Make sure that when expanding macros, you check for whitespace on each side of the macro or punctuation characters: "(", ")", ":", ";", ",", ".",
#       "<", ">", "{". "}", "[", "]"
#       and when expanding macros, you add whitespace
# TODO: Validate macro names as identifiers, but exclude "defined"
# TODO: Macro definition should store exactly what it is defined as without recursive expansion. Recursive expansion occurs when macro is expanded rather
#       than when it is defined
# TODO: Only expand function like macro if its invocation has () after, and make sure that if there is space between macro name and () in definition it is
#       object-like rather than function like
# TODO: Strip whitespace from macro arguments, balance parentheses, figure out how to do complex arguments to macros
# TODO: Add code to handle #undef
# TODO: In macro expansion, check for self-reference
# TODO: Fix up preprocess and preprocessFileContents to fix passing fileEntry repeatedly and reassigning it
# TODO: Fix up is... checks (isInclude, etc.) to just pass the fileEntry
'''
This class implements preprocessing of the Device Tree files. Typically
the build system will compile a board-level device tree source file rather
than an SoC-level device tree file, but the board-level file (explorer_16_32.dts,
for example) will #include the SoC device tree file. 
'''
class Preprocessor:


    def __init__(self, rootDir: str, includePath: list[str] = ["dts", "boards", "overlays"]):
        self.rootDirectory = rootDir
        self.includePaths = [f"{rootDir}/{folder}" for folder in includePath]


    '''
    Finds the given file in the list of include paths and returns the full path
    '''
    def findFile(self, fileName: str):
        
        for folder in self.includePaths:
            if os.path.isfile(f"{folder}/{fileName}"):
                return f"{folder}/{fileName}"
        
        raise Exception(f"Could not find file '{fileName}' in include directories {self.includePaths}")


    def isObjectLikeMacroExpansion(self, inputBuffer: str, inputIndex: int):


        # object-like macro must be punctuated by whitespace or punctuators unless at beginning or end of file
        for macroName in self.objectLikeMacroTable.keys():

            if inputIndex + len(macroName) > len(inputBuffer):
                continue

            macroMatches = (inputBuffer[inputIndex:inputIndex+len(macroName)] == macroName)
            previousCharacterIsValid = False
            nextCharacterIsValid = False

            if (inputIndex == 0) or inputBuffer[inputIndex-1].isspace() or isPunctuator(inputBuffer[inputIndex-1]):
                previousCharacterIsValid = True
            
            if (inputIndex + len(macroName) == len(inputBuffer)) or (inputBuffer[inputIndex+len(macroName)].isspace()) \
                or (isPunctuator(inputBuffer[inputIndex+len(macroName)]) and inputBuffer[inputIndex+len(macroName)] != "("):
                nextCharacterIsValid = True
            
            if macroMatches and previousCharacterIsValid and nextCharacterIsValid:
                return True

        return False


    def isFunctionLikeMacroExpansion(self, inputBuffer: str, inputIndex:int):

        for macroName in self.functionLikeMacroTable.keys():

            if inputIndex + len(macroName) >= len(inputBuffer):
                continue

            macroMatches = (inputBuffer[inputIndex:inputIndex+len(macroName)] == macroName)
            nextCharacterIsValid = inputBuffer[inputIndex+len(macroName)] == "("
            previousCharacterIsValid = False

            if (inputIndex == 0) or inputBuffer[inputIndex-1].isspace() or isPunctuator(inputBuffer[inputIndex-1]):
                previousCharacterIsValid = True

            if macroMatches and previousCharacterIsValid and nextCharacterIsValid:
                return True

        return False



    # TODO: make sure that newline is not allowed
    def parseInclude(self):

        fileEntry: PreprocessedFileEntry = self.inputFileStack.getTop()
        fileEntry.currentInputIndex += len("#include")

        if (fileEntry.nextCharacter() != " ") and (fileEntry.nextCharacter() != "\t"):
            raise Exception(f"Expected 'space' or 'tab' after #include but encountered '{fileEntry.nextCharacter()}'")

        # eat whitespace or line breaks until end of buffer
        while (fileEntry.currentInputIndex < len(fileEntry.inputBuffer)) and \
                ((fileEntry.nextCharacter() == " ") or \
                (fileEntry.nextCharacter() == "\t") or \
                ((fileEntry.nextCharacter() == "\\") and (fileEntry.inputBuffer[fileEntry.currentInputIndex+1] == "\n"))):
            if (fileEntry.nextCharacter() == " ") or (fileEntry.nextCharacter() == "\t"):
                fileEntry.currentInputIndex += 1
            else:
                fileEntry.currentInputLineNumber += 1
                fileEntry.currentInputIndex += 2


        if fileEntry.currentInputIndex >= len(fileEntry.inputBuffer):
            raise Exception(f"Incorrect syntax for #include, but I need to implement proper error messages")
            

        delimiter = None
        if fileEntry.nextCharacter() == "<":
            delimiter = ">"
        elif fileEntry.nextCharacter() == "\"":
            delimiter = "\""
        else:
            raise Exception(f"Wrong syntax for #include. Expected '<' or '\"'. I need better error messages")

        fileNameSpecialChars = {"-", "_", ".", "/"}
        fileEntry.currentInputIndex += 1
        fileNameBeginIndex = fileEntry.currentInputIndex

        # find closing bracket or quote and make sure file name is in proper format
        while (fileEntry.currentInputIndex < len(fileEntry.inputBuffer)) and \
                (fileEntry.nextCharacter() != delimiter) and \
                ((fileEntry.nextCharacter().isalnum()) or (fileEntry.nextCharacter() in fileNameSpecialChars)):
            fileEntry.currentInputIndex += 1

        if fileEntry.currentInputIndex >= len(fileEntry.inputBuffer):
            raise Exception(f"Incorrect syntax for #include, but I need to implement proper error messages")

        # get the file name and run preprocessing on that file
        fileName = fileEntry.inputBuffer[fileNameBeginIndex:fileEntry.currentInputIndex]
        self.preprocessFileContents(fileName)
        fileEntry.currentInputIndex += 1

        self.inputFileStack.setTop(fileEntry)


    # TODO: Make sure to check for already existing macro both in object-like table and function-like table
    # Increment current to after #define
    # Eat whitespace and line breaks until macro name
    # Get macro name and make sure it is valid
    # Parse parameter list
    # Parse macro body
    # Create FunctionMacroEntry (maybe better name)
    def processFunctionLikeMacroDefinition(self):

        fileEntry: PreprocessedFileEntry = self.inputFileStack.getTop()
        fileEntry.currentInputIndex += len("#define")

        # eat whitespace and line breaks
        while (fileEntry.currentInputIndex < len(fileEntry.inputBuffer)) and ((fileEntry.nextCharacter() == " ") or (fileEntry.nextCharacter() == "\t") or \
                ((fileEntry.nextCharacter() == "\\") and (fileEntry.inputBuffer[fileEntry.currentInputIndex+1] == "\n"))):
            if (fileEntry.nextCharacter() == " ") or (fileEntry.nextCharacter() == "\t"):
                fileEntry.currentInputIndex += 1
            elif (fileEntry.nextCharacter() == "\\") and (fileEntry.inputBuffer[fileEntry.currentInputIndex+1] == "\n"):
                fileEntry.currentInputLineNumber += 1
                fileEntry.currentInputIndex += 2

        # process macro name
        beginIndex = fileEntry.currentInputIndex
        while (fileEntry.currentInputIndex < len(fileEntry.inputBuffer)) and isValidMacroNameCharacter(fileEntry.nextCharacter()):
            fileEntry.currentInputIndex += 1
        macroName = fileEntry.inputBuffer[beginIndex:fileEntry.currentInputIndex]


        if fileEntry.nextCharacter() != "(":
            raise Exception(f"Syntax error. Expected '('. Need better error messages.")

        fileEntry.currentInputIndex += 1

        # process whitespace, macro argument, comma, repeat until you hit ")"
        argumentList = []
        while fileEntry.nextCharacter() != ")":

            # eat whitespace and line breaks
            while (fileEntry.currentInputIndex < len(fileEntry.inputBuffer)) and \
                    ((fileEntry.nextCharacter() == " ") or (fileEntry.nextCharacter() == "\t") or \
                    ((fileEntry.nextCharacter() == "\\") and (fileEntry.inputBuffer[fileEntry.currentInputIndex+1] == "\n"))):
                if (fileEntry.nextCharacter() == " ") or (fileEntry.nextCharacter() == "\t"):
                    fileEntry.currentInputIndex += 1
                elif (fileEntry.nextCharacter() == "\\") and (fileEntry.inputBuffer[fileEntry.currentInputIndex+1] == "\n"):
                    fileEntry.currentInputLineNumber += 1
                    fileEntry.currentInputIndex += 2
                else:
                    raise Exception(f"Syntax error. Need better error messages")

            # get parameter name
            argBeginIndex = fileEntry.currentInputIndex
            while (fileEntry.currentInputIndex < len(fileEntry.inputBuffer)) and isValidMacroArgumentCharacter(fileEntry.nextCharacter()):
                fileEntry.currentInputIndex += 1
            argumentList.append(fileEntry.inputBuffer[argBeginIndex:fileEntry.currentInputIndex])

            # eat whitespace and line breaks
            while (fileEntry.currentInputIndex < len(fileEntry.inputBuffer)) and \
                    ((fileEntry.nextCharacter() == " ") or (fileEntry.nextCharacter() == "\t") or \
                    ((fileEntry.nextCharacter() == "\\") and (fileEntry.inputBuffer[fileEntry.currentInputIndex+1] == "\n"))):
                if (fileEntry.nextCharacter() == " ") or (fileEntry.nextCharacter() == "\t"):
                    fileEntry.currentInputIndex += 1
                elif (fileEntry.nextCharacter() == "\\") and (fileEntry.inputBuffer[fileEntry.currentInputIndex+1] == "\n"):
                    fileEntry.currentInputLineNumber += 1
                    fileEntry.currentInputIndex += 2
                else:
                    raise Exception(f"Syntax error. Need better error messages")

            if fileEntry.nextCharacter() == ",":
                fileEntry.currentInputIndex += 1
            elif fileEntry.nextCharacter() == ")":
                continue
            else:
                raise Exception(f"Syntax error. Need better error messages")

        fileEntry.currentInputIndex += 1

        # process macro body
        macroValue = ""
        while (fileEntry.currentInputIndex < len(fileEntry.inputBuffer)) and fileEntry.nextCharacter() != "\n":
            if (fileEntry.nextCharacter() == " ") or (fileEntry.nextCharacter() == "\t"):

                # truncate whitespace to a single space per preprocesser spec
                if (len(macroValue) > 0) and (macroValue[-1] == " "):
                    fileEntry.currentInputIndex += 1
                else:
                    macroValue += " "
                    fileEntry.currentInputIndex += 1

            # strip line breaks
            elif (fileEntry.nextCharacter() == "\\") and (fileEntry.inputBuffer[fileEntry.currentInputIndex+1] == "\n"):
                fileEntry.currentInputLineNumber += 1
                fileEntry.currentInputIndex += 2

            else:
                macroValue += fileEntry.nextCharacter()
                fileEntry.currentInputIndex += 1

        # check if macro already exists and if not, add it to the table
        if macroName in self.objectLikeMacroTable.keys():
            raise Exception(f"Macro {macroName} already exists as an object-like macro. Need better error messages.")
        elif macroName in self.functionLikeMacroTable.keys():
            raise Exception(f"Already existing macro redefined. Need better error messages")
        else:
            macroEntry = FunctionLikeMacroEntry(macroName, argumentList, macroValue)
            self.functionLikeMacroTable[macroName] = macroEntry

        self.inputFileStack.setTop(fileEntry)



    def processObjectLikeMacroDefinition(self):

        fileEntry = self.inputFileStack.getTop()

        beginIndex = fileEntry.currentInputIndex
        beginLineNumber = fileEntry.currentInputLineNumber
        fileEntry.currentInputIndex += len("#define")

        # eat whitespace and line breaks until macro name
        while (fileEntry.currentInputIndex < len(fileEntry.inputBuffer)) and (not isValidMacroNameCharacter(fileEntry.nextCharacter())):

            # strip whitespace
            if (fileEntry.nextCharacter() == " ") or (fileEntry.nextCharacter() == "\t"):
                fileEntry.currentInputIndex += 1

            # strip line break but record increase in source line number
            elif (fileEntry.nextCharacter() == "\\") and (fileEntry.inputBuffer[fileEntry.currentInputIndex+1] == "\n"):
                fileEntry.currentInputLineNumber += 1
                fileEntry.currentInputIndex += 2
            else:
                raise Exception(f"Error processing object like macro. Need better error messages")

        # get the macro name
        macroNameBegin = fileEntry.currentInputIndex
        while (fileEntry.currentInputIndex < len(fileEntry.inputBuffer)) and isValidMacroNameCharacter(fileEntry.nextCharacter()):
            fileEntry.currentInputIndex += 1
        macroName = fileEntry.inputBuffer[macroNameBegin:fileEntry.currentInputIndex]

        # eat whitespace and line breaks until macro body
        while (fileEntry.currentInputIndex < len(fileEntry.inputBuffer)) and \
                ((fileEntry.nextCharacter() == " ") or (fileEntry.nextCharacter() == "\t") or \
                ((fileEntry.nextCharacter() == "\\") and (fileEntry.inputBuffer[fileEntry.currentInputIndex+1] == "\n"))):
            if (fileEntry.nextCharacter() == "\\") and (fileEntry.inputBuffer[fileEntry.currentInputIndex+1] == "\n"):
                fileEntry.currentInputLineNumber += 1
                fileEntry.currentInputIndex += 2
            else:
                fileEntry.currentInputIndex += 1

        # build the macro body by removing line breaks and truncating whitespace to a single space
        macroValue = ""
        while (fileEntry.currentInputIndex < len(fileEntry.inputBuffer)) and fileEntry.nextCharacter() != "\n":
            if (fileEntry.nextCharacter() == " ") or (fileEntry.nextCharacter() == "\t"):

                # truncate whitespace to a single space per preprocesser spec
                if (len(macroValue) > 0) and (macroValue[-1] == " "):
                    fileEntry.currentInputIndex += 1
                else:
                    macroValue += " "
                    fileEntry.currentInputIndex += 1

            # strip line breaks
            elif (fileEntry.nextCharacter() == "\\") and (fileEntry.inputBuffer[fileEntry.currentInputIndex+1] == "\n"):
                fileEntry.currentInputLineNumber += 1
                fileEntry.currentInputIndex += 2

            else:
                macroValue += fileEntry.nextCharacter()
                fileEntry.currentInputIndex += 1

        # check if macro already exists and if not, add it to the table
        if macroName in self.objectLikeMacroTable.keys():
            raise Exception(f"Already existing macro redefined. Need better error messages")
        elif macroName in self.functionLikeMacroTable.keys():
            raise Exception(f"Macro {macroName} already exists as a function-like macro. Need better error messages.")
        else:
            self.objectLikeMacroTable[macroName] = macroValue

        # add the line control entry to keep track of original line number
        lineEntry = ObjectMacroDefine(fileEntry.fileName, beginLineNumber, fileEntry.currentInputLineNumberPreprocessed, \
                                      beginLineNumber - fileEntry.currentInputLineNumber, beginIndex, beginIndex - fileEntry.currentInputIndex, macroName)
        self.currentIncludeTreeNode.lineControlEntries.append(lineEntry)

        self.inputFileStack.setTop(fileEntry)




    def processDefine(self):

        fileEntry: PreprocessedFileEntry = self.inputFileStack.getTop()
        beginIndex = fileEntry.currentInputIndex + len("#define")
        index = beginIndex


        # eat whitespace and line breaks
        while (index < len(fileEntry.inputBuffer)) and \
                ( (fileEntry.inputBuffer[index] == " ") or (fileEntry.inputBuffer[index] == "\t") or \
                ((fileEntry.inputBuffer[index] == "\\") and (fileEntry.inputBuffer[index+1] == "\n")) ):
            if (fileEntry.inputBuffer[index] == " ") or (fileEntry.inputBuffer[index] == "\t"):
                index += 1
            elif (fileEntry.inputBuffer[index] == "\\") and (fileEntry.inputBuffer[index+1] == "\n"):
                index += 2
            else:
                raise Exception(f"Syntax error. Need better error messages.")

        if beginIndex == index:
            raise Exception(f"No whitespace between #define and macro name")

        beginIndex = index
        while (fileEntry.currentInputIndex < len(fileEntry.inputBuffer)) and isValidMacroNameCharacter(fileEntry.inputBuffer[index]):
            index += 1

        if beginIndex == index:
            raise Exception(f"Macro name for #define is non-existent.")

        nextChar = fileEntry.inputBuffer[index]

        if nextChar == "(":
            self.processFunctionLikeMacroDefinition()
        elif (nextChar == " ") or (nextChar == "\t"):
            self.processObjectLikeMacroDefinition()
        else:
            raise Exception(f"Incorrect syntax for #define but I still need better errors rather than exceptions for everything")


        self.inputFileStack.setTop(fileEntry)


    def processUndef(self):
        fileEntry = self.inputFileStack.getTop()
        fileEntry.currentInputIndex += len("#undef")

        # eat whitespace and line breaks
        while ( fileEntry.currentInputIndex < len(fileEntry.inputBuffer) ) and \
            ( (fileEntry.nextCharacter() == " ") or (fileEntry.nextCharacter() == "\t") or \
            ((fileEntry.nextCharacter() == "\\") and (fileEntry.inputBuffer[fileEntry.currentInputIndex+1] == "\n")) ):

            # strip line breaks
            if (fileEntry.nextCharacter() == "\\") and (fileEntry.inputBuffer[fileEntry.currentInputIndex+1] == "\n"):
                fileEntry.currentInputLineNumber += 1
                fileEntry.currentInputIndex += 2

            # eat whitespace
            elif (fileEntry.nextCharacter() == " ") or (fileEntry.nextCharacter() == "\t"):
                fileEntry.currentInputIndex += 1
            else:
                raise Exception(f"Incorrect syntax. Need better error messages")

        # get the macro name
        macroNameBegin = fileEntry.currentInputIndex
        while (fileEntry.currentInputIndex < len(fileEntry.inputBuffer)) and isValidMacroNameCharacter(fileEntry.nextCharacter()):
            fileEntry.currentInputIndex += 1

        if macroNameBegin == fileEntry.currentInputIndex:
            raise Exception(f"Non-existent macro name passed to #undef. Need better error messages.")

        macroName = fileEntry.inputBuffer[macroNameBegin:fileEntry.currentInputIndex]


        # delete the macro from one of the tables or raise error if non-existent
        if macroName in self.objectLikeMacroTable.keys():
            del self.objectLikeMacroTable[macroName]
        elif macroName in self.functionLikeMacroTable.keys():
            del self.functionLikeMacroTable[macroName]
        else:
            raise Exception(f"Macro {macroName} does not exist. Need better error messages.")

        self.inputFileStack.setTop(fileEntry)


    # TODO: Push entry onto ifdef stack
    # TODO: Create entry format. Should have macro name, and type (ifdef, ifndef), as well as if condition is met
    # TODO: If condition is met, continue preprocessing normally, else only check for
    #       corresponding #endif, so push other 
    # TODO: Each section in an ifdef-else block can either be included or not. If included, processing resumes normally
    #       so the preprocess* methods should be broken into 3: preprocess() for top-level file preprocessing, which
    #       calls preprocessFile() which actually sets up the file stack and stuff, and then preprocessSection() which
    #       implements the large if-else block. The preprocessSection() method continues preprocessing the fileEntry at
    #       the top of the stack (with the same input index and input line number) but does not create a new fileEntry
    #       and push it onto the stack, which both preprocessFile() and preprocess() do.
    # TODO: Also need to create a preprocessRemovedSection() (or maybe better name) which resumes preprocessing for sections
    #       where the ifdef or ifndef evaluates to false. It should continue to monitor other ifdefs and increment input
    #       line number, pushing new ifdefs onto stack and popping them until the original encounters and #endif

    #       Design      #
    ########################
    # - Have a state variable enum ConditionalIncludeState which has two states: PREPROCESS_SECTION and REMOVE_SECTION
    # - Set this variable to PREPROCESS_SECTION in preprocess() or preprocessFileContents() at beginning
    # - The preprocess() and preprocessFileContents() methods will setup the inputFileStack and the ifdefStack (per fileEntry)
    #   and then loop while inputIndex < len.
    # - Each iteration of the loop, check the state variable and call either preprocessSection() or preprocessRemovedSection()
    # - The function preprocessSection() has the large if-elif-else statement and iterates while inputIndex < len and state == PREPROCESS_SECTION
    # - Encountering an #else statement will cause the state variable to flip (PREPROCESS_SECTION --> REMOVE_SECTION and vice versa)
    # - This causes the while loop and thus the function to exit and the preprocessRemovedSection() function to be called on the next iteration
    # - Encountering a #endif statement causes the top of the ifdef stack to be popped off. If in the PREPROCESS_SECTION state, this does not cause
    #   a state change, but if in the REMOVE_SECTION state, it does (but only if it was the ifdef that evaluated to false)
    # - For the preprocessRemovedSection() method, only need to push and pop when encountering #ifdef, #ifndef, #if, and #endif. Also need to keep track
    #   of line numbers and input indices. Keep track of the ifdef that started the removal and if that one is popped off the stack, change state to
    #   PREPROCESS_SECTION and return
    def processIfdef(self):
        # check condition
        # create entry and push onto stack
        # if condition true
        #   preprocessSection
        # else
        #   preprocessRemovedSection
        raise Exception(f"Not implemented")

    def processIfndef(self):
        raise Exception(f"Not implemented")

    def processIf(self):
        raise Exception(f"Not implemented")

    def processElse(self):
        raise Exception(f"Not implemented")

    def processEndif(self):
        # pop entry from stack
        raise Exception(f"Not implemented")




    def processObjectLikeMacroExpansion(self):

        fileEntry = self.inputFileStack.getTop()

        macroName = ""
        for macro in self.objectLikeMacroTable.keys():
            if (fileEntry.currentInputIndex + len(macro) < len(fileEntry.inputBuffer)) and (fileEntry.inputBuffer[fileEntry.currentInputIndex:fileEntry.currentInputIndex+len(macro)] == macro):
                macroName = macro
                break

        if macroName == "":
            raise Exception(f"Error in processing object like macro expansion. Need better error messages")

        macroBody = self.objectLikeMacroTable[macroName]

        # set variable for macro has been recursively substituted and loop through macro body making substitutions
        recursiveSubstitutionOccurred = True
        processedMacroBody = ""
        while recursiveSubstitutionOccurred:

            i = 0
            recursiveSubstitutionOccurred = False
            processedMacroBody = ""

            # loop through macro body subtituting other macros encountered
            while i < len(macroBody):
                if self.isObjectLikeMacroExpansion(macroBody, i):

                    # find the sub-macro name from the table and current position
                    subMacroName = ""
                    for macro in self.objectLikeMacroTable.keys():
                        if fileEntry.inputBuffer[fileEntry.currentInputIndex:fileEntry.currentInputIndex+len(macro)] == macro:
                            subMacroName = macro
                            break

                    # prevent recursive expansion of macro with the same name
                    if subMacroName == macroName:
                        processedMacroBody += subMacroName
                        i += len(subMacroName)
                        continue

                    # get the body and substitute
                    subMacroBody = self.objectLikeMacroTable[subMacroName]
                    processedMacroBody += subMacroBody

                    # increment i and set recursive substitution to True to keep expanding
                    i += len(subMacroName)
                    recursiveSubstitutionOccurred = True

                elif self.isFunctionLikeMacroExpansion(macroBody, i):
                    # find macro name
                    # parse parameters
                    # get macro expansion from table
                    # substitute parameters
                    # processedMacroBody += macroExpansion
                    # i += len(macroName)
                    # recursiveSubstitutionOccurred = True
                    pass

                else:
                    processedMacroBody += macroBody[i]
                    i += 1

            macroBody = processedMacroBody

        fileEntry.currentInputIndex += len(macroName)
        self.outputBuffer += processedMacroBody
        self.currentOutputIndex += len(processedMacroBody)

        self.inputFileStack.setTop(fileEntry)




    def parseFunctionLikeMacroArgument(self) -> str:
        parenMatchingStack: Stack = Stack()
        fileEntry: PreprocessedFileEntry = self.inputFileStack.getTop()
        startingIndex: int = fileEntry.currentInputIndex
        done = False

        while not done:
            if fileEntry.nextCharacter() == "(":
                parenMatchingStack.push("(")
                fileEntry.currentInputIndex += 1
            elif fileEntry.nextCharacter() == ")":
                if parenMatchingStack.empty():
                    done = True
                else:
                    parenMatchingStack.pop()
                    fileEntry.currentInputIndex += 1
            elif fileEntry.nextCharacter() == "," and parenMatchingStack.empty():
                done = True
            else:
                fileEntry.currentInputIndex += 1

        arg = fileEntry.inputBuffer[startingIndex:fileEntry.currentInputIndex]
        if fileEntry.nextCharacter() == ",":
            fileEntry.currentInputIndex += 1

        return arg



    def expandMacroArgument(self, arg: str) -> str:

        expandedArgument = ""
        temp = arg
        expansionEncountered = True
        index = 0

        while expansionEncountered:
            expandedArgument = ""
            expansionEncountered = False

            while index < len(temp):
                if self.isObjectLikeMacroExpansion(temp, index):
                    macroName = ""
                    for macro in self.objectLikeMacroTable.keys():
                        if index + len(macro) < len(temp) and temp[index:index+len(macro)] == macro:
                            macroName = macro
                            break
                    expandedArgument += self.objectLikeMacroTable[macroName]
                    index += len(macroName)
                    expansionEncountered = True

                elif self.isFunctionLikeMacroExpansion(temp, index):
                    print("Function-like macro expansion inside of function-like macro expansion args. Ignored.")
                    macroName = ""
                    for macro in self.functionLikeMacroTable.keys():
                        if index + len(macro) < len(temp) and temp[index:index+len(macro)] == macro:
                            macroName = macro
                            break
                    expandedArgument += macroName
                    index += len(macroName)
                else:
                    expandedArgument += temp[index]
                    index += 1
            
            temp = expandedArgument
            index = 0


        return expandedArgument

            # iterate over arg string
            # check if there is a macro to expand at the current index
            # if yes, expand it, set expansionEncountered = True, and increment index by size of macro name
            # else, increment index by 1 and continue


    def expandFunctionLikeMacroBody(self, macroBody: str, argExpansionMapping: dict[str,str]) -> str:

        expandedMacroBody = ""
        temp = macroBody
        expansionEncountered = True
        index = 0

        while expansionEncountered:
            expandedMacroBody = ""
            expansionEncountered = False

            while index < len(temp):
                if self.isObjectLikeMacroExpansion(temp, index):
                    macroName = ""
                    for macro in self.objectLikeMacroTable.keys():
                        if index + len(macro) < len(temp) and temp[index:index+len(macro)] == macro:
                            macroName = macro
                            break
                    expandedMacroBody += self.objectLikeMacroTable[macroName]
                    index += len(macroName)
                    expansionEncountered = True

                elif self.isFunctionLikeMacroExpansion(temp, index):
                    print("Function-like macro expansion inside of function-like macro expansion args. Ignored.")
                    macroName = ""
                    for macro in self.functionLikeMacroTable.keys():
                        if index + len(macro) < len(temp) and temp[index:index+len(macro)] == macro:
                            macroName = macro
                            break
                    expandedMacroBody += macroName
                    index += len(macroName)
                else:
                    arg = None
                    for argName in argExpansionMapping.keys():
                        if index + len(argName) < len(macroBody) and macroBody[index:index+len(argName)] == argName:
                            arg = argName
                            break
                    
                    if arg is None:
                        expandedMacroBody += temp[index]
                        index += 1
                    else:
                        expandedMacroBody += argExpansionMapping[arg]
                        index += len(arg)

            temp = expandedMacroBody
            index = 0


        return expandedMacroBody


    # TODO: get macro name
    # TODO: parse macro arguments
    #        - for each argument, go until you hit "," but match parentheses
    #        - need sub-function to parse it
    # TODO: count args and make sure 
    def processFunctionLikeMacroExpansion(self):

        fileEntry: PreprocessedFileEntry = self.inputFileStack.getTop()

        macroName = ""
        for macro in self.functionLikeMacroTable.keys():
            if (fileEntry.currentInputIndex + len(macro) < len(fileEntry.inputBuffer)) and (fileEntry.inputBuffer[fileEntry.currentInputIndex:fileEntry.currentInputIndex+len(macro)] == macro):
                macroName = macro
                break

        if macroName == "":
            raise Exception(f"Error in processing object like macro expansion. Macro name is null. Need better error messages")

        macroEntry: FunctionLikeMacroEntry = self.functionLikeMacroTable[macroName]

        fileEntry.currentInputIndex += len(macroName)
        fileEntry.currentInputIndex += 1 # since following '('

        args = []
        while fileEntry.nextCharacter() != ")":
            # TODO: eat whitespace
            args.append(self.parseFunctionLikeMacroArgument())

        fileEntry.currentInputIndex += 1

        if len(args) != len(macroEntry.argumentList):
            raise Exception(f"Incorrect number of arguments passed to macro {macroName}. Expected {len(macroEntry.argumentList)} but got {len(args)}")

        expandedArgs = []
        for arg in args:
            expandedArgs.append(self.expandMacroArgument(arg))

        expandedMacroBody = self.expandFunctionLikeMacroBody(macroEntry.macroBody, dict(zip(macroEntry.argumentList, expandedArgs)))
        self.outputBuffer += expandedMacroBody
        self.currentOutputIndex += len(expandedMacroBody)


        # parse macro arguments
        # macroStack = Stack()
        # get arguments
        # match arguments to argument names
        # expand macro arguments
        # scan macro body for argument names and substitute expansion


    def processSingleLineComment(self):

        fileEntry: PreprocessedFileEntry = self.inputFileStack.getTop()
        beginIndex = fileEntry.currentInputIndex


        while (fileEntry.currentInputIndex < len(fileEntry.inputBuffer)) and (fileEntry.inputBuffer[fileEntry.currentInputIndex] != "\n"):
            fileEntry.currentInputIndex += 1

        lineControl = SingleLineComment(fileEntry.fileName, fileEntry.currentInputLineNumber, fileEntry.currentInputLineNumberPreprocessed, \
                                        0, beginIndex, beginIndex - fileEntry.currentInputIndex)

        self.currentIncludeTreeNode.lineControlEntries.append(lineControl)

        self.inputFileStack.setTop(fileEntry)



    def processMultiLineComment(self):

        fileEntry = self.inputFileStack.getTop()

        beginIndex = fileEntry.currentInputIndex
        beginLine = fileEntry.currentInputLineNumber


        while (fileEntry.currentInputIndex < len(fileEntry.inputBuffer)-1) and \
            (fileEntry.inputBuffer[fileEntry.currentInputIndex:fileEntry.currentInputIndex+2] != "*/"):
            if fileEntry.inputBuffer[fileEntry.currentInputIndex] == "\n":
                fileEntry.currentInputLineNumber += 1

            fileEntry.currentInputIndex += 1
        
        if fileEntry.currentInputIndex >= len(fileEntry.inputBuffer)-1:
            raise Exception(f"Incorrect syntax for multi-line comment but I still need to get proper error messages")

        fileEntry.currentInputIndex += 2
        lineControl = MultiLineComment(fileEntry.fileName, beginLine, fileEntry.currentInputLineNumberPreprocessed, \
                                       beginLine-fileEntry.currentInputLineNumber, beginIndex, beginIndex-fileEntry.currentInputIndex)
        self.currentIncludeTreeNode.lineControlEntries.append(lineControl)


        self.inputFileStack.setTop(fileEntry)



    def processString(self):
        fileEntry = self.inputFileStack.getTop()
        self.outputBuffer += fileEntry.inputBuffer[fileEntry.currentInputIndex]
        fileEntry.currentInputIndex += 1

        while (fileEntry.currentInputIndex < len(fileEntry.inputBuffer)) and (fileEntry.inputBuffer[fileEntry.currentInputIndex] != "\""):
            self.outputBuffer += fileEntry.inputBuffer[fileEntry.currentInputIndex]
            fileEntry.currentInputIndex += 1
        
        if fileEntry.currentInputIndex >= len(fileEntry.inputBuffer):
            raise Exception(f"Error in string syntax but I need new error messages")

        self.outputBuffer += fileEntry.inputBuffer[fileEntry.currentInputIndex]
        fileEntry.currentInputIndex += 1

        self.inputFileStack.setTop(fileEntry)



    def preprocessSection(self, fileEntry: PreprocessedFileEntry) -> PreprocessedFileEntry:
        raise Exception(f"Not implemented")



    def preprocessFileContents(self, fileName: str):

        fullFilePath = self.findFile(fileName)
        self.inputFileStack.push(PreprocessedFileEntry(fullFilePath))
        fileEntry: PreprocessedFileEntry = self.inputFileStack.getTop()

        newNode = IncludeTreeNode(self.currentIncludeTreeNode, fileName, self.currentOutputIndex, self.currentOutputLineNumber)
        self.currentIncludeTreeNode.addChild(newNode)
        self.currentIncludeTreeNode = newNode

        # while fileEntry.currentInputIndex < len(fileEntry.inputBuffer) and preprocessFile (make this a state variable)
        # and have two functions preprocessSection() and preprocessRemovedSection()
        while fileEntry.currentInputIndex < len(fileEntry.inputBuffer):

            if isInclude(fileEntry.inputBuffer, fileEntry.currentInputIndex):
                self.parseInclude() # Do whole file before returning

            elif isDefine(fileEntry.inputBuffer, fileEntry.currentInputIndex):
                self.processDefine() # Do whole define before returning

            elif isUndef(fileEntry.inputBuffer, fileEntry.currentInputIndex):
                self.processUndef() # Do whole undef before returning

            elif isIfdef(fileEntry.inputBuffer, fileEntry.currentInputIndex):
                self.processIfdef() # For ifdef, process whole ifdef, but change state and 

            elif isIfndef(fileEntry.inputBuffer, fileEntry.currentInputIndex):
                self.processIfndef()

            elif isIf(fileEntry.inputBuffer, fileEntry.currentInputIndex):
                self.processIf()

            elif isElse(fileEntry.inputBuffer, fileEntry.currentInputIndex):
                self.processElse()

            elif isEndif(fileEntry.inputBuffer, fileEntry.currentInputIndex):
                self.processEndif()

            elif isSingleLineComment(fileEntry.inputBuffer, fileEntry.currentInputIndex):
                self.processSingleLineComment()

            elif isMultiLineComment(fileEntry.inputBuffer, fileEntry.currentInputIndex):
                self.processMultiLineComment()

            elif isString(fileEntry.inputBuffer, fileEntry.currentInputIndex):
                self.processString()

            elif self.isObjectLikeMacroExpansion(fileEntry.inputBuffer, fileEntry.currentInputIndex):
                self.processObjectLikeMacroExpansion()

            elif self.isFunctionLikeMacroExpansion(fileEntry.inputBuffer, fileEntry.currentInputIndex):
                self.processFunctionLikeMacroExpansion()

            elif fileEntry.inputBuffer[fileEntry.currentInputIndex] == "\n":
                self.outputBuffer += "\n"
                self.currentOutputIndex += 1
                self.currentOutputLineNumber += 1

                fileEntry.currentInputIndex += 1
                fileEntry.currentInputLineNumber += 1
                fileEntry.currentInputLineNumberPreprocessed += 1

            else:
                # also need to check for macro in macro tables
                self.outputBuffer += fileEntry.inputBuffer[fileEntry.currentInputIndex]
                self.currentOutputIndex += 1
                fileEntry.currentInputIndex += 1

        self.currentIncludeTreeNode.endIndex = self.currentOutputIndex
        self.currentIncludeTreeNode.endLineNumber = self.currentOutputLineNumber

        self.currentIncludeTreeNode = self.currentIncludeTreeNode.parent




    def preprocess(self, fileName: str):
        self.topLevelFile = fileName

        self.objectLikeMacroTable = {}
        self.functionLikeMacroTable = {}
        self.inputFileStack = Stack()
        self.conditionalIncludeStack = Stack()

        self.outputBuffer = ""
        self.currentOutputIndex = 0
        self.currentOutputLineNumber = 1

        rootNode = IncludeTreeNode(None, fileName, self.currentOutputIndex, self.currentOutputLineNumber)
        self.includeTree = IncludeTree(rootNode)
        self.currentIncludeTreeNode = self.includeTree.root

        # only push fileEntry onto stack before processing next include
        # actually no need for fileStack, since local variables are saved across function calls
        # no. filestack makes it cleaner with no need to repeatedly assign the fileEntry back to itself across calls
        self.inputFileStack.push(PreprocessedFileEntry(fileName))
        fileEntry: PreprocessedFileEntry = self.inputFileStack.getTop()

        while fileEntry.currentInputIndex < len(fileEntry.inputBuffer):

            if isInclude(fileEntry.inputBuffer, fileEntry.currentInputIndex):
                self.parseInclude()

            elif isDefine(fileEntry.inputBuffer, fileEntry.currentInputIndex):
                self.processDefine()

            elif isUndef(fileEntry.inputBuffer, fileEntry.currentInputIndex):
                self.processUndef()

            elif isIfdef(fileEntry.inputBuffer, fileEntry.currentInputIndex):
                self.processIfdef()

            elif isIfndef(fileEntry.inputBuffer, fileEntry.currentInputIndex):
                self.processIfndef()

            elif isIf(fileEntry.inputBuffer, fileEntry.currentInputIndex):
                self.processIf()

            elif isElse(fileEntry.inputBuffer, fileEntry.currentInputIndex):
                self.processElse()

            elif isEndif(fileEntry.inputBuffer, fileEntry.currentInputIndex):
                self.processEndif()

            elif isSingleLineComment(fileEntry.inputBuffer, fileEntry.currentInputIndex):
                self.processSingleLineComment()

            elif isMultiLineComment(fileEntry.inputBuffer, fileEntry.currentInputIndex):
                self.processMultiLineComment()

            elif isString(fileEntry.inputBuffer, fileEntry.currentInputIndex):
                self.processString()

            elif self.isObjectLikeMacroExpansion(fileEntry.inputBuffer, fileEntry.currentInputIndex):
                self.processObjectLikeMacroExpansion()

            elif self.isFunctionLikeMacroExpansion(fileEntry.inputBuffer, fileEntry.currentInputIndex):
                self.processFunctionLikeMacroExpansion()

            elif fileEntry.inputBuffer[fileEntry.currentInputIndex] == "\n":
                self.outputBuffer += "\n"
                self.currentOutputIndex += 1
                self.currentOutputLineNumber += 1

                fileEntry.currentInputIndex += 1
                fileEntry.currentInputLineNumber += 1
                fileEntry.currentInputLineNumberPreprocessed += 1

            else:
                self.outputBuffer += fileEntry.inputBuffer[fileEntry.currentInputIndex]
                self.currentOutputIndex += 1
                fileEntry.currentInputIndex += 1


        self.currentIncludeTreeNode.endIndex = self.currentOutputIndex
        self.currentIncludeTreeNode.endLineNumber = self.currentOutputLineNumber

        print(str(self.objectLikeMacroTable))
        print(str({key: str(value) for key, value in self.functionLikeMacroTable.items()}))


    def writeToOutputFile(self, outputFileName: str):

        with open(outputFileName, "w") as f:
            f.write(self.outputBuffer)



    def getOriginalFileAndLineNumber(self, stringOffset: int, lineNumber: int) -> tuple[str, int]:

        node = self.includeTree.findNodeFromIndex(stringOffset)

        if node is None:
            raise Exception(f"String offset {stringOffset} into file {self.includeTree.root.fileName} is out of range")

        fileName = node.fileName

        # line number within the included file AFTER preprocessing
        # this line number may be different than the line number in
        # the original file before preprocessing due to macro expansions
        # and definitions and removing of comments, etc.
        fileLineNumber = lineNumber - node.startLineNumber


        index = 0
        while node.lineControlEntries[index].preprocessedLineNumber <= fileLineNumber:
            index += 1

        index -= 1
        originalLineNumber = 0

        if node.lineControlEntries[index].preprocessedLineNumber == fileLineNumber:
            originalLineNumber = node.lineControlEntries[index].lineNumber

        else:
            originalLineNumber = node.lineControlEntries[index].lineNumber + (fileLineNumber - node.lineControlEntries[index].preprocessedLineNumber)

        return (fileName, originalLineNumber)


# create output buffer class that has ring buffer that doubles in size up to a point
# and then writes content to a file upon overflow of ring buffer. Overload [] operator
# and maybe some others


# if encounter #define
    # while current < EOF and current < endl
        # find key of define
        # find value of define
        # add (key, value)
        # deal with recursive substitution of macros

# if encounter #define(...)
    # while current < EOF and current < endl


# replace #defines, including multiline ones with '\n's equal in number to make line numbers match up

# add substitution entries that have output index, size and macro name

# each token has file name and line number taken by 