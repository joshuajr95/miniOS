# Author: Joshua Jacobs-Rebhun
# Date: September 20, 2022
# 
#
# This file has the assembly code for performing the context switch.


#include <kdefs.h>



.globl context_switch
.text

context_switch:
    # mtc0 for switch to kernel mode (maybe??)

    # save current context of the processor
    la $k0, current_task_register_base
    lw $k1, 0($k0)

    addi $k1, $k1, REGISTER_SIZE
    sw $at, 0($k0)

    addi $k1, $k1, REGISTER_SIZE
	sw $v0, 0($k1)

    addi $k1, $k1, REGISTER_SIZE
	sw $v1, 0($k1)


    addi $k1, $k1, REGISTER_SIZE
	sw $a0, 0($k1)

    addi $k1, $k1, REGISTER_SIZE
	sw $a1, 0($k1)

    addi $k1, $k1, REGISTER_SIZE
	sw $a2, 0($k1)

    addi $k1, $k1, REGISTER_SIZE
	sw $a3, 0($k1)


    addi $k1, $k1, REGISTER_SIZE
	sw $t0, 0($k1)

    addi $k1, $k1, REGISTER_SIZE
	sw $t1, 0($k1)

    addi $k1, $k1, REGISTER_SIZE
	sw $t2, 0($k1)

    addi $k1, $k1, REGISTER_SIZE
	sw $t3, 0($k1)

    addi $k1, $k1, REGISTER_SIZE
	sw $t4, 0($k1)

    addi $k1, $k1, REGISTER_SIZE
	sw $t5, 0($k1)

    addi $k1, $k1, REGISTER_SIZE
	sw $t6, 0($k1)

    addi $k1, $k1, REGISTER_SIZE
	sw $t7, 0($k1)


    addi $k1, $k1, REGISTER_SIZE
	sw $s0, 0($k1)

    addi $k1, $k1, REGISTER_SIZE
	sw $s1, 0($k1)

    addi $k1, $k1, REGISTER_SIZE
	sw $s2, 0($k1)

    addi $k1, $k1, REGISTER_SIZE
	sw $s3, 0($k1)

    addi $k1, $k1, REGISTER_SIZE
	sw $s4, 0($k1)

    addi $k1, $k1, REGISTER_SIZE
	sw $s5, 0($k1)

    addi $k1, $k1, REGISTER_SIZE
	sw $s6, 0($k1)

    addi $k1, $k1, REGISTER_SIZE
	sw $s7, 0($k1)


    addi $k1, $k1, REGISTER_SIZE
	sw $t8, 0($k1)

    addi $k1, $k1, REGISTER_SIZE
	sw $t9, 0($k1)


    addi $k1, $k1, REGISTER_SIZE
	sw $gp, 0($k1)

    addi $k1, $k1, REGISTER_SIZE
	sw $sp, 0($k1)

    addi $k1, $k1, REGISTER_SIZE
	sw $fp, 0($k1)

    addi $k1, $k1, REGISTER_SIZE
	sw $ra, 0($k1)


    # use the mfc0 instruction to remove the address of the next instruction
    # from the Exception Program Counter (EPC) register in Coprocessor 0 and 
    # store it into the task's context
    mfc0 $k0, $14, 0

    # add 4 bytes to the end of the register array to get location of the
    # program counter. This may not work because compiler may insert spacing
    # into the task control block struct, so probly make function returning
    # the address of the program counter context
    addi $k1, $k1, REGISTER_SIZE
	sw $k0, 0($k1)



    # restore the kernel's stack pointer, frame pointer, and global pointer
    la $k0, kernel_register_base
    lw $k1, 0($k0)

    # calculate the address of the global pointer in the kernel
    # register array as REGISTER_GP *4 (size of registers in bytes)
    
    ###################################################################################
    ### THIS MAY NOT WORK. NEED TO KNOW ABOUT HOW MIPS USES GP FOR GLOBAL DATA      ###
    ### IF GP NEEDS TO BE KNOWN TO ACCESS GLOBAL STRUCTURES THEN CANNOT USE THE     ###
    ### current_task_register_base AND kernel_register_base VARIABLES SINCE MIPS    ###
    ### WILL HAVE NO WAY OF REFERENCING THEM WITHOUT GP BEING PROPERLY DEFINED      ###
    ###################################################################################
    addi $t0, $0, REGISTER_GP
    sll $t0, $t0, 2
    add $k1, $k1, $t0


    lw $gp, 0($k1)
    addi $k1, $k1, REGISTER_SIZE
    lw $sp, 0($k1)
    addi $k1, $k1, REGISTER_SIZE
    lw $fp, 0($k1)


    # schedule next task. This causes the global variable
    # current_task_register_base to be change to the base
    # address of the register array of the next task to be
    # run. This allows the rest of the context switch code
    # to perform the loading of program context from the
    # new task
    la $a0, task_table
    jal schedule_next_task

    # possibly save the kernel's registers ??
    

    # load base address of register array for newly scheduled process into
    # register $k1
    la $k0, current_task_register_base

    # I dont think I need this part since la just puts the label into the $k0 register
    # so no need to load contents at address.
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



    
