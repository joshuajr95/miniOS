/* Author: Joshua Jacobs-Rebhun
 * Date: September 19, 2022
 *
 * 
 * Header file defines a number of global kernel data structures that are
 * relevant to implementing kernel functionality, such as the task table
 * and others.
 */


#ifndef GLOBAL_STRUCTS_H
#define GLOBAL_STRUCTS_H



#include "task.h"
#include "kdefs.h"


// task table and base address
task_table_t task_table;
//task_table_t *TASK_TABLE_BASE_ADDR = &task_table;


// pointer to the base of the register array for the current task
uint32_t *current_task_register_base;

// pointer to the base of the register array for the kernel
uint32_t *kernel_register_base;


void switch_task_regs()
{
    current_task_register_base = task_table.current_task->regs;
}


#endif

