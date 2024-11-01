/* Author: Joshua Jacobs-Rebhun
 * Date: September 21, 2022
 * 
 *
 * This file has the assembly code for performing the general exception dispatch.
 */


// mask for extracting the ExcCode field in the 
// cause register
#define CAUSE_EXCCODE_FIELD_MASK    0x0000007c


// macros for defining the exception codes
// placed in the ExcCode field in the Cause
// register

#define INTERRUPT_EXCEPTION_CODE                        0x00
#define TLB_MODIFICATION_EXCEPTION_CODE                 0x01
#define TLB_LOAD_EXCEPTION_CODE                         0x02
#define TLB_STORE_EXCEPTION_CODE                        0x03
#define ADDRESS_LOAD_ERROR_EXCEPTION_CODE               0x04
#define ADDRESS_STORE_ERROR_EXCEPTION_CODE              0x05
#define INSTRUCTION_BUS_ERROR_EXCEPTION_CODE            0x06
#define DATA_BUS_ERROR_EXCEPTION_CODE                   0x07
#define SYSCALL_EXCEPTION_CODE                          0x08


// define size of registers - 4 for 32-bit systems, 2 for 
// 16-bit systems, and 8 for 64-bit systems

#define REGISTER_SIZE       4       // in bytes


.data


exception_table: .word E0, E1, E2, E3, E4, E5, E6, E7, E8


.section .text.general_exception, code
.set noreorder
.set noat
.set nomips16
.globl _general_exception_context
.ent _general_exception_context


/*
 * This is the name of the function that will be
 * targeted by the xc32 toolchain for handling of
 * general exceptions. The toolchain will place a
 * jump instruction at _ebase + 0x180 that jumps to
 * the label _general_exception_context
 */
_general_exception_context:
    
    # load base address of current task's registers into kernel register
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

    
    # load the kernel context
    la $k0, kernel_register_base
    nop
    lw $k1, 0($k0)
    nop

    lw $sp, SP_BYTE_OFFSET($k1)
    lw $fp, FP_BYTE_OFFSET($k1)
    lw $gp, GP_BYTE_OFFSET($k1)
    lw $ra, RA_BYTE_OFFSET($k1)


    mfc0 $k0, $13, 0                                # load the Cause register into $k0
    nop
    andi $k0, $k0, CAUSE_EXCCODE_FIELD_MASK         # bitwise and to extract the ExcCode field from Cause
                                                    # do not need to shift right by 2 bits since ExcCode is
                                                    # used to index into exceptionTable, which is word-aligned
                                                    # and thus would need to convert exception number to byte
                                                    # address by shifting left by 2 bits again.


    # exception jump table implementation
    la $t0, exception_table                         # load the base address of the exception table
    nop
    add $t0, $t0, $k0                               # add the ExcCode byte address offset to base to get address of exception handler
    lw $t1, 0($t0)                                  # load the address of exception handler
    nop
    jr $t1                                          # jump to the address of the exception handler
    nop



E0:
    j end_exception_block
    nop

E1:
    j TLB_Modification_Exception
    nop

E2:
    j TLB_Load_Exception
    nop

E3:
    j TLB_Store_Exception
    nop

E4:
    j Address_Load_Exception
    nop

E5:
    j Address_Store_Exception
    nop

E6:
    j Instruction_Bus_Error
    nop

E7:
    j Data_Bus_Error
    nop

E8:
    j Syscall_Exception
    nop


# TODO

# TLB exceptions are not implemented since the MIPS M4K core
# uses a fixed memory mapping as opposed to a TLB
TLB_Modification_Exception:
    j end_exception_block
    nop

TLB_Load_Exception:
    j end_exception_block
    nop

TLB_Store_Exception:
    j end_exception_block
    nop

Address_Load_Exception:
    # deal with error
    j end_exception_block
    nop

Address_Store_Exception:
    # deal with error
    j end_exception_block
    nop

Instruction_Bus_Error:
    # deal with error
    j end_exception_block
    nop

Data_Bus_Error:
    # deal with error
    j end_exception_block
    nop


# For MIPS system calls, the system call number must be passed
# in the $v0 register and arguments in the $a0-$a3 registers.
# The syscall exception handler code uses a jump address table
# to jump to the correct syscall handler.
Syscall_Exception:
    jal syscall_dispatch
    nop
    j end_exception_block
    nop



end_exception_block:

    # load the kernel context
    la $k0, kernel_register_base
    nop
    lw $k1, 0($k0)
    nop

    sw $sp, SP_BYTE_OFFSET($k1)
    sw $fp, FP_BYTE_OFFSET($k1)
    sw $gp, GP_BYTE_OFFSET($k1)
    sw $ra, RA_BYTE_OFFSET($k1)


    la $k0, current_task_register_base
    nop
    lw $k1, 0($k0)
    nop


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
    nop


    eret