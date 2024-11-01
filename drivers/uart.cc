
#include "device_driver_subsystem.h"
#include "xc.h"
#include "uart.h"
#include "hardware.h"


extern driver_table_t driver_table;


BEGIN_DRIVER(uart)

uart_cb_t uart_control_block;


// TODO: change this to be better than it is. wont work with other hardware
// or different vector number. need some kind of hardware manifest
// maps UART numbers to ISR vector numbers
int vector_numbers[] = {
    24,
    32,
    31,
    49,
    51,
    50
};


static void set_uart_on_or_off(int device_number, int is_on)
{
    switch (device_number)
    {
    case 1:
        U1MODEbits.ON = is_on;
        break;
    
    case 2:
        U2MODEbits.ON = is_on;
        break;
    
    case 3:
        U3MODEbits.ON = is_on;
        break;
    
    case 4:
        U4MODEbits.ON = is_on;
        break;
    
    case 5:
        U5MODEbits.ON = is_on;
        break;
    
    case 6:
        U6MODEbits.ON = is_on;
        break;
        
    
    default:
        break;
    }
}


static void set_hardware_flow_control(int device_number, int on)
{
    if(on != 0 && on != 1)
        return;

    switch (device_number)
    {
    case 1:
        U1MODEbits.UEN = on << 1;
        break;
    
    case 2:
        U2MODEbits.UEN = on << 1;
        break;
    
    case 3:
        U3MODEbits.UEN = on << 1;
        break;

    case 4:
        U4MODEbits.UEN = on << 1;
        break;

    case 5:
        U5MODEbits.UEN = on << 1;
        break;
    
    case 6:
        U6MODEbits.UEN = on << 1;
        break;
    
    default:
        break;
    }
}

void set_uart_baud(int device_number, unsigned int baud)
{
    int pb_freq = get_peripheral_bus_frequency();


    /*
     * This section determines the pre-scaling factor
     * for the baud rate generator.
     */
    int brgh_high = pb_freq/(4*baud) - 1;
    int brgh_low = pb_freq/(16*baud) - 1;
    int use_high;
    int brgh;

    if(brgh_low < 1 && brgh_low < 1)
    {
        return;
    }
    else if(brgh_high > 0xffff && brgh_low > 0xffff)
    {
        return;
    }
    else if(brgh_high > 0xffff)
    {
        use_high = 0;
        brgh = 16;
    }
    else if(brgh_low < 1)
    {
        use_high = 1;
        brgh = 4;
    }
    else
    {
        use_high = 1;
        brgh = 4;
    }




    switch (device_number)
    {
    case 1:
        U1MODEbits.BRGH = use_high ? 1 : 0;
        U1BRG = pb_freq/(brgh*baud) - 1;
        break;
    
    case 2:
        U2MODEbits.BRGH = use_high ? 1 : 0;
        U2BRG = pb_freq/(brgh*baud) - 1;
        break;
    
    case 3:
        U3MODEbits.BRGH = use_high ? 1 : 0;
        U3BRG = pb_freq/(brgh*baud) - 1;
        break;

    case 4:
        U4MODEbits.BRGH = use_high ? 1 : 0;
        U4BRG = pb_freq/(brgh*baud) - 1;
        break;

    case 5:
        U5MODEbits.BRGH = use_high ? 1 : 0;
        U5BRG = pb_freq/(brgh*baud) - 1;
        break;
    
    case 6:
        U6MODEbits.BRGH = use_high ? 1 : 0;
        U6BRG = pb_freq/(brgh*baud) - 1;
        break;
    
    default:
        break;
    }
}


void set_uart_parity_and_length(int device_number, int parity, int length)
{
    // bit pattern for configuring parity and length of uart transmission
    int bit_pattern;

    if(parity == NO_PARITY && length == UART_9_BITS)
    {
        bit_pattern = 0b11;
    }
    else if(parity == ODD_PARITY && length == UART_8_BITS)
    {
        bit_pattern = 0b10;
    }
    else if(parity == EVEN_PARITY && length == UART_8_BITS)
    {
        bit_pattern = 0b01;
    }
    else if(parity == NO_PARITY && length == UART_8_BITS)
    {
        bit_pattern = 0b00;
    }


    switch (device_number)
    {
    case 1:
        U1MODEbits.PDSEL = bit_pattern;
        break;
    
    case 2:
        U2MODEbits.PDSEL = bit_pattern;
        break;

    case 3:
        U3MODEbits.PDSEL = bit_pattern;
        break;

    case 4:
        U4MODEbits.PDSEL = bit_pattern;
        break;

    case 5:
        U5MODEbits.PDSEL = bit_pattern;
        break;

    case 6:
        U6MODEbits.PDSEL = bit_pattern;
        break;
    
    default:
        break;
    }
}

