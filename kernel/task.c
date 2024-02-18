/* Author: Joshua Jacobs-Rebhun
 * Date: September 20, 2022
 *
 * 
 * This file implements a number of functions regarding task management.
 */

#include "task.h"
#include "stdlib.h"

extern void *_user_stack;
extern void *_user_heap_end;
extern void _exit_main(int status);
extern void _exit_task(int status);
extern uint32_t *current_task_register_base;


static void init_stack_control_block(stack_control_block_t *stacks)
{
    stacks->main_stack.top = _user_stack;
    stacks->free_stack_bitmap = 0xFFFFFFFF;

    // stacks must be aligned to 8-byte boundary
    stacks->stacks[0].top = (void*)(((_user_stack - _user_heap_end)/2) & 0xFFFFFFF8);

    for(int i = 1; i < MAX_TASKS - 1; i++)
    {
        if(IS_LEFT_CHILD(i))
        {
            int parent_index = PARENT_INDEX(i);
            int next_lowest_index = GET_NEXT_LOWEST_STACK_INDEX(i);

            if(next_lowest_index == ABSOLUTE_BOTTOM)
            {
                // aligned to 8-byte boundary
                stacks->stacks[i].top = ((stacks->stacks[parent_index].top - _user_heap_end)/2) & 0xFFFFFFF8;
            }
            else
            {
                // aligned to 8-byte boundary
                stacks->stacks[i].top = ((stacks->stacks[parent_index].top - 
                    stacks->stacks[next_lowest_index].top)/2) & 0xFFFFFFF8;
            }
        }
        else
        {
            int parent_index = PARENT_INDEX(i);
            int next_highest_index = GET_NEXT_HIGHEST_STACK_INDEX(i);

            if(next_highest_index == ABSOLUTE_TOP)
            {
                // aligned to 8-byte boundary
                stacks->stacks[i].top = ((_user_stack - stacks->stacks[parent_index].top)/2) & 0xFFFFFFF8;
            }
            else
            {
                // aligned to 8-byte boundary
                stacks->stacks[i].top = ((stacks->stacks[next_highest_index].top - 
                    stacks->stacks[parent_index].top)/2) & 0xFFFFFFF8;
            }
        }
    }
}


static int get_next_available_stack_index(stack_control_block_t *stack_cb)
{
    int index;

    for(index = 0; index < MAX_TASKS; index++)
    {
        if(IS_STACK_FREE(stack_cb, index))
        {
            break;
        }
    }

    return (index < MAX_TASKS) ? index : -1;
}


void task_table_init(task_table_t *table)
{
    table->next_available_task_number = 0;

    // zero out task table
    memset(table->tasks, 0, sizeof(task_control_block_t)*MAX_TASKS);

    // set all bits in bitmask to free
    memset(table->free_task_bitmap, 0xff, MAX_TASKS/8);

    // initialize the stack management data structure
    init_stack_control_block(&table->task_stacks);

    table->tasks[0].task_id = table->next_available_task_number;
    table->next_available_task_number++;

    table->tasks[0].parent_task_id = TASK_ID_NONE;
    table->tasks[0].state = CREATED;
    table->tasks[0].num_children = 0;
    SET_TASK_IN_USE(table, 0);

    table->tasks[0].stack = &table->task_stacks.main_stack;
    table->tasks[0].stack_index = -1;
    
    // set up task scheduling linked list with root task
    table->tasks[0].next_task = &table->tasks[0];
    table->tasks[0].previous_task = &table->tasks[0];

    table->current_task = table->root;

    // save root task registers
    table->tasks[0].regs[REGISTER_SP] = _user_stack;
    table->tasks[0].regs[REGISTER_FP] = _user_stack;
    table->tasks[0].regs[REGISTER_RA] = _exit_main; // need to define in userspace
}


void schedule_next_task(task_table_t *table)
{
    table->current_task = table->current_task->next_task;
    current_task_register_base = table->current_task->regs;
}

task_control_block_t *get_task(task_table_t *table, int task_id)
{
    task_control_block_t *task = NULL_POINTER;

    for(int i = 0; i < MAX_TASKS; i++)
    {
        if(!IS_TASK_FREE(table, i) && task_id == table->tasks[i].task_id)
            task = &table->tasks[i];
    }

    return task;
}

void run_task(int task_id)
{
    // TODO: Implement setting task into running state
}


taskid_t create_task(task_table_t *table, int parent_task_id, void *function)
{

    // get next free task
    int index = GET_NEXT_FREE_TASK_INDEX(table);
    if(index < 0) return ERROR_TASK_TABLE_FULL;
    task_control_block_t *new_task = &table->tasks[index];
    SET_TASK_IN_USE(table, index);

    // find parent task and return error if not found
    task_control_block_t *parent_task = get_task(table, parent_task_id);
    if(parent_task == NULL_POINTER) return ERROR_TASK_NOT_FOUND;
    
    // get the next available stack region and add to task control block
    int stack_index = get_next_available_stack_index(&table->task_stacks);
    SET_STACK_IN_USE(&table->task_stacks, stack_index);
    new_task->stack_index = stack_index;
    new_task->stack = &table->task_stacks.stacks[stack_index];

    // get next task ID for new task
    new_task->task_id = table->next_available_task_number;
    table->next_available_task_number++;

    // init task regs
    memset(new_task->regs, 0, (NUM_REGS+1)*BYTES_PER_REGISTER);
    new_task->regs[REGISTER_SP] = new_task->stack->top;
    new_task->regs[REGISTER_FP] = new_task->stack->top;
    new_task->regs[REGISTER_RA] = _exit_task;
    new_task->regs[REGISTER_PC] = function;

    // init new task child tasks
    new_task->num_children = 0;
    memset(new_task->child_task_ids, 0, sizeof(int)*MAX_CHILDREN);
    memset(new_task->child_task_bitmask, 0, MAX_CHILDREN/8);

    // add to scheduling list
    task_control_block_t *next_task = table->current_task->next_task;
    next_task->previous_task = new_task;
    new_task->next_task = next_task;
    table->current_task->next_task = new_task;
    new_task->previous_task = table->current_task;
    
    // add new task to children of parent
    new_task->parent_task_id = parent_task_id;
    int child_index = FIRST_FREE_CHILD_INDEX(parent_task);
    SET_CHILD_ACTIVE(parent_task, child_index);
    parent_task->child_task_ids[child_index] = new_task->task_id;
    parent_task->num_children++;

    table->num_tasks++;

    return new_task->task_id;
}