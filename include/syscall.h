

#ifndef SYSCALL_H
#define SYSCALL_H


#include "ktypes.h"


/*
 * Macros defining the system call codes.
 */
#define SYSCALL_CODE_CREATE_TASK        0
#define SYSCALL_CODE_KILL_TASK          1
#define SYSCALL_CODE_YIELD              2
#define SYSCALL_CODE_WAIT               3
#define SYSCALL_CODE_WAITPID            4
#define SYSCALL_CODE_EXIT               5
#define SYSCALL_CODE_OPEN               6
#define SYSCALL_CODE_CLOSE              7
#define SYSCALL_CODE_READ               8
#define SYSCALL_CODE_WRITE              9



#define __SYSCALL   // empty macro for now, may need to use in the future


taskid_t do_syscall_create_task();








#endif

