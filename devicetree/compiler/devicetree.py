

from parser import *
import os
import yaml


# acceptable defaults according to DTSpec
ADDRESS_CELLS_DEFAULT = 2
SIZE_CELLS_DEFAULT = 1


class DTNodePropertyType(Enum):
    STRING = 0
    STRING_ARRAY = 1
    INT = 2
    INT_ARRAY = 3
    BYTE_ARRAY = 4
    PHANDLE_ARRAY = 5
    PHANDLE = 6
    MULTI_PHANDLES = 7
    BOOLEAN = 8


'''
Each property of a Device Tree node may contain multiple values separated by commas.
Each value has a type and a literal value
'''
class DTNodeProperty:

    def __init__(self, name: str, type: DTNodePropertyType, value):
        self.name = name
        self.type = type
        self.value = value

    def __str__(self):
        return f"{self.name}: <{self.type.name}> {str(self.value)}"


class DeviceTreeNode:

    def __init__(self, name, parent, label=None, unitAddress=None):
        self.name = name
        self.label = label
        self.unitAddress = unitAddress
        self.children = []
        self.properties = {}
        self.parent = parent


    def print(self, indentLevel):

        outStr = ""
        for i in range(indentLevel):
            outStr += "\t"

        if self.label is not None:
            outStr += f"{self.label}: "

        outStr += f"{self.name}"

        if self.unitAddress is not None:
            outStr += f"@{self.unitAddress}"
        outStr += "\n"

        for i in range(indentLevel):
            outStr += "\t"
        outStr += "Properties:\n"
        for propertyName in self.properties.keys():
            for i in range(indentLevel):
                outStr += "\t"
            outStr += "  - "
            outStr += str(self.properties[propertyName])
            outStr += "\n"

        print(outStr)

        for subNode in self.children:
            subNode.print(indentLevel+1)


    def setProperty(self, propertyName: str, propertyValue):
        self.properties[propertyName] = propertyValue

    def getProperty(self, propertyName: str):
        return self.properties[propertyName]
    
    def hasProperty(self, propertyName: str) -> bool:
        return propertyName in self.properties.keys()


    def addChild(self, newNode):
        newNode.parent = self
        self.children.append(newNode)

    def findChildByNameAndUnitAddress(self, childName: str, unitAddress: str):
        for child in self.children:
            if child.name == childName and child.unitAddress == unitAddress:
                return child

        return None


'''
Takes a ParseTreeNode of type NODE_PROPERTY and parses it to generate the
property type. This is the first part of translating a device tree node
property from the parse tree structure to the device tree structure.

@param property: The ParseTreeNode of type NODE_PROPERTY to get the type of
@return DTNodePropertyType enum distinguishing the type of this Device Tree property
'''
def generatePropertyType(property: ParseTreeNode) -> DTNodePropertyType:

    if property.type != NodeType.NODE_PROPERTY:
        raise Exception(f"generatePropertyType called on parse tree node of type {property.type.name} at line {property.lineNumber}")

    valueNode = getDTPropertyValueNode(property)

    if valueNode is None:
        return DTNodePropertyType.BOOLEAN

    elif valueNode.children[0].type == NodeType.PROPERTY_VALUE_ARRAY:
        pvArray = valueNode.children[0].children[1:-1]

        if len(pvArray) > 1:
            hasPhandleReference = False
            hasInt = False
            for subnode in pvArray:
                if subnode.type == NodeType.PHANDLE_REFERENCE:
                    hasPhandleReference = True
                elif (subnode.type == NodeType.TERMINAL) and ((subnode.terminalType == TerminalType.DECIMAL_NUMBER) or (subnode.terminalType == TerminalType.HEXADECIMAL_NUMBER)):
                    hasInt = True

            if hasPhandleReference and hasInt:
                return DTNodePropertyType.PHANDLE_ARRAY
            elif hasPhandleReference and not hasInt:
                return DTNodePropertyType.MULTI_PHANDLES
            elif not hasPhandleReference and hasInt:
                return DTNodePropertyType.INT_ARRAY
            else:
                raise Exception(f"Node pvarray does not have types either PHANDLE_ARRAY or INT_ARRAY or MULTI_PHANDLES")

        else:
            if pvArray[0].type == NodeType.PHANDLE_REFERENCE:
                return DTNodePropertyType.PHANDLE
            elif (pvArray[0].type == NodeType.TERMINAL) and ((pvArray[0].terminalType == TerminalType.DECIMAL_NUMBER) or (pvArray[0].terminalType == TerminalType.HEXADECIMAL_NUMBER)):
                return DTNodePropertyType.INT
            else:
                raise Exception(f"Node pvarray does not have types either PHANDLE or INT")

    elif (valueNode.children[0].type == NodeType.TERMINAL) and (valueNode.children[0].terminalType == TerminalType.STRING) and (len(valueNode.children) > 1):
        return DTNodePropertyType.STRING_ARRAY

    elif (valueNode.children[0].type == NodeType.TERMINAL) and (valueNode.children[0].terminalType == TerminalType.STRING):
        return DTNodePropertyType.STRING

    else:
        raise Exception(f"Node with erroneous property type")




