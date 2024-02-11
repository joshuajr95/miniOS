/*
 * Kernel initialization routines.
 */

#include "task.h"
#include "kheap.h"
#include "filesystem.h"
#include "misc.h"

/*
 * Defined in arch/mips/userspace.S
 */
extern void create_userspace();


/*
 * Defined in global_structs.c
 */
extern task_table_t task_table;
extern uint32_t *current_task_register_base;
extern uint32_t *kernel_register_base;


/*
 * Linker defined symbols
 */
extern void *_kernel_stack;
extern heap_cb_t kernel_heap_cb;
extern void *_ramdisk_begin;

void init_kernel()
{
    create_userspace();

    task_table_init(&task_table);

    current_task_register_base = &task_table.current_task->regs[0];
    kernel_register_base = &task_table.kernel_regs[0];

    store_kernel_context();
    init_heap(_kheap_begin);
    
    // not configurable right now
    superblock_t superblock;
    superblock.inode_table_start = 2;
    superblock.inode_table_num_blocks = 2;

    memcpy(_ramdisk_begin, &superblock, sizeof(superblock_t));

    init_filesystem();


    // register device drivers
    // register device filesystem


    // stores the kernel context, loads
    // main task context, and
    go_to_main();
}