set_uart_stop_bits(int device_number, int stop_bits)
{
    int bit = (stop_bits == ONE_STOP_BIT) ? 0 : 1;

    switch (device_number)
    {
    case 1:
        U1MODEbits.STSEL = bit;
        break;
    
    case 2:
        U2MODEbits.STSEL = bit;
        break;

    case 3:
        U3MODEbits.STSEL = bit;
        break;

    case 4:
        U4MODEbits.STSEL = bit;
        break;

    case 5:
        U5MODEbits.STSEL = bit;
        break;

    case 6:
        U6MODEbits.STSEL = bit;
        break;
    
    default:
        break;
    }
}


void enable_uart_interrupts(int device_number)
{
    switch (device_number)
    {
    case 1:
        IEC0bits.U1EIE = 1;
        IEC0bits.U1RXIE = 1;
        IEC0bits.U1TXIE = 1;
        break;
    
    case 2:
        IEC1bits.U2AEIE = 1;
        IEC1bits.U2ARXIE = 1;
        IEC1bits.U2ATXIE = 1;
        break;
    
    case 3:
        IEC1bits.U3AEIE = 1;
        IEC1bits.U3ARXIE = 1;
        IEC1bits.U3ATXIE = 1;
        break;
    
    case 4:
        IEC2bits.U4EIE = 1;
        IEC2bits.U4RXIE = 1;
        IEC2bits.U4TXIE = 1;
        break;
    
    case 5:
        IEC2bits.U5EIE = 1;
        IEC2bits.U5RXIE = 1;
        IEC2bits.U5TXIE = 1;
        break;
    
    case 6:
        IEC2bits.U6EIE = 1;
        IEC2bits.U6RXIE = 1;
        IEC2bits.U6TXIE = 1;
        break;
    
    default:
        break;
    }
}


void disable_uart_interrupts(int device_number)
{
    switch (device_number)
    {
    case 1:
        IEC0bits.U1EIE = 0;
        IEC0bits.U1RXIE = 0;
        IEC0bits.U1TXIE = 0;
        break;
    
    case 2:
        IEC1bits.U2AEIE = 0;
        IEC1bits.U2ARXIE = 0;
        IEC1bits.U2ATXIE = 0;
        break;
    
    case 3:
        IEC1bits.U3AEIE = 0;
        IEC1bits.U3ARXIE = 0;
        IEC1bits.U3ATXIE = 0;
        break;
    
    case 4:
        IEC2bits.U4EIE = 0;
        IEC2bits.U4RXIE = 0;
        IEC2bits.U4TXIE = 0;
        break;
    
    case 5:
        IEC2bits.U5EIE = 0;
        IEC2bits.U5RXIE = 0;
        IEC2bits.U5TXIE = 0;
        break;
    
    case 6:
        IEC2bits.U6EIE = 0;
        IEC2bits.U6RXIE = 0;
        IEC2bits.U6TXIE = 0;
        break;
    
    default:
        break;
    }
}


void configure_uart_interrupts(int device_number)
{
    switch (device_number)
    {
    case 1:
        // configure UART 1 transmit and receive interrupts
        U1STAbits.UTXISEL = 0b01;
        U1STAbits.URXISEL = 0b01;
        break;

    case 2:
        // configure UART 2 transmit and receive interrupts
        U2STAbits.UTXISEL = 0b01;
        U2STAbits.URXISEL = 0b01;
        break;

    case 3:
        // configure UART 3 transmit and receive interrupts
        U3STAbits.UTXISEL = 0b01;
        U3STAbits.URXISEL = 0b01;
        break;

    case 4:
        // configure UART 4 transmit and receive interrupts
        U4STAbits.UTXISEL = 0b01;
        U4STAbits.URXISEL = 0b01;
        break;

    case 5:
        // configure UART 5 transmit and receive interrupts
        U5STAbits.UTXISEL = 0b01;
        U5STAbits.URXISEL = 0b01;
        break;

    case 6:
        // configure UART 6 transmit and receive interrupts
        U6STAbits.UTXISEL = 0b01;
        U6STAbits.URXISEL = 0b01;
        break;
    
    default:
        break;
    }
}


