

from tokenizer import Tokenizer, Token, TokenType, isValidHexadecimalCharacter
from enum import Enum
from typing import List



class ParseError(Exception):
    
    def __init__(self, message: str):
        self.message = message



'''
@enum NodeType

Defines the type of the node. Each non-terminal
node has a unique type here. All terminal nodes
share the TERMINAL NodeType. For terminal node
subtypes, see @ref TerminalType
'''
class NodeType(Enum):
    TERMINAL = 0                   # terminal node (i.e. a single token)
    DEVICE_TREE = 1                # entire device tree file
    FILE_BODY = 2                  # body of the file (file minus the EOF)
    PHANDLE_OVERRIDE = 3           # phandle override node (&name = {};)
    ROOT_NODE_DEFINITION = 4       # root node definition
    NODE_BODY = 5                  # body of the node
    NODE_DEFINITION = 6            # node definition (contains a node body)
    NODE_DECLARATION = 7           # node declaration (name, @address, label)
    NODE_PROPERTY = 8              # property
    NODE_PROPERTY_VALUE = 9        # the value of the property
    PROPERTY_VALUE_ARRAY = 10      # array of values, i.e. phandle array
    NODE_LABEL = 11                # label for node (i.e. uart1: )
    NODE_ADDRESS = 12              # address for node (i.e. @bfc01000)
    PHANDLE_REFERENCE = 13         # &label


'''
@enum TerminalType

This enum describes the type of the terminal node. This is roughly
equivalent to the TokenType enum defined in the tokenizer, but with
some distinctions. Some tokens are ambiguous when parsed by the
tokenizer but become unambiguous when parsed by the recursive descent
parser. For example, node names could also be property names based on
the tokenizer grammar, but in the parser grammar they become unambiguous.
Thus, a new unambiguous TerminalType.NODE_NAME is created.
'''
class TerminalType(Enum):
    LEFT_CURLY_BRACE = 1
    RIGHT_CURLY_BRACE = 2
    COLON = 3
    HEXADECIMAL_NUMBER = 4
    STRING = 5
    HASHTAG = 6
    AT_SYMBOL = 7
    SEMICOLON = 8
    LEFT_ANGLE_BRACKET = 9
    RIGHT_ANGLE_BRACKET = 10
    AMPERSAND = 11
    EQUALS = 12
    COMMA = 13
    FORWARD_SLASH = 14
    DECIMAL_NUMBER = 15
    NODE_LABEL = 16
    NODE_NAME = 17
    PROPERTY_NAME = 18




'''
Represents a node in the parse tree. This includes nodes
for non-terminal productions and terminals themselves.
For example, a node definition will have a ParseTreeNode
representing it, and have sub-nodes representing the
node declaration ([label:] node-name[@unit-address]), the
opening and closing curly braces, the terminating semicolon,
and the node body. The terminals '{', '}', and ';' are
represented by the @ref TerminalNode subclass of this class.
'''
class ParseTreeNode:


    def __init__(self, type: NodeType, parent, lineNumber):
        self.type = type
        self.parent = parent
        self.children: List[ParseTreeNode] = []
        self.lineNumber = lineNumber    # first line at which the node appears


    def isRoot(self) -> bool:
        return self.parent is None


    def __str__(self) -> str:
        return "Node Type: " + str(self.type)


    def getNodeName(self):
        return self.type.name


    def addChild(self, childNode):
        self.children.append(childNode)


    def output(self, indentLevel):
        out = ""
        for i in range(indentLevel):
            out += "   "

        out += self.getNodeName()
        print(out)

        for node in self.children:
            node.output(indentLevel+1)



    def print(self):
        out = "Type: " + self.type.name
        print(out)

        for node in self.children:
            node.print()


    def traverse(self, rootString: str):

        for node in self.children:
            rootString += node.traverse(rootString)
        
        return rootString


'''
Represents a node in the parse tree for a terminal (not a production).
Terminals have actual values associated with them (strings), whereas
a non-terminal represented by the @ref ParseTreeNode class has no
value associated with it since it is composed of terminals that do.
'''
class TerminalNode(ParseTreeNode):


    def __init__(self, parent, lineNumber, terminalType: TerminalType, value: str):
        super().__init__(NodeType.TERMINAL, parent, lineNumber)
        self.terminalType = terminalType
        self.value = value

        assert len(self.children) == 0


    def output(self, indentLevel):
        out = ""
        for i in range(indentLevel):
            out += "   "

        out += self.value
        print(out)


class ParseTree:

    def __init__(self):
        self.rootNode = ParseTreeNode(NodeType.DEVICE_TREE, None, 0)
    
    def print(self):
        self.rootNode.print()
    

    def output(self):
        self.rootNode.output(0)


    def traverse(self) -> str:
        return self.rootNode.traverse("")



