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











extern test_group_t *test_groups_to_run[];
extern int num_test_groups;

//extern test_function tests_to_run[];
//extern char *test_function_names[];
//extern int num_tests;


#endif