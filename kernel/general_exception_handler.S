/* Author: Joshua Jacobs-Rebhun
 * Date: September 21, 2022
 * 
 *
 * This file has the assembly code for performing the general exception dispatch.
 * This code when compiled will be put 
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


# changed it to .kdata since will be in kernel memory
.kdata

# Extra layer of indirection is unnecessary
exception_table: .word E0, E1, E2, E3, E4, E5, E6, E7, E8


# changed it to .ktext since in kernel code segment
.ktext

general_exception_handler:
    
    # load base address of current task's registers into kernel register
    la $k0, current_task_register_base
    lw $k1, 0($k0)


    # save the caller-saved registers, return address,
    # and stack, frame, and global data pointers
    
    sw $t0, T0_BYTE_OFFSET($k1)
    sw $t1, T1_BYTE_OFFSET($k1)
    sw $t2, T2_BYTE_OFFSET($k1)
    sw $t3, T3_BYTE_OFFSET($k1)
    sw $t4, T4_BYTE_OFFSET($k1)
    sw $t5, T5_BYTE_OFFSET($k1)
    sw $t6, T6_BYTE_OFFSET($k1)
    sw $t7, T7_BYTE_OFFSET($k1)
    sw $t8, T8_BYTE_OFFSET($k1)
    sw $t9, T9_BYTE_OFFSET($k1)

    sw $sp, SP_BYTE_OFFSET($k1)
    sw $fp, FP_BYTE_OFFSET($k1)
    sw $gp, GP_BYTE_OFFSET($k1)
    sw $ra, RA_BYTE_OFFSET($k1)

    
    # load the kernel context
    la $k0, kernel_register_base
    lw $k1, 0($k0)

    lw $sp, SP_BYTE_OFFSET($k1)
    lw $fp, FP_BYTE_OFFSET($k1)
    lw $gp, GP_BYTE_OFFSET($k1)
    lw $ra, RA_BYTE_OFFSET($k1)


    mfc0 $k0, $13, 0                                # load the Cause register into $k0
    andi $k0, $k0, CAUSE_EXCCODE_FIELD_MASK         # bitwise and to extract the ExcCode field from Cause
                                                    # do not need to shift right by 2 bits since ExcCode is
                                                    # used to index into exceptionTable, which is word-aligned
                                                    # and thus would need to convert exception number to byte
                                                    # address by shifting left by 2 bits again.


    # exception jump table implementation
    la $t0, exception_table                         # load the base address of the exception table
    add $t0, $t0, $k0                               # add the ExcCode byte address offset to base to get address of exception handler
    lw $t1, 0($t0)                                  # load the address of exception handler
    jr $t1                                          # jump to the address of the exception handler



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
    jal syscall_dispatch
    j end_exception_block



end_exception_block:

    # load the kernel context
    la $k0, kernel_register_base
    lw $k1, 0($k0)

    sw $sp, SP_BYTE_OFFSET($k1)
    sw $fp, FP_BYTE_OFFSET($k1)
    sw $gp, GP_BYTE_OFFSET($k1)
    sw $ra, RA_BYTE_OFFSET($k1)


    la $k0, current_task_register_base              
    lw $k1, 0($k0)


    lw $t0, T0_BYTE_OFFSET($k1)
    lw $t1, T1_BYTE_OFFSET($k1)
    lw $t2, T2_BYTE_OFFSET($k1)
    lw $t3, T3_BYTE_OFFSET($k1)
    lw $t4, T4_BYTE_OFFSET($k1)
    lw $t5, T5_BYTE_OFFSET($k1)
    lw $t6, T6_BYTE_OFFSET($k1)
    lw $t7, T7_BYTE_OFFSET($k1)
    lw $t8, T8_BYTE_OFFSET($k1)
    lw $t9, T9_BYTE_OFFSET($k1)

    lw $sp, SP_BYTE_OFFSET($k1)
    lw $fp, FP_BYTE_OFFSET($k1)
    lw $gp, GP_BYTE_OFFSET($k1)
    lw $ra, RA_BYTE_OFFSET($k1)


    eret