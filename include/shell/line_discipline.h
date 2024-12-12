#ifndef LINE_DISCIPLINE_H
#define LINE_DISCIPLINE_H


#include <stdint.h>

#include "scrollback_buffer.h"


#define ESCAPE_SEQUENCE_BUFFER_SIZE 8
#define MAX_PROMPT_SIZE 16


/**
 * ASCII control code macro definitions.
 */
#define ASCII_DEL   127
#define ASCII_NUL   0
#define ASCII_SOH   1
#define ASCII_STX   2
#define ASCII_ETX   3
#define ASCII_EOT   4
#define ASCII_ENQ   5
#define ASCII_ACK   6
#define ASCII_BEL   7
#define ASCII_BS    8
#define ASCII_TAB   9
#define ASCII_LF    10
#define ASCII_VT    11
#define ASCII_FF    12
#define ASCII_CR    13
#define ASCII_SO    14
#define ASCII_SI    15
#define ASCII_DLE   16
#define ASCII_DC1   17
#define ASCII_DC2   18
#define ASCII_DC3   19
#define ASCII_DC4   20
#define ASCII_NAK   21
#define ASCII_SYN   22
#define ASCII_ETB   23
#define ASCII_CAN   24
#define ASCII_EM    25
#define ASCII_SUB   26
#define ASCII_ESC   27
#define ASCII_FS    28
#define ASCII_GS    29
#define ASCII_RS    30
#define ASCII_US    31





/***************************************
 * Escape sequence buffering data type *
 ***************************************/


/**
 * @typedef escape_sequence_buffer_t
 *
 * Struct for buffering the partially received
 * ANSI escape sequence. This is added to once
 * the ESC character is received and each time
 * a character is received afterward until it
 * matches some stored escape sequence.
 */
typedef struct
{
	char buffer[ESCAPE_SEQUENCE_BUFFER_SIZE];
    int current_index;
	
} escape_sequence_buffer_t;



/**
 * Initializes the given escape sequence buffer.
 *
 * @param buf Buffer to initialize.
 * @return 0 if okay, negative value on error.
 */
int escape_sequence_buffer_init(escape_sequence_buffer_t *buf);



/**
 * Inserts the received data into the escape sequence buffer.
 *
 * @param buf Buffer to insert into.
 * @param data Received data to insert.
 * @return 0 if okay, negative value on error.
 */
int escape_sequence_buffer_insert(escape_sequence_buffer_t *buf, char data);



/**
 * Clears all received data from the buffer.
 *
 * @param buf Buffer to clear.
 * @return 0 if okay, negative value on error.
 */
int escape_sequence_buffer_clear(escape_sequence_buffer_t *buf);









/**
 * @typedef line_discipline_state_t
 *
 * Stores the current state of the line
 * discipline. Can either be in normal
 * operation or processing an ANSI escape sequence.
 */
typedef enum
{
    LINE_DISCIPLINE_NORMAL_OPERATION = 0,
    LINE_DISCIPLINE_PROCESS_ANSI_ESCAPE = 1

} line_discipline_state_t;



/**
 * @typedef line_discipline_t
 *
 * Control block for the line discipline.
 */
typedef struct 
{
	/**
	 * Stores the current state of the line discipline
	 */
	line_discipline_state_t current_state;

	/**
	 * Stores the currently-edited line.
	 */
	current_line_t current_line;

	/**
	 * Stores the command history.
	 */
	scrollback_buffer_t scrollback_buffer;

	/**
	 * Holds the current ANSI escape sequence
	 * while all character are being received.
	 */
	escape_sequence_buffer_t escape_buffer;

	/**
	 * Stores the prompt that needs to be printed.
	 */
	char prompt[MAX_PROMPT_SIZE];


	/**
	 * Buffer for holding the current command
	 * for the shell associated with this
	 * line discipline.
	 */
	char *shell_buffer;


	int (*invoke_shell)();

} line_discipline_t;



/**
 * Sets the prompt that is printed on every line.
 *
 * @param discipline Line discipline whose prompt to set.
 * @param new_prompt Prompt to set to.
 * @return 0 if okay, negative value on error.
 */
int line_discipline_set_prompt(line_discipline_t *discipline, char *new_prompt);



/**
 * Registers the buffer used by the shell to store the current command. The current
 * line is copied to this buffer when the enter key is pressed, see @ref 
 * line_discipline_copy_current_line_to_shell_buffer.
 *
 * @param discipline Line discipline whose prompt to set.
 * @param buffer The shell buffer. Passed in by shell code or init code. Must be
 * 				 at least MAX_LINE_SIZE in length to work properly.
 * @return 0 if okay, negative value on error.
 */
int line_discipline_register_shell_buffer(line_discipline_t *discipline, char *buffer);



/**
 * Copies the currently-edited line into the shell buffer. This should be called before
 * invoking the shell callback function.
 *
 * @param discipline The line discipline.
 * @return 0 if okay, negative value on error.
 */
int line_discipline_copy_current_line_to_shell_buffer(line_discipline_t *discipline);





/**
 * Processes the reception of the ANSI escape sequence
 * corresponding to the UP arrow.
 *
 * @return 0 if okay, negative value on error.
 */
int handle_scroll_up(void);



/**
 * Processes the reception of the ANSI escape sequence
 * corresponding to the DOWN arrow.
 *
 * @return 0 if okay, negative value on error.
 */
int handle_scroll_down(void);



/**
 * Processes the reception of the ANSI escape sequence
 * corresponding to the LEFT arrow.
 *
 * @return 0 if okay, negative value on error.
 */
int handle_scroll_left(void);



/**
 * Processes the reception of the ANSI escape sequence
 * corresponding to the RIGHT arrow.
 *
 * @return 0 if okay, negative value on error.
 */
int handle_scroll_right(void);



/**
 * Processes reception of the delete key (ASCII
 * backspace character).
 *
 * @return 0 if okay, negative value on error.
 */
int handle_delete(void);



/**
 * Processes reception of the return key (ASCII
 * \n or \r).
 *
 * @return 0 if okay, negative value on error.
 */
int handle_return(void);






/**
 * Handles the processing received characters
 * when the line discipline is in the middle
 * of processing and escape sequence. This function
 * is only called when the current state of the
 * line discipline is @ref LINE_DISCIPLINE_PROCESS_ANSI_ESCAPE.
 *
 * @param data Data received from terminal emulator.
 * @return 0 if okay, negative value on error.
 */
int process_ANSI_escape_sequence(char data);



/**
 * Processes the reception of an ASCII control
 * character (0-31 and 127).
 *
 * @param data Data received from terminal emulator.
 * @return 0 if okay, negative value on error.
 */
int process_ASCII_control_char(char data);



/**
 * Processes the reception of a printable ASCII
 * character (such as a-z, A-Z, 0-9, etc.). These
 * are the ASCII value 32-126.
 *
 * @param data Data received from terminal emulator.
 * @return 0 if okay, negative value on error.
 */
int process_printable_ASCII_char(char data);



/**
 * Processes the reception of an ASCII character.
 * Will call either @ref process_ASCII_control_char
 * or @ref process_printable_ASCII_char.
 *
 * @param data Data received from terminal emulator.
 * @return 0 if okay, negative value on error.
 */
int process_ASCII_char(char data);



/**
 * Callback function for serial receive. This is
 * registered with the serial driver (typically a
 * UART) as a receive callback. See @ref uart_receive_callback_t
 * for more info.
 */
int process_next_byte(void *buffer, uint32_t size);



#endif