'''
The recursive descent parser implements parsing of the context-free grammar for the
device tree. It contains a number of methods to parse the productions of the grammar,
one method per production. Parsing starts with the whole file and recursively descends
the parse tree invoking the proper methods based on the tokens received. For each
production parsing method, there is a calling convention for what the state of the parse
tree must be before the method is invoked by the calling production parsing method and
what the state of the parse tree must be left as after the called production parsing method
returns. The former is the responsibility of the caller, while the latter is the responsibility
of the callee. Before the callee is invoked, the caller must have the lowest down parse
tree node be the parent of the node that the callee is supposed to parse and have the
self.currentParseTreeNode member pointing to this node. It cannot add the node to be parsed
by the callee to the tree - that is the responsibility of the callee. The callee will
add the node it is supposed to parse to the tree as its first action and then implement
any more processing necessary to parse the full node, including potentially recursive calls
to parse sub-nodes. Before returning, the callee must set the self.currentParseTreeNode
member to point to the parent of the node it parsed. Thus, before the callee is invoked,
the self.currentParseTreeNode points to the parent node which has no sub-nodes, and after
the callee returns the entire sub-tree represented by the callee node has been added to
the parse tree with the self.currentParseTreeNode member in the same state it was in
before. From the perspective of the caller, the sub-tree seems to just appear out of
nowhere. Sub-nodes are added whenever a new token or set of tokens are encountered, but
the self.currentParseTreeNode pointer, which keeps track of the current non-terminal node
always points to the node representing the current production.

The self.currentToken member points to the current token being looked at, and similarly
there is a calling convention for the state this must be in before and after calling the
method to parse a sub-production. Before calling the method, the self.currentToken points
to the first token that is part of the production. The sub-production method will consume
all of the tokens that are part of its production and after it returns, the self.currentToken
member will point to the next token after the last that is part of its production. Thus,
the calling method will be in the right state to continue parsing.
'''
class RecursiveDescentParser:


    '''
    The lookAhead parameter must be at least 1.
    '''
    def __init__(self, tokenizer: Tokenizer, filePath: str, lookAhead: int):
        self.tokenizer = tokenizer
        self.lookAhead = lookAhead
        self.lookAheadBuffer = [None] * (lookAhead+1)       # currentToken counts as lookahead=0, so if you want to look ahead by 1, need 2 element array
        self.currentToken = None
        self.lookAheadInitialized = False
        self.filePath = filePath
        self.parseTree = None
        self.currentParseTreeNode = ParseTreeNode(NodeType.DEVICE_TREE, None, False)                    # for keeping track of which node we are on during parse tree construction


    def getLineNumber(self) -> int:
        return self.tokenizer.getCurrentLineNumber()


    def getCurrentLine(self) -> str:
        return self.tokenizer.getCurrentLine()


    '''
    Returns the next token to the user. Typically, this will be stored in currentToken.
    Mutates the lookAheadInitialized, and lookAheadBuffer member variables. Index 0
    in the lookAheadBuffer is the current token so it is overwritten when getting
    the next token and all later tokens are moved down 1
    '''
    def getNextToken(self):

        # initialize the lookahead buffer by getting lookAhead number tokens from the tokenizer
        if not self.lookAheadInitialized:
            for i in range(self.lookAhead+1):
                self.lookAheadBuffer[i] = self.tokenizer.getNextToken()
            self.lookAheadInitialized = True

        # move tokens in lookahead buffer up by one
        else:
            for i in range(self.lookAhead):
                self.lookAheadBuffer[i] = self.lookAheadBuffer[i+1]

            self.lookAheadBuffer[self.lookAhead] = self.tokenizer.getNextToken()

        # REMOVE
        # print(self.lookAheadBuffer[0])

        # return first entry in the lookahead buffer
        return self.lookAheadBuffer[0]


    '''
    Does not mutate the lookAheadBuffer.
    '''
    def peekAhead(self, lookAheadIndex=1):
        return self.lookAheadBuffer[lookAheadIndex]


    def parsePhandleReference(self):

        if self.currentToken is None:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Current token is None.")

        currentNode: ParseTreeNode = ParseTreeNode(NodeType.PHANDLE_REFERENCE, self.currentParseTreeNode, self.currentToken.lineNumber)
        self.currentParseTreeNode.addChild(currentNode)
        self.currentParseTreeNode = currentNode

        if self.currentToken.type == TokenType.AMPERSAND:
            newNode: TerminalNode = TerminalNode(self.currentParseTreeNode, self.currentToken.lineNumber, TerminalType.AMPERSAND, self.currentToken.value)
            self.currentParseTreeNode.addChild(newNode)
        else:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Expected \"&\".\n{self.getCurrentLine()}")

        self.currentToken = self.getNextToken()

        if (self.currentToken.type == TokenType.HEX_NUMBER_NO_PREFIX_OR_LABEL_OR_NODE_OR_PROPERTY) or \
            (self.currentToken.type == TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME):
            newNode: TerminalNode = TerminalNode(self.currentParseTreeNode, self.currentToken.lineNumber, TerminalType.NODE_LABEL, self.currentToken.value)
            self.currentParseTreeNode.addChild(newNode)
        else:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Expected node label.\n{self.getCurrentLine()}")

        self.currentToken = self.getNextToken()
        self.currentParseTreeNode = self.currentParseTreeNode.parent


    def parsePropertyValueArray(self):

        if self.currentToken is None:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Current token is None.")

        # add the current node to the parse tree before adding sub-nodes of the production
        currentNode: ParseTreeNode = ParseTreeNode(NodeType.PROPERTY_VALUE_ARRAY, self.currentParseTreeNode, self.currentToken.lineNumber)
        self.currentParseTreeNode.addChild(currentNode)
        self.currentParseTreeNode = currentNode

        if self.currentToken.type == TokenType.LEFT_ANGLE_BRACKET:
            newNode: TerminalNode = TerminalNode(self.currentParseTreeNode, self.currentToken.lineNumber, TerminalType.LEFT_ANGLE_BRACKET, self.currentToken.value)
            self.currentParseTreeNode.addChild(newNode)
        else:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Expected \"<\".\n{self.getCurrentLine()}")

        self.currentToken = self.getNextToken()

        while self.currentToken.type != TokenType.RIGHT_ANGLE_BRACKET:

            if (self.currentToken.type == TokenType.HEXADECIMAL_NUMBER) or (self.currentToken.type == TokenType.HEX_NUMBER_NO_PREFIX_OR_LABEL_OR_NODE_OR_PROPERTY):
                newNode: TerminalNode = TerminalNode(self.currentParseTreeNode, self.currentToken.lineNumber, TerminalType.HEXADECIMAL_NUMBER, self.currentToken.value)
                self.currentParseTreeNode.addChild(newNode)
                self.currentToken = self.getNextToken()

            elif self.currentToken.type == TokenType.DECIMAL_NUMBER:
                newNode: TerminalNode = TerminalNode(self.currentParseTreeNode, self.currentToken.lineNumber, TerminalType.DECIMAL_NUMBER, self.currentToken.value)
                self.currentParseTreeNode.addChild(newNode)
                self.currentToken = self.getNextToken()

            elif self.currentToken.type == TokenType.AMPERSAND:
                self.parsePhandleReference()

            else:
                raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Expected one of: number, hexadecimal number, \"&\".\n{self.getCurrentLine()}")


        newNode: TerminalNode = TerminalNode(self.currentParseTreeNode, self.currentToken.lineNumber, TerminalType.RIGHT_ANGLE_BRACKET, self.currentToken.value)
        self.currentParseTreeNode.addChild(newNode)

        self.currentToken = self.getNextToken()
        self.currentParseTreeNode = self.currentParseTreeNode.parent



    # TODO: Fix this to include types for property values. Probs need to read more about that.
    # Should include parseStringOrStringArray that takes multiple strings separated by commas
    def parseNodePropertyValue(self):

        if self.currentToken is None:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Current token is None.")


        currentNode: ParseTreeNode = ParseTreeNode(NodeType.NODE_PROPERTY_VALUE, self.currentParseTreeNode, self.currentToken.lineNumber)
        self.currentParseTreeNode.addChild(currentNode)
        self.currentParseTreeNode = currentNode


        while self.currentToken.type != TokenType.SEMICOLON:

            if self.currentToken.type == TokenType.STRING:
                newNode: TerminalNode = TerminalNode(self.currentParseTreeNode, self.currentToken.lineNumber, TerminalType.STRING, self.currentToken.value)
                self.currentParseTreeNode.addChild(newNode)
                self.currentToken = self.getNextToken()

            elif self.currentToken.type == TokenType.LEFT_ANGLE_BRACKET:
                self.parsePropertyValueArray()

            else:
                raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Expected one of: string, \"&\", \"<\" but received token of type {self.currentToken.type.name}. Token value: {self.currentToken.value}\n{self.getCurrentLine()}")


            if self.currentToken.type == TokenType.COMMA:
                newNode: TerminalNode = TerminalNode(self.currentParseTreeNode, self.currentToken.lineNumber, TerminalType.COMMA, self.currentToken.value)
                self.currentParseTreeNode.addChild(newNode)
                self.currentToken = self.getNextToken()

        self.currentParseTreeNode = self.currentParseTreeNode.parent


    def parseNodeProperty(self):

        if self.currentToken is None:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Current token is None.")

        currentNode: ParseTreeNode = ParseTreeNode(NodeType.NODE_PROPERTY, self.currentParseTreeNode, self.currentToken.lineNumber)
        self.currentParseTreeNode.addChild(currentNode)
        self.currentParseTreeNode = currentNode

        if self.currentToken.type == TokenType.HASHTAG:
            newNode: TerminalNode = TerminalNode(self.currentParseTreeNode, self.currentToken.lineNumber, TerminalType.HASHTAG, self.currentToken.value)
            self.currentParseTreeNode.addChild(newNode)
            self.currentToken = self.getNextToken()


        if (self.currentToken.type == TokenType.NODE_OR_PROPERTY_NAME) or (self.currentToken.type == TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME) \
            or (self.currentToken.type == TokenType.HEX_NUMBER_NO_PREFIX_OR_LABEL_OR_NODE_OR_PROPERTY):
            newNode: TerminalNode = TerminalNode(self.currentParseTreeNode, self.currentToken.lineNumber, TerminalType.PROPERTY_NAME, self.currentToken.value)
            self.currentParseTreeNode.addChild(newNode)
        else:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Expected node property name.\n{self.getCurrentLine()}")

        self.currentToken = self.getNextToken()

        if self.currentToken.type == TokenType.EQUALS:
            newNode: TerminalNode = TerminalNode(self.currentParseTreeNode, self.currentToken.lineNumber, TerminalType.EQUALS, self.currentToken.value)
            self.currentParseTreeNode.addChild(newNode)
            self.currentToken = self.getNextToken()
            self.parseNodePropertyValue()


        if self.currentToken.type == TokenType.SEMICOLON:
            newNode: TerminalNode = TerminalNode(self.currentParseTreeNode, self.currentToken.lineNumber, TerminalType.SEMICOLON, self.currentToken.value)
            self.currentParseTreeNode.addChild(newNode)
        else:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Expected \";\".\n{self.getCurrentLine()}")

        self.currentToken = self.getNextToken()
        self.currentParseTreeNode = self.currentParseTreeNode.parent


    def parseNodeLabel(self):

        if self.currentToken is None:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Current token is None.")

        currentNode: ParseTreeNode = ParseTreeNode(NodeType.NODE_LABEL, self.currentParseTreeNode, self.currentToken.lineNumber)
        self.currentParseTreeNode.addChild(currentNode)
        self.currentParseTreeNode = currentNode

        if (self.currentToken.type == TokenType.HEX_NUMBER_NO_PREFIX_OR_LABEL_OR_NODE_OR_PROPERTY) or \
            (self.currentToken.type == TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME):
            newNode: TerminalNode = TerminalNode(self.currentParseTreeNode, self.currentToken.lineNumber, TerminalType.NODE_LABEL, self.currentToken.value)
            self.currentParseTreeNode.addChild(newNode)
        else:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Expected node label.\n{self.getCurrentLine()}")

        self.currentToken = self.getNextToken()


        if self.currentToken.type == TokenType.COLON:
            newNode: TerminalNode = TerminalNode(self.currentParseTreeNode, self.currentToken.lineNumber, TerminalType.COLON, self.currentToken.value)
            self.currentParseTreeNode.addChild(newNode)
        else:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Expected \":\".\n{self.getCurrentLine()}")

        self.currentToken = self.getNextToken()
        self.currentParseTreeNode = self.currentParseTreeNode.parent



    def parseNodeAddress(self):

        if self.currentToken is None:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Current token is None.")

        currentNode: ParseTreeNode = ParseTreeNode(NodeType.NODE_ADDRESS, self.currentParseTreeNode, self.currentToken.lineNumber)
        self.currentParseTreeNode.addChild(currentNode)
        self.currentParseTreeNode = currentNode


        if self.currentToken.type == TokenType.AT_SYMBOL:
            newNode: TerminalNode = TerminalNode(self.currentParseTreeNode, self.currentToken.lineNumber, TerminalType.AT_SYMBOL, self.currentToken.value)
            self.currentParseTreeNode.addChild(newNode)
        else:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Expected \"@\".\n{self.getCurrentLine()}")


        self.currentToken = self.getNextToken()


        if self.currentToken.type == TokenType.DECIMAL_NUMBER:
            newNode: TerminalNode = TerminalNode(self.currentParseTreeNode, self.currentToken.lineNumber, TerminalType.DECIMAL_NUMBER, self.currentToken.value)
            self.currentParseTreeNode.addChild(newNode)

        elif (self.currentToken.type == TokenType.HEXADECIMAL_NUMBER) or \
            (self.currentToken.type == TokenType.HEX_NUMBER_NO_PREFIX_OR_LABEL_OR_NODE_OR_PROPERTY):
            newNode: TerminalNode = TerminalNode(self.currentParseTreeNode, self.currentToken.lineNumber, TerminalType.HEXADECIMAL_NUMBER, self.currentToken.value)
            self.currentParseTreeNode.addChild(newNode)
        else:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Expected number. Token: {str(self.currentToken)}.\n{self.getCurrentLine()}")


        self.currentToken = self.getNextToken()
        self.currentParseTreeNode = self.currentParseTreeNode.parent        


    def parseNodeDeclaration(self):

        if self.currentToken is None:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Current token is None.")
        
        currentNode: ParseTreeNode = ParseTreeNode(NodeType.NODE_DECLARATION, self.currentParseTreeNode, self.currentToken.lineNumber)
        self.currentParseTreeNode.addChild(currentNode)
        self.currentParseTreeNode = currentNode

        if self.peekAhead(1).type == TokenType.COLON:
            self.parseNodeLabel()

        if (self.currentToken.type == TokenType.HEX_NUMBER_NO_PREFIX_OR_LABEL_OR_NODE_OR_PROPERTY) or \
            (self.currentToken.type == TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME) or (self.currentToken.type == TokenType.NODE_OR_PROPERTY_NAME):
            newNode: TerminalNode = TerminalNode(self.currentParseTreeNode, self.currentToken.lineNumber, TerminalType.NODE_NAME, self.currentToken.value)
            self.currentParseTreeNode.addChild(newNode)
            self.currentToken = self.getNextToken()
        else:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Expected node name.\n{self.getCurrentLine()}")

        if self.currentToken.type == TokenType.AT_SYMBOL:
            self.parseNodeAddress()
        
        self.currentParseTreeNode = self.currentParseTreeNode.parent



    def parseNodeDefinition(self):

        if self.currentToken is None:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Current token is None.")
        
        currentNode: ParseTreeNode = ParseTreeNode(NodeType.NODE_DEFINITION, self.currentParseTreeNode, self.currentToken.lineNumber)
        self.currentParseTreeNode.addChild(currentNode)
        self.currentParseTreeNode = currentNode

        self.parseNodeDeclaration()

        if self.currentToken.type == TokenType.LEFT_CURLY_BRACE:
            newNode: TerminalNode = TerminalNode(self.currentParseTreeNode, self.currentToken.lineNumber, TerminalType.LEFT_CURLY_BRACE, self.currentToken.value)
            self.currentParseTreeNode.addChild(newNode)
        else:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Expected \"{{\".\n{self.getCurrentLine()}")

        self.currentToken = self.getNextToken()
        self.parseNodeBody()

        if self.currentToken.type == TokenType.RIGHT_CURLY_BRACE:
            newNode: TerminalNode = TerminalNode(self.currentParseTreeNode, self.currentToken.lineNumber, TerminalType.RIGHT_CURLY_BRACE, self.currentToken.value)
            self.currentParseTreeNode.addChild(newNode)
        else:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Expected \"}}\".\n{self.getCurrentLine()}")

        self.currentToken = self.getNextToken()

        if self.currentToken.type == TokenType.SEMICOLON:
            newNode: TerminalNode = TerminalNode(self.currentParseTreeNode, self.currentToken.lineNumber, TerminalType.SEMICOLON, self.currentToken.value)
            self.currentParseTreeNode.addChild(newNode)
        else:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Expected \";\".\n{self.getCurrentLine()}")

        self.currentToken = self.getNextToken()
        self.currentParseTreeNode = self.currentParseTreeNode.parent


    def parseNodeBody(self):

        if self.currentToken is None:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Current token is None.")

        # add node for current production
        currentNode: ParseTreeNode = ParseTreeNode(NodeType.NODE_BODY, self.currentParseTreeNode, self.currentToken.lineNumber)
        self.currentParseTreeNode.addChild(currentNode)
        self.currentParseTreeNode = currentNode

        # check for which sub-parser to call
        while self.currentToken.type != TokenType.RIGHT_CURLY_BRACE:

            # sub-parse property
            if self.currentToken.type == TokenType.HASHTAG or \
                self.peekAhead(1).type == TokenType.EQUALS or \
                self.peekAhead(1).type == TokenType.SEMICOLON:
                self.parseNodeProperty()

            # sub-parse sub-node definition
            elif self.peekAhead(1).type == TokenType.AT_SYMBOL or \
                 self.peekAhead(1).type == TokenType.COLON or \
                 self.peekAhead(1).type == TokenType.LEFT_CURLY_BRACE:
                self.parseNodeDefinition()

            else:
                raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Expected one of: \"#\", \"=\", \";\", \"@\", \":\", \"{{\".\n{self.getCurrentLine()}")

        # move back up 1 level in the parse tree
        self.currentParseTreeNode = self.currentParseTreeNode.parent


    def parseRootNodeDefinition(self):

        if self.currentToken is None:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Current token is None.")


        # add node for current production
        currentNode: ParseTreeNode = ParseTreeNode(NodeType.ROOT_NODE_DEFINITION, self.currentParseTreeNode, self.currentToken.lineNumber)
        self.currentParseTreeNode.addChild(currentNode)
        self.currentParseTreeNode = currentNode

        # check for forward slash
        if self.currentToken.type == TokenType.FORWARD_SLASH:
            newNode: TerminalNode = TerminalNode(self.currentParseTreeNode, self.currentToken.lineNumber, TerminalType.FORWARD_SLASH, self.currentToken.value)
            self.currentParseTreeNode.addChild(newNode)
        else:
            raise ParseError(f"Error in parsing file {self.filePath} at line {self.getLineNumber()}. Expected \"/\".\n{self.getCurrentLine()}")

        self.currentToken = self.getNextToken()

        # check for { after /
        if self.currentToken.type == TokenType.LEFT_CURLY_BRACE:
            newNode: TerminalNode = TerminalNode(self.currentParseTreeNode, self.currentToken.lineNumber, TerminalType.LEFT_CURLY_BRACE, self.currentToken.value)
            self.currentParseTreeNode.addChild(newNode)
        else:
            raise ParseError(f"Error in parsing file {self.filePath} at line {self.getLineNumber()}. Expected \"{{\".\n{self.getCurrentLine()}")

        self.currentToken = self.getNextToken()

        # parse the node body
        self.parseNodeBody()

        # get the closing brace
        if self.currentToken.type == TokenType.RIGHT_CURLY_BRACE:
            newNode: TerminalNode = TerminalNode(self.currentParseTreeNode, self.currentToken.lineNumber, TerminalType.RIGHT_CURLY_BRACE, self.currentToken.value)
            self.currentParseTreeNode.addChild(newNode)
        else:
            raise ParseError(f"Error in parsing file {self.filePath} at line {self.getLineNumber()}. Expected \"}}\".\n{self.getCurrentLine()}")

        self.currentToken = self.getNextToken()

        if self.currentToken.type == TokenType.SEMICOLON:
            newNode: TerminalNode = TerminalNode(self.currentParseTreeNode, self.currentToken.lineNumber, TerminalType.SEMICOLON, self.currentToken.value)
            self.currentParseTreeNode.addChild(newNode)
        else:
            raise ParseError(f"Error in parsing file {self.filePath} at line {self.getLineNumber()}. Expected \";\".\n{self.getCurrentLine()}") 

        self.currentToken = self.getNextToken()
        self.currentParseTreeNode = self.currentParseTreeNode.parent





    def parsePhandleOverride(self):

        if self.currentToken is None:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Current token is None.\n{self.getCurrentLine()}")


        # create the current node in the parse tree, add it to the tree, and move the currentParseTreeNode pointer to point to it
        currentNode: ParseTreeNode = ParseTreeNode(NodeType.PHANDLE_OVERRIDE, self.currentParseTreeNode, self.currentToken.lineNumber)
        self.currentParseTreeNode.addChild(currentNode)
        self.currentParseTreeNode = currentNode

        if self.currentToken.type == TokenType.AMPERSAND:
            self.parsePhandleReference()

        if self.currentToken.type == TokenType.LEFT_CURLY_BRACE:
            newNode: TerminalNode = TerminalNode(self.currentParseTreeNode, self.currentToken.lineNumber, TerminalType.LEFT_CURLY_BRACE, self.currentToken.value)
            self.currentParseTreeNode.addChild(newNode)
        else:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Expected \"{{\".\n{self.getCurrentLine()}")

        self.currentToken = self.getNextToken()
        self.parseNodeBody()

        if self.currentToken.type == TokenType.RIGHT_CURLY_BRACE:
            newNode: TerminalNode = TerminalNode(self.currentParseTreeNode, self.currentToken.lineNumber, TerminalType.RIGHT_CURLY_BRACE, self.currentToken.value)
            self.currentParseTreeNode.addChild(newNode)
        else:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Expected \"}}\".\n{self.getCurrentLine()}")

        self.currentToken = self.getNextToken()

        if self.currentToken.type == TokenType.SEMICOLON:
            newNode: TerminalNode = TerminalNode(self.currentParseTreeNode, self.currentToken.lineNumber, TerminalType.SEMICOLON, self.currentToken.value)
            self.currentParseTreeNode.addChild(newNode)
        else:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Expected \";\".\n{self.getCurrentLine()}")

        self.currentToken = self.getNextToken()
        self.currentParseTreeNode = self.currentParseTreeNode.parent


    def parseFileBody(self):

        if self.currentToken is None:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Current token is None.\n{self.getCurrentLine()}")
        

        newNode = ParseTreeNode(NodeType.FILE_BODY, self.currentParseTreeNode, self.currentToken.lineNumber)
        self.currentParseTreeNode.addChild(newNode)
        self.currentParseTreeNode = newNode

        # continue attempting to parse until hit EOF
        while self.currentToken.type != TokenType.END_OF_FILE:

            # parse root node definition
            if self.currentToken.type == TokenType.FORWARD_SLASH:
                self.parseRootNodeDefinition()

            # parse phandle override
            elif self.currentToken.type == TokenType.AMPERSAND:
                self.parsePhandleOverride()

            else:
                raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}.Expected \"/\" or \"&\".\n{self.getCurrentLine()}")

        # move up one level in the parse tree and return
        self.currentParseTreeNode = self.currentParseTreeNode.parent


    '''
    This is the top-level method for parsing a device tree
    file. Every other method for parsing part of the file
    is ultimately invoked from here or some function invoked
    from here.
    '''
    def parseDeviceTree(self):

        self.currentToken = self.getNextToken()

        if self.currentToken is None:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Current token is None.\n{self.getCurrentLine()}")

        self.parseTree = ParseTree()
        self.currentParseTreeNode = self.parseTree.rootNode

        # only parse file body if it exists
        if self.currentToken.type != TokenType.END_OF_FILE:
            self.parseFileBody()

        # last token must be EOF
        if self.currentToken.type == TokenType.END_OF_FILE:
            newNode: ParseTreeNode = ParseTreeNode(NodeType.TERMINAL, self.currentParseTreeNode, self.currentToken)
            self.currentParseTreeNode.addChild(newNode)
        else:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Expected EOF.\n{self.getCurrentLine()}")


    def getParseTree(self):
        return self.parseTree




