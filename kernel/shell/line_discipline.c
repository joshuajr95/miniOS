

#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include <stdio.h>

#include "line_discipline.h"
#include "scrollback_buffer.h"
#include "terminal_control.h"








typedef int (*escape_sequence_callback_t)(line_discipline_t*);


escape_sequence_callback_t escape_sequence_callbacks[] =
{
	[ANSI_ESCAPE_CURSOR_UP_BY_ONE] = handle_scroll_up,
	[ANSI_ESCAPE_CURSOR_DOWN_BY_ONE] = handle_scroll_down,
	[ANSI_ESCAPE_CURSOR_RIGHT_BY_ONE] = handle_scroll_right,
	[ANSI_ESCAPE_CURSOR_LEFT_BY_ONE] = handle_scroll_left
};




int line_discipline_set_prompt(line_discipline_t *discipline, char *new_prompt)
{
	if(discipline == NULL || new_prompt == NULL) return -1;


	// get the length of the new prompt
	int len = 0;
	for(int i = 0; i <= MAX_PROMPT_SIZE; i++)
	{
		if(new_prompt[i] == 0) break;
		len++;
	}

	if(len > MAX_PROMPT_SIZE || len == 0) return -1;


	int i;
	for(i = 0; i < MAX_PROMPT_SIZE; i++)
	{
		discipline->prompt[i] = new_prompt[i];
		if(discipline->prompt[i] == 0) break;
	}

	// clear rest of line
	for(;i < MAX_PROMPT_SIZE; i++)
	{
		discipline->prompt[i] = 0;
	}

	return 0;
}


int line_discipline_register_shell_buffer(line_discipline_t *discipline, char *buffer)
{
	if(buffer == NULL || discipline == NULL) return -1;

	discipline->shell_buffer = buffer;

	return 0;
}



int line_discipline_copy_current_line_to_shell_buffer(line_discipline_t *discipline)
{
	if(discipline == NULL) return -1;

	int i;
	for(int i = 0; i < MAX_LINE_SIZE; i++)
	{
		discipline->shell_buffer[i] = discipline->current_line.line[i];
	}

	return 0;
}



int line_discipline_init(line_discipline_t *discipline,
						int (*process_next_byte)(line_discipline_t *, void *, uint32_t),
						int (*invoke_shell)(void),
						char *prompt,
						char *shell_buffer)
{
	if(discipline == NULL ||
	   process_next_byte == NULL ||
	   invoke_shell == NULL ||
	   prompt == NULL ||
	   shell_buffer == NULL) return -1;

	int ret;

	discipline->process_next_byte = process_next_byte;
	discipline->invoke_shell = invoke_shell;

	ret = line_discipline_set_prompt(discipline, prompt);
	if(ret < 0) {printf("Set prompt failed."); return -1;}

	ret = line_discipline_register_shell_buffer(discipline, shell_buffer);
	if(ret < 0) {printf("Register shell buffer failed."); return -1;}

	ret = escape_sequence_buffer_init(&discipline->escape_buffer);
	if(ret < 0) {printf("Init esc. seq. buf. failed."); return -1;}

	ret = scrollback_buffer_clear(&discipline->scrollback_buffer);
	if(ret < 0) {printf("Init scroll buf failed."); return -1;}

	ret = line_init(&discipline->current_line);
	if(ret < 0) {printf("Line init failed."); return -1;}

	discipline->current_state = LINE_DISCIPLINE_NORMAL_OPERATION;

	set_cursor(0,0);
	clear_entire_screen();

	for(int i = 0; i < strlen(prompt); i++)
	{
		write_to_terminal(prompt[i]);
	}

	return 0;
}



int escape_sequence_buffer_init(escape_sequence_buffer_t *buf)
{
	if(buf == NULL) return -1;

	for(int i = 0; i < ESCAPE_SEQUENCE_BUFFER_SIZE; i++)
	{
		buf->buffer[i] = 0;
	}
	buf->current_index = 0;

	return 0;
}



int escape_sequence_buffer_insert(escape_sequence_buffer_t *buf, char data)
{
	if(buf == NULL || buf->current_index >= ESCAPE_SEQUENCE_BUFFER_SIZE) return -1;

	buf->buffer[buf->current_index] = data;
	buf->current_index++;

	return 0;
}


int escape_sequence_buffer_clear(escape_sequence_buffer_t *buf)
{
	if(buf == NULL) return -1;

	for(int i = 0; i < ESCAPE_SEQUENCE_BUFFER_SIZE; i++)
	{
		buf->buffer[i] = 0;
	}
	buf->current_index = 0;

	return 0;
}



