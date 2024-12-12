
#include <stdio.h>
#include <string.h>
#include <stddef.h>


#include "scrollback_buffer.h"
#include "test.h"



UNIT_TEST bool test_buffer_entry_init_1()
{
	scrollback_buffer_entry_t entry;
	int ret;

	ret = scrollback_buffer_entry_init(NULL);
	ASSERT(ret < 0);

	ret = scrollback_buffer_entry_init(&entry);
	ASSERT(ret == 0);
	ASSERT(entry.end_index == 0);
	ASSERT(!entry.in_use);

	return true;
}


UNIT_TEST bool test_buffer_entry_insert_1()
{
	scrollback_buffer_entry_t entry;
	int ret;

	ret = scrollback_buffer_entry_insert(NULL, 0, 'a');
	ASSERT(ret < 0);

	ret = scrollback_buffer_entry_init(&entry);
	ASSERT(ret == 0);

	ret = scrollback_buffer_entry_insert(&entry, -1, 'a');
	ASSERT(ret < 0);

	ret = scrollback_buffer_entry_insert(&entry, 2, 'a');
	ASSERT(ret < 0);

	ret = scrollback_buffer_entry_insert(&entry, 80, 'a');
	ASSERT(ret < 0);

	ret = scrollback_buffer_entry_insert(&entry, 0, 'a');
	ASSERT(ret == 0);
	ASSERT(entry.line[0] == 'a');
	ASSERT(entry.in_use);
	ASSERT(entry.end_index == 1);

	return true;
}


UNIT_TEST bool test_buffer_entry_insert_2()
{
	scrollback_buffer_entry_t entry;
	int ret;
	char *str = "hello there";

	ret = scrollback_buffer_entry_init(&entry);
	ASSERT(ret == 0);

	for(int i = 0; i < strlen(str); i++)
	{
		ASSERT(entry.end_index == i);
		ret = scrollback_buffer_entry_insert(&entry, i, str[i]);
		ASSERT(ret == 0);
		ASSERT(entry.line[i] == str[i]);
	}

	ASSERT(entry.end_index == strlen(str));
	ASSERT(entry.in_use);

	ret = scrollback_buffer_entry_insert(&entry, 0, 's');
	ASSERT(strcmp(entry.line, "shello there") == 0);
	ASSERT(entry.end_index == strlen(str) + 1);

	ret = scrollback_buffer_entry_insert(&entry, 6, 'w');
	ASSERT(strcmp(entry.line, "shellow there") == 0);
	ASSERT(entry.end_index == strlen(str) + 2);

	return true;
}



UNIT_TEST bool test_buffer_entry_insert_3()
{
	scrollback_buffer_entry_t entry;
	int ret;
	char *str = "hello there";

	ret = scrollback_buffer_entry_init(&entry);
	ASSERT(ret == 0);

	for(int i = 0; i < strlen(str); i++)
	{
		ASSERT(entry.end_index == i);
		ret = scrollback_buffer_entry_insert(&entry, i, str[i]);
		ASSERT(ret == 0);
		ASSERT(entry.line[i] == str[i]);
	}

	ASSERT(entry.end_index == strlen(str));
	ASSERT(entry.in_use);

	ret = scrollback_buffer_entry_insert(&entry, -1, 's');
	ASSERT(ret < 0);
	ASSERT(entry.end_index == strlen(str));
	ASSERT(entry.in_use);


	ret = scrollback_buffer_entry_insert(&entry, 15, 's');
	ASSERT(ret < 0);
	ASSERT(entry.end_index == strlen(str));
	ASSERT(entry.in_use);

	return true;
}

UNIT_TEST bool test_buffer_entry_insert_4()
{
	scrollback_buffer_entry_t entry;
	int ret;

	ret = scrollback_buffer_entry_init(&entry);
	ASSERT(ret == 0);

	int i;
	for(i = 0; i < MAX_LINE_SIZE; i++)
	{
		ret = scrollback_buffer_entry_insert(&entry, i, 'a');
		ASSERT(ret == 0);
	}

	ret = scrollback_buffer_entry_insert(&entry, i, 'a');
	ASSERT(ret < 0);

	return true;
}