#######################################
# Helper functions to get specific    #
# nodes or values from the parse tree #
#######################################


'''
Gets the string representing the property. If the
property starts with '#', as with '#address-cells',
then it adds the '#' character to the name (since the
'#' character is a separate terminal from the name).
This function can only be passed objects of type
ParseTreeNode with 'type' member equal to NODE_PROPERTY.

@param node: ParseTreeNode representing the root of the
             production for the device tree node property
@return String representing the name of the property.
'''
def getDTPropertyName(node: ParseTreeNode):
    
    if node.type != NodeType.NODE_PROPERTY:
        raise Exception(f"getDTPropertyName called on parse tree node of type {node.type.name} at line {node.lineNumber}")

    propertyName = ""
    for child in node.children:
        if (child.type == NodeType.TERMINAL) and (child.terminalType == TerminalType.PROPERTY_NAME):
            propertyName += child.value

    if (node.children[0].type == NodeType.TERMINAL) and (node.children[0].terminalType == TerminalType.HASHTAG) and (propertyName is not None):
        propertyName = "#" + propertyName

    return propertyName



'''
Gets the ParseTreeNode representing the property value.
This is not the actual value itself, since that could be
any number of things including a number, string, list of
strings, list of numbers, None, etc. Thus, further processing
is needed to validate the ParseTreeNode that is returned.

@param node: ParseTreeNode representing the property itself
             (including the name, #, and property).
@return ParseTreeNode for the property or None if non-existent.
'''
def getDTPropertyValueNode(node: ParseTreeNode):

    if node.type != NodeType.NODE_PROPERTY:
        raise Exception(f"getDTPropertyValueNode called on parse tree node of type {node.type.name} at line {node.lineNumber}")

    i = 0
    for i in range(len(node.children)):
        if (node.children[i].type == NodeType.TERMINAL) and (node.children[i].terminalType == TerminalType.PROPERTY_NAME):
            if (i+2 < len(node.children)) and (node.children[i+1].type == NodeType.TERMINAL) \
                and (node.children[i+1].terminalType == TerminalType.EQUALS) and (node.children[i+2].type == NodeType.NODE_PROPERTY_VALUE):
                return node.children[i+2]

    return None




