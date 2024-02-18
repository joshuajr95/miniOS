

#include "syscall.h"
#include "ktypes.h"
#include "task.h"


extern task_table_t task_table;



/*
 * System call table implementation. This stores the
 * handler function for each system call. Since each
 * system call may have different parameter types and
 * even different numbers of parameters, it is difficult
 * (or impossible) to declare the syscall table using function
 * pointers. Thus, each handler function is cast to a void *
 * pointer before being inserted into the system call table.
 * As long as the system call/function call ABI is not interfered
 * with, this typecasting should not affect the working of
 * these functions. For example, in MIPS, the system call
 * wrapper functions will load the arguments to the system call
 * into the a0-a3 registers, and the system call number into v0.
 * The system call dispatch code will use v0 to select the correct
 * handler function, and the handler function will use the a0-a3
 * registers for arguments to the function. As long as the syscall
 * dispatch code does not modify the a0-a3 registers and the syscall
 * handler function has the same number and type of arguments as the
 * syscall userspace wrapper function, the ABI is unchanged and should
 * work properly.
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





taskid_t do_syscall_create_task(void *function)
{
    taskid_t current_task_id = get_current_task(&task_table);
    taskid_t child_task_id = create_task(&task_table, current_task_id, function);
    schedule_next_task(&task_table);

    // store return value from syscall into task context
    set_task_register_value(&task_table, current_task_id, REGISTER_V0, child_task_id);

    return child_task_id;
}


int do_syscall_kill_task(taskid_t task_id)
{

}

