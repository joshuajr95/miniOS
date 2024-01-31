/* Author: Joshua Jacobs-Rebhun
 * Date: September 19, 2022
 *
 * 
 * Header file defines a number of global kernel data structures that are
 * relevant to implementing kernel functionality, such as the task table
 * and others.
 */



#include "task.h"
#include "kdefs.h"


// task table and base address
task_table_t task_table;


/* 
 * Pointer to the base of the register array for the current task.
 * This is necessary to avoid clobbering any registers during the
 * context switch procedure. The base address of the array containing
 * the stored register context for the next scheduled task will be 
 * stored here at the end of the context switch procedure, which will
 * allow the OS to save all of the registers first thing during the
 * next context switch without clobbering any.
 */
uint32_t *current_task_register_base;


/* 
 * Pointer to the base of the register array for the kernel.
 * This is necessary to restore the kernel context during the
 * context switch procedure. It must be global or otherwise the
 * code in context_switch.S would have no way of knowing about the
 * variable.
 */ 
uint32_t *kernel_register_base;


void switch_task_regs()
{
    current_task_register_base = task_table.current_task->regs;
}




