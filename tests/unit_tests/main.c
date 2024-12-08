#include <stdio.h>


#include "test.h"
#include "test_group.h"




void run_test_groups()
{
	printf("\033[94mRUNNING ALL UNIT TEST GROUPS\033[0m\n");
	printf("------------------------------------------\n\n\n");

	bool result;

	for(int i = 0; i < num_test_groups; i++)
	{
		printf("\033[94mRunning test group %d. Group name: %s\033[0m\n", i, test_groups_to_run[i]->group_name);
		printf("--------------------------------------------------------\n");

		result = run_test_group(test_groups_to_run[i]);

		printf("--------------------------------------------------------\n\n\n\n");
	}
}




int main(int argc, char *argv[])
{

	run_test_groups();

	/*
	for(int i = 0; i < num_tests; i++)
	{
		bool retval = tests_to_run[i]();

		if(retval)
		{
			printf("Test %d \033[92mPASSED\033[0m in function \"%s\" ...\n", i, test_function_names[i]);
		}
		else
		{
			printf("Test %d \033[91mFAILED\033[0m in function \"%s\" ...\n", i, test_function_names[i]);
		}
	}
	*/


	return 0;
}