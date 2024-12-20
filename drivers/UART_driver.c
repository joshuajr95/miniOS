#include "UART_Driver.h"
#include "UART_HAL.h"
#include "NT7603_Driver.h"

#include <stdbool.h>
#include <stddef.h>
#include <sys/attribs.h>
#include <proc/PIC32MX/p32mx795f512l.h>


/**
 * @author Joshua Jacobs-Rebhun
 */


#define UART_RECEIVE_BUFFER_SIZE 64

#define UART1_TABLE_INDEX UART1-1
#define UART2_TABLE_INDEX UART2-1
#define UART3_TABLE_INDEX UART3-1
#define UART4_TABLE_INDEX UART4-1
#define UART5_TABLE_INDEX UART5-1


/***************************************
 * Ring Buffer Implementation for UART *
 ***************************************/


/**
 * @typedef ring_buffer_t
 *
 * Ring buffer implementation.
 */
typedef struct {
    
    /**
     * Actual buffer of data.
     */
    uint8_t data[UART_RECEIVE_BUFFER_SIZE];
    
    /**
     * Number of bytes written to the
     * ring buffer. This modulo UART_RECEIVE_BUFFER_SIZE
     * gives the index of the next byte of data to write.
     */
    uint32_t write_ptr;
    
    /**
     * Number of bytes read from the
     * ring buffer. This modulo UART_RECEIVE_BUFFER_SIZE
     * gives the index of the next byte of data to read.
     */
    uint32_t read_ptr;
    
    
} ring_buffer_t;


#define READ_INDEX(_ring_buffer)    \
    ((_ring_buffer)->read_ptr%UART_RECEIVE_BUFFER_SIZE)


#define WRITE_INDEX(_ring_buffer)   \
    ((_ring_buffer)->write_ptr%UART_RECEIVE_BUFFER_SIZE)

#define NUM_BYTES(_ring_buffer)     \
    (_ring_buffer->write_ptr-_ring_buffer->read_ptr)




typedef struct
{
    /**
     * Callback function for
     * receive interrupt.
     */
    uart_receive_callback_t callback_function;

    /**
     * Number of bytes to receive before
     * triggering callback function.
     */
    uint32_t bytes_to_trigger;

    /**
     * Number of bytes currently in
     * the receive buffer. When this
     * equals bytes_to_trigger, the
     * callback function will be invoked.
     */
    uint32_t current_bytes;


    /**
     * Buffer of data to be received.
     */
    void *receive_buffer;
    
    
    /**
     * Size of each receive buffer in bytes.
     */
    uint32_t buffer_size;

    /**
     * Whether the callback is enabled.
     * Callbacks can be disabled at request
     * of other OS modules. If false,
     * the callback will not be invoked.
     */
    bool is_enabled;

    /**
     * Whether the callback should be
     * repeatedly called. If so, when
     * the callback is invoked, the
     * current number of bytes is reset
     * to 0. If not, is_enabled is
     * set to false upon callback invocation.
     */
    bool is_repeated;
    
} uart_callback_table_entry_t;



//ring_buffer_t uart_receive_buffers[NUM_UART_DEVS];


/**
 * UART callback table. This is where callback functions are
 * installed when UART_register_receive_callback is invoked.
 */
static uart_callback_table_entry_t callback_table[NUM_UART_DEVS];
static uart_device_config_t device_config_table[NUM_UART_DEVS];
static uart_driver_config_t driver_config;




/***************************
 * Static Helper Functions *
 ***************************/


static void UART_configure_hw_baud_regs(uart_device_number_t device_number, uint32_t baud)
{
    int uart_brg;
    
    UART_SET_M_DIVISOR_4(UART2);
    uart_brg = (PERIPHERAL_FREQ/(4*baud)) - 1;
    UART_SET_BAUD_RATE_GENERATOR(UART2, uart_brg);
}


