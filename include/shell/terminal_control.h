#ifndef TERMINAL_CONTROL_H
#define TERMINAL_CONTROL_H




#include <stdint.h>




#define ANSI_ESCAPE_CLEAR_REST_OF_LINE      0
#define ANSI_ESCAPE_SET_CURSOR              1
#define ANSI_ESCAPE_CURSOR_UP_BY_ONE        2
#define ANSI_ESCAPE_CURSOR_DOWN_BY_ONE      3
#define ANSI_ESCAPE_CURSOR_RIGHT_BY_ONE     4
#define ANSI_ESCAPE_CURSOR_LEFT_BY_ONE      5
#define ANSI_ESCAPE_CLEAR_ENTIRE_SCREEN     6



/**
 * Tries to match a given string to an escape sequence.
 *
 * @param esc_seq String containing (partial) escape sequence.
 * @return Index into escape sequence table of matched escape sequence
 *         or negative number if not found.
 */
int match_escape_sequence(char *esc_seq);



/**
 * @typedef cursor_t
 *
 * Structure that represents the terminal cursor.
 */
typedef struct
{
    /**
     * The x coordinate of the cursor.
     */
    int x;

    /**
     * The y coordinate of the cursor.
     */
    int y;
} cursor_t;



/**
 * Sets the cursor to the given x coordinate.
 *
 * @param x_coordinate x coordinate to set the cursor to.
 * @return 0 if okay, negative value on error.
 */
int set_cursor_x(int x_coordinate);



/**
 * Sets the cursor to the given y coordinate.
 *
 * @param y_coordinate y coordinate to set the cursor to.
 * @return 0 if okay, negative value on error.
 */
int set_cursor_y(int y_coordinate);



/**
 * Gets the x coordinate of the cursor.
 *
 * @return x coordinate of the cursor.
 */
int get_cursor_x();



/**
 * Gets the y coordinate of the cursor.
 *
 * @return y coordinate of the cursor.
 */
int get_cursor_y();



/**
 * Sets the cursor to the given position.
 *
 * @param x_coordinate x coordinate to set the cursor to.
 * @param y_coordinate y coordinate to set the cursor to.
 * @return 0 if okay, negative value on error.
 */
int set_cursor(int x_coordinate, int y_coordinate);


/**
 * Moves the cursor to the left (i.e.
 * subtracts 1 from the x coordinate).
 *
 * @return 0 if okay, negative value on error.
 */
int move_cursor_left_one();



/**
 * Moves the cursor to the right (i.e.
 * add 1 to the x coordinate).
 *
 * @return 0 if okay, negative value on error.
 */
int move_cursor_right_one();



/**
 * Moves the cursor up (i.e.
 * subtracts 1 from the y coordinate).
 *
 * @return 0 if okay, negative value on error.
 */
int move_cursor_up_one();



/**
 * Moves the cursor down (i.e.
 * adds 1 to the y coordinate).
 *
 * @return 0 if okay, negative value on error.
 */
int move_cursor_down_one();



/**
 * Clears the rest of the current line (to
 * the right of the cursor).
 *
 * @return 0 if okay, negative value on error.
 */
int clear_rest_of_line();



/**
 * Clear the whole screen.
 *
 * @return 0 if okay, negative value on error.
 */
int clear_entire_screen();



/**
 * Writes the given char to the screen.
 *
 * @param data The ASCII character to write to the screen.
 * @return 0 if okay, negative value on error.
 */
int write_to_terminal(char data);



/**
 * Sends a byte to the terminal.
 *
 * @param byte_to_send Byte to be sent to the terminal.
 * @return 0 if okay, negative value on error.
 */
int terminal_send_byte(uint8_t byte_to_send);


#endif