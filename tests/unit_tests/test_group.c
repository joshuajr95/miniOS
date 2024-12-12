

#include "test_group.h"

#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>



bool run_test_group(char *group_executable_path)
{
	bool result;

	
	pid_t pid = fork();

	if(pid == -1)
	{
		printf("Error occurred forking child process %s...\n", group_executable_path);
	}
	if(pid == 0)
	{
		char *argv[] = {group_executable_path, NULL};
		fflush(stdout);
		int status = execvp(group_executable_path, argv);

	}
	else
	{
		int status;
		waitpid(pid, &status, 0);
	}


	return true;
}