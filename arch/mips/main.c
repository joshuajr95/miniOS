
#include <stdbool.h>
#include <stdio.h>
#include <proc/PIC32MX/p32mx795f512l.h>


#include "UART_HAL.h"
#include "UART_Driver.h"
#include "NT7603_Driver.h"
#include "line_discipline.h"





#define __SET_DEVCFG1(_FWDTEN, _WDTPS, _FCKSM, _FPBDIV, _OSCIOFNC, _POSCMOD, _IESO, _FSOSCEN, _FNOSC)       \
        uint32_t  __attribute__((section(".config_BFC02FF8"))) __dev_config_1_BFC02FF8 = 0xffffffff &       \
        ((_FWDTEN | ~0b1) << 23) & ((_WDTPS | ~0b11111) << 16) & ((_FCKSM | ~0b11) << 14) &                 \
        ((_FPBDIV | ~0b11) << 12) & ((_OSCIOFNC | ~0b1) << 10) & ((_POSCMOD | ~0b11) << 8) &                \
        ((_IESO | ~0b1) << 7) & ((_FSOSCEN | ~0b1) << 5) & (_FNOSC | 0b111)


#define SET_DEVCFG1(_FWDTEN, _WDTPS, _FCKSM, _FPBDIV, _OSCIOFNC, _POSCMOD, _IESO, _FSOSCEN, _FNOSC)         \
        __SET_DEVCFG1(_FWDTEN, _WDTPS, _FCKSM, _FPBDIV, _OSCIOFNC, _POSCMOD, _IESO, _FSOSCEN, _FNOSC)







#define __SET_DEVCFG2(_FPLLODIV, _UPLLEN, _UPLLIDIV, _FPLLMUL, _FPLLIDIV)                                   \
        uint32_t __attribute__((section(".config_BFC02FF4"))) __dev_config_2_BFC02FF4 = 0xffffffff &        \
        ((_FPLLODIV | ~0b111) << 16) & ((_UPLLEN | ~0b1) << 15) & ((_UPLLIDIV | ~0b111) << 8) &             \
        ((_FPLLMUL | ~0b111) << 4) & (_FPLLIDIV | ~0b111)


#define SET_DEVCFG2(_FPLLODIV, _UPLLEN, _UPLLIDIV, _FPLLMUL, _FPLLIDIV)     \
        __SET_DEVCFG2(_FPLLODIV, _UPLLEN, _UPLLIDIV, _FPLLMUL, _FPLLIDIV)


// these lines configure the oscillators for correct operation, since the #pragma config
// does not appear to work
uint32_t __attribute__((section(".config_BFC02FF8"))) __dev_config_1_BFC02FF8 = 0xffffdefb;
uint32_t __attribute__((section(".config_BFC02FF4"))) __dev_config_2_BFC02FF4 = 0xfff8ffd9;




static line_discipline_t discipline;
static uint8_t received_byte;

int process_next_byte(line_discipline_t *discipline, void *buffer, uint32_t size);


static void handle_UART_receive(void *buf, uint32_t size)
{
    discipline.process_next_byte(&discipline, buf, size);
}


static int invoke_shell(void)
{
    NT7603_write_string("shell invoked");
    return 0;
}

static char shell_buffer[MAX_LINE_SIZE];


int terminal_send_byte(uint8_t byte_to_send)
{
    UART_send_byte(UART2, &byte_to_send);
    
    return 0;
}


void main(void)
{
    DDPCON = 0;
    INTCONbits.MVEC = 1;


    __builtin_disable_interrupts();
    IFS1bits.U2RXIF = 0;
    IPC8bits.U2IP = 3;
    IEC1bits.U2RXIE = 1;


    // set config
    uart_device_config_t config;
    config.baud = 115200;
    config.data_size = UART_DATA_EIGHT_BITS;
    config.enable_hw_flow_control = false;
    config.parity = UART_PARITY_NONE;
    config.stop_bits = ONE_STOP_BIT;


    UART_initialize_driver();
    UART_set_device_config(UART2, &config);
    line_discipline_init(&discipline, process_next_byte, invoke_shell, "miniOS % ", &shell_buffer[0]);
    UART_register_receive_callback(UART2, handle_UART_receive, &received_byte, 1, false);

    __builtin_enable_interrupts();

    for(int i = 0; i < 50000; i++);

    NT7603_function_set(true, true, 1);
    NT7603_turn_display_on(true, false, true);
    NT7603_clear_display();
    NT7603_set_entry_mode(true, false);

    
    char buf[32];
    while(1)
    {
        //NT7603_clear_display();
        //snprintf(buf, sizeof(buf), "x: %d, y: %d", get_cursor_x(), get_cursor_y());
        //NT7603_write_string(buf);
        
        //for(int i = 0; i < 10000; i++);
    }

    // NT7603_write_string("Hello, IPE!");
}