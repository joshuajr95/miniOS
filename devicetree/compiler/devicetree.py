

from parser import *
import sys


ADDRESS_CELLS_DEFAULT = 2
SIZE_CELLS_DEFAULT = 1


class DeviceTreeNode:

    def __init__(self, name, label=None, unitAddress=None):
        self.name = name
        self.label = label
        self.unitAddress = unitAddress
        self.children = []
        self.properties = {}
        self.parent = None


    def setAddressCells(self, addressCells):
        self.addressCells = addressCells

    def setSizeCells(self, sizeCells):
        self.sizeCells = sizeCells

    def setAddressAndSizeCells(self, addressCells, sizeCells):
        self.addressCells = addressCells
        self.sizeCells = sizeCells


    def addChild(self, newNode):
        newNode.parent = self
        self.children.append(newNode)






class DeviceTree:

    def __init__(self, rootNode: DeviceTreeNode):
        self.root = rootNode
        self.labels = {}
        self.aliases = {}


    def addLabel(self, label: str, node: DeviceTreeNode):
        self.labels[label] = node

    def removeLabel(self, label: str):
        del(self.labels[label])


    def addAlias(self, alias: str, pathOrLabel: str, isLabel: bool):
        pass




class DeviceTreeBuilder:


    def __init__(self, parseTree: ParseTree):
        self.parseTree = parseTree
        self.currentParseTreeNode = self.parseTree.rootNode



    def handlePhandleOverride(self):

        labelReference = self.currentParseTreeNode.children[0].terminal.value[1:]

        if labelReference not in self.deviceTree.labels.keys():
            print(f"Label {labelReference} not a label in device tree.")
            sys.exit(1)

        saveNode = self.currentDeviceTreeNode
        self.currentDeviceTreeNode = self.deviceTree.labels[labelReference]
        self.currentParseTreeNode = findNodeBody(self.currentParseTreeNode)

        for node in self.currentParseTreeNode.children:
            if node.type == NodeType.PARSE_TREE_NODE_TYPE_NODE_PROPERTY:
                self.currentParseTreeNode = node
                self.handleNodeProperty()
            elif node.type == NodeType.PARSE_TREE_NODE_TYPE_NODE_DEFINITION:
                self.currentParseTreeNode = node
                
                if 
                # find node in tree
                self.handleNodeDefinition()
            else:
                print("Error: Node children must either be properties or subnodes.")
                sys.exit(1)
        
        self.currentParseTreeNode = self.currentParseTreeNode.parent


    def handleAliasNode(self):

        newNodeBody = findNodeBody(self.currentParseTreeNode)

        for child in newNodeBody.children:
            if child.type != NodeType.PARSE_TREE_NODE_TYPE_NODE_PROPERTY:
                print("Error in aliases node: Encountered non-property node.")
                sys.exit(1)

            aliasName = getPropertyName(child)
            aliasValueNode = findPropertyValueNode(child)

            if aliasValueNode.type == PARSE_TREE_NODE_TYPE_TERMINAL and aliasValueNode.terminal.type == TokenType.TOKEN_TYPE_PHANDLE_REFERENCE:
                referenceName = aliasValueNode.terminal.value[1:]
                if referenceName not in self.deviceTree.labels.keys():
                    print(f"Alias {aliasName} references non-existent label {referenceName}.")
                    sys.exit(1)
                self.deviceTree.aliases[aliasName] = self.deviceTree.labels[referenceName]

            elif aliasValueNode.type == PARSE_TREE_NODE_TYPE_TERMINAL and aliasValueNode.terminal.type == TokenType.TOKEN_TYPE_STRING:
                pass
            else:
                print(f"Alias {aliasName} has value that is not a label reference or pathname.")
                sys.exit(1)



    def handleNodeDefinition(self):
        newNodeLabel = getLabel(self.currentParseTreeNode)
        newNodeName = getName(self.currentParseTreeNode)
        newNodeUnitAddress = getUnitAddress(self.currentParseTreeNode)

        # handle this and currentParseTreeNode parent
        if newNodeName == "aliases":
            newDeviceTreeNode = DeviceTreeNode(newNodeName, newNodeLabel, newNodeUnitAddress)
            self.currentDeviceTreeNode.addChild(newDeviceTreeNode)
            self.currentDeviceTreeNode = newDeviceTreeNode
            self.handleAliasNode()
            self.currentDeviceTreeNode = self.currentDeviceTreeNode.parent
            self.currentParseTreeNode = self.currentParseTreeNode.parent
            return

        newDeviceTreeNode = DeviceTreeNode(newNodeName, newNodeLabel, newNodeUnitAddress)
        newDeviceTreeNode.setAddressAndSizeCells(self.currentDeviceTreeNode.addressCells, self.currentDeviceTreeNode.sizeCells)
        self.currentDeviceTreeNode.addChild(newDeviceTreeNode)
        self.currentDeviceTreeNode = newDeviceTreeNode

        if newNodeLabel is not None:
            self.deviceTree.labels[newNodeLabel] = newDeviceTreeNode

        newNodeBody = findNodeBody(self.currentParseTreeNode)

        self.currentParseTreeNode = newNodeBody
        self.handleNodeBody()

        self.currentParseTreeNode = self.currentParseTreeNode.parent
        self.currentDeviceTreeNode = self.currentDeviceTreeNode.parent


    def handleNodeProperty(self):
        propertyName = getPropertyName(self.currentParseTreeNode)
        valueNode = findPropertyValueNode(self.currentParseTreeNode)

        propertyValue = []

        for child in valueNode.children:

            if child.type == NodeType.PARSE_TREE_NODE_TYPE_PROPERTY_VALUE_ARRAY:
                valueArray = []
                i = 1
                listElement = child.children[i]
                while i < len(child.children) and listElement.terminal.type != TokenType.TOKEN_TYPE_RIGHT_ANGLE_BRACKET:
                    valueArray.append(listElement.terminal.value)
                    i += 1
                    listElement = child.children[i]
                propertyValue.append(valueArray)

            elif child.type == NodeType.PARSE_TREE_NODE_TYPE_TERMINAL and child.terminal.type == TokenType.TOKEN_TYPE_STRING:
                propertyValue.append(child.terminal.value)

            elif child.type == NodeType.PARSE_TREE_NODE_TYPE_TERMINAL and child.terminal.type == TokenType.TOKEN_TYPE_PHANDLE_REFERENCE:
                propertyValue.append(child.terminal.value)

            else:
                print("Error: Node property must be value array, string, or phandle.")
                sys.exit(1)


        if propertyName == "address-cells":
            self.currentDeviceTreeNode.setAddressCells(propertyValue[0])
        elif propertyName == "size-cells":
            self.currentDeviceTreeNode.setSizeCells(propertyValue[0])
        else:
            self.currentDeviceTreeNode.properties[propertyName] = propertyValue
            self.currentParseTreeNode = self.currentParseTreeNode.parent


    def handleNodeBody(self):

        for node in self.currentParseTreeNode.children:
            if node.type == NodeType.PARSE_TREE_NODE_TYPE_NODE_PROPERTY:
                self.currentParseTreeNode = node
                self.handleNodeProperty()
            elif node.type == NodeType.PARSE_TREE_NODE_TYPE_NODE_DEFINITION:
                self.currentParseTreeNode = node
                self.handleNodeDefinition()
            else:
                print("Error: Node children must either be properties or subnodes.")
                sys.exit(1)
        
        self.currentParseTreeNode = self.currentParseTreeNode.parent


    def handleRootNodeDefinition(self):

        # multiple root node definitions may exist. The first creates the tree, and
        # subsequent definitions override the tree properties
        if self.deviceTree is None:
            self.currentDeviceTreeNode = DeviceTreeNode("/")
            self.deviceTree = DeviceTree(self.currentDeviceTreeNode)

        self.currentDeviceTreeNode.setAddressAndSizeCells(ADDRESS_CELLS_DEFAULT, SIZE_CELLS_DEFAULT)

        rootNodeBody = findNodeBody(self.currentParseTreeNode)

        if rootNodeBody is None:
            print("Error: Root node does not have a body.")
            sys.exit(1)

        self.currentParseTreeNode = rootNodeBody
        self.handleNodeBody()
        self.currentParseTreeNode = self.currentParseTreeNode.parent




    '''
    Build the device tree structure from the parse tree.
    '''
    def buildDeviceTree(self):

        fileBodyNode = findFirstSubNodeByType(self.parseTree.rootNode, NodeType.PARSE_TREE_NODE_TYPE_FILE_BODY)

        if fileBodyNode is None:
            print("Error: File body appears to be empty.")
            sys.exit(1)

        self.currentParseTreeNode = fileBodyNode

        for node in self.currentParseTreeNode.children:
            if node.type == NodeType.PARSE_TREE_NODE_TYPE_PHANDLE_OVERRIDE:
                self.currentParseTreeNode = node
                self.handlePhandleOverride()
            elif node.type == NodeType.PARSE_TREE_NODE_TYPE_ROOT_NODE_DEFINITION:
                self.currentParseTreeNode = node
                self.handleRootNodeDefinition()
            else:
                print("Error: Node is of unrecognized type.")
                sys.exit(1)




