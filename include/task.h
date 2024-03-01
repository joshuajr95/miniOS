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
#include "ktypes.h"


#define TASK_ID_NONE -1


#define ERROR_TASK_TABLE_FULL       -1
#define ERROR_TASK_NOT_FOUND        -2



/*
 * TODO: Change this enum to a more complete one 
 * (CREATED probably doesn't need to exist, but a
 * BLOCKED state should).
 */
typedef enum
{
    CREATED,
    RUNNING,
    BLOCKED,
    READY,
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
    taskid_t task_id;
    taskid_t parent_task_id;
    taskid_t child_task_ids[MAX_CHILDREN];
    unsigned int child_task_bitmask;
    int num_children;

    /*
     * This variable gives the index into the stack table,
     * which holds the top (highest address) of the stack
     * for a given task.
     */
    int stack_index;

    /*
     * Used by main task since no index.
     */
    task_stack_t *stack;
    


    // next and previous tasks stored in the task list
    struct TASK_CONTROL_BLOCK *next_task;
    struct TASK_CONTROL_BLOCK *previous_task;


    // storage for register data when task is context switched off CPU
    // program counter is at index 0 since register 0 is a constant
    uint32_t regs[NUM_REGS + 1];

} task_control_block_t;


#define IS_CHILD_ACTIVE(_task_control_block, _index)                                \
    __extension__ ({                                                                \
        int in_use;                                                                 \
        unsigned short mask = 0x1 << _index;                                        \
        in_use = ((_task_control_block)->child_task_bitmask & mask) >> _index;      \
        in_use;                                                                     \
    })


#define SET_CHILD_ACTIVE(_task_control_block, _index)       \
    unsigned short mask = 0x1 << _index;                    \
    (_task_control_block)->child_task_bitmask |= mask;

#define SET_CHILD_INACTIVE(_task_control_block, _index)     \
    unsigned short mask = ~(0x1 << _index);                 \
    (_task_control_block)->child_task_bitmask &= mask;


#define FIRST_FREE_CHILD_INDEX(_task_control_block)             \
    __extension__ ({                                            \
        int index;                                              \
        for(index = 0; index < MAX_CHILDREN; index++)           \
        {                                                       \
            if(IS_CHILD_ACTIVE(_task_control_block, index))     \
            {                                                   \
                break;                                          \
            }                                                   \
        }                                                       \
        if(index >= MAX_CHILDREN) index = -1;                   \
        index;                                                  \
    })




/*
 * Used to represent a usable stack starting point
 * for a given task. MiniOS will allocate stacks
 * in a recursive manner, bisecting the total stack
 * space, with each new task created.
 */
typedef struct TASK_STACK
{
    void *top;

} task_stack_t;



/*
 * This structure is used to keep track of
 * the stacks used for the tasks.
 * 
 * To allocate a stack region to a given task, miniOS
 * will start (with main) by allocating the stack at 
 * the top of the global stack region and that task will
 * have the entire global stack region to itself. The next 
 * task will have its stack allocated halfway down the
 * global stack region, effectively splitting the total
 * size of both program's stacks in half. The next two
 * tasks will have their stacks allocated so that they split
 * the two previous tasks' stack spaces in half, and the
 * next four will split those in half, etc. Thus, the
 * stack allocation process is a form of recursive
 * spatial partitioning.
 * 
 * This data structure is needed to ensure that stacks
 * are not allocated all at one end of the stack region,
 * or grouped together, but are spread relatively evenly
 * throughout the global stack region. Since the spatial
 * partitioning can be thought of as a type of binary
 * search, recursively splitting each stack region in half,
 * the data structure is organized as a binary search tree.
 * The data structure has a member to keep track of the
 * first stack that is in use by the program, the main
 * function stack, and it also keeps an array of stacks
 * that can be used when new tasks are created. The
 * elements of the array "stacks" are organized as a 
 * complete binary search tree based on the address of
 * the top (highest address) of the stack. Each node
 * contains the address of the beginning of a task stack
 * and effectively divides a larger stack region into two
 * sub-regions of equal size. Its left and right children
 * further divide each of those regions into equal-sized
 * sub-regions. The tree is serialized into the array
 * using level-order traversal (since it is a complete
 * binary tree) and the macros below are used to find
 * and manipulate child and parent indices.
 */
typedef struct STACK_CONTROL_BLOCK
{
    task_stack_t main_stack;
    task_stack_t stacks[MAX_TASKS - 1];

    uint32_t free_stack_bitmap;

} stack_control_block_t;



#define NO_INDEX -1
#define ABSOLUTE_TOP -2
#define ABSOLUTE_BOTTOM -3


#define SET_STACK_FREE(_stack_control_block, _index)        \
    int mask = 0x1 << _index;                               \
    (_stack_control_block)->free_stack_bitmap |= mask;

#define SET_STACK_IN_USE(_stack_control_block, _index)      \
    int mask = ~(0x1 << _index);                            \
    (_stack_control_block)->free_stack_bitmap &= mask;



#define IS_STACK_FREE(_stack_control_block, _index)                                 \
    __extension__ ({                                                                \
        int mask = 0x1 << _index;                                                   \
        int is_free;                                                                \
        is_free = ((_stack_control_block)->free_stack_bitmap & mask) >> _index;     \
        is_free;                                                                    \
    })


