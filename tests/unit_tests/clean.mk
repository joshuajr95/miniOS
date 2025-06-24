

SHELL := /bin/bash

CLEAN_TARGET=clean

SUBGOALS=$(patsubst %/, %, $(shell ./test_framework_tool.py get_test_packages))


$(info Clean subgoals: $(SUBGOALS))


.PHONY: clean $(SUBGOALS)
clean: $(SUBGOALS)
	if [ -e $(TARGET) ]; then  rm $(TARGET); fi
	if [ -e test.c ]; then rm test.c; fi
	if [ -d $(OBJ_DIR) ]; then rm -rf $(OBJ_DIR); fi


$(SUBGOALS):
	$(MAKE) -C $@ -f tests.mk $(CLEAN_TARGET)