'''
Gets the actual value (not the parse tree node) from
a given DT node property given that it has type
<boolean>. This should be used with caution and
one should check that the property has type string before
invoking this function.

THIS FUNCTION ALWAYS RETURNS TRUE SINCE THE MERE PRESENCE
OF A BOOLEAN PROPERTY INDICATES A 'TRUE' VALUE. THIS FUNCTION
IS MOSTLY HERE FOR UNIFORMITY OF THE INTERFACE TO GET NODE
PROPERTY VALUES.

@param node: ParseTreeNode of type NODE_PROPERTY.
@return True
'''
def getDTPropertyValueBoolean(node: ParseTreeNode) -> str:

    if node.type != NodeType.NODE_PROPERTY:
        raise Exception(f"getDTPropertyValueStringArray called on parse tree node of type {node.type.name} at line {node.lineNumber}")

    # the mere presence of the property indicates a 'True' value
    return "true"


'''
Gets the actual value (not the parse tree node) from
a given DT node property given that it has type
<string>. This should be used with caution and
one should check that the property has type string before
invoking this function.

@param node: ParseTreeNode of type NODE_PROPERTY.
@return String representing value
'''
def getDTPropertyValueString(node: ParseTreeNode) -> str:

    if node.type != NodeType.NODE_PROPERTY:
        raise Exception(f"getDTPropertyValueStringArray called on parse tree node of type {node.type.name} at line {node.lineNumber}")

    prop = getDTPropertyValueNode(node)

    if prop is None:
        raise Exception(f"getDTPropertyValueStringArray called on DT property {getDTPropertyName(node)} at line {node.lineNumber} that has empty value")

    for child in prop.children:
        if (child.type == NodeType.TERMINAL) and (child.terminalType == TerminalType.STRING):
            return child.value
    
    return None