UNIT_TEST bool test_buffer_entry_delete_1()
{
	scrollback_buffer_entry_t entry;
	int ret;
	char *str = "hello there";

	ret = scrollback_buffer_entry_init(&entry);
	ASSERT(ret == 0);

	ret = scrollback_buffer_entry_delete(&entry, 0);
	ASSERT(ret < 0);

	ret = scrollback_buffer_entry_delete(&entry, -1);
	ASSERT(ret < 0);

	ret = scrollback_buffer_entry_delete(&entry, 10);
	ASSERT(ret < 0);

	return true;
}


UNIT_TEST bool test_buffer_entry_delete_2()
{
	scrollback_buffer_entry_t entry;
	int ret;
	char *str = "hello there";

	ret = scrollback_buffer_entry_init(&entry);
	ASSERT(ret == 0);

	for(int i = 0; i < strlen(str); i++)
	{
		ASSERT(entry.end_index == i);
		ret = scrollback_buffer_entry_insert(&entry, i, str[i]);
		ASSERT(ret == 0);
		ASSERT(entry.line[i] == str[i]);
	}

	ret = scrollback_buffer_entry_delete(&entry, strlen(str)-1);
	ASSERT(ret == 0);
	ASSERT(strcmp(entry.line, "hello ther") == 0);
	ASSERT(entry.end_index == strlen(str)-1);


	ret = scrollback_buffer_entry_delete(&entry, 4);
	ASSERT(ret == 0);
	ASSERT(strcmp(entry.line, "hell ther") == 0);
	ASSERT(entry.end_index == strlen(str)-2);

	return true;
}


UNIT_TEST bool test_buffer_entry_in_use_1()
{
	scrollback_buffer_entry_t entry;
	int ret;

	ret = scrollback_buffer_entry_init(&entry);
	ASSERT(ret == 0);
	ASSERT(!entry.in_use);

	ret = scrollback_buffer_entry_set_in_use(&entry);
	ASSERT(ret == 0);
	ASSERT(entry.in_use);

	return true;
}


UNIT_TEST bool test_buffer_entry_in_use_2()
{
	scrollback_buffer_entry_t entry;
	int ret;

	ret = scrollback_buffer_entry_init(&entry);
	ASSERT(ret == 0);
	ASSERT(!entry.in_use);

	ret = scrollback_buffer_entry_set_in_use(&entry);
	ASSERT(ret == 0);
	ASSERT(entry.in_use);
	ASSERT(scrollback_buffer_entry_is_in_use(&entry));

	ret = scrollback_buffer_entry_set_free(&entry);
	ASSERT(ret == 0);
	ASSERT(!entry.in_use);
	ASSERT(!scrollback_buffer_entry_is_in_use(&entry));

	return true;
}


UNIT_TEST bool test_buffer_entry_in_use_3()
{
	int ret;

	ret = scrollback_buffer_entry_set_in_use(NULL);
	ASSERT(ret < 0);

	ret = scrollback_buffer_entry_set_free(NULL);
	ASSERT(ret < 0);


	ASSERT(!scrollback_buffer_entry_is_in_use(NULL));

	return true;
}

UNIT_TEST bool test_buffer_entry_set_line_1()
{
	int ret;
	scrollback_buffer_entry_t entry;

	ret = scrollback_buffer_entry_set_new_line(NULL, NULL);
	ASSERT(ret < 0);
	ret = scrollback_buffer_entry_set_new_line(NULL, "a");
	ASSERT(ret < 0);
	ret = scrollback_buffer_entry_set_new_line(&entry, NULL);

	ret = scrollback_buffer_entry_init(&entry);
	ASSERT(ret == 0);

	ret = scrollback_buffer_entry_set_new_line(&entry, "");
	ASSERT(ret == 0);
	ASSERT(entry.in_use);

	return true;
}

UNIT_TEST bool test_buffer_entry_set_line_2()
{
	scrollback_buffer_entry_t entry;
	int ret;
	char *str = "ls /tmp";

	ret = scrollback_buffer_entry_init(&entry);
	ASSERT(ret == 0);

	ret = scrollback_buffer_entry_set_new_line(&entry, str);
	ASSERT(ret == 0);
	ASSERT(strcmp(entry.line, str) == 0);

	return true;
}


