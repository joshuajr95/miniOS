
SHELL := /bin/bash

CC=gcc
CFLAGS=
TARGET=test_main
SUBTARGET=tests
GEN_TEST_SCRIPT=test_framework_tool.py

SRCS =	test.c			\
		test_group.c	\
		main.c


OBJ_DIR=obj


OBJS = $(patsubst %.c, $(OBJ_DIR)/%.o, $(SRCS))
SUB_OBJS=


#$(info unit_tests Makefile INCLUDE_DIR = $(INCLUDE_PATHS))


# for now, all subdirectories will be built
# as test directories if the all target is
# specified
# grep -v -f <(echo obj) <(ls -d */)
# add ifeq for TESTS=

comma:=,
space:= $(subst ,, )

ifeq ($(MAKECMDGOALS),all)
	SUBGOALS= $(shell ./test_framework_tool.py get_test_packages)
else ifeq ($(MAKECMDGOALS),)
	SUBGOALS= $(shell ./test_framework_tool.py get_test_packages)
else ifeq ($(MAKECMDGOALS),clean)
	SUBGOALS=
else
	SUBGOALS= $(MAKECMDGOALS)
endif

$(info SUBGOALS is $(SUBGOALS))




export CC
export CFLAGS
export GEN_TEST_SCRIPT
export OBJ_DIR
export SUBTARGET
export SHELL
export SUBGOALS
export SUB_OBJS
export OBJS
export TARGET



.PHONY: setup gen_test default all $(SUBGOALS) clean link



# prerequisites must be in this order
default: $(SUBGOALS)
#	$(MAKE) -f link.mk link

all: $(SUBGOALS)
#	$(MAKE) -f link.mk link

setup:
	if [ ! -d $(OBJ_DIR) ]; then mkdir $(OBJ_DIR); fi


$(SUBGOALS): setup main
	python3 $(GEN_TEST_SCRIPT) generate_group $@
	$(MAKE) -C $@ -f tests.mk $(SUBTARGET)

main: gen_test $(OBJS)
	$(CC) $(OBJS) -o $(TARGET)


gen_test:
	python3 $(GEN_TEST_SCRIPT) generate_group_list $(SUBGOALS)
	


$(OBJS): $(OBJ_DIR)/%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@



clean:
	$(MAKE) -f clean.mk clean








