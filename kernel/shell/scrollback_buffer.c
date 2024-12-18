
#include <stddef.h>

#include "scrollback_buffer.h"




int scrollback_buffer_entry_init(scrollback_buffer_entry_t *entry)
{
	if(entry == NULL)
	{
		return -1;
	}


	entry->end_index = 0;
	scrollback_buffer_entry_set_free(entry);

	for(int i = 0; i < MAX_LINE_SIZE; i++)
	{
		entry->line[i] = 0;
	}

	return 0;
}


int scrollback_buffer_entry_insert(scrollback_buffer_entry_t *entry, int cursor, char data)
{

	// check for invalid parameters passed
	if(entry == NULL ||
	   cursor < 0 ||
	   cursor > entry->end_index ||
	   cursor >= MAX_LINE_SIZE ||
	   entry->end_index >= MAX_LINE_SIZE)
	{
		return -1;
	}


	// if cursor in middle of line, shift remaining char down
	if(cursor < entry->end_index)
	{
		for(int i = entry->end_index; i > cursor; i--)
		{
			entry->line[i] = entry->line[i-1];
		}
	}

	entry->line[cursor] = data;
	entry->end_index++;
	scrollback_buffer_entry_set_in_use(entry);

	return 0;
}


int scrollback_buffer_entry_delete(scrollback_buffer_entry_t *entry, int cursor)
{
	if(entry == NULL ||
	   cursor <= 0 ||
	   cursor > entry->end_index ||
	   cursor > MAX_LINE_SIZE - 1 ||
	   entry->end_index > MAX_LINE_SIZE - 1)
	{
		return -1;
	}

	if(cursor < entry->end_index)
	{
		for(int i = cursor; i < entry->end_index; i++)
		{
			entry->line[i] = entry->line[i+1];
		}
	}

	entry->line[entry->end_index] = 0;
	entry->end_index--;

	return 0;
}


int scrollback_buffer_entry_set_new_line(scrollback_buffer_entry_t *entry, char *line)
{
	if(entry == NULL || line == NULL) return -1;

	// get line length
	int len = 0;
	for(int i = 0; i < MAX_LINE_SIZE+1; i++)
	{
		if(line[i] == 0) break;
		len++;
	}

	if(len > MAX_LINE_SIZE) return -1;


	// set the entry to the line and clear chars after end of line
    int i;
	for(i = 0; i < len; i++) entry->line[i] = line[i];
    for(; i < MAX_LINE_SIZE; i++) entry->line[i] = 0;
    
	entry->in_use = true;
    entry->end_index = len;

	return 0;
}


int scrollback_buffer_entry_set_in_use(scrollback_buffer_entry_t *entry)
{
	if(entry == NULL)
	{
		return -1;
	}

	entry->in_use = true;

	return 0;
}



int scrollback_buffer_entry_set_free(scrollback_buffer_entry_t *entry)
{
	if(entry == NULL)
	{
		return -1;
	}

	entry->in_use = false;

	return 0;
}


bool scrollback_buffer_entry_is_in_use(scrollback_buffer_entry_t *entry)
{
	if(entry == NULL)
	{
		return false;
	}
	else
	{
		return entry->in_use;
	}
}







int line_set_cursor(current_line_t *line, int cursor_position)
{
	if(line == NULL ||
	   cursor_position < 0 ||
	   cursor_position > line->end_index ||
	   cursor_position > MAX_LINE_SIZE)
	{
		return -1;
	}

	line->cursor = cursor_position;

	return 0;
}



int line_move_cursor_left(current_line_t *line)
{
	if(line == NULL || line->cursor <= 0) return -1;

	line->cursor--;
	return 0;
}



int line_move_cursor_right(current_line_t *line)
{
	if(line == NULL ||
	   line->cursor >= line->end_index ||
	   line->cursor >= MAX_LINE_SIZE)
	{
		return -1;
	}


	line->cursor++;
	return 0;
}



