
#include "regs.h"

.text
.set noreorder

.globl open
.ent open

# no need for moving arguments into proper registers since
# normal function calls use $a0-$a3 and so do system calls
# also no need to move return value since already returned
# in register $v0
open:
    addi $v0, $0, 6     # move syscall code 6 into $v0
    syscall             # execute syscall
    jr ra              # return from syscall wrapper function
    nop                 # branch delay slot
    
    .end open


