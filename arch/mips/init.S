/*
 * This file contains functions that allow
 * the kernel to set up the userspace
 */

#include "xc.h"

.section .text

.set noreorder
.set nomips16

.globl create_userspace
.ent create_userspace

create_userspace:
 
    # create userspace program segment
    la      t1,_bmxpupba_address
    la      t2,BMXPUPBA
    sw      t1,0(t2)
       
    # create userspace data segment
    la      t1,_bmxdudba_address
    la      t2,BMXDUDBA
    sw      t1,0(t2)

    # make sure there is no space allocated
    # for kernel program or user program in
    # RAM (yet)

    la      t1,_bmxdudba_address
    la      t2,BMXDKPBA
    sw      t1,0(t2)

    la      t1,BMXDRMSZ     # load address of reg containing RAM size
    lw      t3, 0(t1)       # load size of RAM from read-only reg
    la      t2,BMXDUPBA     # load address of reg containing user program base
    sw      t1,0(t2)        # store size of RAM into user program base

    jr ra

    .end create_userspace


.globl store_kernel_context
.ent store_kernel_context

store_kernel_context:

    la t1, kernel_register_base

    sw sp, SP_BYTE_OFFSET(t1)
    sw fp, FP_BYTE_OFFSET(t1)
    sw gp, GP_BYTE_OFFSET(t1)

    .end store_kernel_context


.globl go_to_main
.ent go_to_main

go_to_main:

    # store kernel context
    la t1, kernel_register_base
    
    sw sp, SP_BYTE_OFFSET(t1)
    sw fp, FP_BYTE_OFFSET(t1)
    sw gp, GP_BYTE_OFFSET(t1)
    sw ra, RA_BYTE_OFFSET(t1)


    # load user context
    la t1, current_task_register_base

    lw sp, SP_BYTE_OFFSET(t1)
    lw fp, FP_BYTE_OFFSET(t1)
    lw gp, GP_BYTE_OFFSET(t1)
    lw ra, RA_BYTE_OFFSET(t1)


    # zero out registers to prevent leaking kernel data
    li t1, 0
    li t2, 0
    li t3, 0
    li t4, 0
    li t5, 0
    li t6, 0
    li t7, 0
    li t8, 0
    li t9, 0

    li s0, 0
    li s1, 0
    li s2, 0
    li s3, 0
    li s4, 0
    li s5, 0
    li s6, 0
    li s7, 0

    li a0, 0
    li a1, 0
    li a2, 0
    li a3, 0

    li v0, 0
    li v1, 0

    # put address of main into EPC
    la t1, main
    mtc0 t1, _CP0_EPC   

    # use mfc0 and mtc0 to switch to user mode
    # something here

    ehb
    eret

    





