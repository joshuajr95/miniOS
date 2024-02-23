

#include "timers.h"
#include "kdefs.h"


static timer_control_block_t timer_cb;
static timer_callback_table_t callback_table;
static system_time_t previous_system_time;

/*
 * The following three functions are wrappers
 * for accessing the device driver table to find
 * callback functions for a set timer event.
 */

static void set_one_time_hardware_timer(int timer_number, timer_info_t *info)
{
    // TODO: implement
}


static void set_n_times_hardware_timer(int timer_number, timer_info_t *info, int n)
{
    // TODO: implement
}


static void set_repeating_hardware_timer(int timer_number, timer_info_t *info)
{
    // TODO: implement
}


void get_system_time(system_time_t *system_time)
{
    // TODO: implement
}


void init_timer_system()
{
    memset(timer_cb.timers, 0, sizeof(software_timer_t)*MAX_TIMERS);
    memset(timer_cb.timer_bitmap, 0xFF, MAX_TIMERS/8);
    memset(callback_table.handlers, 0, sizeof(timer_callback_table_entry_t)*MAX_TIMER_CALLBACKS);
    memset(callback_table.free_handler_bitmap, 0xff, MAX_TIMER_CALLBACKS/8);
}


/*
 * Returns index at which callback was inserted.
 */
static int add_handler_to_table(timer_callback_t callback)
{
    int index;

    if(IS_CALLBACK_PRESENT(&callback_table, callback))
    {
        index = FIND_CALLBACK_INDEX(&callback_table, callback);
    }
    else
    {
        index = FIND_FIRST_FREE_CALLBACK_INDEX(&callback_table);
        SET_CALLBACK_IN_USE(&callback_table, index);
        callback_table.handlers[index].count++;
        callback_table.handlers[index].handler = callback;
    }
    
    return index;
}

static void remove_handler_from_table(int index)
{
    callback_table.handlers[index].handler = NULL_POINTER;
    callback_table.handlers[index].count = 0;
    SET_CALLBACK_FREE(&callback_table, index);
}


int start_timer(int type, int repeat, timer_info_t *info, timer_callback_t callback_function)
{
    int timer_number;
    software_timer_t *timer;

    timer_number = GET_NEXT_AVAILABLE_TIMER_INDEX(&timer_cb);
    timer = &timer_cb.timers[timer_number];
    SET_TIMER_IN_USE(&timer_cb, timer_number);

    int handler_index = add_handler_to_table(callback_function);
    timer->callback_function_index = handler_index & 0x3F; // AND mask zeroes all but 6 lowest bits

    switch(type)
    {
        case TIMER_TYPE_REPEATING:
            timer->type = 0b00;
            set_repeating_hardware_timer(timer_number, info);
            break;

        case TIMER_TYPE_ONCE:
            timer->type = 0b01;
            set_one_time_hardware_timer(timer_number, info);
            break;

        case TIMER_TYPE_REPEAT_N:
            timer->type = 0b10;
            set_n_times_hardware_timer(timer_number, info, repeat);
            break;
        
        default:
            break;
    }
    
    return timer_number;
}


void cancel_timer(int timer_number)
{
    software_timer_t *timer = &timer_cb.timers[timer_number];
    int callback_index = timer->callback_function_index;

    callback_table.handlers[callback_index].count--;

    if(callback_table.handlers[callback_index].count < 0)
    {
        callback_table.handlers[callback_index].count = 0;
        callback_table.handlers[callback_index].handler = NULL_POINTER;
        SET_CALLBACK_FREE(&callback_table, callback_index);
    }

    memset(timer, 0, sizeof(software_timer_t));
    SET_TIMER_FREE(&timer_cb, timer_number);
    timer_cb.num_timers--;
}