static int UART_set_UART1_config(uart_device_config_t *config)
{
    // need to set it in device config table and in HW registers
    device_config_table[UART1_TABLE_INDEX].baud = config->baud;
    
    
    if(config->data_size == UART_DATA_NINE_BITS)
    {   
        UART_SET_DATA_LENGTH_9_BITS_NO_PARITY(UART1);
    }
    else if(config->data_size == UART_DATA_EIGHT_BITS)
    {
        switch(config->parity)
        {
            case UART_PARITY_EVEN:
                UART_SET_DATA_LENGTH_8_BITS_EVEN_PARITY(UART1);
                break;

            case UART_PARITY_ODD:
                UART_SET_DATA_LENGTH_8_BITS_ODD_PARITY(UART1);
                break;
                
            case UART_PARITY_NONE:
                UART_SET_DATA_LENGTH_8_BITS_NO_PARITY(UART1);
                break;
                
            default:
                break;
        }
    }
    
    
    // configure stop bits
    switch(config->stop_bits)
    {
        case ONE_STOP_BIT:
            UART_SET_ONE_STOP_BIT(UART1);
            break;

        case TWO_STOP_BITS:
            UART_SET_TWO_STOP_BITS(UART1);
            break;

        default:
            break;
    }


    // configure HW flow control
    if(config->enable_hw_flow_control)
    {
        UART_ENABLE_HW_FLOW_CONTROL(UART1);
    }
    else
    {
        UART_DISABLE_HW_FLOW_CONTROL(UART1);
    }


    return UART_ERROR_NONE;
}


static int UART_set_UART2_config(uart_device_config_t *config)
{
    // need to set it in device config table and in HW registers
    device_config_table[UART2_TABLE_INDEX].baud = config->baud;
    
    
    if(config->data_size == UART_DATA_NINE_BITS)
    {   
        UART_SET_DATA_LENGTH_9_BITS_NO_PARITY(UART2);
    }
    else if(config->data_size == UART_DATA_EIGHT_BITS)
    {
        switch(config->parity)
        {
            case UART_PARITY_EVEN:
                UART_SET_DATA_LENGTH_8_BITS_EVEN_PARITY(UART2);
                break;

            case UART_PARITY_ODD:
                UART_SET_DATA_LENGTH_8_BITS_ODD_PARITY(UART2);
                break;
                
            case UART_PARITY_NONE:
                UART_SET_DATA_LENGTH_8_BITS_NO_PARITY(UART2);
                break;
                
            default:
                break;
        }
    }
    
    
    // configure stop bits
    switch(config->stop_bits)
    {
        case ONE_STOP_BIT:
            UART_SET_ONE_STOP_BIT(UART2);
            break;

        case TWO_STOP_BITS:
            UART_SET_TWO_STOP_BITS(UART2);
            break;

        default:
            break;
    }


    // configure HW flow control
    if(config->enable_hw_flow_control)
    {
        UART_ENABLE_HW_FLOW_CONTROL(UART2);
    }
    else
    {
        UART_DISABLE_HW_FLOW_CONTROL(UART2);
    }


    return UART_ERROR_NONE;
}


static int UART_set_UART3_config(uart_device_config_t *config)
{
    // need to set it in device config table and in HW registers
    device_config_table[UART3_TABLE_INDEX].baud = config->baud;
    
    
    if(config->data_size == UART_DATA_NINE_BITS)
    {   
        UART_SET_DATA_LENGTH_9_BITS_NO_PARITY(UART3);
    }
    else if(config->data_size == UART_DATA_EIGHT_BITS)
    {
        switch(config->parity)
        {
            case UART_PARITY_EVEN:
                UART_SET_DATA_LENGTH_8_BITS_EVEN_PARITY(UART3);
                break;

            case UART_PARITY_ODD:
                UART_SET_DATA_LENGTH_8_BITS_ODD_PARITY(UART3);
                break;
                
            case UART_PARITY_NONE:
                UART_SET_DATA_LENGTH_8_BITS_NO_PARITY(UART3);
                break;
                
            default:
                break;
        }
    }
    
    
    // configure stop bits
    switch(config->stop_bits)
    {
        case ONE_STOP_BIT:
            UART_SET_ONE_STOP_BIT(UART3);
            break;

        case TWO_STOP_BITS:
            UART_SET_TWO_STOP_BITS(UART3);
            break;

        default:
            break;
    }


    // configure HW flow control
    if(config->enable_hw_flow_control)
    {
        UART_ENABLE_HW_FLOW_CONTROL(UART3);
    }
    else
    {
        UART_DISABLE_HW_FLOW_CONTROL(UART3);
    }


    return UART_ERROR_NONE;
}


static int UART_set_UART4_config(uart_device_config_t *config)
{
    // need to set it in device config table and in HW registers
    device_config_table[UART4_TABLE_INDEX].baud = config->baud;
    
    
    if(config->data_size == UART_DATA_NINE_BITS)
    {   
        UART_SET_DATA_LENGTH_9_BITS_NO_PARITY(UART4);
    }
    else if(config->data_size == UART_DATA_EIGHT_BITS)
    {
        switch(config->parity)
        {
            case UART_PARITY_EVEN:
                UART_SET_DATA_LENGTH_8_BITS_EVEN_PARITY(UART4);
                break;

            case UART_PARITY_ODD:
                UART_SET_DATA_LENGTH_8_BITS_ODD_PARITY(UART4);
                break;
                
            case UART_PARITY_NONE:
                UART_SET_DATA_LENGTH_8_BITS_NO_PARITY(UART4);
                break;
                
            default:
                break;
        }
    }
    
    
    // configure stop bits
    switch(config->stop_bits)
    {
        case ONE_STOP_BIT:
            UART_SET_ONE_STOP_BIT(UART4);
            break;

        case TWO_STOP_BITS:
            UART_SET_TWO_STOP_BITS(UART4);
            break;

        default:
            break;
    }


    return UART_ERROR_NONE;
}


