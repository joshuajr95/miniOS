

#include <string.h>
#include <stdio.h>

#include "terminal_control.h"
#include "test.h"




// structs and functions for the test apparatus

typedef struct
{
    char terminal_buffer[64];
    int in;
} terminal_receive_buffer_t;



void trb_clear(terminal_receive_buffer_t *buf)
{
    for(int i = 0; i < 64; i++)
    {
        buf->terminal_buffer[i] = 0;
    }

    buf->in = 0;
}



terminal_receive_buffer_t buf;

extern cursor_t cursor;




int terminal_send_byte(uint8_t byte_to_send)
{
    if(buf.in >= 64) return -1;

    buf.terminal_buffer[buf.in] = byte_to_send;
    buf.in++;

    return 0;
}



/**************
 * Unit Tests *
 **************/



UNIT_TEST bool test_set_cursor_x_1()
{
    int ret;

    trb_clear(&buf);

    ret = set_cursor_x(-1);
    ASSERT(ret < 0);

    ret = set_cursor_x(5);
    ASSERT(ret == 0);
    ASSERT(cursor.x == 6);
    ASSERT(strncmp(buf.terminal_buffer, "\033[1;6H", 64) == 0);

    return true;
}


UNIT_TEST bool test_set_cursor_y_1()
{
    int ret;

    trb_clear(&buf);

    ret = set_cursor_y(-1);
    ASSERT(ret < 0);

    ret = set_cursor(0, 0);
    ASSERT(ret == 0);
    ASSERT(cursor.x == 1 && cursor.y == 1);
    trb_clear(&buf);

    ret = set_cursor_y(5);
    ASSERT(ret == 0);
    ASSERT(cursor.y == 6);

    ASSERT(strncmp(buf.terminal_buffer, "\033[6;1H", 64) == 0);

    return true;
}


UNIT_TEST bool test_set_cursor_1()
{
    int ret;

    trb_clear(&buf);

    ret = set_cursor(-1, 4);
    ASSERT(ret < 0);

    ret = set_cursor(5, 7);
    ASSERT(ret == 0);
    ASSERT(cursor.x == 6);
    ASSERT(cursor.y == 8);
    ASSERT(strncmp(buf.terminal_buffer, "\033[8;6H", 64) == 0)

    return true;
}


UNIT_TEST bool test_move_cursor_left_and_right_1()
{
    int ret;

    trb_clear(&buf);

    ret = set_cursor(0,0);
    ASSERT(ret == 0);
    ASSERT(cursor.x == 1);
    ASSERT(cursor.y == 1);
    ASSERT(strncmp(buf.terminal_buffer, "\033[1;1H", 64) == 0);
    trb_clear(&buf);

    ret = move_cursor_left_one();
    ASSERT(ret < 0);
    ASSERT(cursor.x == 1 && cursor.y == 1);

    ret = move_cursor_right_one();
    ASSERT(ret == 0);
    ASSERT(cursor.x == 2);
    ASSERT(cursor.y == 1);
    ASSERT(strncmp(buf.terminal_buffer, "\033[C", 64) == 0);
    trb_clear(&buf);

    ret = move_cursor_left_one();
    ASSERT(ret == 0);
    ASSERT(cursor.x == 1);
    ASSERT(cursor.y == 1);
    ASSERT(strncmp(buf.terminal_buffer, "\033[D", 64) == 0);

    return true;
}


UNIT_TEST bool test_move_cursor_up_and_down_1()
{
    int ret;

    trb_clear(&buf);

    ret = set_cursor(0,0);
    ASSERT(ret == 0);
    ASSERT(cursor.x == 1);
    ASSERT(cursor.y == 1);
    ASSERT(strncmp(buf.terminal_buffer, "\033[1;1H", 64) == 0);
    trb_clear(&buf);

    ret = move_cursor_up_one();
    ASSERT(ret < 0);
    ASSERT(cursor.x == 1 && cursor.y == 1);

    ret = move_cursor_down_one();
    ASSERT(ret == 0);
    ASSERT(cursor.x == 1);
    ASSERT(cursor.y == 2);
    ASSERT(strncmp(buf.terminal_buffer, "\033[B", 64) == 0);
    trb_clear(&buf);

    ret = move_cursor_up_one();
    ASSERT(ret == 0);
    ASSERT(cursor.x == 1);
    ASSERT(cursor.y == 1);
    ASSERT(strncmp(buf.terminal_buffer, "\033[A", 64) == 0);

    return true;
}


UNIT_TEST bool test_clear_rest_of_line_1()
{
    int ret;

    trb_clear(&buf);
    ret = set_cursor(0,0);
    ASSERT(ret == 0);
    ASSERT(cursor.x == 1);
    ASSERT(cursor.y == 1);
    ASSERT(strncmp(buf.terminal_buffer, "\033[1;1H", 64) == 0);
    trb_clear(&buf);

    ret = clear_rest_of_line();
    ASSERT(ret == 0);
    ASSERT(strncmp(buf.terminal_buffer, "\033[0K", 64) == 0);
    trb_clear(&buf);

    return true;
}


UNIT_TEST bool test_clear_entire_screen_1()
{
    int ret;

    trb_clear(&buf);
    ret = set_cursor(0,0);
    ASSERT(ret == 0);
    ASSERT(cursor.x == 1);
    ASSERT(cursor.y == 1);
    ASSERT(strncmp(buf.terminal_buffer, "\033[1;1H", 64) == 0);
    trb_clear(&buf);

    ret = clear_rest_of_line();
    ASSERT(ret == 0);
    ASSERT(strncmp(buf.terminal_buffer, "\033[0K", 64) == 0);
    trb_clear(&buf);

    return true;
}



