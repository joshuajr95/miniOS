


#include <string.h>
#include <stdio.h>


#include "line_discipline.h"
#include "terminal_control.h"
#include "test.h"



// structs and functions for the test apparatus

#define RECEIVE_BUFFER_SIZE 1024

typedef struct
{
    char terminal_buffer[RECEIVE_BUFFER_SIZE];
    int in;
} terminal_receive_buffer_t;



void trb_clear(terminal_receive_buffer_t *buf)
{
    for(int i = 0; i < RECEIVE_BUFFER_SIZE; i++)
    {
        buf->terminal_buffer[i] = 0;
    }

    buf->in = 0;
}



terminal_receive_buffer_t terminal_receive_buffer;

extern cursor_t cursor;




int terminal_send_byte(uint8_t byte_to_send)
{
    if(terminal_receive_buffer.in >= RECEIVE_BUFFER_SIZE) return -1;

    terminal_receive_buffer.terminal_buffer[terminal_receive_buffer.in] = byte_to_send;
    terminal_receive_buffer.in++;

    return 0;
}



int process_next_byte(line_discipline_t *discipline, void *buffer, uint32_t size);



int invoke_shell(void)
{
    printf("Shell has been invoked.\n");
    return 0;
}



UNIT_TEST bool test_escape_sequence_buffer_init_1()
{
	escape_sequence_buffer_t buf;
	int ret;

	ret = escape_sequence_buffer_init(NULL);
	ASSERT(ret < 0);

	ret = escape_sequence_buffer_init(&buf);
	ASSERT(buf.current_index == 0);

	for(int i = 0; i < ESCAPE_SEQUENCE_BUFFER_SIZE; i++)
	{
		ASSERT(buf.buffer[i] == 0);
	}

	return true;
}



UNIT_TEST bool test_escape_sequence_buffer_insert_1()
{
	escape_sequence_buffer_t buf;
	int ret;

	ret = escape_sequence_buffer_insert(NULL, 'a');
	ASSERT(ret < 0);

	ret = escape_sequence_buffer_init(&buf);
	ASSERT(ret == 0);

	ret = escape_sequence_buffer_insert(&buf, 'a');
	ASSERT(ret == 0);
	ASSERT(buf.buffer[0] == 'a');
	ASSERT(buf.current_index == 1);

	return true;
}


UNIT_TEST bool test_escape_sequence_buffer_insert_2()
{
	escape_sequence_buffer_t buf;
	int ret;


	ret = escape_sequence_buffer_init(&buf);
	ASSERT(ret == 0);

	for(int i = 0; i < ESCAPE_SEQUENCE_BUFFER_SIZE; i++)
	{
		ret = escape_sequence_buffer_insert(&buf, 'a');
		ASSERT(ret == 0);
		ASSERT(buf.current_index == i+1);
	}

	ret = escape_sequence_buffer_insert(&buf, 'a');
	ASSERT(ret < 0);
	ASSERT(buf.current_index == ESCAPE_SEQUENCE_BUFFER_SIZE);

	return true;
}


UNIT_TEST bool test_line_discipline_set_prompt_1()
{
    int ret;
    line_discipline_t discipline;   

    ret = line_discipline_set_prompt(NULL, "a");
    ASSERT(ret < 0);

    ret = line_discipline_set_prompt(&discipline, NULL);
    ASSERT(ret < 0);

    return true;
}


UNIT_TEST bool test_line_discipline_set_prompt_2()
{
    int ret;
    line_discipline_t discipline;

    ret = line_discipline_set_prompt(&discipline, "miniOS \% ");
    ASSERT(ret == 0);
    ASSERT(strncmp(discipline.prompt, "miniOS \% ", MAX_PROMPT_SIZE) == 0);

    return true;
}


UNIT_TEST bool test_line_discipline_set_prompt_3()
{
    int ret;
    line_discipline_t discipline;
    char buf[24];

    for(int i = 0; i < 24; i++) buf[i] = 'a';

    ret = line_discipline_set_prompt(&discipline, buf);
    ASSERT(ret < 0);

    return true;
}


UNIT_TEST bool test_line_discipline_shell_buffer_1()
{
    int ret;
    line_discipline_t discipline;
    char buf[10];

    ret = line_discipline_register_shell_buffer(NULL, &buf[0]);
    ASSERT(ret < 0);
    ret = line_discipline_register_shell_buffer(&discipline, NULL);
    ASSERT(ret < 0);

    return true;
}

UNIT_TEST bool test_line_discipline_shell_buffer_2()
{
    int ret;
    line_discipline_t discipline;
    char buf[10];

    ret = line_discipline_register_shell_buffer(&discipline, &buf[0]);
    ASSERT(ret == 0);
    ASSERT(discipline.shell_buffer == &buf[0]);

    return true;
}


UNIT_TEST bool test_line_discipline_init_1()
{
    int ret;
    line_discipline_t discipline;
    char shell_buf[MAX_LINE_SIZE];
    char prompt[MAX_PROMPT_SIZE];

    ret = line_discipline_init(NULL, process_next_byte, invoke_shell, prompt, shell_buf);
    ASSERT(ret < 0);

    ret = line_discipline_init(&discipline, NULL, invoke_shell, prompt, shell_buf);
    ASSERT(ret < 0);

    ret = line_discipline_init(&discipline, process_next_byte, NULL, prompt, shell_buf);
    ASSERT(ret < 0);

    ret = line_discipline_init(&discipline, process_next_byte, invoke_shell, NULL, shell_buf);
    ASSERT(ret < 0);

    ret = line_discipline_init(&discipline, process_next_byte, invoke_shell, prompt, NULL);
    ASSERT(ret < 0);

    return true;
}