static int UART_set_UART5_config(uart_device_config_t *config)
{
    // need to set it in device config table and in HW registers
    device_config_table[UART5_TABLE_INDEX].baud = config->baud;
    
    
    if(config->data_size == UART_DATA_NINE_BITS)
    {   
        UART_SET_DATA_LENGTH_9_BITS_NO_PARITY(UART5);
    }
    else if(config->data_size == UART_DATA_EIGHT_BITS)
    {
        switch(config->parity)
        {
            case UART_PARITY_EVEN:
                UART_SET_DATA_LENGTH_8_BITS_EVEN_PARITY(UART5);
                break;

            case UART_PARITY_ODD:
                UART_SET_DATA_LENGTH_8_BITS_ODD_PARITY(UART5);
                break;
                
            case UART_PARITY_NONE:
                UART_SET_DATA_LENGTH_8_BITS_NO_PARITY(UART5);
                break;
                
            default:
                break;
        }
    }
    
    
    // configure stop bits
    switch(config->stop_bits)
    {
        case ONE_STOP_BIT:
            UART_SET_ONE_STOP_BIT(UART5);
            break;

        case TWO_STOP_BITS:
            UART_SET_TWO_STOP_BITS(UART5);
            break;

        default:
            break;
    }

    return UART_ERROR_NONE;
}

static void enable_UART1()
{
    UART_ENABLE(UART1);
    UART_ENABLE_RX_PIN(UART1);
    UART_ENABLE_TX_PIN(UART1);
}

static void enable_UART2()
{
    UART_ENABLE(UART2);
    UART_ENABLE_RX_PIN(UART2);
    UART_ENABLE_TX_PIN(UART2);
}

static void enable_UART3()
{
    UART_ENABLE(UART3);
    UART_ENABLE_RX_PIN(UART3);
    UART_ENABLE_TX_PIN(UART3);
}

static void enable_UART4()
{
    UART_ENABLE(UART4);
    UART_ENABLE_RX_PIN(UART4);
    UART_ENABLE_TX_PIN(UART4);
}

static void enable_UART5()
{
    UART_ENABLE(UART5);
    UART_ENABLE_RX_PIN(UART5);
    UART_ENABLE_TX_PIN(UART5);
}



static void disable_UART1()
{
    UART_DISABLE(UART1);
    UART_DISABLE_RX_PIN(UART1);
    UART_DISABLE_TX_PIN(UART1);
}

static void disable_UART2()
{
    UART_DISABLE(UART2);
    UART_DISABLE_RX_PIN(UART2);
    UART_DISABLE_TX_PIN(UART2);
}

static void disable_UART3()
{
    UART_DISABLE(UART3);
    UART_DISABLE_RX_PIN(UART3);
    UART_DISABLE_TX_PIN(UART3);
}

static void disable_UART4()
{
    UART_DISABLE(UART4);
    UART_DISABLE_RX_PIN(UART4);
    UART_DISABLE_TX_PIN(UART4);
}

static void disable_UART5()
{
    UART_DISABLE(UART5);
    UART_DISABLE_RX_PIN(UART5);
    UART_DISABLE_TX_PIN(UART5);
}



/**********************
 * UART API Functions *
 **********************/


void UART_send_byte(uart_device_number_t device_number, uint8_t *value)
{
    switch(device_number)
    {
        case UART1:
            UART_SEND_BYTE(UART1, *value);
            break;

        case UART2:
            UART_SEND_BYTE(UART2, *value);
            break;

        case UART3:
            UART_SEND_BYTE(UART3, *value);
            break;

        case UART4:
            UART_SEND_BYTE(UART4, *value);
            break;

        case UART5:
            UART_SEND_BYTE(UART5, *value);
            break;

        default:
            break;
    }
}


