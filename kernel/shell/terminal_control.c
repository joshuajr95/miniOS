

#include <stddef.h>
#include <stdio.h>
#include <string.h>


#include "terminal_control.h"



/*************************
 * ANSI Escape Sequences *
 *************************/


char *ANSI_escape_sequences[] = {
    [ANSI_ESCAPE_CLEAR_REST_OF_LINE] =          "\033[0K",
    [ANSI_ESCAPE_SET_CURSOR] =                  "\033[%d;%dH",    // 2 arguments must be passed
    [ANSI_ESCAPE_CURSOR_UP_BY_ONE] =            "\033[A",
    [ANSI_ESCAPE_CURSOR_DOWN_BY_ONE] =          "\033[B",
    [ANSI_ESCAPE_CURSOR_RIGHT_BY_ONE] =         "\033[C",
    [ANSI_ESCAPE_CURSOR_LEFT_BY_ONE] =          "\033[D",
    [ANSI_ESCAPE_CLEAR_ENTIRE_SCREEN] =         "\033[2J"
};


int match_escape_sequence(char *esc_seq)
{
    if(esc_seq == NULL) return -1;

    int esc_seq_size = sizeof(ANSI_escape_sequences)/sizeof(ANSI_escape_sequences[0]);
    
    int index;
    for(index = esc_seq_size-1; index >= 0; index--)
    {
        if(strcmp(esc_seq, ANSI_escape_sequences[index]) == 0) break;
    }

    return index;
}





cursor_t cursor;



int set_cursor_x(int x_coordinate)
{
    if(x_coordinate < 0) return -1;

    // set the x coordinate
    cursor.x = x_coordinate;

    // build escape sequence with new x coordinate
    char *esc_seq = ANSI_escape_sequences[ANSI_ESCAPE_SET_CURSOR];
    char buf[32];
    snprintf(buf, sizeof(buf), esc_seq, cursor.y, cursor.x);

    // send escape sequence
    for(int i = 0; buf[i] != 0; i++)
    {
        terminal_send_byte(buf[i]);
    }

    return 0;
}


int set_cursor_y(int y_coordinate)
{
    if(y_coordinate < 0) return -1;

    // set the y coordinate
    cursor.y = y_coordinate;

    // build escape sequence with new y coordinate
    char *esc_seq = ANSI_escape_sequences[ANSI_ESCAPE_SET_CURSOR];
    char buf[32];
    snprintf(buf, sizeof(buf), esc_seq, cursor.y, cursor.x);

    // send escape sequence
    for(int i = 0; buf[i] != 0; i++)
    {
        terminal_send_byte(buf[i]);
    }

    return 0;
}


int get_cursor_x()
{
    return cursor.x;
}


int get_cursor_y()
{
    return cursor.y;
}


int set_cursor(int x_coordinate, int y_coordinate)
{
    if(x_coordinate < 0 || y_coordinate < 0) return -1;

    // set x and y coordinates
    cursor.x = x_coordinate;
    cursor.y = y_coordinate;

    // build escape sequence with x and y coordinates
    char *esc_seq = ANSI_escape_sequences[ANSI_ESCAPE_SET_CURSOR];
    char buf[32];
    snprintf(buf, sizeof(buf), esc_seq, cursor.y, cursor.x);

    // send escape sequence
    for(int i = 0; buf[i] != 0; i++)
    {
        terminal_send_byte(buf[i]);
    }

    return 0;
}



int move_cursor_left_one()
{
    if(cursor.x <= 0) return -1;

    cursor.x--;

    char *esc_seq = ANSI_escape_sequences[ANSI_ESCAPE_CURSOR_LEFT_BY_ONE];
    if(esc_seq == NULL) return -1;

    for(int i = 0; esc_seq[i] != 0; i++)
    {
        terminal_send_byte(esc_seq[i]);
    }

    return 0;
}


int move_cursor_right_one()
{
    cursor.x++;

    char *esc_seq = ANSI_escape_sequences[ANSI_ESCAPE_CURSOR_RIGHT_BY_ONE];
    if(esc_seq == NULL) return -1;

    for(int i = 0; esc_seq[i] != 0; i++)
    {
        terminal_send_byte(esc_seq[i]);
    }

    return 0;
}


int move_cursor_up_one()
{
    if(cursor.y <= 0) return -1;

    cursor.y--;

    char *esc_seq = ANSI_escape_sequences[ANSI_ESCAPE_CURSOR_UP_BY_ONE];
    if(esc_seq == NULL) return -1;

    for(int i = 0; esc_seq[i] != 0; i++)
    {
        terminal_send_byte(esc_seq[i]);
    }

    return 0;
}



int move_cursor_down_one()
{
    cursor.y++;

    char *esc_seq = ANSI_escape_sequences[ANSI_ESCAPE_CURSOR_DOWN_BY_ONE];
    if(esc_seq == NULL) return -1;

    for(int i = 0; esc_seq[i] != 0; i++)
    {
        terminal_send_byte(esc_seq[i]);
    }

    return 0;
}



int clear_rest_of_line()
{
    char *esc_seq = ANSI_escape_sequences[ANSI_ESCAPE_CLEAR_REST_OF_LINE];
    if(esc_seq == NULL) return -1;

    for(int i = 0; esc_seq[i] != 0; i++)
    {
        terminal_send_byte(esc_seq[i]);
    }

    return 0;
}



int clear_entire_screen()
{
    char *esc_seq = ANSI_escape_sequences[ANSI_ESCAPE_CLEAR_ENTIRE_SCREEN];
    if(esc_seq == NULL) return -1;

    for(int i = 0; esc_seq[i] != 0; i++)
    {
        terminal_send_byte(esc_seq[i]);
    }

    return 0;
}



int write_to_terminal(char data)
{
    if(data > 127) return -1;

    terminal_send_byte(data);
    cursor.x++;
    return 0;
}



