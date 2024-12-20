# miniOS


MiniOS is a miniature operating system developed for MCUs and embedded systems. It is relatively simple, allowing for faster development of embedded programs than would otherwise be possible with bare-metal development.


### Building miniOS

To build miniOS, navigate to the top-level directory (the same one this README is in) and run the command `make DEVICE=<device> all`, where device is taken from the Supported Devices list. For example, to build for the PIC32MX795F512L microcontroller, run `make DEVICE=PIC32MX795F512L all`. The build process will create the `build` directory and the output files `miniOS.elf` and `miniOS.hex` will appear in that directory.


### Using miniOS

Since miniOS is designed for microcontrollers, it will not reside on the non-volatile storage already. Thus, to use it you will need to include the header(s) for the various system calls and make use of them in your userspace program. Full documentation of the different system calls implemented is given in docs/system_call_interface.md. MiniOS comes with its own build system that wraps the Microchip xc32 toolchain and ensures that the proper files are included and compiled and that the user program will run correctly.


### Supported Devices

Currently, the only devices supported are the PIC32 family of microcontrollers from Microchip.


### Microchip Hardware and MIPS ISA Documentation

There is a large amount of freely available documentation of the hardware that miniOS is designed for. A non-exhaustive list is shown below:

- PIC32MX Family Reference Manual
- PIC32MX5XX/6XX/7XX Family Data Sheet
- MIPS32 M4K Processor Core Software User's Manual
- MIPS Architecture For Programmers Vol. III: Privileged Resource Architecture
- MPLAB XC32 C/C++ Compiler User's Guide for PIC32M MCUs
- MPLAB XC32 Assembler, Linker, and Utilities User's Guide

Currently (at the time I am writing this), all of the above resources can be found online with a simple Google search (I hesitate to include links in case the links change).