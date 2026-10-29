

#include "devicetree.h"


#define UART_MODE_REGISTER_OFFSET 0
#define UART_STATUS_REGISTER_OFFSET 0x10
#define UART_TXREG_REGISTER_OFFSET 0x20
#define UART_RXREG_REGISTER_OFFSET 0x30
#define UART_BRG_REGISTER_OFFSET 0x40



void write_register(void *address, unsigned int data);


static void *UART_registers_base_address = DEVICETREE_GET_REG_ADDRESS(DEVICETREE_LABEL(uart2));
static unsigned int UART_registers_size = DEVICETREE_GET_REG_SIZE(DEVICETREE_LABEL(uart2));
const char *dev_name = DEVICETREE_LABEL_TO_DEVICE_NAME(uart2);



static int UART_write_register(unsigned int offset, unsigned int data)
{
    void *address = UART_registers_base_address + offset;

    if(address + 4 > UART_registers_base_address + UART_registers_size)
    {
        return -1;
    }

    write_register(address, data);

    return 0;
}




