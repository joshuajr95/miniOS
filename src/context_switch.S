
#include <stddef.h>

#include <task.h>
#include <global_structs.h>



.globl context_switch
.text

context_switch:
    # mtc0 for switch to kernel mode

    # save current context of the processor
    la $k0, current_task_register_base
    lw $k1, 0($k0)

    sw $at, REGISTER_OFFSET(AT)($k1)

    sw $v0, REGISTER_OFFSET(V0)($k1)
    sw $v1, REGISTER_OFFSET(V1)($k1)

    sw $a0, REGISTER_OFFSET(A0)($k1)
    sw $a1, REGISTER_OFFSET(A1)($k1)
    sw $a2, REGISTER_OFFSET(A2)($k1)
    sw $a3, REGISTER_OFFSET(A3)($k1)

    sw $t0, REGISTER_OFFSET(T0)($k1)
    sw $t1, REGISTER_OFFSET(T1)($k1)
    sw $t2, REGISTER_OFFSET(T2)($k1)
    sw $t3, REGISTER_OFFSET(T3)($k1)
    sw $t4, REGISTER_OFFSET(T4)($k1)
    sw $t5, REGISTER_OFFSET(T5)($k1)
    sw $t6, REGISTER_OFFSET(T6)($k1)
    sw $t7, REGISTER_OFFSET(T7)($k1)

    sw $s0, REGISTER_OFFSET(S0)($k1)
    sw $s1, REGISTER_OFFSET(S1)($k1)
    sw $s2, REGISTER_OFFSET(S2)($k1)
    sw $s3, REGISTER_OFFSET(S3)($k1)
    sw $s4, REGISTER_OFFSET(S4)($k1)
    sw $s5, REGISTER_OFFSET(S5)($k1)
    sw $s6, REGISTER_OFFSET(S6)($k1)
    sw $s7, REGISTER_OFFSET(S7)($k1)

    sw $t8, REGISTER_OFFSET(T8)($k1)
    sw $t9, REGISTER_OFFSET(T9)($k1)

    sw $gp, REGISTER_OFFSET(GP)($k1)
    sw $sp, REGISTER_OFFSET(SP)($k1)
    sw $fp, REGISTER_OFFSET(FP)($k1)
    sw $ra, REGISTER_OFFSET(RA)($k1)

    # use the mfc0 instruction to remove the address of the next instruction
    # from Coprocessor 0 and store it into the task's context
    mfc0 $k0, $14
    sw $k0, REGISTER_OFFSET(PC)($k1)


    # restore the kernel's stack pointer, frame pointer, and global pointer
    la $k0, kernel_register_base
    lw $k1, 0($k0)

    lw $gp, REGISTER_OFFSET(GP)($k1)
    lw $sp, REGISTER_OFFSET(SP)($k1)
    lw $fp, REGISTER_OFFSET(FP)($k1)


    # schedule next task
    la $a0, task_table
    jal schedule_next_task

    # possibly save the kernel's registers ??
    

    # load base address of register array for newly scheduled process into
    # register $k1
    la $k0, current_task_register_base
    lw $k1, 0($k0)

    # restore processor state from newly scheduled process
    lw $at, REGISTER_OFFSET(AT)($k1)

    lw $v0, REGISTER_OFFSET(V0)($k1)
    lw $v1, REGISTER_OFFSET(V1)($k1)

    lw $a0, REGISTER_OFFSET(A0)($k1)
    lw $a1, REGISTER_OFFSET(A1)($k1)
    lw $a2, REGISTER_OFFSET(A2)($k1)
    lw $a3, REGISTER_OFFSET(A3)($k1)

    lw $t0, REGISTER_OFFSET(T0)($k1)
    lw $t1, REGISTER_OFFSET(T1)($k1)
    lw $t2, REGISTER_OFFSET(T2)($k1)
    lw $t3, REGISTER_OFFSET(T3)($k1)
    lw $t4, REGISTER_OFFSET(T4)($k1)
    lw $t5, REGISTER_OFFSET(T5)($k1)
    lw $t6, REGISTER_OFFSET(T6)($k1)
    lw $t7, REGISTER_OFFSET(T7)($k1)

    lw $s0, REGISTER_OFFSET(S0)($k1)
    lw $s1, REGISTER_OFFSET(S1)($k1)
    lw $s2, REGISTER_OFFSET(S2)($k1)
    lw $s3, REGISTER_OFFSET(S3)($k1)
    lw $s4, REGISTER_OFFSET(S4)($k1)
    lw $s5, REGISTER_OFFSET(S5)($k1)
    lw $s6, REGISTER_OFFSET(S6)($k1)
    lw $s7, REGISTER_OFFSET(S7)($k1)

    lw $t8, REGISTER_OFFSET(T8)($k1)
    lw $t9, REGISTER_OFFSET(T9)($k1)

    lw $gp, REGISTER_OFFSET(GP)($k1)
    lw $sp, REGISTER_OFFSET(SP)($k1)
    lw $fp, REGISTER_OFFSET(FP)($k1)
    lw $ra, REGISTER_OFFSET(RA)($k1)

    # write new exception return address from the new processes' saved
    # context to the EPC register
    lw $k0, REGISTER_OFFSET(PC)($k1)
    mtc0 $k0, $14

    # return from exception
    eret



    
