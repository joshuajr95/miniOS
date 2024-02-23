#ifndef TIMERS_H
#define TIMERS_H


#include "stdlib.h"

#define MAX_TIMERS 256
#define MAX_TIMER_CALLBACKS 64

#define TIMER_TYPE_REPEATING    0
#define TIMER_TYPE_ONCE         1
#define TIMER_TYPE_REPEAT_N     2

#define TIMER_SIZE_16_BITS      0
#define TIMER_SIZE_32_BITS      1


/*
 * Entry in the timer callback function table.
 * This structure is used since storing a full
 * 4-byte pointer in each timer list slot would
 * make the given table for the hardware timer
 * too big. Also, many timers may use the same
 * callback function, so this saves space.
 * Whether the function is a user space or kernel
 * space function is determined by the address.
 * The parameter passed to it is the current count
 * of the hardware timer.
 */
typedef void (*timer_callback_t)(int);



typedef struct TABLE_ENTRY
{
    timer_callback_t handler;
    unsigned int count:8;

} timer_callback_table_entry_t;



typedef struct CALLBACK_TABLE
{
    timer_callback_table_entry_t handlers[MAX_TIMER_CALLBACKS];
    unsigned char free_handler_bitmap[MAX_TIMER_CALLBACKS/8];

} timer_callback_table_t;



#define IS_CALLBACK_PRESENT(_callback_table, _callback)                 \
    __extension__ ({                                                    \
        int index;                                                      \
        int is_present = 0;                                             \
        for(index = 0; index < MAX_TIMER_CALLBACKS; index++)            \
        {                                                               \
            if((_callback_table)->handlers[index].handler == _callback) \
            {                                                           \
                is_present = 1;                                         \
            }                                                           \
        }                                                               \
        is_present;                                                     \
    })

#define FIND_CALLBACK_INDEX(_callback_table, _callback)                 \
    __extension__ ({                                                    \
        int index;                                                      \
        for(index = 0; index < MAX_TIMER_CALLBACKS; index++)            \
        {                                                               \
            if((_callback_table)->handlers[index].handler == _callback) \
            {                                                           \
                break;                                                  \
            }                                                           \
        }                                                               \
        index;                                                          \
    })

#define FIND_FIRST_FREE_CALLBACK_INDEX(_callback_table)                 \
    __extension__ ({                                                    \
        int index;                                                      \
        for(index = 0; index < MAX_TIMER_CALLBACKS; index++)            \
        {                                                               \
            if(IS_CALLBACK_FREE(_callback_table, index))                \
            {                                                           \
                break;                                                  \
            }                                                           \
        }                                                               \
        index;                                                          \
    })


#define IS_CALLBACK_FREE(_callback_table, _index)                               \
    __extension__ ({                                                            \
        int byte_index = _index/8;                                              \
        int bit_index = _index%8;                                               \
        unsigned char mask = 0x1 << bit_index;                                  \
        int is_free;                                                            \
        is_free = (_callback_table)->free_handler_bitmap[byte_index] & mask;    \
        is_free;                                                                \
    })

#define SET_CALLBACK_FREE(_callback_table, _index)                  \
    int byte_index = _index/8;                                      \
    int bit_index = _index%8;                                       \
    unsigned char mask = 0x1 << bit_index;                          \
    (_callback_table)->free_handler_bitmap[byte_index] |= mask;

#define SET_CALLBACK_IN_USE(_callback_table, _index)                \
    int byte_index = _index/8;                                      \
    int bit_index = _index%8;                                       \
    unsigned char mask = ~(0x1 << bit_index);                       \
    (_callback_table)->free_handler_bitmap[byte_index] &= mask;



/*
 * Entry in the timer table for a given
 * software timer. Since timers are stored
 * as a linked list, it has variables to
 * give the next and previous indices of
 * elements in the list. It also has the
 * index into the callback function table
 * of the callback function of this timer
 * as well as the timer count at which it
 * will stop.
 */
typedef struct TIMER
{
    unsigned int callback_function_index:6;
    unsigned int type:2;

} software_timer_t __attribute__((packed));


typedef struct TIMER_CONTROL_BLOCK
{
    software_timer_t timers[MAX_TIMERS];    // change to dynamically allocate
    char timer_bitmap[MAX_TIMERS/8];
    int num_timers;

} timer_control_block_t;


#define GET_NEXT_AVAILABLE_TIMER_INDEX(_timer_control_block)        \
    __extension__ ({                                                \
        int index;                                                  \
        int byte_index;                                             \
        int bit_index;                                              \
        for(index = 0; index < MAX_TIMERS; index++)                 \
        {                                                           \
            byte_index = index/8;                                   \
            bit_index = index%8;                                    \
            if(IS_TIMER_FREE(_timer_control_block, index))          \
            {                                                       \
                break;                                              \
            }                                                       \
        }                                                           \
        index;                                                      \
    })

#define SET_TIMER_FREE(_timer_control_block, _index)                \
    int byte_index = _index/8;                                      \
    int bit_index = _index%8;                                       \
    int mask = 0x1 << bit_index;                                    \
    (_timer_control_block)->timer_bitmap[byte_index] |= mask;


#define SET_TIMER_IN_USE(_timer_control_block, _index)              \
    int byte_index = _index/8;                                      \
    int bit_index = _index%8;                                       \
    int mask = ~(0x1 << bit_index);                                 \
    (_timer_control_block)->timer_bitmap[byte_index] &= mask;


#define IS_TIMER_FREE(_timer_control_block, _index)                                         \
    __extension__ ({                                                                        \
        int byte_index = _index/8;                                                          \
        int bit_index = _index%8;                                                           \
        int free = ((_timer_control_block)->timer_bitmap[byte_index] >> bit_index) & 0x1;   \
        free;                                                                               \
    })


/*
 * 
 */
typedef struct TIMER_INFO
{
    unsigned short nano;
    unsigned short micro;
    unsigned short milli;
    unsigned short seconds;

} timer_info_t;


typedef struct SYSTEM_TIME
{
    unsigned short micro;
    unsigned short milli;
    unsigned int seconds:8;
    unsigned int minutes:8;
    unsigned int hours:8;
    unsigned short days;

} system_time_t;


/**************************
 * OS Interface functions *
 **************************/

/*
 * Timer type will also store the number of times to repeat
 * if it is of type repeat n. The return value is the timer
 * number, which can be used to interact with the timer afterward.
 */
int start_timer(int type, int repeat, timer_info_t *info, timer_callback_t callback_function);
void get_system_time(system_time_t *system_time);
void cancel_timer(int timer_number);


/*************************************
 * Device Driver Interface functions *
 *************************************/


/*
 * Called by timer driver when timer is done.
 */
void timer_done(int timer_number);



#endif