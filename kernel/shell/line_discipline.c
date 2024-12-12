

#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "line_discipline.h"
#include "scrollback_buffer.h"
#include "terminal_control.h"






escape_sequence_buffer_t escape_sequence_buffer;
line_discipline_t line_discipline;


typedef int (*escape_sequence_callback_t)(void);


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
	for(int i = 0; i < MAX_PROMPT_SIZE; i++)
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

	// clean rest of line
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





int handle_scroll_up(void)
{
	int ret;

	ret = scrollback_buffer_set_current_to_previous_entry(&line_discipline.scrollback_buffer);

	if(ret < 0)
	{
		char echo = ASCII_BEL;
		write_to_terminal(echo);
	}
	else
	{
		scrollback_buffer_entry_t *current_entry = scrollback_buffer_get_current_entry(&line_discipline.scrollback_buffer);
		copy_from_scrollback_buffer_entry_to_line(current_entry, &line_discipline.current_line);
		set_cursor_x(strnlen(line_discipline.prompt, MAX_PROMPT_SIZE));
		clear_rest_of_line();

		for(int i = 0; i < line_discipline.current_line.end_index; i++)
		{
			write_to_terminal(line_discipline.current_line.line[i]);
		}
	}

	return ret;
}


int handle_scroll_down(void)
{
	int ret;

	ret = scrollback_buffer_set_current_to_next_entry(&line_discipline.scrollback_buffer);

	if(ret < 0)
	{
		char echo = ASCII_BEL;
		write_to_terminal(echo);
	}
	else
	{
		scrollback_buffer_entry_t *current_entry = scrollback_buffer_get_current_entry(&line_discipline.scrollback_buffer);
		copy_from_scrollback_buffer_entry_to_line(current_entry, &line_discipline.current_line);
		set_cursor_x(strnlen(line_discipline.prompt, MAX_PROMPT_SIZE));
		clear_rest_of_line();

		for(int i = 0; i < line_discipline.current_line.end_index; i++)
		{
			write_to_terminal(line_discipline.current_line.line[i]);
		}
	}
	
	return ret;
}


int handle_scroll_left(void)
{
	int ret;

	ret = line_move_cursor_left(&line_discipline.current_line);

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


int handle_scroll_right(void)
{
	int ret;

	ret = line_move_cursor_right(&line_discipline.current_line);

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


int handle_delete(void)
{
	int ret;

	ret = line_delete(&line_discipline.current_line);

	if(ret < 0)
	{
		char echo = ASCII_BEL;
		write_to_terminal(echo);
	}
	else
	{
		if(line_discipline.scrollback_buffer.current == line_discipline.scrollback_buffer.latest)
		{
			scrollback_buffer_entry_t *current_entry = scrollback_buffer_get_current_entry(&line_discipline.scrollback_buffer);
			scrollback_buffer_entry_delete(current_entry, line_discipline.current_line.cursor+1);
		}

		int next_cursor = strnlen(line_discipline.prompt, MAX_PROMPT_SIZE) + line_discipline.current_line.cursor;
		set_cursor_x(strnlen(line_discipline.prompt, MAX_PROMPT_SIZE));
		clear_rest_of_line();

		for(int i = 0; i < line_discipline.current_line.end_index; i++)
		{
			write_to_terminal(line_discipline.current_line.line[i]);
		}

		set_cursor_x(next_cursor);
	}

	return ret;
}


int handle_return(void)
{
	int ret;

	scrollback_buffer_entry_t *latest_entry = scrollback_buffer_get_latest_entry(&line_discipline.scrollback_buffer);
	copy_from_line_to_scrollback_buffer_entry(latest_entry, &line_discipline.current_line);

	scrollback_buffer_set_latest_to_next_entry(&line_discipline.scrollback_buffer);
	scrollback_buffer_set_current_entry(&line_discipline.scrollback_buffer, line_discipline.scrollback_buffer.latest);
	latest_entry = scrollback_buffer_get_latest_entry(&line_discipline.scrollback_buffer);
	scrollback_buffer_entry_init(latest_entry);
	scrollback_buffer_entry_set_in_use(latest_entry);

	// copy to shell buffer
	line_discipline_copy_current_line_to_shell_buffer(&line_discipline);

	line_init(&line_discipline.current_line);

	move_cursor_down_one();
	set_cursor_x(0);

	// invoke shell
	line_discipline.invoke_shell();


	for(int i = 0; i < strnlen(line_discipline.prompt, MAX_PROMPT_SIZE); i++)
	{
		write_to_terminal(line_discipline.prompt[i]);
	}

	return 0;
}


int process_ANSI_escape_sequence(char data)
{
	int ret;

	ret = escape_sequence_buffer_insert(&line_discipline.escape_buffer, data);

	if(ret < 0) return -1;

	int index = match_escape_sequence(line_discipline.escape_buffer.buffer);

	if(index >= 0 && escape_sequence_callbacks[index] != NULL)
	{
		ret = escape_sequence_callbacks[index]();
		ret &= escape_sequence_buffer_clear(&line_discipline.escape_buffer);
	}
	else
	{
		ret = -1;
	}
	
	return ret;
}


int process_ASCII_control_char(char data)
{
	switch(data)
    {
        case ASCII_BEL:
            write_to_terminal(data);
            break;

        case ASCII_ESC:
            line_discipline.current_state = LINE_DISCIPLINE_PROCESS_ANSI_ESCAPE;
            escape_sequence_buffer_insert(&line_discipline.escape_buffer, data);
            break;

        case ASCII_DEL:
            // ignored
            break;

        case ASCII_BS:
            handle_delete();
            break;

        case ASCII_TAB:
            // no autocomplete yet
            break;

        case ASCII_LF:
            handle_return();
            break;

        case ASCII_CR:
            handle_return();
            break;

        default:
            break;
    }

	return 0;
}


int process_printable_ASCII_char(char data)
{
	int ret;

	ret = line_insert(&line_discipline.current_line, data);

	if(ret < 0)
	{
		// could not insert latest character typed, so send BELL to alert user
		char echo = ASCII_BEL;
		write_to_terminal(echo);
	}
	else
	{
		// only sync between current line and scrollback buffer if viewing latest entry
		if(line_discipline.scrollback_buffer.current == line_discipline.scrollback_buffer.latest)
		{
			scrollback_buffer_entry_t *latest_entry = scrollback_buffer_get_latest_entry(&line_discipline.scrollback_buffer);
			scrollback_buffer_entry_insert(latest_entry, line_discipline.current_line.cursor-1, data);
		}

		// echo back to terminal (change in future to allow disabling of input echoing)
		write_to_terminal(data);
	}

	return 0;
}


int process_ASCII_char(char data)
{
	if(data < ASCII_DEL && data > ASCII_US)
    {
        // ASCII range 32-126 is printable chars
        process_printable_ASCII_char(data);
    }
    else
    {
        // process ASCII control codes
        process_ASCII_control_char(data);
    }

	return 0;
}


int process_next_byte(void *buffer, uint32_t size)
{
	char data = *((char *)buffer);

    switch(line_discipline.current_state)
    {
        case LINE_DISCIPLINE_PROCESS_ANSI_ESCAPE:
            process_ANSI_escape_sequence(data);
            break;

        case LINE_DISCIPLINE_NORMAL_OPERATION:
            process_ASCII_char(data);
            break;

        default:
            break;
    }

	return 0;
}








