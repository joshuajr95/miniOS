
# System Call Interface Implementation in MiniOS



System calls are the primary way in which user programs interact with the operating system and the hardware. They allow the user to send and receive data over serial ports or the network, create new tasks, and anything else that they might need to do with a microcontroller.


### User Space System Call Implementation

To make a system call in MIPS, the user code must place the system call code (also known as the system call number) in the `$v0` register and any arguments to the system call in the `$a0`-`$a3` registers and then execute the `syscall` instruction. If there are more than four arguments (32-bit arguments, may be more or less depending on the size of the data types passed to the function) to the system call, then the remaining arguments will be passed on the stack. To maintain compatibility with the XC32 compiler calling conventions, space will be allocated on the stack for the arguments in `$a0`-`$a3` but the values of the data at these locations on the stack will be undefined. The argument order on the stack is that the 1st argument is at the lowest address and each successive argument is at a higher address. Thus the data on the stack from `$sp` to `$sp` + 16 is undefined since this is where the `$a0`-`$a3` space is allocated.

Since many users may want to write the userspace code in C/C++, miniOS contains some C/C++ API functions that wrap the system calls. These functions are declared and defined in the `api` directory and are organized by system call type. For example, all of the task-related system calls such as creating and destroying tasks are declared in `api/task.h` and defined in `api/task.S`. The system call numbers are documented in the System Call Numbers section below.


### Kernel Space System Call Implementation

When the user executes the `syscall` instruction, a system call exception occurs and the processor immediately jumps to the address of the general exception handler (see mips_exception_handling.md). The ExcCode field in the Cause register is set with the value indicating that a system call exception has occurred, and the general exception handler jumps to the syscall_dispatch function, which will index into the system call table using the system call number and jump to the callback routine stored in the table. This routine will perform the functionality of the system call and place any return value in the `$v0` and `$v1` registers.


### System Call Numbers


| System Call Number | System Call Name         |
| ------------------ | ------------------------ |
| 0                  | create_task              |
| 1                  | kill_task                |
| 2                  | yield                    |
| 3                  | wait                     |
| 4                  | waitpid                  |
| 5                  | exit                     |
| 6                  | open                     |
| 7                  | close                    |
| 8                  | read                     |
| 9                  | write                    |
| 10                 | mkfile                   |
| 11                 | mkdir                    |
| ??                 | register_event_handler   |

