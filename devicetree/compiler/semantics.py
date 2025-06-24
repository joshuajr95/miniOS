

from tokenizer import TokenType
from parser import ParseTreeNode, NodeType, findFirstSubNodeByType, findSubNodeListByType, findSubNodeListByTypeAndFilter



'''
Call this function on nodes of type NODE_DEFINITION
'''
def checkNodeDefinition(node: ParseTreeNode):
    
    addressNodeList = findSubNodeListByType(node, NodeType.PARSE_TREE_NODE_TYPE_NODE_ADDRESS)
    regNodeList = findRegProperty(node)

    if len(addressNodeList) > 1:
        raise Exception("More than 1 addresses in device tree node definition.")
    
    if len(regNodeList) > 1:
        raise Exception("More than 1 reg properties in device tree node definition.")

    if len(addressNodeList) == 1:
        addressNode = addressNodeList[0]

        if len(regNodeList) != 1:
            raise Exception("No matching reg property for address after @ in node definition.")
        
        regNode = regNodeList[0]
        
        address = addressNode.children[1].terminal.value

        regAddress = regNode


'''
Callback table for semantic checking. The indices
into the table correspond to node types.
'''
callbacks = {
    PARSE_TREE_NODE_TYPE_NODE_DEFINITION: 
}