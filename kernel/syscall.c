

#include "syscall.h"
#include "ktypes.h"



/*
 * System call table.
 */
void *syscall_table[] = {
    [SYSCALL_CODE_CREATE_TASK] = (void*) do_syscall_create_task
};





taskid_t do_syscall_create_task()
{

}