'''
Gets the actual value (not the parse tree node) from
a given DT node property given that it has type
<string-array>. This should be used with caution and
one should check that the property has type string-array before
invoking this function.

@param node: ParseTreeNode of type NODE_PROPERTY.
@return List of strings representing the property value
'''
def getDTPropertyValueStringArray(node: ParseTreeNode) -> List[str]:

    if node.type != NodeType.NODE_PROPERTY:
        raise Exception(f"getDTPropertyValueStringArray called on parse tree node of type {node.type.name} at line {node.lineNumber}")

    strings = []
    prop = getDTPropertyValueNode(node)

    if prop is None:
        raise Exception(f"getDTPropertyValueStringArray called on DT property {getDTPropertyName(node)} at line {node.lineNumber} that has empty value")

    for child in prop.children:
        if (child.type == NodeType.TERMINAL) and (child.terminalType == TerminalType.STRING):
            strings.append(child.value)
    
    return strings


'''
Gets the actual value (not the parse tree node) from
a given DT node property given that it has type
<array>. This should be used with caution and
one should check that the property has type array before
invoking this function.

@param node: ParseTreeNode of type NODE_PROPERTY.
@return List of integers representing the property value
'''
def getDTPropertyValuePhandleArray(node: ParseTreeNode):

    if node.type != NodeType.NODE_PROPERTY:
        raise Exception(f"getDTPropertyPVArray called on parse tree node of type {node.type.name} at line {node.lineNumber}")

    pvArray = []
    prop = getDTPropertyValueNode(node)
    if prop is None:
        raise Exception(f"getDTPropertyPVArray called on DT property {getDTPropertyName(node)} at line {node.lineNumber} that has empty value")

    for child in prop.children:
        if child.type == NodeType.PROPERTY_VALUE_ARRAY:
            for grandchild in child.children:
                if (grandchild.type == NodeType.TERMINAL) and ((grandchild.terminalType == TerminalType.DECIMAL_NUMBER) or (grandchild.terminalType == TerminalType.HEXADECIMAL_NUMBER)):
                    pvArray.append(grandchild.value)
                elif grandchild.type == NodeType.PHANDLE_REFERENCE:
                    pvArray.append(grandchild.children[1].value)
                else:
                    raise Exception(f"getDTPropertyPhandleArray")

    return pvArray



