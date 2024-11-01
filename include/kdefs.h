/* Author: Joshua Jacobs-Rebhun
 * Date: September 19, 2022
 *
 * 
 * Defines a number of constants that relate to kernel or system parameters.
 */

#ifndef KDEFS_H
#define KDEFS_H


// number of registers on a MIPS chip
#define NUM_REGS 32

// Defines the maximum number of children that a given task can have.
// Must be less than the number of total tasks
#define MAX_CHILDREN 32

// Defines maximum number of tasks allowed on the system. Used to prevent
// system overload
#define MAX_TASKS 32


// TODO: make configurable
#define ISR_VECTORS 64

#define BYTES_PER_REGISTER 4


#define NULL_POINTER (void*) 0


// define register offsets into register array

#define REGISTER_AT          1

#define REGISTER_V0          2
#define REGISTER_V1          3

#define REGISTER_A0          4
#define REGISTER_A1          5
#define REGISTER_A2          6
#define REGISTER_A3          7

#define REGISTER_T0          8
#define REGISTER_T1          9
#define REGISTER_T2          10
#define REGISTER_T3          11
#define REGISTER_T4          12
#define REGISTER_T5          13
#define REGISTER_T6          14
#define REGISTER_T7          15

#define REGISTER_S0          16
#define REGISTER_S1          17
#define REGISTER_S2          18
#define REGISTER_S3          19
#define REGISTER_S4          20
#define REGISTER_S5          21
#define REGISTER_S6          22
#define REGISTER_S7          23

#define REGISTER_T8          24
#define REGISTER_T9          25

#define REGISTER_K0          26
#define REGISTER_K1          27

#define REGISTER_GP          28
#define REGISTER_SP          29
#define REGISTER_FP          30
#define REGISTER_RA          31
#define REGISTER_PC          32


// define the byte offsets for each register in the register array
// useful for assembly language files that need to access offset of
// particular registers

#define AT_BYTE_OFFSET          4
#define V0_BYTE_OFFSET          8
#define V1_BYTE_OFFSET          12
#define A0_BYTE_OFFSET          16
#define A1_BYTE_OFFSET          20
#define A2_BYTE_OFFSET          24
#define A3_BYTE_OFFSET          28
#define T0_BYTE_OFFSET          32
#define T1_BYTE_OFFSET          36
#define T2_BYTE_OFFSET          40
#define T3_BYTE_OFFSET          44
#define T4_BYTE_OFFSET          48
#define T5_BYTE_OFFSET          52
#define T6_BYTE_OFFSET          56
#define T7_BYTE_OFFSET          60
#define S0_BYTE_OFFSET          64
#define S1_BYTE_OFFSET          68
#define S2_BYTE_OFFSET          72
#define S3_BYTE_OFFSET          76
#define S4_BYTE_OFFSET          80
#define S5_BYTE_OFFSET          84
#define S6_BYTE_OFFSET          88
#define S7_BYTE_OFFSET          92
#define T8_BYTE_OFFSET          96
#define T9_BYTE_OFFSET          100
#define K0_BYTE_OFFSET          104
#define K1_BYTE_OFFSET          108
#define GP_BYTE_OFFSET          112
#define SP_BYTE_OFFSET          116
#define FP_BYTE_OFFSET          120
#define RA_BYTE_OFFSET          124
#define PC_BYTE_OFFSET          128

#endif