static void copy_from_scrollback_buffer_entry_to_line(scrollback_buffer_entry_t *entry, current_line_t *line)
{
	int i;
	for(i = 0; i < entry->end_index; i++)
	{
		line->line[i] = entry->line[i];
	}
	for(i = entry->end_index; i < MAX_LINE_SIZE; i++)
	{
		line->line[i] = 0;
	}

	line->end_index = entry->end_index;
	line->cursor = line->end_index;
}

static void copy_from_line_to_scrollback_buffer_entry(scrollback_buffer_entry_t *entry, current_line_t *line)
{
	scrollback_buffer_entry_set_new_line(entry, line->line);
}





int handle_scroll_up(line_discipline_t *discipline)
{
	int ret;

	ret = scrollback_buffer_set_current_to_previous_entry(&discipline->scrollback_buffer);

	if(ret < 0)
	{
		// bell means cannot scroll up further
		char echo = ASCII_BEL;
		write_to_terminal(echo);
	}
	else
	{
		// copy new entry to be displayed to line
		scrollback_buffer_entry_t *current_entry = scrollback_buffer_get_current_entry(&discipline->scrollback_buffer);
		copy_from_scrollback_buffer_entry_to_line(current_entry, &discipline->current_line);

		// clear line
		set_cursor_x(strnlen(discipline->prompt, MAX_PROMPT_SIZE));
		clear_rest_of_line();

		// write new line to terminal screen
		for(int i = 0; i < discipline->current_line.end_index; i++)
		{
			write_to_terminal(discipline->current_line.line[i]);
		}
	}

	return ret;
}


int handle_scroll_down(line_discipline_t *discipline)
{
	int ret;

	ret = scrollback_buffer_set_current_to_next_entry(&discipline->scrollback_buffer);

	if(ret < 0)
	{
		// bell if unable to scroll down further
		char echo = ASCII_BEL;
		write_to_terminal(echo);
	}
	else
	{
		// get the text of the new line to be displayed
		scrollback_buffer_entry_t *current_entry = scrollback_buffer_get_current_entry(&discipline->scrollback_buffer);
		copy_from_scrollback_buffer_entry_to_line(current_entry, &discipline->current_line);
		
		// clear line on terminal screen
		set_cursor_x(strnlen(discipline->prompt, MAX_PROMPT_SIZE));
		clear_rest_of_line();

		// write new line to terminal screen
		for(int i = 0; i < discipline->current_line.end_index; i++)
		{
			write_to_terminal(discipline->current_line.line[i]);
		}
	}
	
	return ret;
}


int handle_scroll_left(line_discipline_t *discipline)
{
	int ret;

	// move cursor left in current line
	ret = line_move_cursor_left(&discipline->current_line);

	// move cursor left on terminal screen, or send bell if unable
	if(ret < 0)
	{
		char echo = ASCII_BEL;
		write_to_terminal(echo);
	}
	else
	{
		move_cursor_left_one();
	}

	return ret;
}


int handle_scroll_right(line_discipline_t *discipline)
{
	int ret;

	// move cursor right in the current line
	ret = line_move_cursor_right(&discipline->current_line);

	// move cursor right on terminal screen, or send bell if unable
	if(ret < 0)
	{
		char echo = ASCII_BEL;
		write_to_terminal(echo);

	}
	else
	{
		move_cursor_right_one();
	}

	return ret;
}


int handle_delete(line_discipline_t *discipline)
{
	int ret;

	ret = line_delete(&discipline->current_line);

	if(ret < 0)
	{
		// could not delete. Line might be empty or just at beginning.
		// either way, send bell
		char echo = ASCII_BEL;
		write_to_terminal(echo);
	}
	else
	{
		// syncing between line and scrollback buffer only occurs on latest line
		if(discipline->scrollback_buffer.current == discipline->scrollback_buffer.latest)
		{
			scrollback_buffer_entry_t *current_entry = scrollback_buffer_get_current_entry(&discipline->scrollback_buffer);
			ret = scrollback_buffer_entry_delete(current_entry, discipline->current_line.cursor);
		}

		// send escape sequences to terminal to set cursor and clear line after the end of the prompt
		int next_cursor = strnlen(discipline->prompt, MAX_PROMPT_SIZE) + discipline->current_line.cursor;
		set_cursor_x(strnlen(discipline->prompt, MAX_PROMPT_SIZE));
		clear_rest_of_line();

		// write the line (with 1 less char) to terminal
		for(int i = 0; i < discipline->current_line.end_index; i++)
		{
			write_to_terminal(discipline->current_line.line[i]);
		}

		// since writing shifts the cursor, need to reset it to where it was
		set_cursor_x(next_cursor);
	}

	return ret;
}


