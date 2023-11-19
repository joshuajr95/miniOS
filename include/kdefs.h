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
#define MAX_TASKS 64


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


// Deprecated since C preprocessor will not perform mathematical operations
// defines the byte offset of a given register from the base of the array
//#define REGISTER_OFFSET(register) register*4



#endif