# Author: Joshua Jacobs-Rebhun
# Date: September 21, 2022
# 
#
# This file has the assembly code for performing the general exception dispatch.
# This code when compiled will be put 

#include <global_structs.h>

#define CAUSE_REGISTER_MASK 0x00000076

#define TLB_MODIFICATION_EXCEPTION_CODE 1
#define TLB_LOAD_EXCEPTION_CODE 2
#define TLB_STORE_EXCEPTION_CODE 3
#define ADDRESS_LOAD_ERROR_EXCEPTION_CODE 4
#define ADDRESS_STORE_ERROR_EXCEPTION_CODE 5
#define INSTRUCTION_BUS_ERROR_EXCEPTION_CODE 6
#define DATA_BUS_ERROR_EXCEPTION_CODE 7
#define SYSCALL_EXCEPTION_CODE 8

.data
exceptionTable: .word E0, E1, E2, E3, E4, E5, E6, E7, E8


.text

general_exception_handler:
    
    # load base address of current task's registers into kernel register
    la $k0, current_task_register_base              
    lw $k1, 0($k0)

    # save some registers into current task's context
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

    mfc0 $k0, $13
    andi $k0, $k0, CAUSE_REGISTER_MASK

    # exception jump table implementation
    la $t0, exceptionTable
    add $t0, $t0, $k0
    lw $t1, 0($t0)
    jr $t1

E0:
    j end_exception_block

E1:
    j TLB_Modification_Exception

E2:
    j TLB_Load_Exception

E3:
    j TLB_Store_Exception 

E4:
    j Address_Load_Exception

E5:
    j Address_Store_Exception

E6:
    j Instruction_Bus_Error

E7:
    j Data_Bus_Error

E8:
    j Syscall_Exception


# TLB exceptions are not implemented since the MIPS M4K core
# uses a fixed memory mapping as opposed to a TLB
TLB_Modification_Exception:
    j end_exception_block

TLB_Load_Exception:
    j end_exception_block

TLB_Store_Exception:
    j end_exception_block

Address_Load_Exception:
    # deal with error
    j end_exception_block

Address_Store_Exception:
    # deal with error
    j end_exception_block

Instruction_Bus_Error:
    # deal with error
    j end_exception_block

Data_Bus_Error:
    # deal with error
    j end_exception_block

# For MIPS system calls, the system call number must be passed
# in the $v0 register and arguments in the $a0-$a3 registers.
# The syscall exception handler code uses a jump address table
# to jump to the correct syscall handler.
Syscall_Exception:
    jal handle_syscall




end_exception_block:

    la $k0, current_task_register_base              
    lw $k1, 0($k0)

    # save some registers into current task's context
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

    eret