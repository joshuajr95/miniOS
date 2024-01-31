
# BUILD_DIR, CC, AR are exported to this file
# from the top-level Makefile


DIRNAME = $(shell basename "$$PWD")
OBJ_DIR = $(BUILD_DIR)/$(DIRNAME)

# create kernel build directory if it does not exist
$(shell [ ! -d $(OBJ_DIR) ] && mkdir $(OBJ_DIR) )


MANIFEST_FILE = driver_manifest.yml


DRIVER_SOURCES = $(shell $(SCRIPT_DIR)/get_manifest.sh $(MANIFEST_FILE) )

DRIVER_OBJS = $(patsubst %.c, $(OBJ_DIR)/%.o, $(DRIVER_SOURCES))


AR_FLAGS = q
CFLAGS = 


all: $(DIRNAME).a

$(DIRNAME).a: $(DRIVER_OBJS)
	$(AR) $(AR_FLAGS) $(BUILD_DIR)/$@ $^


$(DRIVER_OBJS): $(OBJ_DIR)/%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@