UNIT_TEST bool test_buffer_entry_set_line_3()
{
	scrollback_buffer_entry_t entry;
	int ret;

	char buf[MAX_LINE_SIZE+1];
	for(int i = 0; i < MAX_LINE_SIZE; i++)
	{
		buf[i] = 'a';
	}
	buf[MAX_LINE_SIZE] = 0;

	char buf2[MAX_LINE_SIZE*2];
	for(int i = 0; i < MAX_LINE_SIZE*2; i++)
	{
		buf2[i] = 'a';
	}

	ret = scrollback_buffer_entry_init(&entry);
	ASSERT(ret == 0);

	ret = scrollback_buffer_entry_set_new_line(&entry, buf);
	ASSERT(ret == 0);

	ret = scrollback_buffer_entry_set_new_line(&entry, buf2);
	ASSERT(ret < 0);

	return true;
}







UNIT_TEST bool test_line_init_1()
{
	current_line_t line;
	int ret;

	ret = line_init(&line);
	ASSERT(ret == 0);
	ASSERT(line.cursor == 0);
	ASSERT(line.end_index == 0);


	return true;
}


UNIT_TEST bool test_line_init_2()
{
	int ret;

	ret = line_init(NULL);
	ASSERT(ret < 0);

	return true;
}


UNIT_TEST bool test_line_insert_1()
{
	int ret;

	ret = line_insert(NULL, 'a');
	ASSERT(ret < 0);


	return true;
}


UNIT_TEST bool test_line_insert_2()
{
	current_line_t line;
	int ret;

	ret = line_init(&line);
	ASSERT(ret == 0);

	ret = line_insert(&line, 'a');
	ASSERT(ret == 0);
	ASSERT(line.cursor == 1);
	ASSERT(line.end_index == 1);


	return true;
}


UNIT_TEST bool test_line_insert_3()
{
	current_line_t line;
	int ret;

	ret = line_init(&line);
	ASSERT(ret == 0);

	int i;
	for(i = 0; i < MAX_LINE_SIZE; i++)
	{
		ret = line_insert(&line, 'a');
		ASSERT(ret == 0);
		ASSERT(line.cursor == i+1);
		ASSERT(line.end_index == i+1);
		ASSERT(line.line[i] == 'a');
	}

	ret = line_insert(&line, 'a');
	ASSERT(ret < 0);
	ASSERT(line.cursor == MAX_LINE_SIZE);
	ASSERT(line.end_index == MAX_LINE_SIZE);

	return true;
}


UNIT_TEST bool test_line_set_cursor_1()
{
	current_line_t line;
	int ret;

	ret = line_init(&line);
	ASSERT(ret == 0);

	ret = line_set_cursor(&line, 5);
	ASSERT(ret < 0);
	ret = line_set_cursor(&line, -1);
	ASSERT(ret < 0);

	return true;
}


UNIT_TEST bool test_line_set_cursor_2()
{
	int ret;

	ret = line_set_cursor(NULL, 5);
	ASSERT(ret < 0);

	return true;
}


UNIT_TEST bool test_line_set_cursor_3()
{
	current_line_t line;
	int ret;

	ret = line_init(&line);
	ASSERT(ret == 0);

	int i;
	for(i = 0; i < MAX_LINE_SIZE; i++)
	{
		ret = line_insert(&line, 'a');
		ASSERT(ret == 0);
		ASSERT(line.cursor == i+1);
		ASSERT(line.end_index == i+1);
		ASSERT(line.line[i] == 'a');
	}

	ret = line_set_cursor(&line, 0);
	ASSERT(ret == 0);
	ASSERT(line.cursor == 0);

	for(i = 1; i < MAX_LINE_SIZE; i++)
	{
		ret = line_set_cursor(&line, i);
		ASSERT(ret == 0);
		ASSERT(line.cursor == i);
	}

	return true;
}


UNIT_TEST bool test_line_set_cursor_4()
{
	current_line_t line;
	int ret;

	ret = line_init(&line);
	ASSERT(ret == 0);

	int i;
	for(i = 0; i < MAX_LINE_SIZE/2; i++)
	{
		ret = line_insert(&line, 'a');
		ASSERT(ret == 0);
		ASSERT(line.cursor == i+1);
		ASSERT(line.end_index == i+1);
		ASSERT(line.line[i] == 'a');
	}

	ret = line_set_cursor(&line, 1);
	ASSERT(ret == 0);
	ASSERT(line.cursor == 1);

	ret = line_set_cursor(&line, (MAX_LINE_SIZE/2)+1);
	ASSERT(ret < 0);
	ASSERT(line.cursor == 1);

	return true;
}


