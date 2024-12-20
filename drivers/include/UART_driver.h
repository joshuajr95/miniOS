#ifndef UART_DRIVER_H
#define UART_DRIVER_H


/**
 * @file UART_driver.h
 *
 * Interface definition for UART driver.
 * ANY UART driver written for MiniOS must
 * be written to implement this header file.
 * Any higher-level code including this file
 * may assume that the functions work as
 * describer.
 */


/**
 * @author Joshua Jacobs-Rebhun
 */


#include <stdbool.h>
#include <stdint.h>



#define UART1           1
#define UART2           2
#define UART3           3
#define UART4           4
#define UART5           5

#define NUM_UART_DEVS   5



/**
 * All possible error codes.
 */
typedef enum
{
    UART_ERROR_NONE=0,
    UART_DATA_LENGTH_NOT_SUPPORTED,
    UART_BAUD_RATE_NOT_SUPPORTED,
    UART_DATA_LENGTH_PARITY_COMB_NOT_SUPPORTED
} uart_error_code_t;



/**
 * @typedef uart_stop_bits_t
 *
 * Enumerated type for setting the
 * number of stop bits.
 */
typedef enum
{
    ONE_STOP_BIT,
    TWO_STOP_BITS
} uart_stop_bits_t;


/**
 * @typedef uart_data_size_t
 *
 * Size, in bits, of each data
 * transmission over UART
 */
typedef enum
{
    UART_DATA_FIVE_BITS,
    UART_DATA_SEVEN_BITS,
    UART_DATA_EIGHT_BITS,
    UART_DATA_NINE_BITS
} uart_data_size_t;


/**
 * @typedef uart_parity_t
 *
 * Enumerated type representing UART
 * parity bit configuration.
 */
typedef enum
{
    UART_PARITY_EVEN,
    UART_PARITY_ODD,
    UART_PARITY_NONE
} uart_parity_t;


/**
 * @typedef uart_device_config_t
 *
 * Struct that holds the configuration options
 * for a given UART device.
 */
typedef struct
{

    /**
     * Number of stop bits used for this UART device.
     */
    uart_stop_bits_t stop_bits;


    /**
     * Size of each data transmission.
     */
    uart_data_size_t data_size;


    /**
     * Parity bit configuration for this UART device.
     */
    uart_parity_t parity;


    /**
     * Baud rate for this UART device.
     */
    uint32_t baud;


    /**
     * Whether to enable HW flow control.
     */
    bool enable_hw_flow_control;

} uart_device_config_t;


/**
 * @typedef uart_driver_configuration_t
 *
 * Holds the UART driver configuration.
 */
typedef struct
{
    /**
     * Number of UART devices supported by
     * the hardware or this driver.
     */
    uint8_t num_uarts;

    /**
     * Max baud rate supported
     */
    uint32_t max_baud;

} uart_driver_config_t;


/**
 * @typedef uart_device_number_t
 *
 * Integer type defines the UART device number.
 */
typedef uint8_t uart_device_number_t;



/**
 * @typedef uart_receive_callback_t
 *
 * Function pointer type for callback function invoked upon
 * reception of data over UART. First parameter is a pointer
 * to the data received, and second parameter is the amount
 * (in bytes) of the received data.
 */
typedef void (*uart_receive_callback_t)(void*, uint32_t);



/**
 * Sends a single byte over UART device.
 *
 * @param device_number Number of the UART device to send data over. See @ref uart_device_number_t.
 * @param value Pointer to data to be sent.
 */
void UART_send_byte(uart_device_number_t device_number, uint8_t *value);


/**
 * Blocking send of a given amount of data over UART device.
 *
 * @param device_number Number of the UART device to send data over. See @ref uart_device_number_t.
 * @param send_buffer Pointer to buffer of data to be sent.
 * @param size Amount of data (in bytes) to be sent.
 */
void UART_send(uart_device_number_t device_number, void *send_buffer, uint32_t size);


/**
 * Receives a single byte from UART device.
 *
 * @param device_number Number of the UART device to receive data from. See @ref uart_device_number_t.
 * @param value Pointer to variable to store received data in.
 */
