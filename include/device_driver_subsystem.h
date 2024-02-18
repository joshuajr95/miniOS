#ifndef DEVICE_DRIVER_SUBSYSTEM_H
#define DEVICE_DRIVER_SUBSYSTEM_H


// maybe have this be part of file type
#define DRIVER_TYPE_CHAR                0
#define DRIVER_TYPE_BLOCK               1
#define DRIVER_TYPE_NET                 2
#define DRIVER_TYPE_TIMER               3
#define DRIVER_TYPE_GPIO                4
#define DRIVER_TYPE_ADC                 5
#define DRIVER_TYPE_PWM                 6


#define DRIVER_SUBTYPE_UART             0
#define DRIVER_SUBTYPE_SPI              1
#define DRIVER_SUBTYPE_I2C              2
#define DRIVER_SUBTYPE_CAN              3
#define DRIVER_SUBTYPE_TIMER            4
#define DRIVER_SUBTYPE_ADC              5
#define DRIVER_SUBTYPE_PWM              6
#define DRIVER_SUBTYPE_DAC              7
#define DRIVER_SUBTYPE_HDD              8
#define DRIVER_SUBTYPE_SSD              9
#define DRIVER_SUBTYPE_ETHERNET         10
#define DRIVER_SUBTYPE_WIFI             11
#define DRIVER_SUBTYPE_BLUETOOTH        12

#define MAX_DRIVER_TYPE             32



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
    int type;
    int subtype;
    char name[16];      // maybe, but could also use subtype to generate name
    union 
    {
        net_driver_t netdev;
        char_driver_t chardev;
        block_driver_t blockdev;
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
    int (*read)(void*, int, unsigned int);


    /*
     * Write callback function.
     */
    int (*write)(void*, int, unsigned int);


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
    int (*init)(void);

} char_driver_t;


typedef struct NETDEV
{

} net_driver_t;


typedef struct BLOCKDEV
{

} block_driver_t;


typedef struct TIMERDRV
{

} timer_driver_t;


typedef struct GPIODEV
{

} gpio_driver_t;


typedef struct ADCDEV
{

} adc_driver_t;


typedef struct PWMDEV
{

} pwm_driver_t;


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
