#ifndef SHELL_H
#define SHELL_H


#include "line_discipline.h"


/**
 * @typedef shell_function_t
 *
 * Function pointer typedef for shell invocation function.
 */
typedef void (*shell_function_t)(char *);



typedef struct
{
   line_discipline_t *line_discipline;

   shell_function_t run_shell;

} shell_t;



int shell_set_line_discipline(shell_t *shell, line_discipline_t *discipline);


int shell_init(shell_t *shell);




#endif