UNIT_TEST bool test_line_discipline_init_2()
{
    int ret;
    line_discipline_t discipline;
    char shell_buf[MAX_LINE_SIZE];
    char *prompt = "miniOS % ";

    ret = line_discipline_init(&discipline, process_next_byte, invoke_shell, prompt, &shell_buf[0]);

    // return value must not be error code
    ASSERT(ret == 0);

    // pointers must be assigned properly
    ASSERT(discipline.process_next_byte == process_next_byte);
    ASSERT(discipline.invoke_shell == invoke_shell);
    ASSERT(strcmp(discipline.prompt, prompt) == 0);
    ASSERT(discipline.shell_buffer == shell_buf);

    // escape sequence buffer must be in initial/cleared state
    ASSERT(discipline.escape_buffer.current_index == 0);
    for(int i = 0; i < ESCAPE_SEQUENCE_BUFFER_SIZE; i++)
    {
        ASSERT(discipline.escape_buffer.buffer[i] == 0);
    }

    // scrollback buffer must be in initial/cleared state
    ASSERT(discipline.scrollback_buffer.current == 0);
    ASSERT(discipline.scrollback_buffer.latest == 0);
    for(int i = 0; i < SCROLLBACK_BUFFER_NUM_ENTRIES; i++)
    {
        scrollback_buffer_entry_t current_entry = discipline.scrollback_buffer.buffer[i];

        ASSERT(!current_entry.in_use);
        ASSERT(current_entry.end_index == 0);
        for(int j = 0; j < MAX_LINE_SIZE; j++)
        {
            ASSERT(current_entry.line[j] == 0);
        }
    }

    ASSERT(discipline.current_line.cursor == 0);
    ASSERT(discipline.current_line.end_index == 0);
    for(int i = 0; i < MAX_LINE_SIZE; i++)
    {
        ASSERT(discipline.current_line.line[i] == 0);
    }

    ASSERT(discipline.current_state == LINE_DISCIPLINE_NORMAL_OPERATION);

    return true;
}