UNIT_TEST bool test_line_move_left_1()
{
	int ret;

	ret = line_move_cursor_left(NULL);
	ASSERT(ret < 0);

	return true;
}


UNIT_TEST bool test_line_move_left_2()
{
	current_line_t line;
	int ret;

	ret = line_init(&line);
	ASSERT(ret == 0);

	ret = line_move_cursor_left(&line);
	ASSERT(ret < 0);

	return true;
}



UNIT_TEST bool test_line_move_right_1()
{
	int ret;

	ret = line_move_cursor_right(NULL);
	ASSERT(ret < 0);

	return true;
}


UNIT_TEST bool test_line_move_right_2()
{
	current_line_t line;
	int ret;

	ret = line_init(&line);
	ASSERT(ret == 0);

	ret = line_move_cursor_right(&line);
	ASSERT(ret < 0);

	return true;
}


UNIT_TEST bool test_line_move_left_right_1()
{
	current_line_t line;
	int ret;

	ret = line_init(&line);
	ASSERT(ret == 0);

	int i;
	for(i = 0; i < MAX_LINE_SIZE/2; i++)
	{
		ret = line_insert(&line, 'a');
		ASSERT(ret == 0);
		ASSERT(line.cursor == i+1);
		ASSERT(line.end_index == i+1);
		ASSERT(line.line[i] == 'a');
	}


	for(i = MAX_LINE_SIZE/2; i > 0; i--)
	{
		ret = line_move_cursor_left(&line);
		ASSERT(ret == 0);
		ASSERT(line.cursor == i-1);
		ASSERT(line.end_index == MAX_LINE_SIZE/2);
	}

	ret = line_move_cursor_left(&line);
	ASSERT(ret < 0);
	ASSERT(line.cursor == 0);


	for(i = 0; i < MAX_LINE_SIZE/2; i++)
	{
		ret = line_move_cursor_right(&line);
		ASSERT(ret == 0);
		ASSERT(line.cursor == i+1);
		ASSERT(line.end_index == MAX_LINE_SIZE/2);
	}

	ret = line_move_cursor_right(&line);
	ASSERT(ret < 0);
	ASSERT(line.cursor == MAX_LINE_SIZE/2);


	return true;
}


UNIT_TEST bool test_line_insert_middle_1()
{
	current_line_t line;
	int ret;
	char *str = "ls /tmp";

	ret = line_init(&line);
	ASSERT(ret == 0);

	for(int i = 0; i < strlen(str); i++)
	{
		ret = line_insert(&line, str[i]);
		ASSERT(ret == 0);
		ASSERT(line.line[i] == str[i]);
	}

	ret = line_set_cursor(&line, 4);
	ASSERT(ret == 0);

	ret = line_insert(&line, 's');
	ASSERT(ret == 0);
	ASSERT(line.cursor == 5);
	ASSERT(line.end_index == strlen(str)+1);
	ASSERT(strcmp(line.line, "ls /stmp") == 0);

	return true;
}


UNIT_TEST bool test_line_delete_1()
{
	int ret;

	ret = line_delete(NULL);
	ASSERT(ret < 0);

	return true;
}

UNIT_TEST bool test_line_delete_2()
{
	current_line_t line;
	int ret;

	ret = line_init(&line);
	ASSERT(ret == 0);

	ret = line_delete(&line);
	ASSERT(ret < 0);
	ASSERT(line.cursor == 0);

	return true;
}



UNIT_TEST bool test_line_insert_delete_1()
{
	current_line_t line;
	int ret;
	char * str = "ls /tmps";

	ret = line_init(&line);
	ASSERT(ret == 0);


	int i;
	for(i = 0; i < strlen(str); i++)
	{
		ret = line_insert(&line, str[i]);
		ASSERT(ret == 0);
		ASSERT(line.cursor == i+1);
		ASSERT(line.line[i] == str[i]);
	}

	ret = line_delete(&line);
	ASSERT(ret == 0);
	ASSERT(line.cursor == strlen(str) - 1);
	ASSERT(strcmp(line.line, "ls /tmp") == 0);


	for(i = 0; i < 3; i++)
	{
		ret = line_move_cursor_left(&line);
		ASSERT(ret == 0);
	}

	ret = line_delete(&line);
	ASSERT(ret == 0);
	ASSERT(strcmp(line.line, "ls tmp") == 0);

	return true;
}