int handle_return(line_discipline_t *discipline)
{
	int ret;

	scrollback_buffer_entry_t *latest_entry = scrollback_buffer_get_latest_entry(&discipline->scrollback_buffer);
	copy_from_line_to_scrollback_buffer_entry(latest_entry, &discipline->current_line);

	scrollback_buffer_set_latest_to_next_entry(&discipline->scrollback_buffer);
	scrollback_buffer_set_current_entry(&discipline->scrollback_buffer, discipline->scrollback_buffer.latest);
	latest_entry = scrollback_buffer_get_latest_entry(&discipline->scrollback_buffer);
	scrollback_buffer_entry_init(latest_entry);
	scrollback_buffer_entry_set_in_use(latest_entry);

	// copy to shell buffer
	line_discipline_copy_current_line_to_shell_buffer(discipline);
	line_init(&discipline->current_line);

	// set cursor to beginning of next line
	set_cursor(0, get_cursor_y() + 1);

	// invoke shell
	discipline->invoke_shell();

	for(int i = 0; i < strnlen(discipline->prompt, MAX_PROMPT_SIZE); i++)
	{
		write_to_terminal(discipline->prompt[i]);
	}

	return 0;
}


int process_ANSI_escape_sequence(line_discipline_t *discipline, char data)
{
	int ret;

	// insert next char in escape sequence
	ret = escape_sequence_buffer_insert(&discipline->escape_buffer, data);
	if(ret < 0) return -1;

	int index = match_escape_sequence(discipline->escape_buffer.buffer);
	if(index >= 0 && escape_sequence_callbacks[index] != NULL)
	{
		// escape sequence found. Invoke callback
		ret = escape_sequence_callbacks[index](discipline);
		ret &= escape_sequence_buffer_clear(&discipline->escape_buffer);
		discipline->current_state = LINE_DISCIPLINE_NORMAL_OPERATION;
	}
	else
	{
		ret = -1;
	}
	
	return ret;
}


int process_ASCII_control_char(line_discipline_t *discipline, char data)
{
	switch(data)
    {
        case ASCII_BEL:
            write_to_terminal(data);
            break;

        case ASCII_ESC:
			// start escape sequence
            discipline->current_state = LINE_DISCIPLINE_PROCESS_ANSI_ESCAPE;
            escape_sequence_buffer_insert(&discipline->escape_buffer, data);
            break;

        case ASCII_DEL:
            // ignored
            break;

        case ASCII_BS:
            handle_delete(discipline);
            break;

        case ASCII_TAB:
            // no autocomplete yet
            break;

        case ASCII_LF:
            handle_return(discipline);
            break;

        case ASCII_CR:
            handle_return(discipline);
            break;

        default:
            break;
    }

	return 0;
}


int process_printable_ASCII_char(line_discipline_t *discipline, char data)
{
	int ret;

	ret = line_insert(&discipline->current_line, data);

	if(ret < 0)
	{
		// could not insert latest character typed, so send BELL to alert user
		char echo = ASCII_BEL;
		write_to_terminal(echo);
	}
	else
	{
		// only sync between current line and scrollback buffer if viewing latest entry
		if(discipline->scrollback_buffer.current == discipline->scrollback_buffer.latest)
		{
			scrollback_buffer_entry_t *latest_entry = scrollback_buffer_get_latest_entry(&discipline->scrollback_buffer);
			scrollback_buffer_entry_insert(latest_entry, discipline->current_line.cursor-1, data);
		}

		// echo back to terminal (change in future to allow disabling of input echoing)
		if(discipline->current_line.cursor < discipline->current_line.end_index)
		{
			int next_cursor = strlen(discipline->prompt) + discipline->current_line.cursor;
			set_cursor_x(next_cursor-1);
			clear_rest_of_line();

			for(int i = discipline->current_line.cursor - 1; i < discipline->current_line.end_index; i++)
			{
				write_to_terminal(discipline->current_line.line[i]);
			}

			set_cursor_x(next_cursor);
		}
		else
		{
			write_to_terminal(data);
		}
	}

	return 0;
}


int process_ASCII_char(line_discipline_t *discipline, char data)
{
	if(data < ASCII_DEL && data > ASCII_US)
    {
        // ASCII range 32-126 is printable chars
        process_printable_ASCII_char(discipline, data);
    }
    else
    {
        // process ASCII control codes
        process_ASCII_control_char(discipline, data);
    }

	return 0;
}


int process_next_byte(line_discipline_t *discipline, void *buffer, uint32_t size)
{
	char data = *((char *)buffer);

    switch(discipline->current_state)
    {
        case LINE_DISCIPLINE_PROCESS_ANSI_ESCAPE:
            process_ANSI_escape_sequence(discipline, data);
            break;

        case LINE_DISCIPLINE_NORMAL_OPERATION:
            process_ASCII_char(discipline, data);
            break;

        default:
            break;
    }

	return 0;
}








