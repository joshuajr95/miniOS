#ifndef TEST_GROUP_H
#define TEST_GROUP_H


#include <stdbool.h>



#define MAX_TEST_GROUP_NAME_LENGTH 256



typedef bool (*test_function)(void);



typedef struct
{
	test_function *funcs;
	char **func_names;
	int num_tests;
	char group_name[MAX_TEST_GROUP_NAME_LENGTH];

} test_group_t;


bool run_test_group(test_group_t *group);



#endif

