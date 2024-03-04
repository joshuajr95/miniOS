#ifndef DEVICE_DRIVER_SUBSYSTEM_H
#define DEVICE_DRIVER_SUBSYSTEM_H


#define DRIVER_TYPE_UART             0
#define DRIVER_TYPE_SPI              1
#define DRIVER_TYPE_I2C              2
#define DRIVER_TYPE_CAN              3
#define DRIVER_TYPE_TIMER            4
#define DRIVER_TYPE_ADC              5
#define DRIVER_TYPE_PWM              6
#define DRIVER_TYPE_DAC              7
#define DRIVER_TYPE_HDD              8
#define DRIVER_TYPE_SSD              9
#define DRIVER_TYPE_ETHERNET         10
#define DRIVER_TYPE_WIFI             11
#define DRIVER_TYPE_BLUETOOTH        12

#define MAX_DRIVER_TYPE             32



char *dev_file_names[] = {
    [DRIVER_TYPE_UART] = "uart",
    [DRIVER_TYPE_SPI] = "spi",
    [DRIVER_TYPE_I2C] = "i2c",
    [DRIVER_TYPE_CAN] = "can",
    [DRIVER_TYPE_TIMER] = "timer",
    [DRIVER_TYPE_ADC] = "adc",
    [DRIVER_TYPE_PWM] = "pwm",
    [DRIVER_TYPE_DAC] = "dac",
    [DRIVER_TYPE_HDD] = "hdd",
    [DRIVER_TYPE_SSD] = "ssd",
    [DRIVER_TYPE_ETHERNET] "eth",
    [DRIVER_TYPE_WIFI] = "wifi",
    [DRIVER_TYPE_BLUETOOTH] = "bluetooth"
};






/*
 * These are used to define the driver namespaces, which
 * allows all of the driver callback functions to be named
 * similarly without needing to prefix each with extra
 * information to prevent naming collisions.
 */
#define BEGIN_DRIVER(_driver_name) namespace _driver_name {

#define END_DRIVER }


typedef struct DRIVER
{
    int file_type;
    int driver_type;
    union 
    {
        char_driver_t chardev;
        block_driver_t blockdev;
        net_driver_t netdev;
        timer_driver_t timerdev;
        gpio_driver_t gpiodev;
        adc_driver_t adcdev;
        pwm_driver_t pwmdev;
    } u;
    
} driver_t;



typedef struct CHARDEV
{
    /*
     * Callback function for the open syscall.
     * This will be invoked by the OS for a given
     * device whenever the user invokes the
     * open syscall on that device's file.
     */
    int (*open)(int);


    /*
     * Close callback function.
     */
    void (*close)(int);


    /*
     * Read callback function.
     */
    int (*read)(int, void*, unsigned short);


    /*
     * Write callback function.
     */
    int (*write)(int, void*, unsigned short);


    // TODO: These should not be part of the driver table,
    //       which is supposed to be the interface to syscall
    //       implementation. Need a separate interface to
    //       interrupt handlers.

    /*
     * Callback function for interrupt generated
     * on error during transmission or reception.
     */
    int (*error_interrupt)(int);


    /*
     * Callback function for interrupt generated
     * on transmission done.
     */
    int (*transmit_interrupt)(int);


    /*
     * Callback function for interrupt
     * generated on reception of data.
     */
    int (*receive_interrupt)(int);


    /*
     * Initialization routine for the device.
     */
    int (*init)(int*);

} char_driver_t;


typedef struct NETDEV
{
    /*
     * Callback function for the open syscall.
     * This will be invoked by the OS for a given
     * device whenever the user invokes the
     * open syscall on that device's file.
     */
    // pass in the device number
    int (*open)(int);


    /*
     * Close callback function.
     */
    void (*close)(int);


    /*
     * Read callback function.
     */
    int (*read)(int, void*, unsigned short);


    /*
     * Write callback function.
     */
    int (*write)(int, void*, unsigned short);


    int (*init)(int*);

} net_driver_t;


typedef struct BLOCKDEV
{
    /*
     * Callback function for the open syscall.
     * This will be invoked by the OS for a given
     * device whenever the user invokes the
     * open syscall on that device's file.
     */
    int (*open)(int);


    /*
     * Close callback function.
     */
    void (*close)(int);


    /*
     * Read callback function.
     */
    int (*read)(int, void*, unsigned short);


    /*
     * Write callback function.
     */
    int (*write)(int, void*, unsigned short);


    int (*init)(int*);

} block_driver_t;


typedef struct TIMERDRV
{
    int (*init)(int*);

} timer_driver_t;


typedef struct GPIODEV
{
    int (*init)(int*);

} gpio_driver_t;


typedef struct ADCDEV
{
    int (*init)(int*);

} adc_driver_t;


typedef struct PWMDEV
{
    int (*init)(int*);

} pwm_driver_t;



typedef struct DRIVER_TABLE
{
    driver_t drivers[MAX_DRIVER_TYPE];
    unsigned char drivers_bitmap[MAX_DRIVER_TYPE/8];

} driver_table_t;




#define SET_DRIVER_IN_USE(_driver_table, _driver_number)        \
    int byte_index = _driver_number/8;                          \
    unsigned char bit_index = _driver_number%8;                 \
    unsigned char mask = 0x1 << bit_index;                      \
    (_driver_table)->drivers[byte_index] |= mask;


#define SET_DRIVER_FREE(_driver_table, _driver_number)          \
    int byte_index = _driver_number/8;                          \
    unsigned char bit_index = _driver_number%8;                 \
    unsigned char mask = ~(0x1 << bit_index);                   \
    (_driver_table)->drivers[byte_index] &= mask;



/*************************
 * Function Declarations *
 *************************/

void init_dev_drivers();

void register_char_driver(char_driver_t *chardev);
void register_net_driver(net_driver_t *netdev);
void register_block_driver(block_driver_t *blockdev);
void register_timer_driver(timer_driver_t *timerdev);
void register_gpio_driver(gpio_driver_t *gpiodev);
void register_adc_driver(adc_driver_t *adcdev);
void register_pwm_driver(pwm_driver_t *pwmdev);



#endif
