




$(foreach subgoal, $(SUBGOALS), $(eval SUB_OBJS := $(SUB_OBJS) $(patsubst %.o, $(OBJ_DIR)/$(subgoal)/%.o, $(shell ls $(OBJ_DIR)/$(subgoal)))))



.PHONY: link

link:
	$(CC) $(OBJS) $(SUB_OBJS) -o $(TARGET)