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




// TODO: may need different method since namespace may cause linkage
// problems with C client code

/*
 * These are used to define the driver namespaces, which
 * allows all of the driver callback functions to be named
 * similarly without needing to prefix each with extra
 * information to prevent naming collisions.
 */
#define BEGIN_DRIVER(_driver_name)      namespace _driver_name {

#define END_DRIVER(_driver_name)        }


enum uart_parity {
    EVEN_PARITY,
    ODD_PARITY,
    NO_PARITY
};

enum uart_stop_bits {
    ONE_STOP_BIT,
    TWO_STOP_BITS
};


enum uart_data_size {
    UART_8_BITS,
    UART_9_BITS
};


typedef struct UART_OPTIONS
{
    unsigned int baud;
    int parity;
    int stop_bits;
    int size;
    int hardware_flow_control;

} uart_options_t;


typedef struct DRIVER_OPTIONS
{
    unsigned short driver_type;

    union
    {
        uart_options_t uart_opts;
        spi_options_t spi_opts;
        i2c_options_t i2c_opts;
        can_options_t can_opts;
        // TODO: rest of opts
    } u;
    
} driver_options_t;


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
    int (*open)(int, driver_options_t*);


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



/*
 * Callback functions for Interrupt Service
 * Routines (ISRs) for various types of device
 * drivers. Since each driver handles 
 */

typedef struct CHAR_ISR
{
    void (*error)(int device_number);
    void (*receive)(int device_number);
    void (transmit)(int device_number);

} char_isr_callbacks_t

typedef struct DRIVER_ISRS
{
    int driver_type;
    union
    {
        char_isr_callbacks_t char_isr_callbacks;
        // TODO: rest
    } u;

} driver_isr_callbacks_t;




/*
typedef struct CHAR_WAIT_QUEUE
{
    // task waiting on 
    taskid_t task;

    // task could be waiting for more data
    // to arrive of for data to be sent so
    // that there is more space in the buffer
    unsigned char read_or_write;

    // task's buffer. Will increment when data is received
    void *buffer;

} char_wait_queue_t;


typedef struct DEVICE_WAIT_QUEUE
{
    // file type (i.e. char, block, net, etc.)
    int device_type;

    union
    {
        char_wait_queue_t char_wait_queue;
        block_wait_queue_t block_wait_queue;
        net_wait_queue_t net_wait_queue;
        // TODO: rest of file types
    } u;

} dev_wait_queue_t;
*/


typedef struct DRIVER_TABLE
{
    /*
     * Drivers member stores the callback functions for
     * system call implementations (open/close, read/write, etc.)
     * and driver_isrs member stores callback functions for
     * interrupt service routines (data received, data transmitted,
     * transmission/reception error). These are separate to
     * enforce separation of ISR interface and syscall interface.
     */
    driver_t drivers[MAX_DRIVER_TYPE];
    driver_isr_callbacks_t driver_isrs[MAX_DRIVER_TYPE];

    /*
     * Since some interrupt vectors are shared (for example
     * UART 1, SPI 3, and I2C 3), must record a mapping of
     * which interrupt vectors are being used by which device.
     */
    unsigned char isr_vector_to_major_minor[ISR_VECTORS];
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





typedef struct RING_BUFFER
{
    void *buffer;
    int buffer_size;
    unsigned int in;
    unsigned int out;

} ring_buffer_t;

#define IN_INDEX(_ring_buffer) ((_ring_buffer)->in % (_ring_buffer)->buffer_size)
#define OUT_INDEX(_ring_buffer) ((_ring_buffer)->out % (_ring_buffer)->buffer_size)

int ring_buffer_init(ring_buffer_t *ring_buffer, int buf_size);
int read_from_ring_buffer(ring_buffer_t *ring_buffer, void *output, int size);
int write_to_ring_buffer(ring_buffer_t *ring_buffer, void *input, int size);


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
