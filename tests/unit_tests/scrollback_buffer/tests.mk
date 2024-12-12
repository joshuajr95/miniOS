

# CC, CFLAGS, GEN_TEST_SCRIPT, OBJ_DIR, SUBTARGET, SHELL, SUBGOALS, SUB_OBJS, and OBJS
# are all exported from top-level Makefile


CURRENT_DIR=$(shell basename $$(pwd))
TEST_GROUP_NAME=$(CURRENT_DIR)_GROUP
TEST_GROUP_FILE=$(patsubst %, %.c, $(TEST_GROUP_NAME))
TEST_GROUP_HEADER=$(patsubst %, %.h, $(TEST_GROUP_NAME))
EXEC_FILE_NAME=$(CURRENT_DIR)_main
COPY_DIR=cpy

INCLUDE_PATHS += -I..




SRCS = $(shell cd .. ; ./test_framework_tool.py get_source_file_paths $(CURRENT_DIR); cd $(CURRENT_DIR))
BASENAMES=$(foreach src, $(SRCS), $(shell basename $(src)))

TEST_SRCS =	test_scrollback_buffer.c			\
			$(TEST_GROUP_FILE)


TEST_OBJS = $(patsubst %.c, ../$(OBJ_DIR)/$(CURRENT_DIR)/%.o, $(TEST_SRCS))
OBJS = $(patsubst %.c, ../$(OBJ_DIR)/$(CURRENT_DIR)/%.o, $(BASENAMES))




########################
# Targets for sub-make #
########################

.PHONY: clean setup


$(SUBTARGET): setup $(OBJS) $(TEST_OBJS)
	$(CC) $(CFLAGS) $(OBJS) $(TEST_OBJS) -o ../$(OBJ_DIR)/$(CURRENT_DIR)/$(EXEC_FILE_NAME)

# create subfolder in object file folder for this folder's object files
setup:
	if [ ! -d ../$(OBJ_DIR)/$(CURRENT_DIR) ]; then mkdir ../$(OBJ_DIR)/$(CURRENT_DIR); fi
	if [ ! -d $(COPY_DIR) ]; then mkdir $(COPY_DIR); fi
	for src in $(SRCS); do cp $$src $(COPY_DIR)/$$(basename $$src); done

$(OBJS): ../$(OBJ_DIR)/$(CURRENT_DIR)/%.o: $(COPY_DIR)/%.c
	$(CC) $(CFLAGS) $(INCLUDE_PATHS) -c $< -o $@



$(TEST_OBJS): ../$(OBJ_DIR)/$(CURRENT_DIR)/%.o: %.c
	$(CC) $(CFLAGS) $(INCLUDE_PATHS) -c $< -o $@


clean:
	if [ -e $(TEST_GROUP_FILE) ]; then rm $(TEST_GROUP_FILE); fi
	if [ -e $(TEST_GROUP_HEADER) ]; then rm $(TEST_GROUP_HEADER); fi
	if [ -d $(COPY_DIR) ]; then rm -rf $(COPY_DIR); fi



