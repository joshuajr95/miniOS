


SUB_DIR= $(OBJ_DIR)/shell


SRCS =	line_discipline.c		\
		scrollback_buffer.c		\
		terminal_control.c


OBJS= $(patsubst %.c, $(SUB_DIR)/%.o, $(SRCS))


build: setup $(OBJS)


setup:
	if [ ! -d $(SUB_DIR) ]; then mkdir $(SUB_DIR); fi


$(OBJS): $(SUB_DIR)/%.o: %.c
	$(CC) $(INCLUDE_PATHS) $(CFLAGS) -c $< -o $@




