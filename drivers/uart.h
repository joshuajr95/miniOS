#ifndef UART_H
#define UART_H

#include "device_driver_subsystem.h"
#include "task.h"


#define RING_BUFFER_FULL 1


#define NUM_UARTS 6


typedef struct UART_CONTROL_BLOCK
{
    unsigned char open_uart_bitmap;

    unsigned int read_buffer_size;
    unsigned int write_buffer_size;

    ring_buffer_t read_buffers[NUM_UARTS];
    ring_buffer_t write_buffers[NUM_UARTS];

    // only used when option for blocking on not enough data
    dev_wait_queue_t wait_queues[NUM_UARTS];

} uart_cb_t;


#define is_uart_open(_uart_cb, _uart_number) (((_uart_cb)->open_uart_bitmap >> _uart_number) & 0x1;)
#define set_uart_open(_uart_cb, _uart_number) ((_uart_cb)->open_uart_bitmap |= (0x1 << _uart_number);)
#define set_uart_closed(_uart_cb, _uart_number) ((_uart_cb)->open_uart_bitmap &= ~(0x1 << _uart_number);)






#endif