/**********************************************************************************************************
 * Line Discipline Test Plan:
 * --------------------------
 *
 * - Figure out issues with buffer_entry.in_use and scrolling.
 *
 * 1. Send char ('a' for example)
 *      - Check that current line == 'a' and scrollback_buffer[latest] == scrollback_buffer[latest] == 'a'
 *      - Check that cursor == 1
 *      - Check that terminal cursor.x == strlen(prompt) + 1
 *      - Check that 'a' was echoed to terminal
 *      - Check that current state == normal
 *      - Check that escape sequence buffer is empty
 *
 * 2. Send whole command (ls /dev)
 *      - For each char in command, check that char was echoed to terminal, cursor == i,
 *              and terminal cursor.x == strlen(prompt) + i
 *      - Check that current line == command and scrollback_buffer[latest] == command
 *      - Check that cursor == len(command)
 *      - Check that terminal cursor.x == strlen(prompt) + strlen(command)
 *
 * 3. Send command larger than line size
 *      - For each char in command, check that char was echoed to terminal and check cursor.x
 *      - Check that once beyond end, cursor does not change
 *      - Check that once beyond end, bell char sent to terminal each time.
 *      - Check that terminal cursor.x == strlen(prompt) + strlen(command)
 *
 * 4. Send command and then enter
 *      - For each char in command, check that char was echoed to terminal, check that 
 *              terminal cursor.x == strlen(prompt) + cursor, check that current_line[cursor] == char,
 *              and scrollback_buffer[current][cursor] == char
 *      - Check that set cursor x,y to 0,y+1 sequence echoed to
 *              terminal and cursor.x == 0 and cursor.y = previous_y + 1
 *      - Check that after that, prompt printed to terminal
 *      - Check that cursor.x == strlen(prompt)
 *      - Check that scrollback_buffer.current == scrollback_buffer.latest
 *      - Check that scrollback_buffer.latest == previous latest + 1
 *      - Check that current line is clear (end_index == cursor == line[i] forall i == 0)
 *      - Check that scrollback_buffer[latest] is clear and in use
 *      - Check that scrollback_buffer[latest-1] == command
 *      - Check that shell_buffer == command
 *      - Check that invoke_shell was called
 *
 * 5. Send command and then move_cursor_left escape sequence
 *      - For each char in command, check that char was echoed to terminal, check that 
 *              terminal cursor.x == strlen(prompt) + cursor, check that current_line[cursor] == char,
 *              and scrollback_buffer[current][cursor] == char
 *      - Check that current_state is normal, and then after ESC received change state to process_esc_seq.
 *      - Check that escape sequence buffer contains proper escape sequence, and then cleared
 *      - Check that escape sequence echoed to terminal
 *      - Check that state is normal after escape sequence received.
 *      - Check that current_line.cursor == prev - 1
 *      - Check that cursor.x == current_line.cursor + strlen(prompt)
 *
 * 6. Send move_cursor_left and move_cursor_right escape sequences
 *      - Check that cursor.x == strlen(prompt) and current_line.cursor == 0
 *      - Check that bell char sent to terminal
 *      - Check that state changes to in_esc_seq and then back, and that buffer is cleared
 *      - Check that chars not placed in current_line while in escape sequence
 *
 * 7. Send command and then move_cursor_left until at beginning
 *      - For each char in command, check that char was echoed to terminal, check that 
 *              terminal cursor.x == strlen(prompt) + cursor, check that current_line[cursor] == char,
 *              and scrollback_buffer[current][cursor] == char
 *      - Same as above, but for each left escape sequence
 *      - Once at beginning, check that:
 *          - cursor.x == strlen(prompt)
 *          - current_line.cursor == 0
 *          - bell sent to terminal
 *
 * 8. Send command and then move_cursor_right escape sequence
 *          - For each char in command, check that char was echoed to terminal, check that 
 *              terminal cursor.x == strlen(prompt) + cursor, check that current_line[cursor] == char,
 *              and scrollback_buffer[current][cursor] == char
 *          - Check that cursor.x not changed and current_line.cursor not changed
 *          - bell sent to terminal
 *          - state changes to process_esc_seq and then back
 *          - esc seq buffer contains correct chars and cleared
 *
 * 9. Send command and then delete
 *          - For each char in command, check that char was echoed to terminal, check that 
 *              terminal cursor.x == strlen(prompt) + cursor, check that current_line[cursor] == char,
 *              and scrollback_buffer[current][cursor] == char
 *          - Check that after delete, cursor.x - 1, current_line.cursor - 1
 *          - Check that deleted from end of current_line and from end of scrollback_buffer[latest]
 *
 * 10. Send command, move cursor left, and insert new char
 *          - For each char in command, check that char was echoed to terminal, check that 
 *              terminal cursor.x == strlen(prompt) + cursor, check that current_line[cursor] == char,
 *              and scrollback_buffer[current][cursor] == char
 *          - Check that state changed in escape sequence and back after
 *          - Check that escape sequence echoed to screen.
 *          - Check that cursor.x and current_line.cursor - 1
 *          - Check that after insert current_line[cursor] == char and rest of line shifted right
 *          - Check that cursor.x incremented and current_line.cursor incremented.
 *
 * 11. Send command, move cursor left, and delete char
 *          - For each char in command, check that char was echoed to terminal, check that 
 *              terminal cursor.x == strlen(prompt) + cursor, check that current_line[cursor] == char,
 *              and scrollback_buffer[current][cursor] == char
 *          - Check that state changed in escape sequence and back after
 *          - Check that escape sequence echoed to screen.
 *          - Check that cursor.x and current_line.cursor - 1
 *          - Check that after delete current_line[cursor-1] deleted and rest of line shifted left
 *          - Check that cursor.x decremented and current_line.cursor decremented.
 *
 * 12. Send scroll up sequence
 *          - Check that bell sent
 *          - Check that current and latest unchanged, and cursor unchanged
 *
 * 13. Send scroll down sequence
 *          - Check that bell sent
 *          - Check that current and latest unchanged, and cursor unchanged
 *
 * 14. Send command, return and scroll up
 *          - Same checks as in send command and return
 *          - Check that scrollback_buffer.current moved up one
 *          - Check that current_line == scrollback_buffer[current]
 *          - Check that current_line is printed
 *
 * 15. Send command, return, scroll up, and then scroll down
 *          - Same as above, but then check that current_line changed back
 * 
 * - Send return with no command (check that ignored)
 * - Send multiple returns (check ignored and buffers unused)
 * - Send multiple commands, up arrow, and return
 ***********************************************************************************************************/


UNIT_TEST bool test_line_discipline_1()
{
    int ret;
    line_discipline_t discipline;
    char shell_buf[MAX_LINE_SIZE];
    char *prompt = "miniOS % ";
    char command = 'a';

    ret = line_discipline_init(&discipline, process_next_byte, invoke_shell, prompt, shell_buf);
    trb_clear(&terminal_receive_buffer);

    // return value must not be error code
    ASSERT(ret == 0);

    // send byte to line discipline
    ret = discipline.process_next_byte(&discipline, &command, 1);
    ASSERT(ret == 0);

    ASSERT(discipline.current_line.line[0] == 'a');
    ASSERT(discipline.current_line.cursor == 1);
    ASSERT(discipline.current_line.end_index == 1);
    ASSERT(get_cursor_x() == strlen(prompt) + 1);
    ASSERT(strcmp(terminal_receive_buffer.terminal_buffer, "a") == 0);
    ASSERT(discipline.current_state == LINE_DISCIPLINE_NORMAL_OPERATION);
    ASSERT(discipline.escape_buffer.current_index == 0);

    return true;
}


UNIT_TEST bool test_line_discipline_2()
{
    int ret;
    line_discipline_t discipline;
    char shell_buf[MAX_LINE_SIZE];
    char *prompt = "miniOS % ";
    char *command = "ls /dev";

    ret = line_discipline_init(&discipline, process_next_byte, invoke_shell, prompt, shell_buf);
    trb_clear(&terminal_receive_buffer);

    // return value must not be error code
    ASSERT(ret == 0);

    for(int i = 0; i < strlen(command); i++)
    {
        ret = discipline.process_next_byte(&discipline, &command[i], 1);
        ASSERT(ret == 0);

        ASSERT(discipline.current_line.line[i] == command[i]);
        ASSERT(discipline.current_line.cursor == i+1);
        ASSERT(discipline.current_line.end_index == i+1);
        ASSERT(get_cursor_x() == strlen(prompt) + i + 1);
        ASSERT(terminal_receive_buffer.terminal_buffer[i] == command[i]);
        ASSERT(discipline.current_state == LINE_DISCIPLINE_NORMAL_OPERATION);
        ASSERT(discipline.escape_buffer.current_index == 0);
        ASSERT(discipline.scrollback_buffer.current == discipline.scrollback_buffer.latest);
        ASSERT(discipline.scrollback_buffer.buffer[discipline.scrollback_buffer.current].line[i] == command[i]);
    }

    return true;
}


