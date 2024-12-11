# Makefile used for building the MiniOS


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

export BUILD_DIR
export SCRIPT_DIR
export BASEDIR
export INCLUDE_PATHS

# Microchip provides toolchain for PIC32 MCUs
# Use the g++ compiler since it allows for overloading
# and the use of namespaces, which is useful for
# the device driver subsystem
ifeq ($(firstword $(MAKECMDGOALS)),unit_tests)
	SUBGOAL= $(lastword $(MAKECMDGOALS))
	CC=gcc
else
	CC = xc32-g++
	AR = xc32-ar
endif


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
	$(MAKE) -C $(KERNEL_DIR) -f $(KERNEL_DIR)/$(KERNEL_DIR).mk all

$(DRIVER_DIR):
	$(MAKE) -C $(DRIVER_DIR) -f $(DRIVER_DIR)/$(DRIVER_DIR).mk all

$(ARCH):
	$(MAKE) -C $(ARCH_DIR)/$(ARCH) -f $(ARCH_DIR)/$(ARCH)/$(ARCH)_arch.mk all

$(API_DIR):
	$(MAKE) -C $(API_DIR) -f $(API_DIR)/$(API_DIR).mk all



# can either specify the tests to run with TESTS=<comma-separated list of tests>
# or otherwise the 'all' target
ifeq ($(TESTS),)
unit_tests:
	cd $(UNIT_TEST_DIR); python3 $(UNIT_TEST_DIR)/$(UNIT_TEST_TOOL) set_root_dir $(BASEDIR)
	$(MAKE) -C $(UNIT_TEST_DIR) $(SUBGOAL)
else
unit_tests:
	cd $(UNIT_TEST_DIR); python3 $(UNIT_TEST_DIR)/$(UNIT_TEST_TOOL) set_root_dir $(BASEDIR)
	$(MAKE) -C $(UNIT_TEST_DIR) TESTS=$(TESTS) default
endif
