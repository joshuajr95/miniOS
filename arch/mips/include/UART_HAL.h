#ifndef UART_HAL_H
#define UART_HAL_H



/**
 * @file UART_HAL.h
 *
 * Hardware Abstraction Layer (HAL) for
 * PIC32MX795F512L UART. This file implements
 * a layer of abstraction on top of that
 * provided by the xc.h header written by Microchip.
 * That header provides some abstraction in terms
 * of allowing the user to refer to hardware configuration
 * registers (called Special Function Registers, or SFRs)
 * by name instead of address, but the names are still
 * somewhat cryptic and function-like macros that allow
 * the user to, say, enable UART 1 by calling 
 * UART_ENABLE(UART1) make programming drivers much
 * easier and more intuitive. This file also allows
 * code to be written for any UART on the PIC32, because
 * the UART number is a parameter.
 */


#include <proc/PIC32MX/p32mx795f512l.h>


#define PERIPHERAL_FREQ 40000000

// TODO: remove semicolons and change _n to x


/**
 * Macros have a two-level structure, which
 * allows for recursive expansion of macros
 * passed as arguments to function-like macros.
 * This means, for example, that a macro call
 * like UART_ENABLE(UART2) is possible.
 */



#define __UART_ENABLE(x)                    U ## x ## MODEbits.ON = 1
#define __UART_DISABLE(x)                   U ## x ## MODEbits.ON = 0

#define __UART_ENABLE_HW_FLOW_CONTROL(x)    U ## x ## MODEbits.UEN = 0b10
#define __UART_DISABLE_HW_FLOW_CONTROL(x)   U ## x ## MODEbits.UEN = 0b00

#define __UART_SET_M_DIVISOR_16(x)          U ## x ## MODEbits.BRGH = 0
#define __UART_SET_M_DIVISOR_4(x)           U ## x ## MODEbits.BRGH = 1

#define __UART_SET_DATA_LENGTH_9_BITS_NO_PARITY(x)      U ## x ## MODEbits.PDSEL = 0b11
#define __UART_SET_DATA_LENGTH_8_BITS_EVEN_PARITY(x)    U ## x ## MODEbits.PDSEL = 0b10
#define __UART_SET_DATA_LENGTH_8_BITS_ODD_PARITY(x)     U ## x ## MODEbits.PDSEL = 0b01
#define __UART_SET_DATA_LENGTH_8_BITS_NO_PARITY(x)      U ## x ## MODEbits.PDSEL = 0b00

#define __UART_SET_ONE_STOP_BIT(x)           U ## x ## MODEbits.STSEL = 0
#define __UART_SET_TWO_STOP_BITS(x)          U ## x ## MODEbits.STSEL = 1

#define __UART_TX_SET_TO_INTERRUPT_WHILE_FIFO_EMPTY(x)       U ## x ## STAbits.UTXISEL = 0b10
#define __UART_TX_SET_TO_INTERRUPT_AFTER_FIFO_TRANSMIT(x)    U ## x ## STAbits.UTXISEL = 0b01
#define __UART_TX_SET_TO_INTERRUPT_WHILE_FIFO_NOT_FULL(x)    U ## x ## STAbits.UTXISEL = 0b00

#define __UART_RX_SET_TO_INTERRUPT_WHILE_SIX_OR_MORE_BYTES(x)    U ## x ## STAbits.URXISEL = 0b10
#define __UART_RX_SET_TO_INTERRUPT_WHILE_FOUR_OR_MORE_BYTES(x)   U ## x ## STAbits.URXISEL = 0b01
#define __UART_RX_SET_TO_INTERRUPT_WHILE_NOT_EMPTY(x)            U ## x ## STAbits.URXISEL = 0b00

#define __UART_ENABLE_RX_PIN(x)              U ## x ## STAbits.URXEN = 1
#define __UART_DISABLE_RX_PIN(x)             U ## x ## STAbits.URXEN = 0

#define __UART_ENABLE_TX_PIN(x)              U ## x ## STAbits.UTXEN = 1
#define __UART_DISABLE_TX_PIN(x)             U ## x ## STAbits.UTXEN = 0

#define __UART_ENABLE_TX_PIN(x)              U ## x ## STAbits.UTXEN = 1
#define __UART_DISABLE_TX_PIN(x)             U ## x ## STAbits.UTXEN = 0

#define __UART_IS_TX_BUFFER_FULL(x)          (U ## x ## STAbits.UTXBF == 1)
#define __UART_IS_TX_BUFFER_EMPTY(x)         (U ## x ## STAbits.TRMT == 0)

#define __UART_PARITY_ERROR_OCCURRED(x)     (U ## x ## STAbits.PERR == 1)
#define __UART_FRAMING_ERROR_OCCURRED(x)     (U ## x ## STAbits.FERR == 1)
#define __UART_OVERFLOW_ERROR_OCCURRED(x)    (U ## x ## STAbits.OERR == 1)

#define __UART_RX_BUFFER_HAS_DATA(x)         (U ## x ## STAbits.URXDA == 1)

#define __UART_GET_BAUD_RATE_GENERATOR(x)    ({int ret; ret = U ## x ## BRG; ret;})
#define __UART_SET_BAUD_RATE_GENERATOR(x, brg)      (U ## x ## BRG = brg)