#define IS_RIGHT_CHILD(_index)                          \
    __extension__ ({                                    \
        int is_right;                                   \
        is_right = (_index > 0 && (_index % 2 == 0));   \
        is_right;                                       \
    })


#define IS_LEFT_CHILD(_index)                           \
    __extension__ ({                                    \
        int is_left;                                    \
        is_left = (_index % 2 == 1);                    \
        is_left;                                        \
    })


#define LEFT_CHILD_INDEX(_index)                        \
    __extension__ ({                                    \
        int left_child;                                 \
        left_child = 2*_index + 1;                      \
        left_child;                                     \
    })

#define RIGHT_CHILD_INDEX(_index)                       \
    __extension__ ({                                    \
        int right_child;                                \
        right_child = 2*_index + 2;                     \
        right_child;                                    \
    })


#define PARENT_INDEX(_index)                            \
    __extension__ ({                                    \
        int parent;                                     \
        if(IS_RIGHT_CHILD(_index))                      \
        {                                               \
            parent = (_index - 2)/2;                    \
        }                                               \
        else if(IS_LEFT_CHILD(_index))                  \
        {                                               \
            parent = (_index - 1)/2;                    \
        }                                               \
        else                                            \
        {                                               \
            parent = NO_INDEX;                          \
        }                                               \
        parent;                                         \
    })


#define GET_NEXT_LOWEST_STACK_INDEX(_index)                                     \
    __extension__ ({                                                            \
        int current = _index;                                                   \
        int lowest_index;                                                       \
        while(PARENT_INDEX(current) != NO_INDEX && IS_LEFT_CHILD(current))      \
        {                                                                       \
            current = PARENT_INDEX(current);                                    \
        }                                                                       \
        if(current == 0)                                                        \
        {                                                                       \
            lowest_index = ABSOLUTE_BOTTOM;                                     \
        }                                                                       \
        else                                                                    \
        {                                                                       \
            lowest_index = PARENT_INDEX(current);                               \
        }                                                                       \
        lowest_index;                                                           \
    })


#define GET_NEXT_HIGHEST_STACK_INDEX(_index)                                    \
    __extension__ ({                                                            \
        int current = _index;                                                   \
        int highest_index;                                                      \
        while(PARENT_INDEX(current) != NO_INDEX && IS_RIGHT_CHILD(current))     \
        {                                                                       \
            current = PARENT_INDEX(current);                                    \
        }                                                                       \
        if(current == 0)                                                        \
        {                                                                       \
            highest_index = ABSOLUTE_TOP;                                       \
        }                                                                       \
        else                                                                    \
        {                                                                       \
            highest_index = PARENT_INDEX(current);                              \
        }                                                                       \
        highest_index;                                                          \
    })




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

    stack_control_block_t task_stacks;

    // bitmap uses MAX_TASKS (32) bits 
    uint32_t free_task_bitmap;

    // stores the registers the kernel is using
    uint32_t kernel_regs[NUM_REGS];

    // array of task control blocks used for 
    task_control_block_t tasks[MAX_TASKS];

} task_table_t;


/*
 * These macros manipulate the free task bitmask
 * to keep track of which indices into the task
 * table are free for use.
 */
#define SET_TASK_FREE(_task_table, _task_index)                 \
    unsigned int mask = 0x1;                                    \
    (_task_table)->free_task_bitmap |= (mask << _task_index);


#define SET_TASK_IN_USE(_task_table, _task_index)               \
    unsigned int mask = 0x1;                                    \
    (_task_table)->free_task_bitmap &= ~(mask << _task_index);



#define IS_TASK_FREE(_task_table, _task_index)                              \
    __extension__ ({                                                        \
        int is_free = 0;                                                    \
        unsigned int mask = 0x1 << _task_index;                             \
        is_free = ((_task_table)->free_task_bitmap & mask) >> _task_index;  \
        is_free;                                                            \
    })


#define GET_NEXT_FREE_TASK_INDEX(_task_table)                               \
    __extension__ ({                                                        \
        int free_index;                                                     \
        for(free_index = 0; free_index < MAX_TASKS; free_index++)           \
        {                                                                   \
            if(IS_TASK_FREE(_task_table, free_index))                       \
            {                                                               \
                break;                                                      \
            }                                                               \
        }                                                                   \
        if(free_index == MAX_TASKS) free_index = -1;                        \
        free_index;                                                         \
    })





void task_table_init(task_table_t *table);
void schedule_next_task(task_table_t *table);
task_control_block_t *get_task(task_table_t *table, int task_id);

taskid_t get_current_task(task_table_t *table);

int set_task_register_value(task_table_t *table, int task_id, int register_number, unsigned int value);


/*
 * Creates a new task to run the given function. 
 * Returns the task id of the created task.
 */ 
taskid_t create_task(task_table_t *table, int parent_task_id, void *function);
void kill_task(unsigned int task_id);   // kills all children as well
void exit_task(task_table_t *table);    // parent inherits children
void run_task(int task_id);
void yield_task(int task_id);
void sleep_task(task_table_t *table);

// stops the current task from running and sets it into the idle state
void wait_on_task();



#endif
