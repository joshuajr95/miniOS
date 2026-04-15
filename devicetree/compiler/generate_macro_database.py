

from devicetree import *


# generate and add the properties to the current node
'''
for property in nodePropertyList:
    propertyName = getDTPropertyName(property)
    if propertyName == "reg":
        regArray = self.generateRegArray(property)
        self.currentDeviceTreeNode.setProperty("reg", DTNodeProperty("reg", DTNodePropertyType.INT_ARRAY, regArray))
    elif propertyName == "interrupts":
        self.generateInterruptsArray(property)
        # get interrupt-parent property
        # get interrupt parent #interrupt-cells
        # process interrupts property
        # add phandle reference fixup
    elif propertyName.endswith("s") and (propertyName[:-1] in self.specifierSpaces):
        pass # process phandle array for specifier
                # add phandle reference fixup
    elif propertyName.endswith("s") and (propertyName.split("-")[-1][:-1] in self.specifierSpaces):
        pass # process phandle array for specifier
                # add phandle reference fixup
    elif (propertyName.startswith("#")) and (propertyName.split("-")[-1] == "cells") and (propertyName != "#address-cells") and (propertyName != "#size-cells"):
        self.specifierSpaces.add(propertyName.split("-")[0][1:])
        cells = getDTPropertyValueInt(property)
        self.currentDeviceTreeNode.setProperty(propertyName, DTNodeProperty(propertyName, DTNodePropertyType.INT, cells))
    else:
        propertyValue = generatePropertyValue(property)
        self.currentDeviceTreeNode.setProperty(propertyName, propertyValue)
        # add phandle reference fixup
'''


# TODO: move expandTo32BitWidth to this file and potentially fix it up
# TODO: move generateRegArray to this file and fix it up (remove self and change to deviceTreeNode instead of ParseTreeNode)
# TODO: move generateInterruptsArray to this file and 


'''
This function should only be called for hexadecimal numbers.
Regular decimal numbers should not need sign extension.
'''
def expandTo32BitWidth(number: str) -> str:

    temp = number

    hasPrefix = False
    if temp[:2] == "0x":
        temp = temp[2:]
        hasPrefix = True

    # 8 == number of hex chars in 32-bit int
    if len(temp) > 8:
        raise Exception(f"Hex char 0x{temp} is larger than 32 bits")

    for i in range(8 - len(temp)):
        temp = "0" + temp
    
    if hasPrefix:
        temp = "0x" + temp

    return temp



def generateInterruptsArray(property: DeviceTreeNode):
    raise Exception(f"Not implemented")


def generateRegArray(dtNode: DeviceTreeNode):

    if dtNode.parent is None:
        raise Exception(f"Device tree node {dtNode.name} does not have parent. Cannot get #address-cells or #size-cells.")

    addressCells = int(dtNode.parent.getProperty("#address-cells").value)
    sizeCells = int(dtNode.parent.getProperty("#size-cells").value)

    # need to add function to parse int array
    intArray = dtNode.getProperty("reg").value

    if intArray is None:
        raise Exception(f"intArray is None, somehow...")

    i = 0
    regArray = []

    # for toggling between address and size cells in array
    isAddress = True
    while i < len(intArray):

        # handle the address cells (merge each part of the address into a single number)
        if isAddress:
            addr = expandTo32BitWidth(intArray[i])
            j = i + 1
            while j < i + addressCells:
                if intArray[i][:2] == "0x":
                    addr += expandTo32BitWidth(intArray[j][2:])
                else:
                    addr += expandTo32BitWidth(intArray[j])
                j += 1
            regArray.append(addr)
            i += addressCells

        # handle the size cells (merge each part of the size into a single number)
        else:
            size = expandTo32BitWidth(intArray[i])
            j = i + 1
            while j < i + sizeCells:
                if intArray[i][:2] == "0x":
                    size += expandTo32BitWidth(intArray[j][2:])
                else:
                    size += expandTo32BitWidth(intArray[j])
                j += 1
            regArray.append(size)
            i += sizeCells

    return regArray


# TODO: check for 'reg' property and if found, generateRegArray
# TODO: check for 'interrupts' property and if found generateInterruptsArray
# TODO: check for '<specifier>s' phandle-array and if found generate phandle array
def validateAndFixUpDeviceTreeNode(deviceTreeNode: DeviceTreeNode):
    raise Exception("Not implemented")


