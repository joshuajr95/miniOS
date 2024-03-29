# Makefile used for building the MiniOS

BASEDIR = 			$(shell pwd)
KERNEL_DIR =		$(BASEDIR)/kernel
DRIVER_DIR = 		$(BASEDIR)/drivers
INCLUDE_DIR =		$(BASEDIR)/include
BUILD_DIR =			$(BASEDIR)/build
API_DIR =			$(BASEDIR)/api
SCRIPT_DIR = 		$(BASEDIR)/scripts
ARCH_DIR = 			$(BASEDIR)/arch

export BUILD_DIR
export SCRIPT_DIR

# Microchip provides toolchain for PIC32 MCUs
# Use the g++ compiler since it allows for overloading
# and the use of namespaces, which is useful for
# the device driver subsystem
CC = xc32-g++
AR = xc32-ar

export CC
export AR

CFLAGS = 

ARCH=mips

#########################################################
#					BUILD RULES							#
#########################################################


# build all of the targets
all: $(KERNEL_DIR) $(DRIVER_DIR) $(ARCH) $(API_DIR)


$(KERNEL_DIR):
	$(MAKE) --directory $(KERNEL_DIR) -f $(KERNEL_DIR)/$(KERNEL_DIR).mk all

$(DRIVER_DIR):
	$(MAKE) --directory $(DRIVER_DIR) -f $(DRIVER_DIR)/$(DRIVER_DIR).mk all

$(ARCH):
	$(MAKE) --directory $(ARCH_DIR)/$(ARCH) -f $(ARCH_DIR)/$(ARCH)/$(ARCH)_arch.mk all

$(API_DIR):
	$(MAKE) --directory $(API_DIR) -f $(API_DIR)/$(API_DIR).mk all
