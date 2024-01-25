

#include "syscall.h"
#include "ktypes.h"



/*
 * System call table.
 */
void *syscall_table[] = {
    [SYSCALL_CODE_CREATE_TASK]  = __SYSCALL_TABLE__ do_syscall_create_task,
    [SYSCALL_CODE_KILL_TASK]    = __SYSCALL_TABLE__ do_syscall_kill_task,
    [SYSCALL_CODE_YIELD]        = __SYSCALL_TABLE__ do_syscall_yield,
    [SYSCALL_CODE_WAIT]         = __SYSCALL_TABLE__ do_syscall_wait,
    [SYSCALL_CODE_WAITPID]      = __SYSCALL_TABLE__ do_syscall_waitpid,
    [SYSCALL_CODE_EXIT]         = __SYSCALL_TABLE__ do_syscall_exit,
    [SYSCALL_CODE_OPEN]         = __SYSCALL_TABLE__ do_syscall_open,
    [SYSCALL_CODE_CLOSE]        = __SYSCALL_TABLE__ do_syscall_close
};





taskid_t do_syscall_create_task()
{

}


int do_syscall_kill_task(taskid_t task_id)
{

}

