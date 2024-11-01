
#include <xc.h>




void __ISR(24, IPL3SOFT) uart1_spi3_i2c3_shared_vector_ISR(void)
{
    int major = driver_table.isr_vector_to_major_minor[_UART_1_VECTOR] >> 3;
    int minor = driver_table.isr_vector_to_major_minor[_UART_1_VECTOR] & 0x7;

    if(IFS0bits.U1EIF)
    {
        driver_table.driver_isrs[major].u.char_isr_callbacks.error(minor);
        IFS0bits.U1EIF = 0;
    }
    else if(IFS0bits.U1RXIF)
    {
        driver_table.driver_isrs[major].u.char_isr_callbacks.receive(minor);
        IFS0bits.U1RXIF = 0;
    }
    
    else if(IFS0bits.U1TXIF)
    {
        driver_table.driver_isrs[major].u.char_isr_callbacks.transmit(minor);
        IFS0bits.U1TXIF = 0;
    }
    
}