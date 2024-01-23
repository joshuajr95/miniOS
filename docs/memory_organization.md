
# Memory Organization in PIC32 and miniOS


The PIC32 line of microcontrollers implements two separate address spaces: virtual and physical. All hardware resources including data memory, program flash, boot flash, configuration registers, special function registers (SFRs), and peripherals are mapped to fixed locations in physical memory. Virtual addresses are used only by the CPU to access RAM and to fetch and execute instructions, while peripherals, the DMA controller, and the flash controller use physical addresses directly. The specific locations of flash, RAM, and various peripherals depends on the specific processor model and can be found in the PIC32MX Family Reference Manual or in the PIC32MX Family Data Sheet (see the README).


### User Mode and Kernel Mode Memory Segments

The MIPS M4K core used the the PIC32 MCUs has both a kernel mode and user mode of operation. In the same manner as most processor cores, when in kernel mode the processor can access any meaningful memory address, but when in user mode the processor is restricted to only user mode memory. The top 2 GB of the virtual address space from 0x80000000 to 0xffffffff are divided among the 4 kernel segments: KSEG0, KSEG1, KSEG2, KSEG3. The bottom 2 GB of the virtual address space from 0x00000000 to 0x7fffffff are the user program segment: USEG.


### Virtual to Physical Address Translation and Vice-Versa

The PIC32 MCUs implement a fixed memory translation scheme that does not use page tables or TLBs. To translate any of the kernel segment virtual addresses to the corresponding physical addresses, simply perform a bitwise AND operation with the following mask (in hex): 0x1fffffff. This means that all of the kernel segment virtual addresses map to the same set of physical addresses. To translate from physical addresses to KSEG0 virtual addresses or to a KSEG1 virtual address, perform a bitwise OR operation with the mask 0x80000000 or 0xA0000000, respectively. To translate between USEG virtual addresses and physical addresses, add 0x40000000 to the corresponding virtual address. The physical-to-virtual translation would simply be a subtraction of the same value.


### Flash Memory and Data RAM Partitioning

At startup, the kernel segments are active and the user segment is not mapped. In order to make
the user segment active, the bus matrix control registers must be initialized. The flash memory can be partitioned into two segments: a kernel code segment and a user code segment. The RAM, however, can be partitioned into 4 segments: kernel code segment, kernel data segment, user code
segment, and user data segment.

The bus matrix control register used to control the partitioning of flash memory between user program and kernel is BMXPUPBA. To partition flash, it must be initialized as follows: 
    BMXPUPBA = BMXPFMSZ - User_program_size
where BMXPFMSZ is a read-only register that gives the size of the total amount of flash the given MCU model contains. When the BMXPUPBA register is not set (the default value is 0), the user segment is not active and the entire flash memory is mapped as the kernel segment. When it is set, KSEG0 program flash will contain all the virtual addresses from 0x9D000000 to 0x9D000000 + BMXPUPBA - 1 (similar for KSEG1 but with the base address for KSEG1). The user segment program flash virtual addresses will start at 0x7D000000 + BMXPUPBA and go to 0x7D000000 + BMXPFMSZ (BMXPUPBA + User_program_size).

The kernel data RAM partition is always active and is located at virtual address 0x80000000 (KSEG0) or 0xA0000000 (KSEG1). The size of the system's data RAM is stored in the read-only register BMXDRMSZ. The PIC32MX allows both kernel and user code to execute from RAM, which requires configuration using the bus matrix registers. The kernel program RAM partition starts at 0x80000000 + BMXDKPBA (KSEG0) or 0xA0000000 + BMXDKPBA (KSEG1) where BMXDKPBA is the control register that stores the base address of the kernel code in RAM. The kernel program RAM partition size is defined by BMXDUDBA - BMXDKPBA, where BMXDUDBA is the control register that gives the start address of the user data RAM segment. The user data RAM segment starts at virtual address 0x7F000000 + BMXDUDBA and has size BMXDUPBA - BMXDUDBA where BMXDUPBA is the control register that stores the start address of the user program RAM partition. The user program RAM partition starts at 0x7F000000 + BMXDUPBA and goes to 0x7F000000 + BMXDRMSZ. Since each RAM segment starts where the previous segment ends, some of the segments can be configured to not exist by setting the base address of the next segment to be the same as that of the current segment.


#### Potential Issue with Memory Segment Placement in Linker Script

When placing memory regions in the linker script, should the user program segment in flash memory be placed at the user segment base address or at the end of the kernel segment? User segment is not active at startup,
so it may not work to place it at the user segment virtual address. Will need to test this.