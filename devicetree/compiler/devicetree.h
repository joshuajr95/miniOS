/**
 * API to the Device Tree macro database
 */


#include "devicetree_database.h"


/**
 * These macros perform concatenation of tokens for
 * device tree macro database manipulation. However,
 * the token-pasting operator (##) inhibits expansion
 * of sub-macros, so we need the DT_CONCAT* macros since
 * the arguments will be fully macro expanded before
 * being concatenated
 */
#define CONCAT(_a, _b) _a ## _b
#define CONCAT3(_a, _b, _c) _a ## _b ## _c
#define CONCAT4(_a, _b, _c, _d) _a ## _b ## _c ## _d
#define CONCAT5(_a, _b, _c, _d, _e) _a ## _b ## _c ## _d ## _e
#define CONCAT6(_a, _b, _c, _d, _e, _f) _a ## _b ## _c ## _d ## _e ## _f

#define DT_CONCAT2(_a, _b) CONCAT(_a, _b)
#define DT_CONCAT3(_a, _b, _c) CONCAT3(_a, _b, _c)
#define DT_CONCAT4(_a, _b, _c, _d) CONCAT4(_a, _b, _c, _d)
#define DT_CONCAT5(_a, _b, _c, _d, _e) CONCAT5(_a, _b, _c, _d, _e)
#define DT_CONCAT6(_a, _b, _c, _d, _e, _f) CONCAT6(_a, _b, _c, _d, _e, _f)




/**
 * API Functions
 */
#define DEVICETREE_GET_PARENT(_node) DT_CONCAT2(_node, _PARENT)
#define DEVICETREE_PROPERTY(_node, _property) DT_CONCAT3(_node, _PROPERTY_, _property)


#define DEVICETREE_CHOSEN(_chosen) DT_CONCAT2(DT_CHOSEN_, _chosen)
#define DEVICETREE_ALIAS(_alias) DT_CONCAT2(DT_ALIAS_, _alias)
#define DEVICETREE_NODE(_nodepath) DT_CONCAT2(DT_NODE_, _nodepath)
#define DEVICETREE_LABEL(_label) DT_CONCAT2(DT_LABEL_, _label)
#define DEVICETREE_LABEL_TO_DEVICE_NAME(_label) # _label



#define DEVICETREE_GET_STATUS(_node) DEVICETREE_PROPERTY(_node, status)

#define DEVICETREE_GET_NUM_REGS(_node) DT_CONCAT2(_node, _PROPERTY_reg_LENGTH)
#define DEVICETREE_GET_REG_ADDRESS_BY_INDEX(_node, _index) DT_CONCAT4(_node, _PROPERTY_reg_, _index, _address)
#define DEVICETREE_GET_REG_SIZE_BY_INDEX(_node, _index) DT_CONCAT4(_node, _PROPERTY_reg_, _index, _size)

#define DEVICETREE_GET_REG_ADDRESS(_node) DEVICETREE_GET_REG_ADDRESS_BY_INDEX(_node, 0)
#define DEVICETREE_GET_REG_SIZE(_node) DEVICETREE_GET_REG_SIZE_BY_INDEX(_node, 0)

#define DEVICETREE_GET_INTERRUPT_NUMBER(_node, _index)  DT_CONCAT4(_node, _PROPERTY_interrupts_, _index, _0) 
#define DEVICETREE_GET_INTERRUPT_FLAGS(_node, _index)   DT_CONCAT4(_node, _PROPERTY_interrupts_, _index, _1)
#define DEVICETREE_GET_INTERRUPT_PARENT(_node) DT_CONCAT2(_node, _PROPERTY_interrupt_parent)
