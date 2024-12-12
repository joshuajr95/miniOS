#ifndef TEST_H
#define TEST_H



#include <stdbool.h>
#include "test_group.h"


#define UNIT_TEST

// assert macro works with test framework
#define ASSERT(_condition)														\
	if(!(_condition))															\
	{																			\
		printf("ASSERT failed in file %s at line %d\n", __FILE__, __LINE__);	\
		return false;															\
	}


extern char *test_group_names[];
extern char *test_group_executables[];
extern int num_test_groups;


#endif