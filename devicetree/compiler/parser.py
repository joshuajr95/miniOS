

from tokenizer import Tokenizer, Token, TokenType
from enum import Enum
from typing import List



class ParseError(Exception):
    
    def __init__(self, message: str):
        self.message = message



class NodeType(Enum):
    PARSE_TREE_NODE_TYPE_TERMINAL = 0                   # terminal node (i.e. a single token)
    PARSE_TREE_NODE_TYPE_DEVICE_TREE = 1                # entire device tree file
    PARSE_TREE_NODE_TYPE_FILE_BODY = 2                  # body of the file (file minus the EOF)
    PARSE_TREE_NODE_TYPE_PHANDLE_OVERRIDE = 3           # phandle override node (&name = {};)
    PARSE_TREE_NODE_TYPE_ROOT_NODE_DEFINITION = 4       # root node definition
    PARSE_TREE_NODE_TYPE_NODE_BODY = 5                  # body of the node
    PARSE_TREE_NODE_TYPE_NODE_DEFINITION = 6            # node definition (contains a node body)
    PARSE_TREE_NODE_TYPE_NODE_DECLARATION = 7           # node declaration (name, @address, label)
    PARSE_TREE_NODE_TYPE_NODE_PROPERTY = 8              # property
    PARSE_TREE_NODE_TYPE_NODE_PROPERTY_VALUE = 9        # the value of the property
    PARSE_TREE_NODE_TYPE_PROPERTY_VALUE_ARRAY = 10      # array of values, i.e. phandle array
    PARSE_TREE_NODE_TYPE_NODE_LABEL = 11                # label for node (i.e. uart1: )
    PARSE_TREE_NODE_TYPE_NODE_ADDRESS = 12              # address for node (i.e. @bfc01000)



class ParseTreeNode:

    nodeNames = {
        NodeType.PARSE_TREE_NODE_TYPE_TERMINAL: "TERMINAL",
        NodeType.PARSE_TREE_NODE_TYPE_DEVICE_TREE: "DEVICE_TREE_FILE",
        NodeType.PARSE_TREE_NODE_TYPE_FILE_BODY: "FILE_BODY",
        NodeType.PARSE_TREE_NODE_TYPE_PHANDLE_OVERRIDE: "PHANDLE_OVERRIDE",
        NodeType.PARSE_TREE_NODE_TYPE_ROOT_NODE_DEFINITION: "ROOT_NODE_DEFINITION",
        NodeType.PARSE_TREE_NODE_TYPE_NODE_BODY: "NODE_BODY",
        NodeType.PARSE_TREE_NODE_TYPE_NODE_DEFINITION: "NODE_DEFINITION",
        NodeType.PARSE_TREE_NODE_TYPE_NODE_DECLARATION: "NODE_DECLARATION",
        NodeType.PARSE_TREE_NODE_TYPE_NODE_PROPERTY: "NODE_PROPERTY",
        NodeType.PARSE_TREE_NODE_TYPE_NODE_PROPERTY_VALUE: "NODE_PROPERTY_VALUE",
        NodeType.PARSE_TREE_NODE_TYPE_PROPERTY_VALUE_ARRAY: "PROPERTY_VALUE_ARRAY",
        NodeType.PARSE_TREE_NODE_TYPE_NODE_LABEL: "NODE_LABEL",
        NodeType.PARSE_TREE_NODE_TYPE_NODE_ADDRESS: "NODE_ADDRESS"
    }


    def __init__(self, type: NodeType, parent, terminal: Token = None):
        self.type = type
        self.parent = parent

        if self.type == NodeType.PARSE_TREE_NODE_TYPE_TERMINAL and terminal is None:
            raise Exception("Terminal node in parse tree must contain reference to token.")
        elif self.type != NodeType.PARSE_TREE_NODE_TYPE_TERMINAL and terminal is not None:
            raise Exception("Non-terminal parse tree node must not contain reference to token.")
        else:
            self.terminal = terminal

        self.children: List[ParseTreeNode] = []


    def isRoot(self) -> bool:
        return self.parent is None


    def __str__(self) -> str:
        out = "Node Type: " + str(self.type)

        if self.type == NodeType.PARSE_TREE_NODE_TYPE_TERMINAL:
            out += "Terminal: " + str(self.terminal)

        return out


    def getNodeName(self):
        if self.type == NodeType.PARSE_TREE_NODE_TYPE_TERMINAL:
            out = Token.tokenNames[self.terminal.type] + ": "
            if self.terminal.value is None:
                out += "NONE"
            else:
                out += self.terminal.value
            
            return out

        else:
            return ParseTreeNode.nodeNames[self.type]



    def isTerminal(self) -> bool:
        return self.type == NodeType.PARSE_TREE_NODE_TYPE_TERMINAL


    def addChild(self, childNode):
        self.children.append(childNode)


    def output(self, indentLevel, higherLevelString):
        out = ""
        for i in range(indentLevel):
            out += "\t"

        out += self.getNodeName()
        print(out)

        for node in self.children:
            node.output(indentLevel+1, None)



    def print(self):
        if self.type == NodeType.PARSE_TREE_NODE_TYPE_TERMINAL:
            out = "Terminal:  <" + str(self.terminal) + ">  Parent: " + ParseTreeNode.nodeNames[self.parent.type]
            print(out)
        else:
            out = "Type: " + ParseTreeNode.nodeNames[self.type]
            print(out)

        for node in self.children:
            node.print()


    def traverse(self, rootString: str):

        for node in self.children:
            if node.type == NodeType.PARSE_TREE_NODE_TYPE_TERMINAL:
                rootString += node.terminal.value
            else:
                rootString += node.traverse(rootString)
        
        return rootString