UNIT_TEST bool test_line_discipline_3()
{
    int ret;
    line_discipline_t discipline;
    char shell_buf[MAX_LINE_SIZE];
    char *prompt = "miniOS % ";
    char command[MAX_LINE_SIZE+1];

    for(int i = 0; i < MAX_LINE_SIZE+1; i++)
    {
        command[i] = 'a';
    }

    ret = line_discipline_init(&discipline, process_next_byte, invoke_shell, prompt, shell_buf);
    trb_clear(&terminal_receive_buffer);

    // return value must not be error code
    ASSERT(ret == 0);

    for(int i = 0; i < MAX_LINE_SIZE; i++)
    {
        ret = discipline.process_next_byte(&discipline, &command[i], 1);
        ASSERT(ret == 0);

        ASSERT(discipline.current_line.line[i] == command[i]);
        ASSERT(discipline.current_line.cursor == i+1);
        ASSERT(discipline.current_line.end_index == i+1);

        ASSERT(get_cursor_x() == strlen(prompt) + i + 1);
        ASSERT(terminal_receive_buffer.terminal_buffer[i] == command[i]);

        ASSERT(discipline.current_state == LINE_DISCIPLINE_NORMAL_OPERATION);
        ASSERT(discipline.escape_buffer.current_index == 0);
        ASSERT(discipline.scrollback_buffer.current == discipline.scrollback_buffer.latest);
        ASSERT(discipline.scrollback_buffer.buffer[discipline.scrollback_buffer.current].line[i] == command[i]);
    }

    ret = discipline.process_next_byte(&discipline, &command[MAX_LINE_SIZE], 1);
    
    // process_next_byte does not return error code
    ASSERT(ret == 0);

    ASSERT(discipline.current_line.cursor == MAX_LINE_SIZE);
    ASSERT(discipline.current_line.end_index == MAX_LINE_SIZE);
    ASSERT(get_cursor_x() == strlen(prompt) + MAX_LINE_SIZE);
    ASSERT(terminal_receive_buffer.terminal_buffer[terminal_receive_buffer.in-1] == ASCII_BEL);

    return true;
}


UNIT_TEST bool test_line_discipline_4()
{
    int ret;
    line_discipline_t discipline;
    char shell_buf[MAX_LINE_SIZE];
    char *prompt = "miniOS % ";
    char *command = "ls /dev";

    ret = line_discipline_init(&discipline, process_next_byte, invoke_shell, prompt, shell_buf);
    trb_clear(&terminal_receive_buffer);

    // return value must not be error code
    ASSERT(ret == 0);

    for(int i = 0; i < strlen(command); i++)
    {
        ret = discipline.process_next_byte(&discipline, &command[i], 1);
        ASSERT(ret == 0);

        ASSERT(discipline.current_line.line[i] == command[i]);
        ASSERT(discipline.current_line.cursor == i+1);
        ASSERT(discipline.current_line.end_index == i+1);
        ASSERT(get_cursor_x() == strlen(prompt )+ i + 1);
        ASSERT(terminal_receive_buffer.terminal_buffer[i] == command[i]);
        ASSERT(discipline.current_state == LINE_DISCIPLINE_NORMAL_OPERATION);
        ASSERT(discipline.escape_buffer.current_index == 0);
        ASSERT(discipline.scrollback_buffer.current == discipline.scrollback_buffer.latest);
        ASSERT(discipline.scrollback_buffer.buffer[discipline.scrollback_buffer.current].line[i] == command[i]);
    }

    int prev_y = cursor.y;
    char enter = ASCII_CR;
    ret = discipline.process_next_byte(&discipline, &enter, 1);
    ASSERT(ret == 0);

    ASSERT(get_cursor_x() == strlen(discipline.prompt));
    ASSERT(cursor.y == prev_y + 1);

    ASSERT(discipline.scrollback_buffer.current == discipline.scrollback_buffer.latest);
    ASSERT(discipline.scrollback_buffer.current == 1);
    ASSERT(strcmp(discipline.scrollback_buffer.buffer[discipline.scrollback_buffer.latest-1].line, command) == 0);
    ASSERT(strcmp(discipline.scrollback_buffer.buffer[discipline.scrollback_buffer.latest].line, "") == 0);
    ASSERT(discipline.scrollback_buffer.buffer[discipline.scrollback_buffer.latest-1].in_use);
    ASSERT(discipline.scrollback_buffer.buffer[discipline.scrollback_buffer.latest].in_use);

    ASSERT(strcmp(discipline.current_line.line, "") == 0);
    ASSERT(discipline.current_line.end_index == 0);
    ASSERT(discipline.current_line.cursor == 0);
    
    ASSERT(strcmp(discipline.shell_buffer, command) == 0);

    return true;
}