'''
Convert a name from device tree format to a
format that is acceptable for C preprocessor
macros
'''
def convertName(name: str):
    convertibleCharacters = ['#', ',', '.', '?', '-']
    convertedName = ""

    for letter in name:
        if letter in convertibleCharacters:
            convertedName += "_"
        else:
            convertedName += letter
    
    return convertedName


# TODO: Generate top comment and include guard
# TODO: For each node, fixup the node with 'reg' property
# TODO: Generate DT_NODE_<path>_parent
# TODO: Generate DT_NODE_<path>_PROPERTY_<property-name>
# TODO: Generate matching driver macro
# TODO: Handle partial node path, so you don't have to go all the way back up to the top
# TODO: Device tree API macros
class MacroDatabaseGenerator:

    def __init__(self, outputFilePath: str, deviceTree: DeviceTree):

        fileName = outputFilePath.split("/")
        fileNameSplit = fileName[-1].split(".")
        if len(fileNameSplit) != 2 or fileNameSplit[-1] != "h":
            raise Exception(f"MacroDatabaseGenerator passed output file name {fileName} that is not a .h C header file")

        self.outputFilePath = outputFilePath
        self.deviceTree = deviceTree
        self.currentDeviceTreeNode = self.deviceTree.root
        self.partialPath = ""

        self.activeDevices = {}


    def generateRegMacros(self, nodePath: str):
        addressCells = int(self.currentDeviceTreeNode.parent.getProperty("#address-cells").value)
        sizeCells = int(self.currentDeviceTreeNode.parent.getProperty("#size-cells").value)
        regArray = self.currentDeviceTreeNode.getProperty("reg").value

        if len(regArray) % (addressCells + sizeCells) != 0:
            raise Exception(f"Property 'reg' is incomplete. Needs a whole number of (base, size) pairs. len is {len(regArray)}. reg: {regArray}. node: {self.currentDeviceTreeNode.name}")

        regLength = len(regArray)//(addressCells + sizeCells)
        self.fileHandle.write(f"#define DT_NODE_{nodePath}_PROPERTY_reg_LENGTH   {regLength}\n")

        i = 0
        regIndex = 0

        # for toggling between address and size cells in array
        isAddress = True
        while i < len(regArray):
            if isAddress:

                addr = expandTo32BitWidth(regArray[i])
                j = i + 1

                while j < i + addressCells:
                    if regArray[i][:2] == "0x":
                        addr += expandTo32BitWidth(regArray[j][2:])
                    else:
                        addr += expandTo32BitWidth(regArray[j])
                    j += 1

                self.fileHandle.write(f"#define DT_NODE_{nodePath}_PROPERTY_reg_{regIndex}_address   {addr}\n")

                i += addressCells
            
            else:

                size = expandTo32BitWidth(regArray[i])
                j = i + 1

                while j < i + sizeCells:
                    if regArray[i][:2] == "0x":
                        size += expandTo32BitWidth(regArray[j][2:])
                    else:
                        size += expandTo32BitWidth(regArray[j])
                    j += 1

                self.fileHandle.write(f"#define DT_NODE_{nodePath}_PROPERTY_reg_{regIndex}_size   {size}\n")

                i += sizeCells
                regIndex += 1

            isAddress = not isAddress


    def generateInterrupts(self, nodePath: str, interruptCells: int, property: DTNodeProperty):

        interruptArray = property.value
        if len(interruptArray) % interruptCells != 0:
            raise Exception(f"The 'interrupts' array for node '{self.currentDeviceTreeNode.name}' must have length that is a multiple of {interruptCells}")

        numInterrupts = len(interruptArray) // interruptCells
        i = 0

        self.fileHandle.write(f"#define DT_NODE_{nodePath}_PROPERTY_interrupts_LENGTH   {numInterrupts}\n")

        while i < numInterrupts:
            j = 0
            while j < interruptCells:
                interruptElement = interruptArray[i*interruptCells+j]
                self.fileHandle.write(f"#define DT_NODE_{nodePath}_PROPERTY_interrupts_{i}_{j}   {interruptElement}\n")
                j += 1
            
            i += 1



    def generateStringPropertyMacros(self, nodePath: str, propertyName: str, property: DTNodeProperty):
        convertedPropertyName = convertName(propertyName)
        self.fileHandle.write(f"#define DT_NODE_{nodePath}_PROPERTY_{convertedPropertyName}   \"{property.value}\"\n")


    def generateStringArrayPropertyMacros(self, nodePath: str, propertyName: str, property: DTNodeProperty):
        convertedPropertyName = convertName(propertyName)
        self.fileHandle.write(f"#define DT_NODE_{nodePath}_PROPERTY_{convertedPropertyName}_LENGTH   {len(property.value)}\n")

        for i, prop in enumerate(property.value):
            self.fileHandle.write(f"#define DT_NODE_{nodePath}_PROPERTY_{convertedPropertyName}_{i}   \"{prop}\"\n")


    def generateIntPropertyMacros(self, nodePath: str, propertyName: str, property: DTNodeProperty):
        convertedPropertyName = convertName(propertyName)
        self.fileHandle.write(f"#define DT_NODE_{nodePath}_PROPERTY_{convertedPropertyName}   {property.value}\n")


    def generateIntArrayPropertyMacros(self, nodePath: str, propertyName: str, property: DTNodeProperty):
        convertedPropertyName = convertName(propertyName)
        self.fileHandle.write(f"#define DT_NODE_{nodePath}_PROPERTY_{convertedPropertyName}_LENGTH   {len(property.value)}\n")

        for i, prop in enumerate(property.value):
            self.fileHandle.write(f"#define DT_NODE_{nodePath}_PROPERTY_{convertedPropertyName}_{i}   {prop}\n")


    def generatePhandleArrayPropertyMacros(self, nodePath: str, propertyName: str, property: DTNodeProperty):
        raise Exception("Not implemented")


    def generatePhandlePropertyMacros(self, nodePath: str, propertyName: str, property: DTNodeProperty):
        convertedPropertyName = convertName(propertyName)
        self.fileHandle.write(f"#define DT_NODE_{nodePath}_PROPERTY_{convertedPropertyName} DT_LABEL_{property.value}\n")


    def generateMultiplePhandlesPropertyMacros(self, nodePath: str, propertyName: str, property: DTNodeProperty):
        convertedPropertyName = convertName(propertyName)
        self.fileHandle.write(f"#define DT_NODE_{nodePath}_PROPERTY_{convertedPropertyName}_LENGTH   {len(property.value)}\n")

        for i, prop in enumerate(property.value):
            self.fileHandle.write(f"#define DT_NODE_{nodePath}_PROPERTY_{convertedPropertyName}_{i} DT_LABEL_{prop}\n")


    def generateBooleanArrayPropertyMacros(self, nodePath: str, propertyName: str, property: DTNodeProperty):
        convertedPropertyName = convertName(propertyName)
        self.fileHandle.write(f"#define DT_NODE_{nodePath}_PROPERTY_{convertedPropertyName}   {property.value}\n")


    # TODO: if 'reg', then do generateRegArray
    # TODO: remove '#', '?', ',', '.' from property name
    # TODO: convert property name
    # TODO: switch on type
    def generatePropertyMacros(self, nodePath: str, propertyName: str, property: DTNodeProperty):
    
        if propertyName == "reg":
            self.generateRegMacros(nodePath)
            return
        elif propertyName == "compatible":
            self.generateStringArrayPropertyMacros(nodePath, "compatible", property)
            return
        elif propertyName == "interrupts":
            if not self.currentDeviceTreeNode.hasProperty("interrupt-parent"):
                raise Exception(f"Device tree node '{self.currentDeviceTreeNode.name}' has property 'interrupts' but no corresponding property 'interrupt-parent'")
            
            interruptParentPhandle = self.currentDeviceTreeNode.getProperty("interrupt-parent").value
            interruptParentNode = self.deviceTree.labels[interruptParentPhandle]

            if not interruptParentNode.hasProperty("interrupt-controller"):
                raise Exception(f"Device tree node '{self.currentDeviceTreeNode.name}' has 'interrupt-parent' property that points to node '{interruptParentNode.name}' which does not have 'interrupt-controller' property")

            if not interruptParentNode.hasProperty("#interrupt-cells"):
                raise Exception(f"Interrupt controller node '{interruptParentNode.name}' does not have '#interrupt-cells' property")
            
            interruptCells = int(interruptParentNode.getProperty("#interrupt-cells").value)
            self.generateInterrupts(nodePath, interruptCells, property)
            return


        if property.type == DTNodePropertyType.STRING:
            self.generateStringPropertyMacros(nodePath, propertyName, property)

        elif property.type == DTNodePropertyType.STRING_ARRAY:
            self.generateStringArrayPropertyMacros(nodePath, propertyName, property)

        elif property.type == DTNodePropertyType.INT:
            self.generateIntPropertyMacros(nodePath, propertyName, property)

        elif property.type == DTNodePropertyType.INT_ARRAY:
            self.generateIntArrayPropertyMacros(nodePath, propertyName, property)

        elif property.type == DTNodePropertyType.BYTE_ARRAY:
            pass

        elif property.type == DTNodePropertyType.PHANDLE:
            self.generatePhandlePropertyMacros(nodePath, propertyName, property)

        elif property.type == DTNodePropertyType.PHANDLE_ARRAY:
            self.generatePhandleArrayPropertyMacros(nodePath, propertyName, property)

        elif property.type == DTNodePropertyType.MULTI_PHANDLES:
            self.generateMultiplePhandlesPropertyMacros(nodePath, propertyName, property)

        elif property.type == DTNodePropertyType.BOOLEAN:
            self.generateBooleanArrayPropertyMacros(nodePath, propertyName, property)




    def generateNode(self):
        commentStr = f"// properties for device tree '{self.currentDeviceTreeNode.name}"
        if self.currentDeviceTreeNode.unitAddress is not None:
            commentStr += f"@{self.currentDeviceTreeNode.unitAddress}"
        commentStr += "' node\n"
        self.fileHandle.write(commentStr)

        nodePath = self.partialPath + "_" + convertName(self.currentDeviceTreeNode.name)
        if self.currentDeviceTreeNode.unitAddress is not None:
            nodePath += "_" + self.currentDeviceTreeNode.unitAddress

        self.currentDeviceTreeNode.partialPath = nodePath

        self.fileHandle.write(f"#define DT_NODE_{nodePath}_PARENT   DT_NODE_{self.partialPath}\n")

        for propertyName in self.currentDeviceTreeNode.properties.keys():
            property = self.currentDeviceTreeNode.properties[propertyName]
            self.generatePropertyMacros(nodePath, propertyName, property)

        # TODO: Generate instances
        # TODO: Allow for multiple compatibles
        # add reference to current device tree node only if this node is active (status = "okay")
        if self.currentDeviceTreeNode.hasProperty("compatible") and self.currentDeviceTreeNode.hasProperty("status"):
            compatibleProperty = self.currentDeviceTreeNode.getProperty("compatible").value[0]
            status = self.currentDeviceTreeNode.getProperty("status").value
            if status == "okay":
                if compatibleProperty not in self.activeDevices.keys():
                    self.activeDevices[compatibleProperty] = set()

                self.activeDevices[compatibleProperty].add(self.currentDeviceTreeNode)


        self.fileHandle.write("\n\n")

        for subNode in self.currentDeviceTreeNode.children:
            partialPathSave = self.partialPath
            self.partialPath = nodePath

            if self.currentDeviceTreeNode.unitAddress is not None:
                self.partialPath += "_" + self.currentDeviceTreeNode.unitAddress

            currentDeviceTreeNodeSave = self.currentDeviceTreeNode
            self.currentDeviceTreeNode = subNode

            self.generateNode()

            self.currentDeviceTreeNode = currentDeviceTreeNodeSave
            self.partialPath = partialPathSave


    def generateRootNode(self):
        self.currentDeviceTreeNode = self.deviceTree.root
        self.fileHandle.write("// properties for device tree '/' node\n")

        nodePath = "root"
        self.currentDeviceTreeNode.partialPath = nodePath
        self.fileHandle.write(f"#define DT_NODE_{nodePath}_PARENT\n")

        for propertyName in self.currentDeviceTreeNode.properties.keys():
            property = self.currentDeviceTreeNode.properties[propertyName]
            self.generatePropertyMacros(nodePath, propertyName, property)


        self.fileHandle.write("\n\n")

        for subNode in self.currentDeviceTreeNode.children:
            self.partialPath = nodePath

            currentDeviceTreeNodeSave = self.currentDeviceTreeNode
            self.currentDeviceTreeNode = subNode

            self.generateNode()

            self.currentDeviceTreeNode = currentDeviceTreeNodeSave
            self.partialPath = ""



    def generateLabels(self):
        
        self.fileHandle.write("// labels\n")

        for label in self.deviceTree.labels.keys():
            partialNodePath = self.deviceTree.labels[label].partialPath
            self.fileHandle.write(f"#define DT_LABEL_{label}   DT_NODE_{partialNodePath}\n")


    def generateAliases(self):
        
        for aliasName in self.deviceTree.aliases.keys():
            convertedAliasName = convertName(aliasName)
            property = self.deviceTree.aliases[aliasName]
            if property.type == DTNodePropertyType.PHANDLE:
                phandle = property.value
                self.fileHandle.write(f"#define DT_ALIAS_{convertedAliasName}   DT_LABEL_{phandle}\n")
            elif property.type == DTNodePropertyType.STRING:
                string = property.value
                self.fileHandle.write(f"#define DT_ALIAS_{convertedAliasName}   \"{string}\"\n")

    def generateChosen(self):
        
        for chosenName in self.deviceTree.chosen.keys():
            convertedChosenName = convertName(chosenName)
            property = self.deviceTree.chosen[chosenName]
            if property.type == DTNodePropertyType.PHANDLE:
                phandle = property.value
                self.fileHandle.write(f"#define DT_CHOSEN_{convertedChosenName}   DT_LABEL_{phandle}\n")
            elif property.type == DTNodePropertyType.STRING:
                string = property.value
                self.fileHandle.write(f"#define DT_CHOSEN_{convertedChosenName}   \"{string}\"\n")


    def generateIncludedMakefile(self):
        raise Exception("Not implemented")


    def generateInstances(self):

        for compatible in self.activeDevices.keys():
            convertedCompatible = convertName(compatible)

            self.fileHandle.write(f"#define DT_COMPATIBLE_{convertedCompatible}_NUM_INSTANCES   {len(self.activeDevices[compatible])}\n")

            for i, instance in enumerate(self.activeDevices[compatible]):
                nodePath = instance.partialPath
                self.fileHandle.write(f"#define DT_COMPATIBLE_{convertedCompatible}_INSTANCE_{i}   DT_NODE_{nodePath}\n")


    def generateIncludeGuardTop(self):
        outputFileName = self.outputFilePath.split("/")
        includeGuardMacro = ""
        for letter in outputFileName[-1]:
            if letter == "-" or letter == ".":
                includeGuardMacro += "_"
            elif letter.isalnum():
                includeGuardMacro += letter.upper()
            else:
                includeGuardMacro += letter
        
        self.includeGuardMacro = includeGuardMacro

        self.fileHandle.write(f"#ifndef {self.includeGuardMacro}\n")
        self.fileHandle.write(f"#define {self.includeGuardMacro}\n")



    def generateIncludeGuardBottom(self):
        self.fileHandle.write(f"#endif // {self.includeGuardMacro}\n")


    # TODO: write comment at top stating that it is auto-generated and not to modify and to see devicetree/compiler for implementation
    # TODO: write include guard
    # TODO: call generateRootNode (will recursively call generateNode)
    # TODO: call generateLabels
    # TODO: call generateAliases
    # TODO: call generateChosen
    # TODO: call generateIncludedMakefile
    # TODO: (later) call generateConfigFile
    def generateDatabase(self):
        self.fileHandle = open(self.outputFilePath, "w")

        self.fileHandle.write("// THIS FILE IS AUTO-GENERATED. DO NOT EDIT\n")
        self.fileHandle.write("// See devicetree/compiler directory for implementation\n")
        self.generateIncludeGuardTop()

        self.fileHandle.write("\n\n")
        self.generateRootNode()
        self.fileHandle.write("\n\n")

        self.generateLabels()
        self.fileHandle.write("\n\n")

        self.generateInstances()
        self.fileHandle.write("\n\n")

        self.generateChosen()
        self.fileHandle.write("\n\n")

        self.generateAliases()
        self.fileHandle.write("\n\n")

        self.generateIncludeGuardBottom()
        self.fileHandle.close()



