/* Author: Joshua Jacobs-Rebhun
 * Date: September 15, 2022
 *
 * 
 * This file defines a number of data structures and functions related to
 * the implementation of tasks in miniOS.
 */

#ifndef TASK_H
#define TASK_H

#include "stdint.h"
#include "kdefs.h"


#define TASK_ID_NONE -1


typedef enum
{
    CREATED,
    RUNNING,
    IDLE,
    TERMINATED

} task_state_t;


/*
 * Defines the task control block data structure used to store data about current
 * tasks. Contains a number of information such as the state, id number, parent,
 * children, and register data for use during context switching.
 */
typedef struct TASK_CONTROL_BLOCK
{
    // enum type holds the current state of the task
    task_state_t state;


    // information about task ids and parent and child tasks
    int task_id;
    int parent_task_id;
    int children_task_ids[MAX_CHILDREN];
    int num_children;


    // next and previous tasks stored in the task list
    struct TASK_CONTROL_BLOCK *next_task;
    struct TASK_CONTROL_BLOCK *previous_task;


    // storage for register data when task is context switched off CPU
    // program counter is at index 0 since register 0 is a constant
    uint32_t regs[NUM_REGS + 1];

} task_control_block_t;





/*
 * Task table data type used for storing currently existing tasks. Maintains
 * the current number of tasks on the system, as well as the head task, tail task
 * and the task linked list. Task control blocks (TCBs) are stored in a hash 
 * table where each TCB has pointers to the previous and next TCB. Thus the 
 * linked list structure is overlayed on top of the hash table data structure.
 */
typedef struct TASK_TABLE
{
    unsigned int num_tasks;
    task_control_block_t *root;
    task_control_block_t *current_task;

    unsigned int next_available_task_number;

    // stores the registers the kernel is using
    uint32_t kernel_regs[NUM_REGS];

    // array of task control blocks used for 
    task_control_block_t tasks[MAX_TASKS];

} task_table_t;


void task_table_init(task_table_t *table);
void schedule_next_task(task_table_t *table);
void insert_task(task_table_t *table);
void delete_task(task_table_t *table);


// function pointer type used for input to the create task function and
// simplifies the function definition interface
typedef void *(*task_function_t)(void *);


// creates a task to run the given function. Returns the task id of 
// the created task
unsigned int create_task(task_function_t function);

// sets the given task into the running mode
void run_task(unsigned int task_id);

// stops the current task from running and sets it into the idle state
void pause_task();

void kill_task(unsigned int task_id);



#endif