UNIT_TEST bool test_line_discipline_5()
{
    int ret;
    line_discipline_t discipline;
    char shell_buf[MAX_LINE_SIZE];
    char *prompt = "miniOS % ";
    char *command = "ls /dev";
    char *move_left = "\033[D";

    ret = line_discipline_init(&discipline, process_next_byte, invoke_shell, prompt, shell_buf);
    trb_clear(&terminal_receive_buffer);

    // return value must not be error code
    ASSERT(ret == 0);

    for(int i = 0; i < strlen(command); i++)
    {
        ret = discipline.process_next_byte(&discipline, &command[i], 1);
        ASSERT(ret == 0);

        ASSERT(discipline.current_line.line[i] == command[i]);
        ASSERT(discipline.current_line.cursor == i+1);
        ASSERT(discipline.current_line.end_index == i+1);
        ASSERT(get_cursor_x() == strlen(prompt )+ i + 1);
        ASSERT(terminal_receive_buffer.terminal_buffer[i] == command[i]);
        ASSERT(discipline.current_state == LINE_DISCIPLINE_NORMAL_OPERATION);
        ASSERT(discipline.escape_buffer.current_index == 0);
        ASSERT(discipline.scrollback_buffer.current == discipline.scrollback_buffer.latest);
        ASSERT(discipline.scrollback_buffer.buffer[discipline.scrollback_buffer.current].line[i] == command[i]);
    }

    for(int i = 0; i < strlen(move_left); i++)
    {
        ret = discipline.process_next_byte(&discipline, &move_left[i], 1);
        ASSERT(ret == 0);

        

        if(i < strlen(move_left)-1)
        {
            ASSERT(discipline.escape_buffer.buffer[i] == move_left[i]);
            ASSERT(discipline.current_state == LINE_DISCIPLINE_PROCESS_ANSI_ESCAPE);
        }
        else
        {
            ASSERT(discipline.current_state == LINE_DISCIPLINE_NORMAL_OPERATION);
        }
    }

    ASSERT(discipline.escape_buffer.current_index == 0);
    ASSERT(discipline.current_line.cursor == strlen(command)-1);
    ASSERT(get_cursor_x() == strlen(command)-1 + strlen(prompt));

    return true;
}



UNIT_TEST bool test_line_discipline_6()
{
    int ret;
    line_discipline_t discipline;
    char shell_buf[MAX_LINE_SIZE];
    char *prompt = "miniOS % ";
    char *command = "ls /dev";
    char *move_left = "\033[D";
    char *move_right = "\033[C";

    ret = line_discipline_init(&discipline, process_next_byte, invoke_shell, prompt, shell_buf);
    trb_clear(&terminal_receive_buffer);

    // return value must not be error code
    ASSERT(ret == 0);


    for(int i = 0; i < strlen(move_left); i++)
    {
        ret = discipline.process_next_byte(&discipline, &move_left[i], 1);
        ASSERT(ret == 0);

        

        if(i < strlen(move_left)-1)
        {
            ASSERT(discipline.escape_buffer.buffer[i] == move_left[i]);
            ASSERT(discipline.current_state == LINE_DISCIPLINE_PROCESS_ANSI_ESCAPE);
        }
        else
        {
            ASSERT(discipline.current_state == LINE_DISCIPLINE_NORMAL_OPERATION);
        }
    }

    ASSERT(discipline.escape_buffer.current_index == 0);
    ASSERT(discipline.current_line.cursor == 0);
    ASSERT(get_cursor_x() == strlen(prompt));


    for(int i = 0; i < strlen(move_right); i++)
    {
        ret = discipline.process_next_byte(&discipline, &move_right[i], 1);
        ASSERT(ret == 0);

        

        if(i < strlen(move_right)-1)
        {
            ASSERT(discipline.escape_buffer.buffer[i] == move_right[i]);
            ASSERT(discipline.current_state == LINE_DISCIPLINE_PROCESS_ANSI_ESCAPE);
            ASSERT(discipline.escape_buffer.current_index == i+1);
        }
        else
        {
            ASSERT(discipline.current_state == LINE_DISCIPLINE_NORMAL_OPERATION);
            ASSERT(discipline.escape_buffer.current_index == 0);
        }
    }

    ASSERT(discipline.escape_buffer.current_index == 0);
    ASSERT(discipline.current_line.cursor == 0);
    ASSERT(get_cursor_x() == strlen(prompt));

    return true;
}