'''
Gets the actual value (not the parse tree node) from
a given DT node property given that it has type
<array>. This should be used with caution and
one should check that the property has type array before
invoking this function.

@param node: ParseTreeNode of type NODE_PROPERTY.
@return List of integers representing the property value
'''
def getDTPropertyValueIntArray(node: ParseTreeNode):

    if node.type != NodeType.NODE_PROPERTY:
        raise Exception(f"getDTPropertyIntArray called on parse tree node of type {node.type.name} at line {node.lineNumber}")

    intArray = []
    prop = getDTPropertyValueNode(node)
    if prop is None:
        raise Exception(f"getDTPropertyIntArray called on DT property {getDTPropertyName(node)} at line {node.lineNumber} that has empty value")

    for child in prop.children:
        if child.type == NodeType.PROPERTY_VALUE_ARRAY:
            for grandchild in child.children:
                if (grandchild.type == NodeType.TERMINAL) and ((grandchild.terminalType == TerminalType.DECIMAL_NUMBER) or (grandchild.terminalType == TerminalType.HEXADECIMAL_NUMBER)):
                    intArray.append(grandchild.value)
                elif (grandchild.type == NodeType.TERMINAL) and ((grandchild.terminalType == TerminalType.LEFT_ANGLE_BRACKET) or (grandchild.terminalType == TerminalType.RIGHT_ANGLE_BRACKET)):
                    pass
                else:
                    raise Exception(f"getDTPropertyIntArray called on property node whose type is not array")

    return intArray




'''
Gets the actual value (not the parse tree node) from
a given DT node property given that it has type
<int>. This should be used with caution and
one should check that the property has type int before
invoking this function.

@param node: ParseTreeNode of type NODE_PROPERTY.
@return List of integers representing the property value
'''
def getDTPropertyValueInt(node: ParseTreeNode):

    if node.type != NodeType.NODE_PROPERTY:
        raise Exception(f"getDTPropertyIntArray called on parse tree node of type {node.type.name} at line {node.lineNumber}")

    prop = getDTPropertyValueNode(node)
    if prop is None:
        raise Exception(f"getDTPropertyIntArray called on DT property {getDTPropertyName(node)} at line {node.lineNumber} that has empty value")

    for child in prop.children:
        if child.type == NodeType.PROPERTY_VALUE_ARRAY:
            for grandchild in child.children:
                if (grandchild.type == NodeType.TERMINAL) and ((grandchild.terminalType == TerminalType.DECIMAL_NUMBER) or (grandchild.terminalType == TerminalType.HEXADECIMAL_NUMBER)):
                    return grandchild.value
                elif (grandchild.type == NodeType.TERMINAL) and ((grandchild.terminalType == TerminalType.LEFT_ANGLE_BRACKET) or (grandchild.terminalType == TerminalType.RIGHT_ANGLE_BRACKET)):
                    pass
                else:
                    raise Exception(f"getDTPropertyIntArray called on property {getDTPropertyName(node)} node whose type is not int")

    return None



'''
Gets the actual value (not the parse tree node) from
a given DT node property given that it has type
<phandle>. This should be used with caution and
one should check that the property has type phandle before
invoking this function.

@param node: ParseTreeNode of type NODE_PROPERTY.
@return Phandle (label of another node) representing the property value
'''
def getDTPropertyValuePhandle(node: ParseTreeNode):
    if node.type != NodeType.NODE_PROPERTY:
        raise Exception(f"getDTPropertyValuePhandle called on parse tree node of type {node.type.name} at line {node.lineNumber}")

    prop = getDTPropertyValueNode(node)
    if prop is None:
        raise Exception(f"getDTPropertyValuePhandle called on DT property {getDTPropertyName(node)} at line {node.lineNumber} that has empty value")

    for child in prop.children:
        if child.type == NodeType.PROPERTY_VALUE_ARRAY:
            for grandchild in child.children:
                if grandchild.type == NodeType.PHANDLE_REFERENCE:
                    return grandchild.children[1].value
                elif (grandchild.type == NodeType.TERMINAL) and ((grandchild.terminalType == TerminalType.LEFT_ANGLE_BRACKET) or (grandchild.terminalType == TerminalType.RIGHT_ANGLE_BRACKET)):
                    pass
                else:
                    raise Exception(f"getDTPropertyValuePhandle called on property node whose type is not array")

    return None




