
# Exception and Interrupt Handling in MIPS Architecture


---

### Processor Interrupt Modes

The MIPS architecture specifies a particular procedure for interrupt and exception handling. This document will describe exception handling in release 2 and later of the MIPS architecture since that is what is used in the PIC32MX795F512L microcontroller.

MIPS allows for 3 different interrupt modes: 

1. Interrupt Compatibility Mode
2. Vectored Interrupt Mode
3. External Interrupt Controller (EIC) Mode.


#### Interrupt Compatibility Mode

Interrupt compatibility mode is the default mode for the processor (i.e. the state it is in on reset) and it does not allow for vectoring of interrupts. In this mode, the interrupts/exceptions are dispatched through the general exception vector offset of 0x180 if the IV bit in the CAUSE register is 0, or to offset 0x200 if IV is 1. This mode is in effect if the IV bit in the CAUSE register is set to 0, if the BEV bit in the STATUS register is set to 1, or if the VS bit in IntCtl is set to 0. This mode is mostly not used but is present on reset of the processor, so it needs to be covered.


#### Vectored Interrupt (VI) Mode

Vectored interrupt mode is the most common mode used by microprocessors and allows the processor to use a priority encoder to give different priorities to different interrupts and to allow different interrupt sources to be dispatched to different offsets from the exception base address (exception base address is covered below). Each different interrupt source is given a unique number, called a vector, and this vector along with a processor setting called the vector spacing is used to determine the interrupt vector offset. Vectored interrupt mode is in effect if the following are all true:

- Config3~VInt~ = 1     (enable vectored interrupts)
- Config3~VEIC~ = 0     (disable external interrupt controller)
- IntCtl~VS~ != 0       (vector spacing not 0)
- Cause~IV~ = 1         (determines whether interrupt uses general exception or special interrupt vector)
- Status~BEV~ = 0       (normal exception operation as opposed to bootstrap operation)

In vectored interrupt mode, there are 6 hardware interrupt sources and 8 vector numbers (0 thru 7), which are dispatched to offsets that are described below.


#### External Interrupt Controller (EIC) Mode

External interrupt controller mode is the mode used in the MIPS M4K core in the PIC32MX795F512L microcontroller and is similar to vectored interrupt mode. This mode is in effect if the following are all true:

- Config3~VEIC~ = 1
- IntCtl~VS~ != 0
- Cause~IV~ = 1
- Status~BEV~ = 0

In this mode, the prioritization of interrupts is handled by an External Interrupt Controller (EIC), and this EIC supplies the processor with the interrupt vector and priority level. The processor then takes care of dispatching the interrupt to the proper offset for the interrupt handler. The interrupt vector numbers for EIC mode range from 1 to 63 (inclusive), and 0 is used for encoding "no interrupt".


### Interrupt/Exception Vector Locations

As noted above, for each interrupt mode the exception handling code is located at specific locations in memory. The specific location depends on the type of the interrupt and the interrupt mode the processor is in. In each mode, the exception/interrupt handlers are placed at offsets from what is known as the exception vector base address. The exception vector base address is determined by the value stored in the Coprocessor 0 EBase register (EBase stands for exception base address). The value of the EBase register on processor reset is 0x80000000, which is the only possible value of the exception vector base address in release 1 of the MIPS architecture, and is done this way to maintain backward compatibility. This default address may not be appropriate for a given microcontroller's memory map (indeed in the PIC32MX795F512L, this is the start address of the RAM) and thus, the value in the EBase register may be changed to be more appropriate for the given microcontroller. There are 4 main exceptions (no pun intended) to the use of the value of EBase for the base address of exceptions. The reset, soft reset, and NMI exceptions are always dispatched to location 0xBFC00000, and EJTAG exceptions are always dispatched to 0xBFC00480 (Reset is the exception that happens when the processor is first turned on, so on power up, the program counter register begins fetching instructions from address 0xBFC00000). Thus, it may make more sense to relocate the base address for exceptions to 0xBFC00000 or somewhere nearby. This would be done in startup code that would be run upon power up.

The addresses for all other exceptions/interrupts are a combination of a vector offset and a base address. As stated above, the base address is determined by the value in EBase. The vector offset is determined by a number of different factors. For example, a TLB refill exception (irrelevant for PIC32MX795F512L since it does not utilize paging at all) always goes to vector offset 0x000, a cache error goes to offset 0x100,and a general exception (system calls, as one example) goes to offset 0x180. For interrupt compatibility mode, all interrupts are vectored to offset 0x200. However, for VI mode and EIC mode the interrupt handler offset is determined by the vector number and the vector spacing. The vector spacing determines how far apart each interrupt handler will be, ranging from a spacing of 32 bytes to 512 bytes. Thus, the formula for the exception vector address is as follows:

        EV Address = EBase + vectorOffset

The vectorOffset part of the above equation is one of the following:
- 0x000 (TLB refill)
- 0x100 (cache error)
- 0x180 (general exception, e.g. syscall)
- vectorOffset = 0x200 + vectorNumber * vectorSpacing (interrupts)

The vector spacing is controlled through the value stored in IntCtl~VS~ in Coprocessor 0.


### Exception Processing

The hardware processing of exceptions/interrupts depends on the type that has occurred. If the EXL bit in the Status register is set, as it is for any exception except for Reset, Soft Reset, Non-Maskable Interrupt (NMI), or Cache Error, the Exception Program Counter (EPC) register in Coprocessor 0 is loaded with the PC at which execution will be restarted. This value will be the address of the next instruction (i.e. excepting instruction + 4) for regular exceptions or the address of excepting instruction if it is branch delay slot. Whether the exception occurred in the branch delay slot will be indicated by the processor setting the BD bit int the Cause register upon occurrance of the exception.


## Use of Exceptions in miniOS

System Calls, integer overflows, traps, and breakpoints all use the general exception vector, and are distinguished by the value in the ExcCode field in the Cause register. Of particular interest are the system calls which are documented in system_call_interface.md. External interrupts from devices are handled by the device driver subsystem, which is documented in device_driver_subsystem.md. The timer interrupt that is used for determining when to perform context switch is handled by the context switch procedure which is documented in context_switch_procedure.md.