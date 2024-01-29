
OUTPUT_FORMAT("elf32-tradlittlemips")
OUTPUT_ARCH(pic32mx)


SECTIONS
{
    .utext : { *(.text) }
    .udata : { *(.data) }

}