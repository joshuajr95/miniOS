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

# do I need extra layer of indirection or can I just put 
# exception handler addresses here directly?
exception_table: .word E0, E1, E2, E3, E4, E5, E6, E7, E8


# changed it to .ktext since in kernel code segment
.ktext

general_exception_handler:
    
    # load base address of current task's registers into kernel register
    la $k0, current_task_register_base              
    lw $k1, 0($k0)
    

    # save registers to the current tasks context
    # by iterating over the registers and incrementing
    # the pointer to the regs array by REGISTER_SIZE each time
    addi $k1, $k1, REGISTER_SIZE
    sw $at, 0($k1)

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


# I don't think I need these but will check again tomorrow
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

    la $k0, current_task_register_base              
    lw $k1, 0($k0)

    # load registers from stored context
    addi $k1, $k1, REGISTER_SIZE
	lw $at, 0($k1)


    addi $k1, $k1, REGISTER_SIZE
	lw $v0, 0($k1)

    addi $k1, $k1, REGISTER_SIZE
	lw $v1, 0($k1)


    addi $k1, $k1, REGISTER_SIZE
	lw $a0, 0($k1)

    addi $k1, $k1, REGISTER_SIZE
	lw $a1, 0($k1)

    addi $k1, $k1, REGISTER_SIZE
	lw $a2, 0($k1)

    addi $k1, $k1, REGISTER_SIZE
	lw $a3, 0($k1)


    addi $k1, $k1, REGISTER_SIZE
	lw $t0, 0($k1)

    addi $k1, $k1, REGISTER_SIZE
	lw $t1, 0($k1)

    addi $k1, $k1, REGISTER_SIZE
	lw $t2, 0($k1)

    addi $k1, $k1, REGISTER_SIZE
	lw $t3, 0($k1)

    addi $k1, $k1, REGISTER_SIZE
	lw $t4, 0($k1)

    addi $k1, $k1, REGISTER_SIZE
	lw $t5, 0($k1)

    addi $k1, $k1, REGISTER_SIZE
	lw $t6, 0($k1)

    addi $k1, $k1, REGISTER_SIZE
	lw $t7, 0($k1)


    addi $k1, $k1, REGISTER_SIZE
	lw $s0, 0($k1)

    addi $k1, $k1, REGISTER_SIZE
	lw $s1, 0($k1)

    addi $k1, $k1, REGISTER_SIZE
	lw $s2, 0($k1)

    addi $k1, $k1, REGISTER_SIZE
	lw $s3, 0($k1)

    addi $k1, $k1, REGISTER_SIZE
	lw $s4, 0($k1)

    addi $k1, $k1, REGISTER_SIZE
	lw $s5, 0($k1)

    addi $k1, $k1, REGISTER_SIZE
	lw $s6, 0($k1)

    addi $k1, $k1, REGISTER_SIZE
	lw $s7, 0($k1)


    addi $k1, $k1, REGISTER_SIZE
	lw $t8, 0($k1)

    addi $k1, $k1, REGISTER_SIZE
	lw $t9, 0($k1)


    addi $k1, $k1, REGISTER_SIZE
	lw $gp, 0($k1)

    addi $k1, $k1, REGISTER_SIZE
	lw $sp, 0($k1)

    addi $k1, $k1, REGISTER_SIZE
	lw $fp, 0($k1)

    addi $k1, $k1, REGISTER_SIZE
	lw $ra, 0($k1)


    eret