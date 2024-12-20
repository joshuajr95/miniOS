

# BUILD_DIR, CC, AR are exported to this file
# from the top-level Makefile


DIRNAME = $(shell basename "$$PWD")
OBJ_DIR = $(BUILD_DIR)/$(DIRNAME)



# This variable stores a list of subdirectories
# that must be recursively made before making
# the current directory. If you add a subsystem
# in a subdirectory, the sub-make in that directory
# will be invoked using the below list of submakes.
# The make will look for a makefile named build.mk
# so name your makefiles appropriately

# --- ADD NEW SUBDIRECTORIES HERE --- #
SUBMAKES =	shell




#############################################
#											#
#		ADD NEW SOURCE FILES HERE			#
#											#
#############################################

#KERNEL_SRCS =	filesystem.c		\
				global_structs.c	\
				list.c				\
				syscall.c			\
				task.c				\
				init.c

KERNEL_SRCS = 

# kernel object files are in build/{current_dir}
KERNEL_OBJS = $(patsubst %.c, $(OBJ_DIR)/%.o, $(KERNEL_SRCS))


#CFLAGS = -mprocessor=$(TARGET_HW) -g -fno-common -legacy-libc -mdfp=$(DFP_PATH)

AR_FLAGS = q



export OBJ_DIR

# For partial linking, do not include crt0.o or any C standard
# library files or any default libraries. Also, the output file
# should another relocatable object file, not an executable.
#LINK_FLAGS = -nostartfiles -nodefaultlibs -nostdlib --relocatable

.PHONY: clean all setup $(SUBMAKES)

all: setup $(KERNEL_OBJS) $(SUBMAKES)


# build the kernel directory relocatable file from the 
# individual relocatable files corresponding to each
#$(DIRNAME).a: $(KERNEL_OBJS)
#	$(AR) $(AR_FLAGS) $(BUILD_DIR)/$@ $^


$(SUBMAKES):
	$(MAKE) -C $@ -f build.mk build

setup:
	if [ ! -d $(OBJ_DIR) ]; then mkdir $(OBJ_DIR); fi


$(KERNEL_OBJS): $(OBJ_DIR)/%.o: %.c
	$(CC) $(INCLUDE_PATHS) $(CFLAGS) -c $< -o $@