UNIT_TEST bool test_line_discipline_7()
{
    int ret;
    line_discipline_t discipline;
    char shell_buf[MAX_LINE_SIZE];
    char *prompt = "miniOS % ";
    char *command = "ls /dev";
    char *move_left = "\033[D";

    ret = line_discipline_init(&discipline, process_next_byte, invoke_shell, prompt, shell_buf);
    trb_clear(&terminal_receive_buffer);

    // return value must not be error code
    ASSERT(ret == 0);

    // send command
    for(int i = 0; i < strlen(command); i++)
    {
        ret = discipline.process_next_byte(&discipline, &command[i], 1);
        ASSERT(ret == 0);

        ASSERT(discipline.current_line.line[i] == command[i]);
        ASSERT(discipline.current_line.cursor == i+1);
        ASSERT(discipline.current_line.end_index == i+1);
        ASSERT(get_cursor_x() == strlen(prompt )+ i + 1);
        ASSERT(terminal_receive_buffer.terminal_buffer[i] == command[i]);
        ASSERT(discipline.current_state == LINE_DISCIPLINE_NORMAL_OPERATION);
        ASSERT(discipline.escape_buffer.current_index == 0);
        ASSERT(discipline.scrollback_buffer.current == discipline.scrollback_buffer.latest);
        ASSERT(discipline.scrollback_buffer.buffer[discipline.scrollback_buffer.current].line[i] == command[i]);
    }

    // send x number of move_left escape sequences
    for(int i = strlen(command)-1; i >= 0; i--)
    {
        for(int j = 0; j < strlen(move_left); j++)
        {
            ret = discipline.process_next_byte(&discipline, &move_left[j], 1);
            ASSERT(ret == 0);

            if(j < strlen(move_left)-1)
            {
                ASSERT(discipline.escape_buffer.current_index == j+1);
                ASSERT(discipline.escape_buffer.buffer[j] == move_left[j]);
                ASSERT(discipline.current_state == LINE_DISCIPLINE_PROCESS_ANSI_ESCAPE);
            }
            else
            {
                ASSERT(discipline.current_state == LINE_DISCIPLINE_NORMAL_OPERATION);
                ASSERT(discipline.escape_buffer.current_index == 0);
            }
        }

        ASSERT(discipline.current_line.cursor == i);
        ASSERT(get_cursor_x() == strlen(discipline.prompt) + i);
    }

    return true;
}



UNIT_TEST bool test_line_discipline_8()
{
    int ret;
    line_discipline_t discipline;
    char shell_buf[MAX_LINE_SIZE];
    char *prompt = "miniOS % ";
    char *command = "ls /dev";
    char *move_right = "\033[C";

    ret = line_discipline_init(&discipline, process_next_byte, invoke_shell, prompt, shell_buf);
    trb_clear(&terminal_receive_buffer);

    // return value must not be error code
    ASSERT(ret == 0);

    for(int i = 0; i < strlen(command); i++)
    {
        ret = discipline.process_next_byte(&discipline, &command[i], 1);
        ASSERT(ret == 0);

        ASSERT(discipline.current_state == LINE_DISCIPLINE_NORMAL_OPERATION);
        ASSERT(discipline.current_line.cursor == i+1);
        ASSERT(discipline.current_line.end_index == i+1);
        ASSERT(discipline.current_line.line[i] == command[i]);

        ASSERT(discipline.scrollback_buffer.current == discipline.scrollback_buffer.latest);
        ASSERT(discipline.scrollback_buffer.buffer[discipline.scrollback_buffer.current].end_index == i+1);
        ASSERT(discipline.scrollback_buffer.buffer[discipline.scrollback_buffer.current].in_use);
        ASSERT(discipline.scrollback_buffer.buffer[discipline.scrollback_buffer.current].line[i] == command[i]);

        ASSERT(discipline.escape_buffer.current_index == 0);

        ASSERT(get_cursor_x() == strlen(prompt)+i+1);
        ASSERT(terminal_receive_buffer.terminal_buffer[i] == command[i]);
    }


    for(int i = 0; i < strlen(move_right); i++)
    {
        ret = discipline.process_next_byte(&discipline, &move_right[i], 1);
        ASSERT(ret == 0);

        if(i < strlen(move_right)-1)
        {
            ASSERT(discipline.escape_buffer.buffer[i] == move_right[i]);
            ASSERT(discipline.escape_buffer.current_index == i+1);
            ASSERT(discipline.current_state == LINE_DISCIPLINE_PROCESS_ANSI_ESCAPE);
        }
        else
        {
            ASSERT(discipline.escape_buffer.current_index == 0);
            ASSERT(discipline.current_state == LINE_DISCIPLINE_NORMAL_OPERATION);
        }
    }

    ASSERT(discipline.current_line.cursor == strlen(command));
    ASSERT(discipline.current_line.end_index == strlen(command));
    ASSERT(get_cursor_x() == strlen(command) + strlen(prompt));

    return true;
}


UNIT_TEST bool test_line_discipline_9()
{
    int ret;
    line_discipline_t discipline;
    char shell_buf[MAX_LINE_SIZE];
    char *prompt = "miniOS % ";
    char *command = "ls /dev";

    ret = line_discipline_init(&discipline, process_next_byte, invoke_shell, prompt, shell_buf);
    trb_clear(&terminal_receive_buffer);

    // return value must not be error code
    ASSERT(ret == 0);

    for(int i = 0; i < strlen(command); i++)
    {
        ret = discipline.process_next_byte(&discipline, &command[i], 1);
        ASSERT(ret == 0);

        ASSERT(discipline.current_state == LINE_DISCIPLINE_NORMAL_OPERATION);
        ASSERT(discipline.current_line.cursor == i+1);
        ASSERT(discipline.current_line.end_index == i+1);
        ASSERT(discipline.current_line.line[i] == command[i]);

        ASSERT(discipline.scrollback_buffer.current == discipline.scrollback_buffer.latest);
        ASSERT(discipline.scrollback_buffer.buffer[discipline.scrollback_buffer.current].end_index == i+1);
        ASSERT(discipline.scrollback_buffer.buffer[discipline.scrollback_buffer.current].in_use);
        ASSERT(discipline.scrollback_buffer.buffer[discipline.scrollback_buffer.current].line[i] == command[i]);

        ASSERT(discipline.escape_buffer.current_index == 0);

        ASSERT(get_cursor_x() == strlen(prompt)+i+1);
        ASSERT(terminal_receive_buffer.terminal_buffer[i] == command[i]);
    }

    char del = ASCII_BS;
    ret = discipline.process_next_byte(&discipline, &del, 1);

    ASSERT(discipline.current_state == LINE_DISCIPLINE_NORMAL_OPERATION);

    ASSERT(discipline.current_line.cursor = strlen(command)-1);
    ASSERT(discipline.current_line.end_index = strlen(command)-1);
    ASSERT(strcmp(discipline.current_line.line, "ls /de") == 0);

    ASSERT(discipline.scrollback_buffer.current == discipline.scrollback_buffer.latest);
    ASSERT(discipline.scrollback_buffer.buffer[discipline.scrollback_buffer.current].end_index == strlen(command)-1);
    ASSERT(discipline.scrollback_buffer.buffer[discipline.scrollback_buffer.current].in_use);

    ASSERT(discipline.scrollback_buffer.buffer[discipline.scrollback_buffer.current].line[strlen(command)-1] == 0);

    ASSERT(discipline.escape_buffer.current_index == 0);
    ASSERT(get_cursor_x() == strlen(prompt)+ strlen(command)-1);

    return true;
}


