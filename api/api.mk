


# BUILD_DIR, CC, AR are exported to this file
# from the top-level Makefile

DIRNAME = $(shell basename "$$PWD")
OBJ_DIR = $(BUILD_DIR)/$(DIRNAME)

# create api build directory if it does not exist
$(shell [ ! -d $(OBJ_DIR) ] && mkdir $(OBJ_DIR) )


#############################################
#											#
#		ADD NEW SOURCE FILES HERE			#
#											#
#############################################

API_SRCS = 	filesystem.S	\
			task.S			


API_OBJS = $(patsubst %.S, $(OBJ_DIR)/%.o, $(API_SRCS))

AR_FLAGS = q
API_FLAGS = 

$(DIRNAME).a: $(API_OBJS)
	$(AR) $(AR_FLAGS) $(BUILD_DIR)/$@ $^

$(API_OBJS): $(OBJ_DIR)/%.o: %.S
	$(CC) $(API_FLAGS) -c $< -o $@