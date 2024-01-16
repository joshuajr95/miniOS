# Makefile used for building the MiniOS

SOURCE_DIR =		kernel
INCLUDE_DIR =		include
BUILD_DIR =			build
API_DIR =			api

PREPROCESS_DIR = 	$(BUILD_DIR)/preprocess
OBJ_DIR =			$(BUILD_DIR)/obj


# this needs to be changed to the compiler for
# the PIC32 - xc32 i think
CC = gcc

CFLAGS = 


# target binary name
TARGET=minios

# C source files need separate compilation from the
# MIPS assembly source files
C_SOURCES =		$(SOURCE_DIR)/global_structs.c		\
				$(SOURCE_DIR)/list.c				\
				$(SOURCE_DIR)/task.c


# MIPS assembly sources may need separate treatment
ASM_SOURCES = 	$(SOURCE_DIR)/context_switch.S				\
				$(SOURCE_DIR)/general_exception_handler.S	\
				$(SOURCE_DIR)/syscall_dispatch.S


C_PREPROCESS =		$(patsubst $(SOURCE_DIR)/%.c, $(PREPROCESS_DIR)/%.i, $(C_SOURCES))
ASM_PREPROCESS =	$(patsubst $(SOURCE_DIR)/%.S, $(PREPROCESS_DIR)/%.s, $(ASM_SOURCES))


C_OBJS =	$(patsubst $(SOURCE_DIR)/%.c, $(OBJ_DIR)/%.o, $(C_SOURCES))
ASM_OBJS =	$(patsubst $(SOURCE_DIR)/%.S, $(OBJ_DIR)/%.o, $(ASM_SOURCES))



#########################################################
#					BUILD RULES							#
#########################################################

# static pattern rules to build object files from
# preprocessed intermediate files
$(C_OBJS): $(OBJ_DIR)/%.o: $(PREPROCESS_DIR)/%.i
	$(CC) $(CFLAGS) -c $< -o $@

$(ASM_OBJS): $(OBJ_DIR)/%.o: $(PREPROCESS_DIR)/%.s
	$(CC) -c $< -o $@



# static pattern rules to preprocess source files
$(C_PREPROCESS): $(PREPROCESS_DIR)/%.i: $(SOURCE_DIR)/%.c
	$(CC) -E $< -o $@

$(ASM_PREPROCESS): $(PREPROCESS_DIR)/%.s: $(SOURCE_DIR)/%.S
	$(CC) -E $< -o $@


$(BUILD_DIR)/$(TARGET): $(C_OBJS) $(ASM_OBJS)
	$(CC) $^ -o $@