UNIT_TEST bool test_line_discipline_10()
{
    int ret;
    line_discipline_t discipline;
    char shell_buf[MAX_LINE_SIZE];
    char *prompt = "miniOS % ";
    char *command = "ls /dev";
    char *move_left = "\033[D";

    ret = line_discipline_init(&discipline, process_next_byte, invoke_shell, prompt, shell_buf);
    trb_clear(&terminal_receive_buffer);

    // return value must not be error code
    ASSERT(ret == 0);

    for(int i = 0; i < strlen(command); i++)
    {
        ret = discipline.process_next_byte(&discipline, &command[i], 1);
        ASSERT(ret == 0);

        ASSERT(discipline.current_state == LINE_DISCIPLINE_NORMAL_OPERATION);
        ASSERT(discipline.current_line.cursor == i+1);
        ASSERT(discipline.current_line.end_index == i+1);
        ASSERT(discipline.current_line.line[i] == command[i]);

        ASSERT(discipline.scrollback_buffer.current == discipline.scrollback_buffer.latest);
        ASSERT(discipline.scrollback_buffer.buffer[discipline.scrollback_buffer.current].end_index == i+1);
        ASSERT(discipline.scrollback_buffer.buffer[discipline.scrollback_buffer.current].in_use);
        ASSERT(discipline.scrollback_buffer.buffer[discipline.scrollback_buffer.current].line[i] == command[i]);

        ASSERT(discipline.escape_buffer.current_index == 0);

        ASSERT(get_cursor_x() == strlen(prompt)+i+1);
        ASSERT(terminal_receive_buffer.terminal_buffer[i] == command[i]);
    }

    for(int i = 0; i < strlen(move_left); i++)
    {
        ret = discipline.process_next_byte(&discipline, &move_left[i], 1);
        ASSERT(ret == 0);

        if(i < strlen(move_left)-1)
        {
            ASSERT(discipline.escape_buffer.buffer[i] == move_left[i]);
            ASSERT(discipline.escape_buffer.current_index == i+1);
            ASSERT(discipline.current_state == LINE_DISCIPLINE_PROCESS_ANSI_ESCAPE);
        }
        else
        {
            ASSERT(discipline.escape_buffer.current_index == 0);
            ASSERT(discipline.current_state == LINE_DISCIPLINE_NORMAL_OPERATION);
        }
    }

    ASSERT(discipline.current_line.cursor == strlen(command)-1);
    ASSERT(discipline.current_line.end_index == strlen(command));
    ASSERT(get_cursor_x() == strlen(command) + strlen(prompt)-1);


    char new_char = 'l';
    ret = discipline.process_next_byte(&discipline, &new_char, 1);

    ASSERT(discipline.current_state == LINE_DISCIPLINE_NORMAL_OPERATION);

    ASSERT(discipline.current_line.cursor = strlen(command));
    ASSERT(discipline.current_line.end_index = strlen(command)+1);
    ASSERT(strcmp(discipline.current_line.line, "ls /delv") == 0);

    ASSERT(discipline.scrollback_buffer.current == discipline.scrollback_buffer.latest);
    ASSERT(discipline.scrollback_buffer.buffer[discipline.scrollback_buffer.current].end_index == strlen(command)+1);
    ASSERT(discipline.scrollback_buffer.buffer[discipline.scrollback_buffer.current].in_use);

    ASSERT(discipline.escape_buffer.current_index == 0);
    ASSERT(get_cursor_x() == strlen(prompt)+ strlen(command));

    return true;
}