UNIT_TEST bool test_buffer_clear_1()
{
	scrollback_buffer_t buffer;
	int ret;

	ret = scrollback_buffer_clear(&buffer);
	
	ASSERT(ret == 0);
	ASSERT(buffer.current == 0);
	ASSERT(buffer.latest == 0);

	return true;
}

UNIT_TEST bool test_buffer_clear_2()
{
	int ret;

	ret = scrollback_buffer_clear(NULL);
	ASSERT(ret < 0);

	return true;
}





UNIT_TEST bool test_buffer_current_next_1()
{
	scrollback_buffer_t buffer;
	int ret;

	ret = scrollback_buffer_clear(&buffer);
	ASSERT(ret == 0);
	ASSERT(buffer.current == 0);

	// can't set current ahead of latest
	ret = scrollback_buffer_set_current_to_next_entry(&buffer);
	ASSERT(ret < 0);
	ASSERT(buffer.current == 0);

	ret = scrollback_buffer_set_current_to_next_entry(NULL);
	ASSERT(ret < 0);

	ret = scrollback_buffer_set_latest_to_next_entry(NULL);
	ASSERT(ret < 0);

	return true;
}


UNIT_TEST bool test_buffer_next_prev_1()
{
	scrollback_buffer_t buffer;
	int ret;

	ret = scrollback_buffer_clear(&buffer);
	ASSERT(ret == 0);
	ASSERT(buffer.current == 0);
	ASSERT(buffer.latest == 0);


	int i;
	for(i = 0; i < SCROLLBACK_BUFFER_NUM_ENTRIES-1; i++)
	{
		ret = scrollback_buffer_set_latest_to_next_entry(&buffer);
		ASSERT(ret == 0);
		ASSERT(buffer.latest == i+1);
		ASSERT(buffer.current == 0);
		ASSERT((buffer.latest - buffer.current) < SCROLLBACK_BUFFER_NUM_ENTRIES);
	}


	for(i = 0; i < SCROLLBACK_BUFFER_NUM_ENTRIES-1; i++)
	{
		ret = scrollback_buffer_set_current_to_next_entry(&buffer);
		ASSERT(ret == 0);
		ASSERT(buffer.current == i+1);
	}

	ret = scrollback_buffer_set_current_to_next_entry(&buffer);
	ASSERT(ret < 0);
	ASSERT(buffer.current == SCROLLBACK_BUFFER_NUM_ENTRIES-1);


	for(i = SCROLLBACK_BUFFER_NUM_ENTRIES-1; i > 0; i--)
	{
		ret = scrollback_buffer_set_current_to_previous_entry(&buffer);
		ASSERT(ret == 0);
		ASSERT(buffer.current == i-1);
	}

	ret = scrollback_buffer_set_current_to_previous_entry(&buffer);
	ASSERT(ret < 0);
	ASSERT(buffer.current == 0);


	return true;
}


// test cycling around buffer
UNIT_TEST bool test_buffer_next_prev_cycle_1()
{
	scrollback_buffer_t buffer;
	int ret;

	ret = scrollback_buffer_clear(&buffer);
	ASSERT(ret == 0);
	ASSERT(buffer.current == 0);
	ASSERT(buffer.latest == 0);


	int i;
	for(i = 0; i < SCROLLBACK_BUFFER_NUM_ENTRIES+4; i++)
	{
		ret = scrollback_buffer_set_latest_to_next_entry(&buffer);
		ASSERT(ret == 0);
		ret = scrollback_buffer_set_current_to_next_entry(&buffer);
		ASSERT(ret == 0);
		ASSERT(buffer.latest == i+1);
		ASSERT(buffer.current == i+1);
		
		ASSERT(CURRENT_INDEX(&buffer) == LATEST_INDEX(&buffer));
		ASSERT(CURRENT_INDEX(&buffer) >= 0 && CURRENT_INDEX(&buffer) < SCROLLBACK_BUFFER_NUM_ENTRIES);
		ASSERT(LATEST_INDEX(&buffer) >= 0 && LATEST_INDEX(&buffer) < SCROLLBACK_BUFFER_NUM_ENTRIES);
	}


	return true;
}



