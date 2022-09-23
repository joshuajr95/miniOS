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
#define PC          0

#define AT          1

#define V0          2
#define V1          3

#define A0          4
#define A1          5
#define A2          6
#define A3          7

#define T0          8
#define T1          9
#define T2          10
#define T3          11
#define T4          12
#define T5          13
#define T6          14
#define T7          15

#define S0          16
#define S1          17
#define S2          18
#define S3          19
#define S4          20
#define S5          21
#define S6          22
#define S7          23

#define T8          24
#define T9          25

#define K0          26
#define K1          27

#define GP          28
#define SP          29
#define FP          30
#define RA          31


// defines the byte offset of a given register from the base of the array
#define REGISTER_OFFSET(register) register*4



#endif