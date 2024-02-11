/* Author: Joshua Jacobs-Rebhun
 * Date: September 20, 2022
 *
 * 
 * This file implements a number of functions regarding task management.
 */

#include "task.h"

extern void*_user_stack;
extern void _exit_main();


void task_table_init(task_table_t *table)
{
    table->next_available_task_number = 0;

    table->tasks[0].task_id = table->next_available_task_number;
    table->next_available_task_number++;

    table->tasks[0].parent_task_id = TASK_ID_NONE;
    table->tasks[0].state = CREATED;
    table->tasks[0].num_children = 0;
    
    // set up task scheduling linked list with root task
    table->tasks[0].next_task = &table->tasks[0];
    table->tasks[0].previous_task = &table->tasks[0];

    table->current_task = table->root;

    // save root task registers
    table->tasks[0].regs[REGISTER_SP] = _user_stack;
    table->tasks[0].regs[REGISTER_FP] = _user_stack;
    table->tasks[0].regs[REGISTER_RA] = (uint32_t) _exit_main; // need to define in userspace
}

void schedule_next_task(task_table_t *table)
{

}