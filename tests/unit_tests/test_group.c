

#include "test_group.h"

#include <stdio.h>



bool run_test_group(test_group_t *group)
{
	bool result;


	for(int i = 0; i < group->num_tests; i++)
	{

		result = group->funcs[i]();

		if(result)
		{
			printf("\tTest %d \033[92mPASSED\033[0m in function \"%s\" ...\n", i, group->func_names[i]);
		}
		else
		{
			printf("\tTest %d \033[91mFAILED\033[0m in function \"%s\" ...\n", i, group->func_names[i]);
		}
	}


	return true;
}