void UART_receive_byte(uart_device_number_t device_number, uint8_t *value);


/**
 * Blocking receive of a given amount of data from UART device.
 *
 * @param device_number Number of the UART device to receive data from. See @ref uart_device_number_t.
 * @param send_buffer Pointer to buffer to store received data in.
 * @param size Amount of data (in bytes) to be received.
 */
void UART_receive(uart_device_number_t device_number, void *send_buffer, uint32_t size);


/**
 * Registers a callback function for UART receive event.
 *
 * @param device_number Number of the UART device to receive data from.
 *          See @ref uart_device_number_t.
 * @param callback_function Function to be invoked when specified amount 
 *          of data is received.See @ref uart_receive_callback_t.
 * @param receive_buffer Buffer to store received data.
 * @param bytes_to_trigger Number of bytes that must be received before invoking
 *          the callback function. This is passed to the callback function
 *          as the second parameter on a receive event.
 * @param is_repeated Whether to invoke the callback repeatedly upon reception of data
 */
void UART_register_receive_callback(uart_device_number_t device_number,
                                    uart_receive_callback_t callback_function,
                                    void *receive_buffer,
                                    uint32_t bytes_to_trigger,
                                    bool is_repeated);


/**
 * Deregisters a callback function for UART receive event.
 *
 * @param device_number Number of the UART device to receive data from.
 *          See @ref uart_device_number_t.
 */
void UART_deregister_receive_callback(uart_device_number_t device_number);


/**
 * Gets the configuration for a given UART device. Configuration is co
 *
 * @param device_number Number of the UART device to receive data from.
 *          See @ref uart_device_number_t.
 * @param config Pointer to device configuration struct that will store
 *          config info. See @ref uart_device_config_t. Configuration information
 *          is copied into the struct referenced by this parameter.
 */
void UART_get_device_config(uart_device_number_t device_number, uart_device_config_t *config);


/**
 * Sets the configuration for a given UART device.
 *
 * @param device_number Number of the UART device to receive data from.
 *          See @ref uart_device_number_t.
 * @param config Pointer to UART device configuration struct that holds the
 *          configuration information to be set. See @ref uart_device_config_t.
 *          Configuration information is copied from the parameter, so
 *          it may be allocated on the stack.
 *
 * @return Error code. See @ref uart_error_code_t.
 */
int UART_set_device_config(uart_device_number_t device_number, uart_device_config_t *config);


/**
 * Check whether a given UART device supports hardware
 * flow control.
 *
 * @param device_number Number of the UART device to receive data from.
 *          See @ref uart_device_number_t.
 * @return Whether device supports hardware flow control.
 */
bool UART_device_supports_hw_flow_control(uart_device_number_t device_number);


/**
 * Turn on the given UART and enable the TX and RX pins.
 *
 * @param device_number Number of the UART device to receive data from.
 *          See @ref uart_device_number_t.
 */
void UART_enable(uart_device_number_t device_number);


/**
 * Disables the given UART device.
 *
 * @param device_number Number of the UART device to receive data from.
 *          See @ref uart_device_number_t.
 */
void UART_disable(uart_device_number_t device_number);


/**
 * Enables and configures receive interrupts for the given UART
 * device.
 *
 * @param device_number Number of the UART device to receive data from.
 *          See @ref uart_device_number_t.
 */
void UART_enable_RX_interrupts(uart_device_number_t device_number);


/**
 * Disables receive interrupts for the given UART device.
 *
 * @param device_number Number of the UART device to receive data from.
 *          See @ref uart_device_number_t.
 */
void UART_disable_RX_interrupts(uart_device_number_t device_number);


/**
 * Enables and configures transmit interrupts for the UART device.
 * @param device_number Number of the UART device to receive data from.
 *          See @ref uart_device_number_t.
 */
void UART_enable_TX_interrupts(uart_device_number_t device_number);


/**
 * Initializes the driver.
 */
void UART_initialize_driver();

#endif