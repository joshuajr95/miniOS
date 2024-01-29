/*
 * This is the linker script that is used to
 * link all of the relocatable object files compiled
 * from .c files in the kernel directory into
 * another large relocatable file for that directory.
 * The files in the kernel directory as well as those
 * in the drivers directory are kernel files and
 * thus the sections need to be placed in kernel space.
 * Certain parts of the script are taken from the default
 * linker script for the 
 */

OUTPUT_FORMAT("elf32-tradlittlemips")
OUTPUT_ARCH(pic32mx)


SECTIONS
{
    .config_BFC02FF0 : { KEEP(*(.config_BFC02FF0)) }
    .config_BFC02FF4 : { KEEP(*(.config_BFC02FF4)) }
    .config_BFC02FF8 : { KEEP(*(.config_BFC02FF8)) }
    .config_BFC02FFC : { KEEP(*(.config_BFC02FFC)) }
}

SECTIONS
{
    .text : { *(.text) }
    .data : { *(.data) }
    .bss : { *(.bss) }
    .sbss : { *(.sbss) }


    /* 
     * The following sections are taken from
     * the XC32 default linker script. They are
     * usually not needed but could be useful so
     * they are kept nonetheless.
     */
    .gptab.sdata : { *(.gptab.sdata) }
    .gptab.data : { *(.gptab.data) }
  	.gptab.sbss : { *(.gptab.sbss) }
    .gptab.bss : { *(.gptab.bss) }
  	.mdebug.abi32 : { KEEP(*(.mdebug.abi32)) }
  	.mdebug.abiN32 : { KEEP(*(.mdebug.abiN32)) }
  	.mdebug.abi64 : { KEEP(*(.mdebug.abi64)) }
  	.mdebug.abiO64 : { KEEP(*(.mdebug.abiO64)) }
    .mdebug.eabi32 : { KEEP(*(.mdebug.eabi32)) }
    .mdebug.eabi64 : { KEEP(*(.mdebug.eabi64)) }
    .gcc_compiled_long32 : { KEEP(*(.gcc_compiled_long32)) }
    .gcc_compiled_long64 : { KEEP(*(.gcc_compiled_long64)) }
    /* Stabs debugging sections.  */
    .stab           : { *(.stab) }
    .stabstr        : { *(.stabstr) }
    .stab.excl      : { *(.stab.excl) }
    .stab.exclstr   : { *(.stab.exclstr) }
    .stab.index     : { *(.stab.index) }
    .stab.indexstr  : { *(.stab.indexstr) }
    .comment        : { *(.comment) }
    /* DWARF debug sections.
        Symbols in the DWARF debugging sections are relative to the beginning
        of the section so we begin them at 0.  */
    /* DWARF 1 */
    .debug           : { *(.debug) }
    .line            : { *(.line) }
    /* GNU DWARF 1 extensions */
    .debug_srcinfo   : { *(.debug_srcinfo) }
    .debug_sfnames   : { *(.debug_sfnames) }
    /* DWARF 1.1 and DWARF 2 */
    .debug_aranges   : { *(.debug_aranges) }
    .debug_pubnames  : { *(.debug_pubnames) }
    /* DWARF 2 */
    .debug_info      : { *(.debug_info .gnu.linkonce.wi.*) }
    .debug_abbrev    : { *(.debug_abbrev) }
    .debug_line      : { *(.debug_line) }
    .debug_frame     : { *(.debug_frame) }
    .debug_str       : { *(.debug_str) }
    .debug_loc       : { *(.debug_loc) }
    .debug_macinfo   : { *(.debug_macinfo) }
    /* SGI/MIPS DWARF 2 extensions */
    .debug_weaknames  : { *(.debug_weaknames) }
    .debug_funcnames  : { *(.debug_funcnames) }
    .debug_typenames  : { *(.debug_typenames) }
    .debug_varnames   : { *(.debug_varnames) }
    .debug_pubtypes  : { *(.debug_pubtypes) }
    .debug_ranges    : { *(.debug_ranges) }
    /DISCARD/ : { *(.rel.dyn) }
    .gnu.attributes 0 : { KEEP (*(.gnu.attributes)) }
    /DISCARD/ : { *(.note.GNU-stack) }
    /DISCARD/ : { *(.note.GNU-stack) *(.gnu_debuglink) *(.gnu.lto_*) *(.discard) }
}
