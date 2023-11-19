# Author: Joshua Jacobs-Rebhun
# Date: October 1, 2022
#
#
#
# This file implements the dispatch of system calls to the respective handler
# functions, which are implemented in syscall.c

#include <syscall.h>

.kdata 
syscall_table: .word S0, S1, S2



.ktext

syscall_dispatch:
    la $t0, syscall_table
    sll $v0, $v0, 2
    add $t0, $t0, $v0
    lw $t1, 0($t0)
    jr $t1



S0:

