/* 
 * Author: Joshua Jacobs-Rebhun
 * Date: September 20, 2022
 *
 *
 * This file has the assembly code for performing the context switch.
 * This code will only work for non-Position-Independent Code, since
 * position independent code will use $gp for global data addressing
 * and thus $gp will need to be stored somewhere and restored first
 * thing during context switch.
 */


#include "kdefs.h"




.text
.set noreorder
.set nomips16

.globl _context_switch
.ent _context_switch
_context_switch:

    # save current context of the processor
    la $k0, current_task_register_base
    nop
    lw $k1, 0($k0)
    nop

    sw $at, AT_BYTE_OFFSET($k0)

	sw $v0, V0_BYTE_OFFSET($k1)
	sw $v1, V1_BYTE_OFFSET($k1)

	sw $a0, A0_BYTE_OFFSET($k1)
	sw $a1, A1_BYTE_OFFSET($k1)
	sw $a2, A2_BYTE_OFFSET($k1)
	sw $a3, A3_BYTE_OFFSET($k1)

	sw $t0, T0_BYTE_OFFSET($k1)
    sw $t1, T1_BYTE_OFFSET($k1)
    sw $t2, T2_BYTE_OFFSET($k1)
    sw $t3, T3_BYTE_OFFSET($k1)
    sw $t4, T4_BYTE_OFFSET($k1)
    sw $t5, T5_BYTE_OFFSET($k1)
    sw $t6, T6_BYTE_OFFSET($k1)
    sw $t7, T7_BYTE_OFFSET($k1)

	sw $s0, S0_BYTE_OFFSET($k1)
	sw $s1, S1_BYTE_OFFSET($k1)
	sw $s2, S2_BYTE_OFFSET($k1)
	sw $s3, S3_BYTE_OFFSET($k1)
	sw $s4, S4_BYTE_OFFSET($k1)
	sw $s5, S5_BYTE_OFFSET($k1)
	sw $s6, S6_BYTE_OFFSET($k1)
	sw $s7, S7_BYTE_OFFSET($k1)

    sw $t8, T8_BYTE_OFFSET($k1)
    sw $t9, T9_BYTE_OFFSET($k1)

	sw $gp, GP_BYTE_OFFSET($k1)
	sw $sp, SP_BYTE_OFFSET($k1)
	sw $fp, FP_BYTE_OFFSET($k1)
	sw $ra, RA_BYTE_OFFSET($k1)


    # use the mfc0 instruction to remove the address of the next instruction
    # from the Exception Program Counter (EPC) register in Coprocessor 0 and 
    # store it into the task's context
    mfc0 $k0, $14, 0
    nop

    # store the EPC value (next user instruction to execute) in PC index
    # of user task register array
	sw $k0, PC_BYTE_OFFSET($k1)



    # restore the kernel's stack pointer, frame pointer, and global pointer
    la $k0, kernel_register_base
    nop
    lw $k1, 0($k0)
    nop
    
    
    lw $gp, GP_BYTE_OFFSET($k1)
    lw $sp, SP_BYTE_OFFSET($k1)
    lw $fp, FP_BYTE_OFFSET($k1)
    lw $ra, RA_BYTE_OFFSET($k1)


    # schedule next task. This causes the global variable
    # current_task_register_base to be change to the base
    # address of the register array of the next task to be
    # run. This allows the rest of the context switch code
    # to perform the loading of program context from the
    # new task
    la $a0, task_table
    nop
    jal schedule_next_task
    nop

    # save the kernel's registers
    la $k0, kernel_register_base
    nop
    lw $k1, 0($k0)
    nop
    
    sw $gp, GP_BYTE_OFFSET($k1)
    sw $sp, SP_BYTE_OFFSET($k1)
    sw $fp, FP_BYTE_OFFSET($k1)
    sw $ra, RA_BYTE_OFFSET($k1)


    # load base address of register array for newly scheduled process into
    # register $k1
    la $k0, current_task_register_base
    nop
    lw $k1, 0($k0)
    nop

    # restore processor state from newly scheduled process
    lw $at, AT_BYTE_OFFSET($k0)

	lw $v0, V0_BYTE_OFFSET($k1)
	lw $v1, V1_BYTE_OFFSET($k1)

	lw $a0, A0_BYTE_OFFSET($k1)
	lw $a1, A1_BYTE_OFFSET($k1)
	lw $a2, A2_BYTE_OFFSET($k1)
	lw $a3, A3_BYTE_OFFSET($k1)

	lw $t0, T0_BYTE_OFFSET($k1)
    lw $t1, T1_BYTE_OFFSET($k1)
    lw $t2, T2_BYTE_OFFSET($k1)
    lw $t3, T3_BYTE_OFFSET($k1)
    lw $t4, T4_BYTE_OFFSET($k1)
    lw $t5, T5_BYTE_OFFSET($k1)
    lw $t6, T6_BYTE_OFFSET($k1)
    lw $t7, T7_BYTE_OFFSET($k1)

	lw $s0, S0_BYTE_OFFSET($k1)
	lw $s1, S1_BYTE_OFFSET($k1)
	lw $s2, S2_BYTE_OFFSET($k1)
	lw $s3, S3_BYTE_OFFSET($k1)
	lw $s4, S4_BYTE_OFFSET($k1)
	lw $s5, S5_BYTE_OFFSET($k1)
	lw $s6, S6_BYTE_OFFSET($k1)
	lw $s7, S7_BYTE_OFFSET($k1)

    lw $t8, T8_BYTE_OFFSET($k1)
    lw $t9, T9_BYTE_OFFSET($k1)

	lw $gp, GP_BYTE_OFFSET($k1)
	lw $sp, SP_BYTE_OFFSET($k1)
	lw $fp, FP_BYTE_OFFSET($k1)
	lw $ra, RA_BYTE_OFFSET($k1)

    # write new exception return address from the new processes' saved
    # context to the EPC register
    lw $k0, PC_BYTE_OFFSET($k1)
    nop
    mtc0 $k0, $14
    nop

    # return from exception
    eret



    