UNIT_TEST bool test_line_discipline_11()
{
    int ret;
    line_discipline_t discipline;
    char shell_buf[MAX_LINE_SIZE];
    char *prompt = "miniOS % ";
    char *command = "ls /dev";
    char *move_left = "\033[D";

    ret = line_discipline_init(&discipline, process_next_byte, invoke_shell, prompt, shell_buf);
    trb_clear(&terminal_receive_buffer);

    // return value must not be error code
    ASSERT(ret == 0);

    for(int i = 0; i < strlen(command); i++)
    {
        ret = discipline.process_next_byte(&discipline, &command[i], 1);
        ASSERT(ret == 0);

        ASSERT(discipline.current_state == LINE_DISCIPLINE_NORMAL_OPERATION);
        ASSERT(discipline.current_line.cursor == i+1);
        ASSERT(discipline.current_line.end_index == i+1);
        ASSERT(discipline.current_line.line[i] == command[i]);

        ASSERT(discipline.scrollback_buffer.current == discipline.scrollback_buffer.latest);
        ASSERT(discipline.scrollback_buffer.buffer[discipline.scrollback_buffer.current].end_index == i+1);
        ASSERT(discipline.scrollback_buffer.buffer[discipline.scrollback_buffer.current].in_use);
        ASSERT(discipline.scrollback_buffer.buffer[discipline.scrollback_buffer.current].line[i] == command[i]);

        ASSERT(discipline.escape_buffer.current_index == 0);

        ASSERT(get_cursor_x() == strlen(prompt)+i+1);
        ASSERT(terminal_receive_buffer.terminal_buffer[i] == command[i]);
    }

    for(int i = 0; i < strlen(move_left); i++)
    {
        ret = discipline.process_next_byte(&discipline, &move_left[i], 1);
        ASSERT(ret == 0);

        if(i < strlen(move_left)-1)
        {
            ASSERT(discipline.escape_buffer.buffer[i] == move_left[i]);
            ASSERT(discipline.escape_buffer.current_index == i+1);
            ASSERT(discipline.current_state == LINE_DISCIPLINE_PROCESS_ANSI_ESCAPE);
        }
        else
        {
            ASSERT(discipline.escape_buffer.current_index == 0);
            ASSERT(discipline.current_state == LINE_DISCIPLINE_NORMAL_OPERATION);
        }
    }

    ASSERT(discipline.current_line.cursor == strlen(command)-1);
    ASSERT(discipline.current_line.end_index == strlen(command));
    ASSERT(get_cursor_x() == strlen(command) + strlen(prompt)-1);


    char del = ASCII_BS;
    ret = discipline.process_next_byte(&discipline, &del, 1);

    ASSERT(discipline.current_state == LINE_DISCIPLINE_NORMAL_OPERATION);

    ASSERT(discipline.current_line.cursor = strlen(command)-2);
    ASSERT(discipline.current_line.end_index = strlen(command)-1);
    ASSERT(strcmp(discipline.current_line.line, "ls /dv") == 0);

    ASSERT(discipline.scrollback_buffer.current == discipline.scrollback_buffer.latest);
    ASSERT(discipline.scrollback_buffer.buffer[discipline.scrollback_buffer.current].end_index == strlen(command)-1);
    ASSERT(discipline.scrollback_buffer.buffer[discipline.scrollback_buffer.current].in_use);

    ASSERT(discipline.escape_buffer.current_index == 0);
    ASSERT(get_cursor_x() == strlen(prompt)+ strlen(command)-2);

    return true;
}

UNIT_TEST bool test_line_discipline_12()
{
    int ret;
    line_discipline_t discipline;
    char shell_buf[MAX_LINE_SIZE];
    char *prompt = "miniOS % ";
    char *move_up = "\033[A";

    ret = line_discipline_init(&discipline, process_next_byte, invoke_shell, prompt, shell_buf);
    trb_clear(&terminal_receive_buffer);

    // return value must not be error code
    ASSERT(ret == 0);

    for(int i = 0; i < strlen(move_up); i++)
    {
        ret = discipline.process_next_byte(&discipline, &move_up[i], 1);

        if(i < strlen(move_up)-1)
        {
            ASSERT(discipline.escape_buffer.buffer[i] == move_up[i]);
            ASSERT(discipline.escape_buffer.current_index == i+1);
            ASSERT(discipline.current_state == LINE_DISCIPLINE_PROCESS_ANSI_ESCAPE);
        }
        else
        {
            ASSERT(discipline.escape_buffer.current_index == 0);
            ASSERT(discipline.current_state == LINE_DISCIPLINE_NORMAL_OPERATION);
        }
    }

    ASSERT(discipline.scrollback_buffer.current == discipline.scrollback_buffer.latest);

    return true;
}


UNIT_TEST bool test_line_discipline_13()
{
    int ret;
    line_discipline_t discipline;
    char shell_buf[MAX_LINE_SIZE];
    char *prompt = "miniOS % ";
    char *move_down = "\033[B";

    ret = line_discipline_init(&discipline, process_next_byte, invoke_shell, prompt, shell_buf);
    trb_clear(&terminal_receive_buffer);

    // return value must not be error code
    ASSERT(ret == 0);

    for(int i = 0; i < strlen(move_down); i++)
    {
        ret = discipline.process_next_byte(&discipline, &move_down[i], 1);

        if(i < strlen(move_down)-1)
        {
            ASSERT(discipline.escape_buffer.buffer[i] == move_down[i]);
            ASSERT(discipline.escape_buffer.current_index == i+1);
            ASSERT(discipline.current_state == LINE_DISCIPLINE_PROCESS_ANSI_ESCAPE);
        }
        else
        {
            ASSERT(discipline.escape_buffer.current_index == 0);
            ASSERT(discipline.current_state == LINE_DISCIPLINE_NORMAL_OPERATION);
        }
    }

    ASSERT(discipline.scrollback_buffer.current == discipline.scrollback_buffer.latest);

    return true;
}

/*
UNIT_TEST bool test_line_discipline_14()
{
    int ret;
    line_discipline_t discipline;
    char shell_buf[MAX_LINE_SIZE];
    char *prompt = "miniOS % ";
    char *command = "ls /dev";
    char *move_up = "\033[A";

}
*/




