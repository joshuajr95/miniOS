

# BUILD_DIR, CC, AR are exported to this file
# from the top-level Makefile


DIRNAME = $(shell basename "$$PWD")
OBJ_DIR = $(BUILD_DIR)/$(DIRNAME)

# create kernel build directory if it does not exist
$(shell [ ! -d $(OBJ_DIR) ] && mkdir $(OBJ_DIR) )


#############################################
#											#
#		ADD NEW SOURCE FILES HERE			#
#											#
#############################################

KERNEL_SRCS =	filesystem.c		\
				global_structs.c	\
				list.c				\
				syscall.c			\
				task.c				\
				init.c


# kernel object files are in build/{current_dir}
KERNEL_OBJS = $(patsubst %.c, $(OBJ_DIR)/%.o, $(KERNEL_SRCS))


# empty for now
CFLAGS =

AR_FLAGS = q

# For partial linking, do not include crt0.o or any C standard
# library files or any default libraries. Also, the output file
# should another relocatable object file, not an executable.
LINK_FLAGS = -nostartfiles -nodefaultlibs -nostdlib --relocatable


all: $(DIRNAME).a


# build the kernel directory relocatable file from the 
# individual relocatable files corresponding to each
$(DIRNAME).a: $(KERNEL_OBJS)
	$(AR) $(AR_FLAGS) $(BUILD_DIR)/$@ $^


$(KERNEL_OBJS): $(OBJ_DIR)/%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@