void enable_pins(int device_number)
{
    switch (device_number)
    {
    case 1:
        U1STAbits.URXEN = 1;
        U1STAbits.UTXEN = 1;
        break;

    case 2:
        U2STAbits.URXEN = 1;
        U2STAbits.UTXEN = 1;
        break;

    case 3:
        U3STAbits.URXEN = 1;
        U3STAbits.UTXEN = 1;
        break;

    case 4:
        U4STAbits.URXEN = 1;
        U4STAbits.UTXEN = 1;
        break;

    case 5:
        U5STAbits.URXEN = 1;
        U5STAbits.UTXEN = 1;
        break;
    
    case 6:
        U6STAbits.URXEN = 1;
        U6STAbits.UTXEN = 1;
        break;
    
    default:
        break;
    }
}

void disable_pins(int device_number)
{
    switch (device_number)
    {
    case 1:
        U1STAbits.URXEN = 0;
        U1STAbits.UTXEN = 0;
        break;

    case 2:
        U2STAbits.URXEN = 0;
        U2STAbits.UTXEN = 0;
        break;

    case 3:
        U3STAbits.URXEN = 0;
        U3STAbits.UTXEN = 0;
        break;

    case 4:
        U4STAbits.URXEN = 0;
        U4STAbits.UTXEN = 0;
        break;

    case 5:
        U5STAbits.URXEN = 0;
        U5STAbits.UTXEN = 0;
        break;
    
    case 6:
        U6STAbits.URXEN = 0;
        U6STAbits.UTXEN = 0;
        break;
    
    default:
        break;
    }
}


int set_isr_vector(int driver_type, int device_number)
{
    if(driver_table.isr_vector_to_major_minor[vector_numbers[device_number]] != 0)
    {
        return 1;
    }

    driver_table.isr_vector_to_major_minor[vector_numbers[device_number]] = (driver_type << 3) | device_number;

    return 0;
}


int get_data(int device_number)
{
    unsigned int data;

    switch (device_number)
    {
    case 1:
        while(U1RX)
        break;
    
    default:
        break;
    }
}


int __open__(int device_number, uart_options_t *options)
{
    // check if shared ISR vector already in use and if so, return error
    if(set_isr_vector(DRIVER_TYPE_UART, device_number))
        return 1

    // sets the uart on and marks device file as open
    set_uart_open(&uart_control_block, device_number);
    set_uart_on_or_off(device_number, 1);

    // configures baud, parity, length, stop bits, and hardware flow control
    set_hardware_flow_control(device_number, options->hardware_flow_control);
    set_uart_baud(device_number, options->baud);
    set_uart_parity_and_length(device_number, options->parity, options->size);
    set_uart_stop_bits(device_number, options->stop_bits);

    // configures interrupts
    configure_uart_interrupts(device_number);
    enable_uart_interrupts(device_number);

    // enable RX and TX pins
    enable_pins(device_number);

    return 0;
}


void __close__(int device_number)
{
    set_uart_closed(&uart_control_block, device_number);
    set_uart_on_or_off(device_number, 0);
    disable_pins(device_number);
    disable_uart_interrupts(device_number);
}


int __read__(int device_number, void *buffer, unsigned short size)
{
    // move from ring buffer to task buffer
    // return amount read
}

int __write__(int device_number, void *buffer, unsigned short size)
{
    // TODO 
}


int __init__(int *device_numbers)
{
    // initialize ring buffers
    for(int i = 0; i < NUM_UARTS; i++)
    {
        ring_buffer_init(&uart_control_block.read_buffers[i], uart_control_block.read_buffer_size);
        ring_buffer_init(&uart_control_block.write_buffers[i], uart_control_block.write_buffer_size);
    }


}


void __error__(int device_number)
{
    // TODO
}

void __transmit__(int device_number)
{
    // TODO
}

void __receive__(int device_number)
{
    int data = get_data(device_number, uart_control_block.read_buffers[device_number]);
}



// TODO: make table of ISR callbacks and move ISRs to other file
// also read section in book on ISRs
    // table mapping ISR vector number to major and minor number of file using ISR since some devices share ISR vectors
    // table is added to when device is opened 
    // table is checked for open file somehow
    // separate table mapping major and minor numbers to ISRs






END_DRIVER(uart)