void UART_receive_byte(uart_device_number_t device_number, uint8_t *value)
{
    switch(device_number)
    {
        case UART1:
            UART_RECEIVE_BYTE(UART1, *value);
            break;

        case UART2:
            UART_RECEIVE_BYTE(UART2, *value);
            break;

        case UART3:
            UART_RECEIVE_BYTE(UART3, *value);
            break;

        case UART4:
            UART_RECEIVE_BYTE(UART4, *value);
            break;

        case UART5:
            UART_RECEIVE_BYTE(UART5, *value);
            break;

        default:
            break;
    }
}


void UART_send(uart_device_number_t device_number, void *send_buffer, uint32_t size)
{
    while(size > 0)
    {
        UART_send_byte(device_number, (uint8_t*)send_buffer);
        send_buffer++;
        size--;
    }
}

void UART_receive(uart_device_number_t device_number, void *send_buffer, uint32_t size)
{
    while(size > 0)
    {
        UART_receive_byte(device_number, (uint8_t*)send_buffer);
        send_buffer++;
        size--;
    }
}


void UART_register_receive_callback(uart_device_number_t device_number,
                                    uart_receive_callback_t callback_function,
                                    void *receive_buffer,
                                    uint32_t bytes_to_trigger,
                                    bool is_repeated)
{
    callback_table[device_number-1].callback_function = callback_function;
    callback_table[device_number-1].receive_buffer = receive_buffer;
    callback_table[device_number-1].bytes_to_trigger = bytes_to_trigger;
    callback_table[device_number-1].current_bytes = 0;
    callback_table[device_number-1].is_repeated = is_repeated;
    callback_table[device_number-1].is_enabled = true;
}


void UART_deregister_receive_callback(uart_device_number_t device_number)
{
    callback_table[device_number-1].callback_function = NULL;
    callback_table[device_number-1].receive_buffer = NULL;
    callback_table[device_number-1].bytes_to_trigger = 0;
    callback_table[device_number-1].current_bytes = 0;
    callback_table[device_number-1].is_enabled = false;
    callback_table[device_number-1].is_repeated = false;
}


void UART_get_device_config(uart_device_number_t device_number, uart_device_config_t *config)
{
    // pointer to config struct typecast to bytes pointer
    uint8_t *read_ptr = (uint8_t*) &device_config_table[device_number-1];
    uint8_t *write_ptr = (uint8_t*) config;
    
    // byte copy
    for(int i = 0; i < sizeof(uart_device_config_t); i++, read_ptr++, write_ptr++)
    {
        *write_ptr = *read_ptr;
    }
}


int UART_set_device_config(uart_device_number_t device_number, uart_device_config_t *config)
{
    int err_code;
    
    // check for erroneous config
    if(config->baud < 0 || config->baud > driver_config.max_baud)
    {
        return UART_BAUD_RATE_NOT_SUPPORTED;
    }
    
    if(config->data_size == UART_DATA_NINE_BITS &&
        config->parity != UART_PARITY_NONE)
    {
        return UART_DATA_LENGTH_PARITY_COMB_NOT_SUPPORTED;
    }
    else if(config->data_size != UART_DATA_NINE_BITS &&
            config->data_size != UART_DATA_EIGHT_BITS)
    {
        return UART_DATA_LENGTH_NOT_SUPPORTED;
    }
    
    
    // set baud requires BRG reg calculation
    UART_configure_hw_baud_regs(device_number, config->baud);
    
    
    
    switch(device_number)
    {
        case UART1:
            err_code = UART_set_UART1_config(config);
            break;
        case UART2:
            err_code = UART_set_UART2_config(config);
            break;
        case UART3:
            err_code = UART_set_UART3_config(config);
            break;
        case UART4:
            err_code = UART_set_UART4_config(config);
            break;
        case UART5:
            err_code = UART_set_UART5_config(config);
            break;
    }

    return err_code;
}


bool UART_device_supports_hw_flow_control(uart_device_number_t device_number)
{
    return device_number < UART4 && device_number > 0;
}


void UART_enable(uart_device_number_t device_number)
{
    switch(device_number)
    {
        case UART1:
            enable_UART1();
            break;
        case UART2:
            enable_UART2();
            break;
        case UART3:
            enable_UART3();
            break;
        case UART4:
            enable_UART4();
            break;
        case UART5:
            enable_UART5();
            break;
    }
}


void UART_disable(uart_device_number_t device_number)
{
    switch(device_number)
    {
        case UART1:
            disable_UART1();
            break;
        case UART2:
            disable_UART2();
            break;
        case UART3:
            disable_UART3();
            break;
        case UART4:
            disable_UART4();
            break;
        case UART5:
            disable_UART5();
            break;
    }
}