#define __UART_WRITE_TO_TX_FIFO(x, value)       U ## x ## TXREG = (value)
#define __UART_READ_FROM_RX_FIFO(x, value)      (value) = U ## x ## RXREG



#define UART_ENABLE(x)                      __UART_ENABLE(x)
#define UART_DISABLE(x)                     __UART_DISABLE(x)

#define UART_ENABLE_HW_FLOW_CONTROL(x)      __UART_ENABLE_HW_FLOW_CONTROL(x)
#define UART_DISABLE_HW_FLOW_CONTROL(x)     __UART_DISABLE_HW_FLOW_CONTROL(x)

#define UART_SET_M_DIVISOR_16(x)            __UART_SET_M_DIVISOR_16(x)
#define UART_SET_M_DIVISOR_4(x)             __UART_SET_M_DIVISOR_4(x)


#define UART_SET_DATA_LENGTH_9_BITS_NO_PARITY(x)   __UART_SET_DATA_LENGTH_9_BITS_NO_PARITY(x)
#define UART_SET_DATA_LENGTH_8_BITS_EVEN_PARITY(x) __UART_SET_DATA_LENGTH_8_BITS_EVEN_PARITY(x)
#define UART_SET_DATA_LENGTH_8_BITS_ODD_PARITY(x)  __UART_SET_DATA_LENGTH_8_BITS_ODD_PARITY(x)
#define UART_SET_DATA_LENGTH_8_BITS_NO_PARITY(x)   __UART_SET_DATA_LENGTH_8_BITS_NO_PARITY(x)

#define UART_SET_ONE_STOP_BIT(x)            __UART_SET_ONE_STOP_BIT(x)
#define UART_SET_TWO_STOP_BITS(x)           __UART_SET_TWO_STOP_BITS(x)



#define UART_TX_SET_TO_INTERRUPT_WHILE_FIFO_EMPTY(x)   \
        __UART_TX_SET_TO_INTERRUPT_WHILE_FIFO_EMPTY(x)

#define UART_TX_SET_TO_INTERRUPT_AFTER_FIFO_TRANSMIT(x) \
        __UART_TX_SET_TO_INTERRUPT_AFTER_FIFO_TRANSMIT(x)

#define UART_TX_SET_TO_INTERRUPT_WHILE_FIFO_NOT_FULL(x) \
        __UART_TX_SET_TO_INTERRUPT_WHILE_FIFO_NOT_FULL(x)



#define UART_RX_SET_TO_INTERRUPT_WHILE_SIX_OR_MORE_BYTES(x)     \
        __UART_RX_SET_TO_INTERRUPT_WHILE_SIX_OR_MORE_BYTES(x)

#define UART_RX_SET_TO_INTERRUPT_WHILE_FOUR_OR_MORE_BYTES(x)    \
        __UART_RX_SET_TO_INTERRUPT_WHILE_FOUR_OR_MORE_BYTES(x)

#define UART_RX_SET_TO_INTERRUPT_WHILE_NOT_EMPTY(x) \
        __UART_RX_SET_TO_INTERRUPT_WHILE_NOT_EMPTY(x)


#define UART_ENABLE_RX_PIN(x)              __UART_ENABLE_RX_PIN(x)
#define UART_DISABLE_RX_PIN(x)             __UART_DISABLE_RX_PIN(x)

#define UART_ENABLE_TX_PIN(x)              __UART_ENABLE_TX_PIN(x)
#define UART_DISABLE_TX_PIN(x)             __UART_DISABLE_TX_PIN(x)

#define UART_IS_TX_BUFFER_FULL(x)          __UART_IS_TX_BUFFER_FULL(x)
#define UART_IS_TX_BUFFER_EMPTY(x)         __UART_IS_TX_BUFFER_EMPTY(x)

#define UART_PARITY_ERROR_OCCURRED(x)      __UART_PARITY_ERROR_OCCURRED(x)
#define UART_FRAMING_ERROR_OCCURRED(x)     __UART_FRAMING_ERROR_OCCURRED(x)
#define UART_OVERFLOW_ERROR_OCCURRED(x)    __UART_OVERFLOW_ERROR_OCCURRED(x)


#define UART_RX_BUFFER_HAS_DATA(x)         __UART_RX_BUFFER_HAS_DATA(x)


// only if xc32 has statement expressions
#define UART_GET_BAUD_RATE_GENERATOR(x)    __UART_GET_BAUD_RATE_GENERATOR(x)
#define UART_SET_BAUD_RATE_GENERATOR(x, brg)      __UART_SET_BAUD_RATE_GENERATOR(x, brg)


#define UART_WRITE_TO_TX_FIFO(x, value)       __UART_WRITE_TO_TX_FIFO(x, value)
#define UART_READ_FROM_RX_FIFO(x, value)      __UART_READ_FROM_RX_FIFO(x, value)



// blocking send and receive
#define UART_SEND_BYTE(_n, _value)          \
    while(UART_IS_TX_BUFFER_FULL(_n));      \
    UART_WRITE_TO_TX_FIFO(_n, *value);

#define UART_RECEIVE_BYTE(_n, _value)       \
    while(!UART_RX_BUFFER_HAS_DATA(_n));    \
    UART_READ_FROM_RX_FIFO(_n, _value);


#endif