'''
Gets the actual value (not the parse tree node) from
a given DT node property given that it has type
<phandles> (multiple). This should be used with caution and
one should check that the property has type phandles before
invoking this function.

@param node: ParseTreeNode of type NODE_PROPERTY.
@return Phandle list (label of another node) representing the property value
'''
def getDTPropertyValueMultiPhandle(node: ParseTreeNode):
    if node.type != NodeType.NODE_PROPERTY:
        raise Exception(f"getDTPropertyValuePhandle called on parse tree node of type {node.type.name} at line {node.lineNumber}")

    prop = getDTPropertyValueNode(node)
    if prop is None:
        raise Exception(f"getDTPropertyValuePhandle called on DT property {getDTPropertyName(node)} at line {node.lineNumber} that has empty value")

    phandles = []
    for child in prop.children:
        if child.type == NodeType.PROPERTY_VALUE_ARRAY:
            for grandchild in child.children:
                if grandchild.type == NodeType.PHANDLE_REFERENCE:
                    phandles.append(grandchild.children[1].value)
                elif (grandchild.type == NodeType.TERMINAL) and ((grandchild.terminalType == TerminalType.LEFT_ANGLE_BRACKET) or (grandchild.terminalType == TerminalType.RIGHT_ANGLE_BRACKET)):
                    pass
                else:
                    raise Exception(f"getDTPropertyValuePhandle called on property node whose type is not array")

    return None



'''
Gets the ParseTreeNode representing the node declaration ([label:] node-name[@unit-address])
for a given node definition. This function can only be passed a ParseTreeNode with
node type of NODE_DEFINITION. It will raise an exception otherwise.

@param node: ParseTreeNode representing the node definition
@return ParseTreeNode representing the node declaration
'''
def getDTNodeDeclaration(node: ParseTreeNode):

    if node.type != NodeType.NODE_DEFINITION:
        raise Exception(f"getDTNodeDeclaration called on parse tree node with type {node.type.name} at line {node.lineNumber}")

    for child in node.children:
        if child.type == NodeType.NODE_DECLARATION:
            return child

    raise Exception(f"getDTNodeDeclaration called on parse tree node which somehow does not have a name, label, or unit address. This should have been caught by the parser. Reconsider your entire life.")



'''
Gets the node name for a given node definition. This is returned as a string.
Can only be passed a ParseTreeNode of type NODE_DEFINITION.

@param node: ParseTreeNode representing the node definition.
@return string representing the name of the node with the unit address appended.
'''
def getDTNodeName(node: ParseTreeNode):

    if (node.type != NodeType.NODE_DEFINITION) and (node.type != NodeType.ROOT_NODE_DEFINITION) and (node.type != NodeType.PHANDLE_OVERRIDE):
        raise Exception(f"getDTNodeName called on parse tree node with type {node.type.name} at line {node.lineNumber}")

    if node.type == NodeType.ROOT_NODE_DEFINITION:
        return "/"

    if node.type == NodeType.PHANDLE_OVERRIDE:
        if node.children[0].type == NodeType.PHANDLE_REFERENCE:
            return node.children[0].children[0].value + node.children[0].children[1].value
        else:
            raise Exception(f"Node of type PHANDLE_OVERRIDE does not appear to have proper format")

    nodeDeclaration = getDTNodeDeclaration(node)

    for child in nodeDeclaration.children:
        if (child.type == NodeType.TERMINAL) and (child.terminalType == TerminalType.NODE_NAME):
            return str(child.value)

    return None



'''
Gets the label from a given node. Can only be passed a ParseTreeNode
with type of NODE_DEFINITION.

@param node: ParseTreeNode representing the node definition
@return string representing the node label or None if non-existent
'''
def getDTNodeLabel(node: ParseTreeNode):

    if node.type != NodeType.NODE_DEFINITION:
        raise Exception(f"getDTNodeLabel called with node of type {node.type.name} at line {node.lineNumber}")

    nodeDeclaration = getDTNodeDeclaration(node)

    for child in nodeDeclaration.children:
        if child.type == NodeType.NODE_LABEL:
            for terminal in child.children:
                if (terminal.type == NodeType.TERMINAL) and (terminal.terminalType == TerminalType.NODE_LABEL):
                    return terminal.value

    return None


'''
Gets just the unit address from the node definition.

@param node: ParseTreeNode representing the node definition
@return string representing the unit address or None if non-existent
'''
def getDTNodeUnitAddress(node: ParseTreeNode):

    if node.type != NodeType.NODE_DEFINITION:
        raise Exception(f"getDTNodeUnitAddress called with node of type {node.type.name} at line {node.lineNumber}")

    nodeDeclaration = getDTNodeDeclaration(node)

    for child in nodeDeclaration.children:
        if child.type == NodeType.NODE_ADDRESS:
            for grandchild in child.children:
                if (grandchild.type == NodeType.TERMINAL) and \
                    ((grandchild.terminalType == TerminalType.HEXADECIMAL_NUMBER) or (grandchild.terminalType == TerminalType.DECIMAL_NUMBER)):
                    return grandchild.value

    return None



'''
Gets the ParseTreeNode representing the body of the node (enclosed by the
opening and closing curly brace). Can only be passed a node with type of
NODE_DEFINITION.

@param node: ParseTreeNode representing the node definition
@return ParseTreeNode for the device tree node body or None if empty
'''
def getDTNodeBody(node: ParseTreeNode):
    
    if (node.type != NodeType.NODE_DEFINITION) and (node.type != NodeType.ROOT_NODE_DEFINITION) and (node.type != NodeType.PHANDLE_OVERRIDE):
        raise Exception(f"getDTNodeBody called on device tree node with type {node.type.name} at line {node.lineNumber}")

    for child in node.children:
        if child.type == NodeType.NODE_BODY:
            return child

    return None


