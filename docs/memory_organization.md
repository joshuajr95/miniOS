
# Memory Organization in PIC32 and miniOS


The PIC32 line of microcontrollers implements two separate address spaces: virtual and physical.
All hardware resources including data memory, program flash, boot flash, configuration registers,
special function registers (SFRs), and peripherals are mapped to fixed locations in physical
memory. Virtual addresses are used only by the CPU to access RAM and to fetch and execute
instructions, while peripherals, the DMA controller, and the flash controller use physical
addresses directly. The specific locations of flash, RAM, and various peripherals depends on the
specific processor model and can be found in the PIC32MX Family Reference Manual or in the 
PIC32MX Family Data Sheet (see the README).


### User Mode and Kernel Mode Memory Segments

The MIPS M4K core used the the PIC32 MCUs has both a kernel mode and user mode of operation.
In the same manner as most processor cores, when in kernel mode the processor can access
any meaningful memory address, but when in user mode the processor is restricted to only
user mode memory. The top 2 GB of the virtual address space from 0x80000000 to 0xffffffff
are divided among the 4 kernel segments: KSEG0, KSEG1, KSEG2, KSEG3. The bottom 2 GB of
the virtual address space from 0x00000000 to 0x7fffffff are the user program segment: USEG.