'''
Takes a ParseTreeNode of type NODE_PROPERTY and parses it to generate
a DTNodeProperty object that can be inserted into a DeviceTreeNode's
'properties' dictionary. This is used as part of the process of converting
the parse tree into the actual device tree
'''
def generatePropertyValue(property: ParseTreeNode) -> DTNodeProperty:

    propertyName = getDTPropertyName(property)
    propertyType: DTNodePropertyType = generatePropertyType(property)


    callbacks = {
        DTNodePropertyType.BOOLEAN : getDTPropertyValueBoolean,
        DTNodePropertyType.STRING : getDTPropertyValueString,
        DTNodePropertyType.STRING_ARRAY : getDTPropertyValueStringArray,
        DTNodePropertyType.PHANDLE_ARRAY : getDTPropertyValuePhandleArray,
        DTNodePropertyType.INT_ARRAY : getDTPropertyValueIntArray,
        DTNodePropertyType.INT : getDTPropertyValueInt,
        DTNodePropertyType.PHANDLE : getDTPropertyValuePhandle,
        DTNodePropertyType.MULTI_PHANDLES : getDTPropertyValueMultiPhandle
    }

    propertyValue = callbacks[propertyType](property)
    return DTNodeProperty(propertyName, propertyType, propertyValue)


def validateCompatibleProperty(node: ParseTreeNode):

    propertyName = getDTPropertyName(node)

    if propertyName != "compatible":
        raise Exception(f"Property '{propertyName}' is not 'compatible' but was passed to validateCompatibleProperty.")

    propertyValue = getDTPropertyValueNode(node)

    for child in propertyValue.children:
        if (child.type == NodeType.TERMINAL) and ((child.terminalType == TerminalType.STRING) or (child.terminalType == TerminalType.COMMA)):
            continue
        else:
            raise Exception(f"'Compatible' property does not have value of type <string> or <string-list>")

def duplicatePropertiesExist(properties: List[ParseTreeNode]):

    duplicatesExist = False

    # keeps track of already processed properties
    # for duplicate checking
    alreadyExistingPropertyNames = {}

    for property in properties:
        propertyName = getDTPropertyName(property)

        if propertyName in alreadyExistingPropertyNames.keys():
            duplicatesExist = True

        alreadyExistingPropertyNames[propertyName] = True
    
    return duplicatesExist



class DeviceTree:

    def __init__(self, rootNode: DeviceTreeNode):
        self.root = rootNode
        self.labels = {}
        self.aliases = {}
        self.chosen = {}

        # for special specifiers (gpios and #gpio-cells, pwms and #pwm-cells, etc.)
        self.specifierSpaces = set()


    def addLabel(self, label: str, node: DeviceTreeNode):
        self.labels[label] = node

    def removeLabel(self, label: str):
        del(self.labels[label])

    def print(self):
        labelStr = "Device Tree:\n"
        labelStr += "Labels:\n"

        for labelName in self.labels.keys():
            labelStr += labelName
            labelStr += " --> "
            labelStr += self.labels[labelName].name

            if self.labels[labelName].unitAddress is not None:
                labelStr += "@"
                labelStr += self.labels[labelName].unitAddress
            
            labelStr += "\n"

        
        print(labelStr)

        chosenStr = "Chosen:\n"
        for chosen in self.chosen.keys():
            chosenStr += chosen
            chosenStr += " := "
            chosenStr += self.chosen[chosen]
            chosenStr += "\n"

        print(chosenStr)

        print("\nNodes:\n")

        self.root.print(0)
            