'''
Gets a list of all properties in a given node definition, filtered by the filtering
function passed in. The filtering function returns true for all property nodes
that must be included in the output list of properties. The default is just to
return true for all nodes. This function must be passed a ParseTreeNode with
type NODE_DEFINITION and optionally a function that takes a ParseTreeNode with
type NODE_PROPERTY and returns True if that node should be included in the output
list and False if it should not be included.

@param node: ParseTreeNode that represents the node definition
@param filterFunc: (Optional) Function that takes in a ParseTreeNode with type
                   NODE_PROPERTY and returns True if the property node should be
                   included in the output list, and False otherwise
@return List[ParseTreeNode] of all properties found satisfying filterFunc
'''
def getDTNodeProperties(node: ParseTreeNode, filterFunc = lambda x: True) -> list[ParseTreeNode]:

    if (node.type != NodeType.NODE_DEFINITION) and (node.type != NodeType.ROOT_NODE_DEFINITION) and (node.type != NodeType.PHANDLE_OVERRIDE):
        raise Exception(f"getDTNodeProperties called on device tree node with type {node.type.name} at line {node.lineNumber}")

    nodeBody = getDTNodeBody(node)
    if nodeBody is None:
        return []

    properties = []
    for child in nodeBody.children:
        if (child.type == NodeType.NODE_PROPERTY) and (filterFunc(child)):
            properties.append(child)

    return properties


'''
Gets a list of the sub-nodes contained within this device tree node definition.
Must be passed a ParseTreeNode with type NODE_DEFINITION. The filtering function
returns True for all nodes that should be included in the output list, defaulting
to returning true for all nodes.

@param node: ParseTreeNode representing the device tree node definition.
@param filterFunc: Function taking in ParseTreeNode with type NODE_DEFINITION as
                   a parameter, and returning True if the node should be included
                   and False otherwise.
@return List[ParseTreeNode] of all sub-nodes found satisfying filterFunc
'''
def getDTNodeSubNodes(node: ParseTreeNode, filterFunc = lambda x: True) -> list[ParseTreeNode]:

    if (node.type != NodeType.NODE_DEFINITION) and (node.type != NodeType.ROOT_NODE_DEFINITION) and (node.type != NodeType.PHANDLE_OVERRIDE):
        raise Exception(f"getDTNodeSubNodes called on device tree node with type {node.type.name} at line {node.lineNumber}")

    nodeBody = getDTNodeBody(node)
    if nodeBody is None:
        return []

    subnodes = []
    for child in nodeBody.children:
        if (child.type == NodeType.NODE_DEFINITION) and (filterFunc(child)):
            subnodes.append(child)

    return subnodes



'''
Gets a property node with a given name. This function must
be passed a ParseTreeNode with type NODE_DEFINITION

@param node: ParseTreeNode representing the node definition
@param name: String representing the name of the property to find
@return Property node with the given name
'''
def getDTNodePropertyByName(node: ParseTreeNode, name: str):
    
    def filterProperties(propNode: ParseTreeNode):
        propName = ""
        if (propNode.children[0].type == NodeType.TERMINAL) and (propNode.children[0].terminalType == TerminalType.HASHTAG):
            propName += "#"
        for child in propNode.children:
            if (child.type == NodeType.TERMINAL) and (child.terminalType == TerminalType.PROPERTY_NAME):
                propName += child.value
        
        return name == propName

    # assume that only first property is valid. Should run a check
    # for duplicate properties first as part of validation
    props = getDTNodeProperties(node, filterProperties)

    if len(props) > 0:
        return props[0]

    return None


def getDTNodeSubNodesByName(node: ParseTreeNode, name: str):
    raise Exception(f"getDTNodeSubNodesByName in {__file__} not implemented")
        





'''
TODO
'''
def getDTFileBody(node: ParseTreeNode):

    if node.type != NodeType.DEVICE_TREE:
        raise Exception(f"Function getDTFileBody passed node of type {node.type.name} at line {node.lineNumber}. Expected node of type DEVICE_TREE.")

    for child in node.children:
        if child.type == NodeType.FILE_BODY:
            return child

    return None


'''
TODO
'''
def getDTRootNodeDefinitions(node: ParseTreeNode):

    if node.type != NodeType.FILE_BODY:
        raise Exception(f"Function getDTRootNodeDefinitions passed node of type {node.type.name} at line {node.lineNumber}. Expected node of type FILE_BODY")

    rootNodeDefinitions = []
    for child in node.children:
        if child.type == NodeType.ROOT_NODE_DEFINITION:
            rootNodeDefinitions.append(child)

    return rootNodeDefinitions


'''
TODO
'''
def getDTPhandleOverrides(node: ParseTreeNode):

    if node.type != NodeType.FILE_BODY:
        raise Exception(f"Function getDTPhandleOverrides passed node of type {node.type.name} at line {node.lineNumber}. Expected node of type FILE_BODY")

    phandleOverrides = []
    for child in node.children:
        if child.type == NodeType.PHANDLE_OVERRIDE:
            phandleOverrides.append(child)

    return phandleOverrides


'''
TODO
'''
def getDTRootNodeBody(node: ParseTreeNode):

    if node.type != NodeType.ROOT_NODE_DEFINITION:
        raise Exception(f"Function getDTRootNodeBody passed node of type {node.type.name} at line {node.lineNumber}. Expected node of type ROOT_NODE_DEFINITION.")

    for child in node.children:
        if child.type == NodeType.NODE_BODY:
            return child

    return None


'''
TODO
'''
def getDTPhandleOverrideBody(node: ParseTreeNode):

    if node.type != NodeType.PHANDLE_OVERRIDE:
        raise Exception(f"Function getDTPhandleOverrideBody passed node of type {node.type.name} at line {node.lineNumber}. Expected node of type PHANDLE_OVERRIDE.")

    for child in node.children:
        if child.type == NodeType.NODE_BODY:
            return child

    return None



def getDTPhandleOverrideLabel(node: ParseTreeNode):

    if node.type != NodeType.PHANDLE_OVERRIDE:
        raise Exception(f"Function getDTPhandleOverrideLabel passed node of type {node.type.name} at line {node.lineNumber}. Expected node of type PHANDLE_OVERRIDE.")

    if node.children[0].type != NodeType.PHANDLE_REFERENCE:
        raise Exception(f"Phandle override node does not appear to have phandle reference")
    
    return node.children[0].children[1].value


'''
TODO
'''
def getDTPropertyContainingNode(node: ParseTreeNode):
    
    if node.type != NodeType.NODE_PROPERTY:
        raise Exception(f"getDTPropertyContainingNode called on parse tree node of type {node.type.name} at line {node.lineNumber}")

    return node.parent.parent


'''
TODO
'''
def getDTNodeParentNode(node: ParseTreeNode):

    if node.type != NodeType.NODE_DEFINITION:
        raise Exception(f"getDTNodeParentNode called on parse tree node of type {node.type.name} at line {node.lineNumber}")

    return node.parent.parent