void UART_configure_RX_interrupts(uart_device_number_t device_number)
{
    switch(device_number)
    {
        case UART1:
            UART_RX_SET_TO_INTERRUPT_WHILE_NOT_EMPTY(UART1);
            break;
        case UART2:
            UART_RX_SET_TO_INTERRUPT_WHILE_NOT_EMPTY(UART2);
            break;
        case UART3:
            UART_RX_SET_TO_INTERRUPT_WHILE_NOT_EMPTY(UART3);
            break;
        case UART4:
            UART_RX_SET_TO_INTERRUPT_WHILE_NOT_EMPTY(UART4);
            break;
        case UART5:
            UART_RX_SET_TO_INTERRUPT_WHILE_NOT_EMPTY(UART5);
            break;
    }
    
}


void UART_configure_TX_interrupts(uart_device_number_t device_number)
{
    switch(device_number)
    {
        case UART1:
            UART_TX_SET_TO_INTERRUPT_AFTER_FIFO_TRANSMIT(UART1);
            break;
        case UART2:
            UART_TX_SET_TO_INTERRUPT_AFTER_FIFO_TRANSMIT(UART2);
            break;
        case UART3:
            UART_TX_SET_TO_INTERRUPT_AFTER_FIFO_TRANSMIT(UART3);
            break;
        case UART4:
            UART_TX_SET_TO_INTERRUPT_AFTER_FIFO_TRANSMIT(UART4);
            break;
        case UART5:
            UART_TX_SET_TO_INTERRUPT_AFTER_FIFO_TRANSMIT(UART5);
            break;
    }
}


void UART_initialize_driver()
{
    // setup the callback table and receive buffers
    for(int i = 0; i < NUM_UART_DEVS; i++)
    {
        callback_table[i].buffer_size = UART_RECEIVE_BUFFER_SIZE;
        callback_table[i].bytes_to_trigger = 0;
        callback_table[i].current_bytes = 0;
        callback_table[i].callback_function = NULL;
        callback_table[i].receive_buffer = NULL;
        callback_table[i].is_enabled = false;
        callback_table[i].is_repeated = false;
    }
    
    UART_enable(UART2);
    UART_configure_RX_interrupts(UART2);
    
    driver_config.max_baud = 500000;
    driver_config.num_uarts = 5;
}



/**********************************
 * ISR definitions for UART Driver
 **********************************/

void UART_2_handle_receive(void)
{
    uint8_t received_byte, bytes_received = 0;
    uint8_t *receive_buffer = (uint8_t*) callback_table[UART2_TABLE_INDEX].receive_buffer;
    uint8_t current_index = callback_table[UART2_TABLE_INDEX].current_bytes;
    
    while(UART_RX_BUFFER_HAS_DATA(UART2))
    {
        UART_READ_FROM_RX_FIFO(UART2, received_byte);
        receive_buffer[current_index] = received_byte;
        current_index++;
        bytes_received++;
        callback_table[UART2_TABLE_INDEX].current_bytes++;
        
        
        if(bytes_received >= callback_table[UART2_TABLE_INDEX].bytes_to_trigger && 
            callback_table[UART2_TABLE_INDEX].is_enabled && callback_table[UART2_TABLE_INDEX].callback_function)
        {
            callback_table[UART2_TABLE_INDEX].callback_function(
                            callback_table[UART2_TABLE_INDEX].receive_buffer,
                            callback_table[UART2_TABLE_INDEX].current_bytes);
            
            callback_table[UART2_TABLE_INDEX].current_bytes = 0;
        }
    }

    // clear interrupt flag
    IFS1bits.U2RXIF = 0;
}


void UART_2_handle_transmit(void)
{
    // just clear the interrupt flag
    IFS1bits.U2TXIF = 0;
}


void UART_2_handle_error(void)
{
    // print error to LCD display
    
    if(UART_PARITY_ERROR_OCCURRED(UART2))
    {
        NT7603_write_string("Parity error.");
    }
    else if(UART_FRAMING_ERROR_OCCURRED(UART2))
    {
        NT7603_write_string("Framing error.");
    }
    else if(UART_OVERFLOW_ERROR_OCCURRED(UART2))
    {
        NT7603_write_string("Overflow error.");
    }
    
    IFS1bits.U2EIF = 0;
}



void __ISR(_UART_2_VECTOR, IPL5SOFT) UART_2_general_ISR(void)
{
    if(IFS1bits.U2RXIF == 1)
    {
        UART_2_handle_receive();
    }
    else if(IFS1bits.U2TXIF == 1)
    {
        UART_2_handle_transmit();
    }
    else if(IFS1bits.U2EIF == 1)
    {
        UART_2_handle_error();
    }
}

