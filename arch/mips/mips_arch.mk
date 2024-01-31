


# BUILD_DIR, CC, AR are exported to this file
# from the top-level Makefile

LIB_DIR = lib
OBJ_DIR = obj
BOOT_DIR = boot

# create arch obj directory if it does not exist
$(shell [ ! -d $(OBJ_DIR) ] && mkdir $(OBJ_DIR) )



#############################################
#											#
#		ADD NEW SOURCE FILES HERE			#
#											#
#############################################

ASM_SOURCES =	context_switch.S				\
				general_exception_handler.S		\
				syscall_dispatch.S

BOOT_SOURCES =	crt0.S		\
				crti.S		\
				crtn.S



ASM_OBJS = $(patsubst %.S, $(OBJ_DIR)/%.o, $(ASM_SOURCES))
BOOT_OBJS = $(patsubst $(BOOT_DIR)/%.S, $(OBJ_DIR)/%.o, $(BOOT_SOURCES))


AR_FLAGS = q
CFLAGS	=
ASM_FLAGS =
BOOT_FLAGS = 


all: mips.a boot.a

mips.a: $(ASM_OBJS)
	$(AR) $(AR_FLAGS) $(LIB_DIR)/$@ $^

boot.a: $(BOOT_OBJS)
	$(AR) $(AR_FLAGS) $(LIB_DIR)/$@ $^


$(ASM_OBJS): $(OBJ_DIR)/%.o: %.S
	$(CC) $(ASM_FLAGS) -c $< -o $@

$(BOOT_OBJS): $(OBJ_DIR)/%.o: $(BOOT_DIR)/%.S
	$(CC) $(BOOT_FLAGS) -c $< -o $@