int line_init(current_line_t *line)
{
	if(line == NULL) return -1;


	line->cursor = 0;
	line->end_index = 0;

	for(int i = 0; i < MAX_LINE_SIZE; i++)
	{
		line->line[i] = 0;
	}

	return 0;
}



int line_insert(current_line_t *line, char data)
{
	if(line == NULL || line->end_index >= MAX_LINE_SIZE)
	{
		return -1;
	}


	// if cursor in middle of line, shift remaining char down
	if(line->cursor < line->end_index)
	{
		for(int i = line->end_index; i > line->cursor; i--)
		{
			line->line[i] = line->line[i-1];
		}
	}

	line->line[line->cursor] = data;
	line->end_index++;
	line->cursor++;

	return 0;
}



int line_delete(current_line_t *line)
{
	if(line == NULL || line->cursor <= 0)
	{
		return -1;
	}


	if(line->cursor < line->end_index)
	{
		for(int i = line->cursor; i < line->end_index; i++)
		{
			line->line[i-1] = line->line[i];
		}
	}

	line->cursor--;
	line->end_index--;
	line->line[line->end_index] = 0;

	return 0;
}







int scrollback_buffer_set_current_to_next_entry(scrollback_buffer_t *buffer)
{
	if(buffer == NULL ||
	   buffer->current >= buffer->latest)
	{
	   	return -1;
	}

	buffer->current++;

	return 0;
}



int scrollback_buffer_set_current_to_previous_entry(scrollback_buffer_t *buffer)
{
	if(buffer == NULL ||
	   buffer->current <= 0 ||
	   buffer->current <= buffer->latest - SCROLLBACK_BUFFER_NUM_ENTRIES + 1)
	{
		return -1;
	}
	
	buffer->current--;

	return 0;
}



int scrollback_buffer_set_latest_to_next_entry(scrollback_buffer_t *buffer)
{
	if(buffer == NULL ||
	   buffer->latest >= buffer->current + SCROLLBACK_BUFFER_NUM_ENTRIES - 1)
	{
		return -1;
	}

	buffer->latest++;

	return 0;
}



int scrollback_buffer_set_current_entry(scrollback_buffer_t *buffer, int entry_number)
{
	if(buffer == NULL ||
	   entry_number < 0 ||
	   entry_number > buffer->latest ||
	   entry_number < buffer->latest - SCROLLBACK_BUFFER_NUM_ENTRIES+1)
	{
		return -1;
	}

	buffer->current = entry_number;

	return 0;
}




scrollback_buffer_entry_t *scrollback_buffer_get_current_entry(scrollback_buffer_t *buffer)
{
	if(buffer == NULL) return NULL;

	return &buffer->buffer[CURRENT_INDEX(buffer)];
}


scrollback_buffer_entry_t *scrollback_buffer_get_latest_entry(scrollback_buffer_t *buffer)
{
	if(buffer == NULL) return NULL;

	return &buffer->buffer[LATEST_INDEX(buffer)];
}


scrollback_buffer_entry_t *scrollback_buffer_get_entry(scrollback_buffer_t *buffer, int entry_number)
{
	if(buffer == NULL ||
	   entry_number > buffer->latest ||
	   entry_number < buffer->latest - SCROLLBACK_BUFFER_NUM_ENTRIES+1)
	{
	  	return NULL;
	}


	return &buffer->buffer[entry_number%SCROLLBACK_BUFFER_NUM_ENTRIES];
}



int scrollback_buffer_clear(scrollback_buffer_t *buffer)
{
	int ret;

	if(buffer == NULL)
	{
		return -1;
	}

    buffer->current = 0;
    buffer->latest = 0;

    for(int i = 0; i < SCROLLBACK_BUFFER_NUM_ENTRIES; i++)
    {
        scrollback_buffer_entry_t *entry = &buffer->buffer[i];
        if(entry == NULL) return -1;
        if(scrollback_buffer_entry_init(entry) < 0) return -1;
    }

    return 0;
}