class ParseTree:

    def __init__(self):
        self.rootNode = ParseTreeNode(NodeType.PARSE_TREE_NODE_TYPE_DEVICE_TREE, None, None)
    
    def print(self):
        self.rootNode.print()
    

    def output(self):
        self.rootNode.output(0, None)


    def traverse(self) -> str:
        return self.rootNode.traverse("")




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
        self.currentParseTreeNode = None                    # for keeping track of which node we are on during parse tree construction


    def getLineNumber(self) -> int:
        return self.tokenizer.getCurrentLineNumber()


    def getCurrentLine(self) -> str:
        return self.tokenizer.getCurrentLine()


    '''
    Returns the next token to the user. Typically, this will be stored in currentToken.
    Mutates the lookAheadInitialized, and lookAheadBuffer member variables.
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

        # return first entry in the lookahead buffer
        return self.lookAheadBuffer[0]


    '''
    Does not mutate the lookAheadBuffer.
    '''
    def peekAhead(self, lookAheadIndex=1):
        return self.lookAheadBuffer[lookAheadIndex]



    def parsePropertyValueArray(self):

        if self.currentToken is None:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Current token is None.")
        
        currentNode: ParseTreeNode = ParseTreeNode(NodeType.PARSE_TREE_NODE_TYPE_PROPERTY_VALUE_ARRAY, self.currentParseTreeNode, None)
        self.currentParseTreeNode.addChild(currentNode)
        self.currentParseTreeNode = currentNode

        if self.currentToken.type == TokenType.TOKEN_TYPE_LEFT_ANGLE_BRACKET:
            newNode: ParseTreeNode = ParseTreeNode(NodeType.PARSE_TREE_NODE_TYPE_TERMINAL, self.currentParseTreeNode, self.currentToken)
            self.currentParseTreeNode.addChild(newNode)
        else:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Expected \"<\".\n{self.getCurrentLine()}")

        self.currentToken = self.getNextToken()

        while self.currentToken.type != TokenType.TOKEN_TYPE_RIGHT_ANGLE_BRACKET:

            if self.currentToken.type == TokenType.TOKEN_TYPE_HEXADECIMAL_NUMBER:
                newNode: ParseTreeNode = ParseTreeNode(NodeType.PARSE_TREE_NODE_TYPE_TERMINAL, self.currentParseTreeNode, self.currentToken)
                self.currentParseTreeNode.addChild(newNode)

            elif self.currentToken.type == TokenType.TOKEN_TYPE_DECIMAL_NUMBER:
                newNode: ParseTreeNode = ParseTreeNode(NodeType.PARSE_TREE_NODE_TYPE_TERMINAL, self.currentParseTreeNode, self.currentToken)
                self.currentParseTreeNode.addChild(newNode)

            elif self.currentToken.type == TokenType.TOKEN_TYPE_PHANDLE_REFERENCE:
                newNode: ParseTreeNode = ParseTreeNode(NodeType.PARSE_TREE_NODE_TYPE_TERMINAL, self.currentParseTreeNode, self.currentToken)
                self.currentParseTreeNode.addChild(newNode)

            else:
                raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Expected one of: number, hexadecimal number, \"&\".\n{self.getCurrentLine()}")

            self.currentToken = self.getNextToken()

        newNode: ParseTreeNode = ParseTreeNode(NodeType.PARSE_TREE_NODE_TYPE_TERMINAL, self.currentParseTreeNode, self.currentToken)
        self.currentParseTreeNode.addChild(newNode)

        self.currentToken = self.getNextToken()
        self.currentParseTreeNode = self.currentParseTreeNode.parent


    def parseNodePropertyValue(self):

        if self.currentToken is None:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Current token is None.")


        currentNode: ParseTreeNode = ParseTreeNode(NodeType.PARSE_TREE_NODE_TYPE_NODE_PROPERTY_VALUE, self.currentParseTreeNode, None)
        self.currentParseTreeNode.addChild(currentNode)
        self.currentParseTreeNode = currentNode


        while self.currentToken.type != TokenType.TOKEN_TYPE_SEMICOLON:

            if self.currentToken.type == TokenType.TOKEN_TYPE_STRING:
                newNode: ParseTreeNode = ParseTreeNode(NodeType.PARSE_TREE_NODE_TYPE_TERMINAL, self.currentParseTreeNode, self.currentToken)
                self.currentParseTreeNode.addChild(newNode)
                self.currentToken = self.getNextToken()

            elif self.currentToken.type == TokenType.TOKEN_TYPE_PHANDLE_REFERENCE:
                newNode: ParseTreeNode = ParseTreeNode(NodeType.PARSE_TREE_NODE_TYPE_TERMINAL, self.currentParseTreeNode, self.currentToken)
                self.currentParseTreeNode.addChild(newNode)
                self.currentToken = self.getNextToken()

            elif self.currentToken.type == TokenType.TOKEN_TYPE_LEFT_ANGLE_BRACKET:
                self.parsePropertyValueArray()

            else:
                raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Expected one of: string, \"&\", \"<\".\n{self.getCurrentLine()}")

        self.currentParseTreeNode = self.currentParseTreeNode.parent


    def parseNodeProperty(self):

        if self.currentToken is None:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Current token is None.")

        currentNode: ParseTreeNode = ParseTreeNode(NodeType.PARSE_TREE_NODE_TYPE_NODE_PROPERTY, self.currentParseTreeNode, None)
        self.currentParseTreeNode.addChild(currentNode)
        self.currentParseTreeNode = currentNode

        if self.currentToken.type == TokenType.TOKEN_TYPE_HASHTAG:
            newNode: ParseTreeNode = ParseTreeNode(NodeType.PARSE_TREE_NODE_TYPE_TERMINAL, self.currentParseTreeNode, self.currentToken)
            self.currentParseTreeNode.addChild(newNode)
            self.currentToken = self.getNextToken()


        if self.currentToken.type == TokenType.TOKEN_TYPE_NAME:
            newNode: ParseTreeNode = ParseTreeNode(NodeType.PARSE_TREE_NODE_TYPE_TERMINAL, self.currentParseTreeNode, self.currentToken)
            self.currentParseTreeNode.addChild(newNode)
        else:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Expected node property name.\n{self.getCurrentLine()}")

        self.currentToken = self.getNextToken()

        if self.currentToken.type == TokenType.TOKEN_TYPE_EQUALS:
            newNode: ParseTreeNode = ParseTreeNode(NodeType.PARSE_TREE_NODE_TYPE_TERMINAL, self.currentParseTreeNode, self.currentToken)
            self.currentParseTreeNode.addChild(newNode)
            self.currentToken = self.getNextToken()
            self.parseNodePropertyValue()


        if self.currentToken.type == TokenType.TOKEN_TYPE_SEMICOLON:
            newNode: ParseTreeNode = ParseTreeNode(NodeType.PARSE_TREE_NODE_TYPE_TERMINAL, self.currentParseTreeNode, self.currentToken)
            self.currentParseTreeNode.addChild(newNode)
        else:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Expected \";\".\n{self.getCurrentLine()}")

        self.currentToken = self.getNextToken()
        self.currentParseTreeNode = self.currentParseTreeNode.parent


    def parseNodeLabel(self):

        if self.currentToken is None:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Current token is None.")

        currentNode: ParseTreeNode = ParseTreeNode(NodeType.PARSE_TREE_NODE_TYPE_NODE_LABEL, self.currentParseTreeNode, None)
        self.currentParseTreeNode.addChild(currentNode)
        self.currentParseTreeNode = currentNode

        if self.currentToken.type == TokenType.TOKEN_TYPE_NAME:
            newNode: ParseTreeNode = ParseTreeNode(NodeType.PARSE_TREE_NODE_TYPE_TERMINAL, self.currentParseTreeNode, self.currentToken)
            self.currentParseTreeNode.addChild(newNode)
        else:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Expected node label.\n{self.getCurrentLine()}")

        self.currentToken = self.getNextToken()


        if self.currentToken.type == TokenType.TOKEN_TYPE_COLON:
            newNode: ParseTreeNode = ParseTreeNode(NodeType.PARSE_TREE_NODE_TYPE_TERMINAL, self.currentParseTreeNode, self.currentToken)
            self.currentParseTreeNode.addChild(newNode)
        else:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Expected \":\".\n{self.getCurrentLine()}")

        self.currentToken = self.getNextToken()
        self.currentParseTreeNode = self.currentParseTreeNode.parent



    def parseNodeAddress(self):

        if self.currentToken is None:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Current token is None.")

        currentNode: ParseTreeNode = ParseTreeNode(NodeType.PARSE_TREE_NODE_TYPE_NODE_ADDRESS, self.currentParseTreeNode, None)
        self.currentParseTreeNode.addChild(currentNode)
        self.currentParseTreeNode = currentNode


        if self.currentToken.type == TokenType.TOKEN_TYPE_AT_SYMBOL:
            newNode: ParseTreeNode = ParseTreeNode(NodeType.PARSE_TREE_NODE_TYPE_TERMINAL, self.currentParseTreeNode, self.currentToken)
            self.currentParseTreeNode.addChild(newNode)
        else:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Expected \"@\".\n{self.getCurrentLine()}")


        self.currentToken = self.getNextToken()


        if self.currentToken.type == TokenType.TOKEN_TYPE_DECIMAL_NUMBER:       # maybe also HEX number??
            newNode: ParseTreeNode = ParseTreeNode(NodeType.PARSE_TREE_NODE_TYPE_TERMINAL, self.currentParseTreeNode, self.currentToken)
            self.currentParseTreeNode.addChild(newNode)
        else:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Expected number. Token: {str(self.currentToken)}.\n{self.getCurrentLine()}")


        self.currentToken = self.getNextToken()
        self.currentParseTreeNode = self.currentParseTreeNode.parent        


    def parseNodeDeclaration(self):

        if self.currentToken is None:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Current token is None.")
        
        currentNode: ParseTreeNode = ParseTreeNode(NodeType.PARSE_TREE_NODE_TYPE_NODE_DECLARATION, self.currentParseTreeNode, None)
        self.currentParseTreeNode.addChild(currentNode)
        self.currentParseTreeNode = currentNode


        if self.peekAhead(1).type == TokenType.TOKEN_TYPE_COLON:
            self.parseNodeLabel()

        if self.currentToken.type == TokenType.TOKEN_TYPE_NAME:
            newNode: ParseTreeNode = ParseTreeNode(NodeType.PARSE_TREE_NODE_TYPE_TERMINAL, self.currentParseTreeNode, self.currentToken)
            self.currentParseTreeNode.addChild(newNode)
            self.currentToken = self.getNextToken()
        else:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Expected node name.\n{self.getCurrentLine()}")

        if self.currentToken.type == TokenType.TOKEN_TYPE_AT_SYMBOL:
            self.parseNodeAddress()
        
        self.currentParseTreeNode = self.currentParseTreeNode.parent



    def parseNodeDefinition(self):

        if self.currentToken is None:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Current token is None.")
        
        currentNode: ParseTreeNode = ParseTreeNode(NodeType.PARSE_TREE_NODE_TYPE_NODE_DEFINITION, self.currentParseTreeNode, None)
        self.currentParseTreeNode.addChild(currentNode)
        self.currentParseTreeNode = currentNode

        self.parseNodeDeclaration()

        if self.currentToken.type == TokenType.TOKEN_TYPE_LEFT_CURLY_BRACE:
            newNode: ParseTreeNode = ParseTreeNode(NodeType.PARSE_TREE_NODE_TYPE_TERMINAL, self.currentParseTreeNode, self.currentToken)
            self.currentParseTreeNode.addChild(newNode)
        else:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Expected \"{{\".\n{self.getCurrentLine()}")

        self.currentToken = self.getNextToken()
        self.parseNodeBody()

        if self.currentToken.type == TokenType.TOKEN_TYPE_RIGHT_CURLY_BRACE:
            newNode: ParseTreeNode = ParseTreeNode(NodeType.PARSE_TREE_NODE_TYPE_TERMINAL, self.currentParseTreeNode, self.currentToken)
            self.currentParseTreeNode.addChild(newNode)
        else:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Expected \"}}\".\n{self.getCurrentLine()}")

        self.currentToken = self.getNextToken()

        if self.currentToken.type == TokenType.TOKEN_TYPE_SEMICOLON:
            newNode: ParseTreeNode = ParseTreeNode(NodeType.PARSE_TREE_NODE_TYPE_TERMINAL, self.currentParseTreeNode, self.currentToken)
            self.currentParseTreeNode.addChild(newNode)
        else:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Expected \";\".\n{self.getCurrentLine()}")

        self.currentToken = self.getNextToken()
        self.currentParseTreeNode = self.currentParseTreeNode.parent


    def parseNodeBody(self):

        if self.currentToken is None:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Current token is None.")


        # add node for current production
        currentNode: ParseTreeNode = ParseTreeNode(NodeType.PARSE_TREE_NODE_TYPE_NODE_BODY, self.currentParseTreeNode, None)
        self.currentParseTreeNode.addChild(currentNode)
        self.currentParseTreeNode = currentNode

        # check for which sub-parser to call
        while self.currentToken.type == TokenType.TOKEN_TYPE_NAME or self.currentToken.type == TokenType.TOKEN_TYPE_HASHTAG:

            # sub-parse property
            if self.currentToken.type == TokenType.TOKEN_TYPE_HASHTAG or \
                self.peekAhead(1).type == TokenType.TOKEN_TYPE_EQUALS or \
                self.peekAhead(1).type == TokenType.TOKEN_TYPE_SEMICOLON:
                self.parseNodeProperty()

            # sub-parse sub-node definition
            elif self.peekAhead(1).type == TokenType.TOKEN_TYPE_AT_SYMBOL or \
                self.peekAhead(1).type == TokenType.TOKEN_TYPE_COLON or \
                    self.peekAhead(1).type == TokenType.TOKEN_TYPE_LEFT_CURLY_BRACE:
                self.parseNodeDefinition()

            else:
                raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Expected one of: \"#\", \"=\", \";\", \"@\", \":\", \"{{\".\n{self.getCurrentLine()}")

        # move back up 1 level in the parse tree
        self.currentParseTreeNode = self.currentParseTreeNode.parent


    def parseRootNodeDefinition(self):

        if self.currentToken is None:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Current token is None.")
        

        # add node for current production
        currentNode: ParseTreeNode = ParseTreeNode(NodeType.PARSE_TREE_NODE_TYPE_ROOT_NODE_DEFINITION, self.currentParseTreeNode, None)
        self.currentParseTreeNode.addChild(currentNode)
        self.currentParseTreeNode = currentNode

        # check for forward slash
        if self.currentToken.type == TokenType.TOKEN_TYPE_FORWARD_SLASH:
            newNode: ParseTreeNode = ParseTreeNode(NodeType.PARSE_TREE_NODE_TYPE_TERMINAL, self.currentParseTreeNode, self.currentToken)
            self.currentParseTreeNode.addChild(newNode)
        else:
            raise ParseError(f"Error in parsing file {self.filePath} at line {self.getLineNumber()}. Expected \"/\".\n{self.getCurrentLine()}")

        self.currentToken = self.getNextToken()

        # check for { after /
        if self.currentToken.type == TokenType.TOKEN_TYPE_LEFT_CURLY_BRACE:
            newNode: ParseTreeNode = ParseTreeNode(NodeType.PARSE_TREE_NODE_TYPE_TERMINAL, self.currentParseTreeNode, self.currentToken)
            self.currentParseTreeNode.addChild(newNode)
        else:
            raise ParseError(f"Error in parsing file {self.filePath} at line {self.getLineNumber()}. Expected \"{{\".\n{self.getCurrentLine()}")

        self.currentToken = self.getNextToken()

        # parse the node body
        self.parseNodeBody()

        # get the closing brace
        if self.currentToken.type == TokenType.TOKEN_TYPE_RIGHT_CURLY_BRACE:
            newNode: ParseTreeNode = ParseTreeNode(NodeType.PARSE_TREE_NODE_TYPE_TERMINAL, self.currentParseTreeNode, self.currentToken)
            self.currentParseTreeNode.addChild(newNode)
        else:
            raise ParseError(f"Error in parsing file {self.filePath} at line {self.getLineNumber()}. Expected \"}}\".\n{self.getCurrentLine()}")

        self.currentToken = self.getNextToken()

        if self.currentToken.type == TokenType.TOKEN_TYPE_SEMICOLON:
            newNode: ParseTreeNode = ParseTreeNode(NodeType.PARSE_TREE_NODE_TYPE_TERMINAL, self.currentParseTreeNode, self.currentToken)
            self.currentParseTreeNode.addChild(newNode)
        else:
            raise ParseError(f"Error in parsing file {self.filePath} at line {self.getLineNumber()}. Expected \";\".\n{self.getCurrentLine()}") 

        self.currentToken = self.getNextToken()
        self.currentParseTreeNode = self.currentParseTreeNode.parent





    def parsePhandleOverride(self):

        if self.currentToken is None:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Current token is None.\n{self.getCurrentLine()}")


        # create the current node in the parse tree, add it to the tree, and move the currentParseTreeNode pointer to point to it
        currentNode: ParseTreeNode = ParseTreeNode(NodeType.PARSE_TREE_NODE_TYPE_PHANDLE_OVERRIDE, self.currentParseTreeNode, None)
        self.currentParseTreeNode.addChild(currentNode)
        self.currentParseTreeNode = currentNode

        if self.currentToken.type == TokenType.TOKEN_TYPE_PHANDLE_REFERENCE:
            newNode: ParseTreeNode = ParseTreeNode(NodeType.PARSE_TREE_NODE_TYPE_TERMINAL, self.currentParseTreeNode, self.currentToken)
            self.currentParseTreeNode.addChild(newNode)

        else:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Expected \"{{\".\n{self.getCurrentLine()}")

        self.currentToken = self.getNextToken()

        if self.currentToken.type == TokenType.TOKEN_TYPE_LEFT_CURLY_BRACE:
            newNode: ParseTreeNode = ParseTreeNode(NodeType.PARSE_TREE_NODE_TYPE_TERMINAL, self.currentParseTreeNode, self.currentToken)
            self.currentParseTreeNode.addChild(newNode)

        else:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Expected \"{{\".\n{self.getCurrentLine()}")

        self.currentToken = self.getNextToken()
        self.parseNodeBody()


        if self.currentToken.type == TokenType.TOKEN_TYPE_RIGHT_CURLY_BRACE:
            newNode: ParseTreeNode = ParseTreeNode(NodeType.PARSE_TREE_NODE_TYPE_TERMINAL, self.currentParseTreeNode, self.currentToken)
            self.currentParseTreeNode.addChild(newNode)
        else:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Expected \"}}\".\n{self.getCurrentLine()}")

        self.currentToken = self.getNextToken()
        self.currentParseTreeNode = self.currentParseTreeNode.parent


    def parseFileBody(self):

        if self.currentToken is None:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Current token is None.\n{self.getCurrentLine()}")
        

        newNode = ParseTreeNode(NodeType.PARSE_TREE_NODE_TYPE_FILE_BODY, self.currentParseTreeNode, None)
        self.currentParseTreeNode.addChild(newNode)
        self.currentParseTreeNode = newNode

        # continue attempting to parse until hit EOF
        while self.currentToken.type != TokenType.TOKEN_TYPE_END_OF_FILE:

            # parse root node definition
            if self.currentToken.type == TokenType.TOKEN_TYPE_FORWARD_SLASH:
                self.parseRootNodeDefinition()

            # parse phandle override
            elif self.currentToken.type == TokenType.TOKEN_TYPE_PHANDLE_REFERENCE:
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
        if self.currentToken.type != TokenType.TOKEN_TYPE_END_OF_FILE:
            self.parseFileBody()

        # last token must be EOF
        if self.currentToken.type == TokenType.TOKEN_TYPE_END_OF_FILE:
            newNode: ParseTreeNode = ParseTreeNode(NodeType.PARSE_TREE_NODE_TYPE_TERMINAL, self.currentParseTreeNode, self.currentToken)
            self.currentParseTreeNode.addChild(newNode)
        else:
            raise ParseError(f"Error in parsing device tree file {self.filePath} at line {self.getLineNumber()}. Expected EOF.\n{self.getCurrentLine()}")


    def getParseTree(self):
        return self.parseTree

