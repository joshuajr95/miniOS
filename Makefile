# Makefile used for building MiniOS


ARCH=mips

SHELL := /bin/bash

BASEDIR = 			$(shell pwd)
KERNEL_DIR =		$(BASEDIR)/kernel
DRIVER_DIR = 		$(BASEDIR)/drivers
INCLUDE_DIR =		$(BASEDIR)/include
BUILD_DIR =			$(BASEDIR)/build
API_DIR =			$(BASEDIR)/api
SCRIPT_DIR = 		$(BASEDIR)/scripts
ARCH_DIR = 			$(BASEDIR)/arch
TEST_DIR = 			$(BASEDIR)/tests
UNIT_TEST_DIR = 	$(TEST_DIR)/unit_tests


UNIT_TEST_TOOL =	test_framework_tool.py
INCLUDE_PATHS = -I$(INCLUDE_DIR)
INCLUDE_PATHS += -I$(INCLUDE_DIR)/shell
INCLUDE_PATHS += -I$(DRIVER_DIR)/include
INCLUDE_PATHS += -I$(ARCH_DIR)/$(ARCH)/include

# DEVICE variable must be passed on command-line
TARGET_HW = $(shell ./scripts/generate_target.sh $(DEVICE))

# not portable, so should change in the future
DFP_PATH = /Applications/microchip/mplabx/v5.50/packs/Microchip/PIC32MX_DFP/1.5.259

LINK_MAP_FILE=$(BUILD_DIR)/$(DEVICE)_memory.map


# find all object files in the build directory
OBJS=$(shell find $(BUILD_DIR) -name "*.o" 2> /dev/null)

EXECUTABLE_TARGET=miniOS.elf
HEX_FILE_TARGET=miniOS.hex

export BUILD_DIR
export SCRIPT_DIR
export BASEDIR
export INCLUDE_PATHS
export TARGET_HW
export DFP_PATH


CFLAGS = 

# different compilers used for MCU target and unit test target
ifeq ($(firstword $(MAKECMDGOALS)),unit_tests)
	SUBGOALS= $(wordlist 2, 100, $(MAKECMDGOALS))
#	MAKECMDGOALS=$(firstword $(MAKECMDGOALS))
	CC=gcc
else
	CC = /Applications/microchip/xc32/v4.10/bin/xc32-gcc
	AR = xc32-ar
	HEXIFY = xc32-bin2hex
	CFLAGS += -g -x c -mprocessor=$(TARGET_HW) -fno-common -legacy-libc -mdfp="$(DFP_PATH)" -D__$(DEVICE)__
endif


export CC
export AR


LINK_FLAGS = -mprocessor=$(TARGET_HW) -legacy-libc -mdfp="$(DFP_PATH)" -Wl,--defsym=_min_heap_size=1024,--no-code-in-dinit,--no-dinit-in-serial-mem,-Map=$(LINK_MAP_FILE)



#########################################################
#					BUILD RULES							#
#########################################################


.PHONY: clean setup all unit_tests $(KERNEL_DIR) $(DRIVER_DIR) $(ARCH)


# build all of the targets
all: setup $(KERNEL_DIR) $(DRIVER_DIR) $(ARCH) #$(API_DIR)
	$(MAKE) link

$(KERNEL_DIR):
	$(MAKE) -C $(KERNEL_DIR) -f $(KERNEL_DIR)/kernel.mk all

$(DRIVER_DIR):
	$(MAKE) -C $(DRIVER_DIR) -f $(DRIVER_DIR)/drivers.mk all

$(ARCH):
	$(MAKE) -C $(ARCH_DIR)/$(ARCH) -f $(ARCH_DIR)/$(ARCH)/$(ARCH)_arch.mk all

#$(API_DIR):
#	$(MAKE) -C $(API_DIR) -f $(API_DIR)/$(API_DIR).mk all


link:
	$(CC) $(LINK_FLAGS) $(OBJS) -o $(BUILD_DIR)/$(EXECUTABLE_TARGET)
	$(HEXIFY) $(BUILD_DIR)/$(EXECUTABLE_TARGET)

setup:
	if [ ! -d $(BUILD_DIR) ]; then mkdir $(BUILD_DIR); fi



unit_tests:
	cd $(UNIT_TEST_DIR); python3 $(UNIT_TEST_DIR)/$(UNIT_TEST_TOOL) set_root_dir $(BASEDIR)
	$(MAKE) -C $(UNIT_TEST_DIR) $(SUBGOALS)


clean:
	rm -rf $(BUILD_DIR)

