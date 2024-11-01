/**
 * @author Joshua Jacobs-Rebhun
 * 
 * This file implements the dispatch of system calls to the respective handler
 * functions, which are implemented in syscall.c
 */



.text
.set noreorder

.globl _syscall_dispatch
.ent _syscall_dispatch
_syscall_dispatch:

    # load syscall table and then load syscall handling routine
    la $t0, syscall_table
    sll $v0, $v0, 2
    add $t0, $t0, $v0
    lw $t1, 0($t0)

    # decrement stack pointer to save return address
    addi $sp, $sp, -4
    sw $ra, 0($sp)

    # jump to syscall handler
    jalr $t1
    nop

    # reload return address
    lw $ra, 0($sp)
    addi $sp, $sp, 4

    jr $ra
    nop