UNIT_TEST bool test_buffer_set_current_1()
{
	scrollback_buffer_t buffer;
	int ret;

	ret = scrollback_buffer_clear(&buffer);
	ASSERT(ret == 0);
	ASSERT(buffer.current == 0);
	ASSERT(buffer.latest == 0);

	int i;
	for(i = 0; i < SCROLLBACK_BUFFER_NUM_ENTRIES-1; i++)
	{
		ret = scrollback_buffer_set_latest_to_next_entry(&buffer);
		ASSERT(ret == 0);
	}

	for(i = 0; i < SCROLLBACK_BUFFER_NUM_ENTRIES-1; i++)
	{
		ret = scrollback_buffer_set_current_entry(&buffer, i);
		ASSERT(ret == 0);
		ASSERT(buffer.current == i);
	}

	ret = scrollback_buffer_set_current_entry(&buffer, -1);
	ASSERT(ret < 0);
	ret = scrollback_buffer_set_current_entry(&buffer, 500);
	ASSERT(ret < 0);
	ret = scrollback_buffer_set_current_entry(&buffer, buffer.latest+1);
	ASSERT(ret < 0);
	ret = scrollback_buffer_set_current_entry(&buffer, buffer.latest);
	ASSERT(ret == 0);


	for(i = 0; i < SCROLLBACK_BUFFER_NUM_ENTRIES-1; i++)
	{
		ret = scrollback_buffer_set_latest_to_next_entry(&buffer);
		ASSERT(ret == 0);
	}

	ret = scrollback_buffer_set_current_entry(&buffer, 2);
	ASSERT(ret < 0);


	return true;
}


UNIT_TEST bool test_buffer_set_current_2()
{
	int ret;

	ret = scrollback_buffer_set_current_entry(NULL, 0);
	ASSERT(ret < 0);

	return true;
}


UNIT_TEST bool test_buffer_get_current_entry_1()
{
	scrollback_buffer_entry_t *entry;
	entry = scrollback_buffer_get_current_entry(NULL);
	ASSERT(entry == NULL);

	return true;
}


UNIT_TEST bool test_buffer_get_current_entry_2()
{
	scrollback_buffer_t buffer;
	scrollback_buffer_entry_t *entry;
	int ret;

	ret = scrollback_buffer_clear(&buffer);
	ASSERT(ret == 0);

	entry = scrollback_buffer_get_current_entry(&buffer);
	ASSERT(entry != NULL);
	ASSERT(entry == &buffer.buffer[CURRENT_INDEX(&buffer)]);

	return true;
}



UNIT_TEST bool test_buffer_get_entry_1()
{
	scrollback_buffer_t buffer;
	int ret;
	scrollback_buffer_entry_t *entry;

	ret = scrollback_buffer_clear(&buffer);
	ASSERT(ret == 0);

	int i;
	for(i = 0; i < SCROLLBACK_BUFFER_NUM_ENTRIES-1; i++)
	{
		ret = scrollback_buffer_set_latest_to_next_entry(&buffer);
		ASSERT(ret == 0);
	}

	for(i = 0; i < SCROLLBACK_BUFFER_NUM_ENTRIES-1; i++)
	{
		entry = scrollback_buffer_get_entry(&buffer, i);
		ASSERT(entry != NULL);
		ASSERT(entry == &buffer.buffer[i])
	}

	entry = scrollback_buffer_get_entry(&buffer, -1);
	ASSERT(entry == NULL);
	entry = scrollback_buffer_get_entry(&buffer, buffer.latest+1);
	ASSERT(entry == NULL);

	ret = scrollback_buffer_set_current_to_next_entry(&buffer);
	ASSERT(ret == 0);
	ret = scrollback_buffer_set_latest_to_next_entry(&buffer);
	ASSERT(ret == 0);

	ret = scrollback_buffer_set_current_to_next_entry(&buffer);
	ASSERT(ret == 0);
	ret = scrollback_buffer_set_latest_to_next_entry(&buffer);
	ASSERT(ret == 0);

	entry = scrollback_buffer_get_entry(&buffer, 0);
	ASSERT(entry == NULL);


	return true;
}


UNIT_TEST bool test_buffer_get_entry_2()
{
	scrollback_buffer_entry_t *entry = scrollback_buffer_get_entry(NULL, 0);
	ASSERT(entry == NULL);

	return true;
}