class DeviceTreeBuilder:


    def __init__(self, parseTree: ParseTree):
        self.parseTree = parseTree
        self.currentParseTreeNode = self.parseTree.rootNode
        self.deviceTree = None
        self.currentDeviceTreeNode = None
        self.bindings = {}
        self.loadDTBindings("bindings")


    def loadDTBindings(self, bindingsDirectory: str):

        files = os.listdir(bindingsDirectory)

        # iterate over binding YAML files in the 'bindings' directory and
        # read the YAML files into Python objects
        for fileName in files:
            if fileName.endswith(".yml") or fileName.endswith(".yaml"):
                with open(f"{bindingsDirectory}/{fileName}", "r") as fileHandle:
                    self.bindings[fileName] = yaml.safe_load(fileHandle)



    def matchCompatibleToBinding(self, compatibleStrings: List[str]):

        for compat in compatibleStrings:
            for binding in self.bindings.values():
                if "compatible" in binding.keys() and binding["compatible"] == compat:
                    return binding

        return None

    def getBindingFromNodeName(self, nodeName: str):

        for fileName in self.bindings.keys():
            firstPart = fileName.split(".")[0]

            if firstPart == nodeName:
                return self.bindings[fileName]

        return None


    def checkDeviceTreeForMissingProperties(self):

        binding = None
        if self.currentDeviceTreeNode.hasProperty("compatible"):
            compatibleStrings = self.currentDeviceTreeNode.getProperty("compatible").value
            binding = self.matchCompatibleToBinding(compatibleStrings)

            if binding is None:
                raise Exception(f"nodeBinding is None. There does not appear to be a matching binding for compatible '{self.currentDeviceTreeNode.getProperty('compatible').value}'.")

        else:
            nodeName = self.currentDeviceTreeNode.name
            binding = self.getBindingFromNodeName(nodeName)
            if binding is None:
                raise Exception(f"nodeBinding is None. There does not appear to be a matching binding for node '{self.currentDeviceTreeNode.name}'")


        if "properties" not in binding.keys():
            raise Exception(f"Binding for node {getDTNodeName(self.currentParseTreeNode)} does not have 'properties' list")

        bindingPropertiesDictionary = binding["properties"]
        nodePropertyNames = list(self.currentDeviceTreeNode.properties.keys())

        # check for missing required properties
        for propertyName in bindingPropertiesDictionary.keys():
            if bindingPropertiesDictionary[propertyName]["required"] and propertyName not in nodePropertyNames and bindingPropertiesDictionary[propertyName]["type"] == "boolean":
                self.currentDeviceTreeNode.setProperty(propertyName, DTNodeProperty(propertyName, DTNodePropertyType.BOOLEAN, "false"))
            elif bindingPropertiesDictionary[propertyName]["required"] and propertyName not in nodePropertyNames:
                raise Exception(f"Required property '{propertyName}' for node '{self.currentDeviceTreeNode.name}' is not found")


        for subNode in self.currentDeviceTreeNode.children:
            currentDeviceTreeNodeSave = self.currentDeviceTreeNode
            self.currentDeviceTreeNode = subNode
            self.checkDeviceTreeForMissingProperties()
            self.currentDeviceTreeNode = currentDeviceTreeNodeSave



    def validateNodeWithBinding(self, node: ParseTreeNode, binding):

        if "properties" not in binding.keys():
            raise Exception(f"Binding for node {getDTNodeName(node)} does not have 'properties' list")

        bindingPropertiesDictionary = binding["properties"]
        nodeProperties = getDTNodeProperties(node)

        # find property in binding
        # if not found, continue
        for property in nodeProperties:
            propertyName = getDTPropertyName(property)
            if propertyName not in bindingPropertiesDictionary.keys():
                continue    # TODO: emit warning, not error

            propertyBinding = bindingPropertiesDictionary[propertyName]

            # check property type
            propertyTypeToString = {
                DTNodePropertyType.BOOLEAN : "boolean",
                DTNodePropertyType.BYTE_ARRAY : "byte-array",
                DTNodePropertyType.INT : "int",
                DTNodePropertyType.INT_ARRAY : "array",
                DTNodePropertyType.MULTI_PHANDLES : "phandles",
                DTNodePropertyType.PHANDLE : "phandle",
                DTNodePropertyType.PHANDLE_ARRAY : "phandle-array",
                DTNodePropertyType.STRING : "string",
                DTNodePropertyType.STRING_ARRAY : "string-array"
            }

            propertyType = generatePropertyType(property)
            if propertyTypeToString[propertyType] != propertyBinding["type"]:
                raise Exception(f"Property '{propertyName}' in device tree node '{getDTNodeName(node)} has type '{propertyType.name}' but expected '{propertyBinding['type']}' from binding.")


            if "const" in propertyBinding.keys():
                expectedPropertyValue = str(propertyBinding["const"])
                actualPropertyValue = generatePropertyValue(property)
                if actualPropertyValue.value != expectedPropertyValue:
                    raise Exception(f"Property '{propertyName}' in device tree node '{getDTNodeName(node)}' has value {actualPropertyValue.value} but expected {expectedPropertyValue} from binding")

            if "enum" in propertyBinding.keys():
                expectedPropertyValueArray = str(propertyBinding["enum"])
                actualPropertyValue = generatePropertyValue(property)
                if actualPropertyValue.value not in expectedPropertyValueArray:
                    raise Exception(f"Property '{propertyName}' in device tree node '{getDTNodeName(node)}' has value {actualPropertyValue.value} but expected one of <{', '.join(expectedPropertyValueArray)}> from binding")



    def handlePhandleOverride(self):

        phandleLabel = getDTPhandleOverrideLabel(self.currentParseTreeNode)
        self.currentDeviceTreeNode = self.deviceTree.labels[phandleLabel]

        self.handleNodeBodyOverride()



    def handleAliasesNode(self):

        if self.currentDeviceTreeNode.name != "/":
            raise Exception(f"'aliases' node must be a child of root node")
        
        aliasProperties = getDTNodeProperties(self.currentParseTreeNode)
        for property in aliasProperties:
            propertyName = getDTPropertyName(property)
            propertyType = generatePropertyType(property)

            if propertyType == DTNodePropertyType.PHANDLE:
                propertyValue = getDTPropertyValuePhandle(property)
                self.deviceTree.aliases[propertyName] = DTNodeProperty(propertyName, propertyType, propertyValue)
            elif propertyType == DTNodePropertyType.STRING:
                propertyValue = getDTPropertyValueString(property)
                self.deviceTree.aliases[propertyName] = DTNodeProperty(propertyName, propertyType, propertyValue)
            else:
                raise Exception(f"Properties in 'aliases' node must have types STRING or PHANDLE, but encountered property '{propertyName}' with type {propertyType.name}")

        subNodes = getDTNodeSubNodes(self.currentParseTreeNode)
        if len(subNodes) > 0:
            raise Exception(f"'aliases' node cannot have child nodes")


    def handleChosenNode(self):

        if self.currentDeviceTreeNode.name != "/":
            raise Exception(f"'chosen' node must be a child of root node")

        chosenProperties = getDTNodeProperties(self.currentParseTreeNode)
        for property in chosenProperties:
            propertyName = getDTPropertyName(property)
            propertyType = generatePropertyType(property)

            if propertyType == DTNodePropertyType.PHANDLE:
                propertyValue = getDTPropertyValuePhandle(property)
                self.deviceTree.chosen[propertyName] = DTNodeProperty(propertyName, propertyType, propertyValue)
            elif propertyType == DTNodePropertyType.STRING:
                propertyValue = getDTPropertyValueString(property)
                self.deviceTree.chosen[propertyName] = DTNodeProperty(propertyName, propertyType, propertyValue)
            else:
                raise Exception(f"Properties in 'chosen' node must have types STRING or PHANDLE, but encountered property '{propertyName}' with type {propertyType.name}")

        subNodes = getDTNodeSubNodes(self.currentParseTreeNode)
        if len(subNodes) > 0:
            raise Exception(f"'chosen' node cannot have child nodes")


    def handleNodeDefinitionOverride(self):

        # get the name, label, and unit address
        nodeName = getDTNodeName(self.currentParseTreeNode)
        nodeLabel = getDTNodeLabel(self.currentParseTreeNode)
        nodeUnitAddress = getDTNodeUnitAddress(self.currentParseTreeNode)

        if nodeName == "aliases":
            self.handleAliasesNode()
        elif nodeName == "chosen":
            self.handleChosenNode()
        else:
            self.handleNodeBodyOverride()


    def handleNodeBodyOverride(self):

        overrideProperties = getDTNodeProperties(self.currentParseTreeNode)
        if duplicatePropertiesExist(overrideProperties):
            raise Exception(f"Duplicate properties exist in device tree node {getDTNodeName(self.currentParseTreeNode)}")

        nodeName = self.currentDeviceTreeNode.name
        nodeBinding = None

        if self.currentDeviceTreeNode.hasProperty("compatible"):
            nodeBinding = self.matchCompatibleToBinding(self.currentDeviceTreeNode.getProperty("compatible").value)
            if nodeBinding is None:
                raise Exception(f"nodeBinding is None. There does not appear to be a matching binding for compatible '{self.currentDeviceTreeNode.getProperty('compatible').value}'.")

        else:
            nodeBinding = self.getBindingFromNodeName(nodeName)

        self.validateNodeWithBinding(self.currentParseTreeNode, nodeBinding)


        for property in overrideProperties:
            propertyName = getDTPropertyName(property)

            if (propertyName.startswith("#")) and (propertyName.split("-")[-1] == "cells") and (propertyName != "#address-cells") and (propertyName != "#size-cells"):
                self.deviceTree.specifierSpaces.add(propertyName.split("-")[0][1:])

            propertyVal = generatePropertyValue(property)
            self.currentDeviceTreeNode.setProperty(propertyName, propertyVal)

        subNodes = getDTNodeSubNodes(self.currentParseTreeNode)
        for subNode in subNodes:
            subNodeName = getDTNodeName(subNode)
            subNodeUnitAddress = getDTNodeUnitAddress(subNode)
            if subNodeUnitAddress is None:
                subNodeUnitAddress = ""
            existingDTNode = self.currentDeviceTreeNode.findChildByNameAndUnitAddress(subNodeName, subNodeUnitAddress)
            if existingDTNode is None:
                currentParseTreeNodeSave = self.currentParseTreeNode
                self.currentParseTreeNode = subNode
                self.handleNodeDefinition()
                self.currentParseTreeNode = currentParseTreeNodeSave
            else:
                currentParseTreeNodeSave = self.currentParseTreeNode
                currentDeviceTreeNodeSave = self.currentDeviceTreeNode
                self.currentParseTreeNode = subNode
                self.currentDeviceTreeNode = existingDTNode
                self.handleNodeDefinitionOverride()
                self.currentParseTreeNode = currentParseTreeNodeSave
                self.currentDeviceTreeNode = currentDeviceTreeNodeSave
            

    def handleNodeDefinition(self):

        # get the name, label, and unit address
        nodeName = getDTNodeName(self.currentParseTreeNode)
        nodeLabel = getDTNodeLabel(self.currentParseTreeNode)
        nodeUnitAddress = getDTNodeUnitAddress(self.currentParseTreeNode)

        if nodeName == "aliases":
            self.handleAliasesNode()
        elif nodeName == "chosen":
            self.handleChosenNode()
        else:
            # create new device tree node, add it as a child of the current, and set it to be the current node
            newDeviceTreeNode: DeviceTreeNode = DeviceTreeNode(nodeName, self.currentDeviceTreeNode, nodeLabel, nodeUnitAddress)
            self.currentDeviceTreeNode.addChild(newDeviceTreeNode)
            self.currentDeviceTreeNode = newDeviceTreeNode

            # add the label to the label map, so that label lookups go to the current node
            if nodeLabel is not None:
                self.deviceTree.labels[nodeLabel] = self.currentDeviceTreeNode

            self.handleNodeBody()

            self.currentDeviceTreeNode = self.currentDeviceTreeNode.parent



    def handleNodeBody(self):

        # get all of the node's properties, iterate over them and check for duplicates
        nodePropertyList = getDTNodeProperties(self.currentParseTreeNode)
        if duplicatePropertiesExist(nodePropertyList):
            raise Exception(f"Duplicate properties exist in device tree node {getDTNodeName(self.currentParseTreeNode)}")


        nodeBinding = None

        # get 'compatible' property
        compatibleProperty = getDTNodePropertyByName(self.currentParseTreeNode, "compatible")


        # if 'compatible' property exists, use it to load a binding, otherwise load a binding using the node name
        if compatibleProperty is not None:
            validateCompatibleProperty(compatibleProperty)
            compatibleStrings = getDTPropertyValueStringArray(compatibleProperty)
            self.currentDeviceTreeNode.setProperty("compatible", DTNodeProperty("compatible", DTNodePropertyType.STRING_ARRAY, compatibleStrings))
            nodePropertyList.remove(compatibleProperty)

            # use 'compatible' property to find matching binding and error if not found
            nodeBinding = self.matchCompatibleToBinding(self.currentDeviceTreeNode.getProperty("compatible").value)
            if nodeBinding is None:
                raise Exception(f"nodeBinding is None. There does not appear to be a matching binding for compatible '{self.currentDeviceTreeNode.getProperty('compatible').value}'.")
        else:
            nodeBinding = self.getBindingFromNodeName(self.currentDeviceTreeNode.name)
            if nodeBinding is None:
                raise Exception(f"nodeBinding is None. There does not appear to be a matching binding for node '{self.currentDeviceTreeNode.name}'")


        # use the matched binding to validate the device tree node
        self.validateNodeWithBinding(self.currentParseTreeNode, nodeBinding)


        for property in nodePropertyList:
            propertyName = getDTPropertyName(property)
            propertyType = generatePropertyType(property)
            
            if (propertyName.startswith("#")) and (propertyName.split("-")[-1] == "cells") and (propertyName != "#address-cells") and (propertyName != "#size-cells"):
                self.deviceTree.specifierSpaces.add(propertyName.split("-")[0][1:])

            propertyValue = generatePropertyValue(property)
            self.currentDeviceTreeNode.setProperty(propertyName, propertyValue)


        subNodes = getDTNodeSubNodes(self.currentParseTreeNode)

        if len(subNodes) > 0 and ( (not self.currentDeviceTreeNode.hasProperty("#address-cells")) or (not self.currentDeviceTreeNode.hasProperty("#size-cells")) ):
            pass # TODO: add warning that node with children does not have #address-cells and/or #size-cells


        for subNode in subNodes:
            currentParseTreeNodeSave = self.currentParseTreeNode
            self.currentParseTreeNode = subNode
            self.handleNodeDefinition()
            self.currentParseTreeNode = currentParseTreeNodeSave




    def handleRootNodeDefinition(self):

        # multiple root node definitions may exist. The first creates the tree, and
        # subsequent definitions override the tree properties
        if self.deviceTree is None:
            self.currentDeviceTreeNode = DeviceTreeNode("/", None, label=None, unitAddress=None)
            self.deviceTree = DeviceTree(self.currentDeviceTreeNode)

            self.handleNodeBody()

        else:
            self.currentDeviceTreeNode = self.deviceTree.root
            self.handleNodeBodyOverride()



    '''
    Build the device tree structure from the parse tree.
    '''
    def buildDeviceTree(self):

        fileBodyNode = getDTFileBody(self.parseTree.rootNode)

        # handle empty file body without crashing
        if fileBodyNode is None:
            rootNode = DeviceTreeNode("/", None)
            self.deviceTree = DeviceTree(rootNode)
            return

        rootNodes = getDTRootNodeDefinitions(fileBodyNode)
        for node in rootNodes:
            self.currentParseTreeNode = node
            self.handleRootNodeDefinition()

        phandleOverrides = getDTPhandleOverrides(fileBodyNode)
        for node in phandleOverrides:
            self.currentParseTreeNode = node
            self.handlePhandleOverride()

        self.currentDeviceTreeNode = self.deviceTree.root
        self.checkDeviceTreeForMissingProperties()





