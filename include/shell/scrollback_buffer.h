#ifndef SCROLLBACK_BUFFER_H
#define SCROLLBACK_BUFFER_H


#include <stdbool.h>



#define MAX_LINE_SIZE 64
#define SCROLLBACK_BUFFER_NUM_ENTRIES 8





/**
 * @typedef scrollback_buffer_entry_t
 *
 * Individual entry in the scrollback_buffer.
 */
typedef struct
{
	/**
	 * Actual text of the command entered.
	 */
    char line[MAX_LINE_SIZE];

    /**
     * Index of the final character of the command + 1
     */
    int end_index;

    /**
     * Whether the entry is used. When terminal is
     * initially started, the entries in the scrollback
     * buffer are not filled, so to prevent the up/down
     * arrows from cycling through empty entries, this
     * member variable is needed.
     */
    bool in_use;

} scrollback_buffer_entry_t;


/**
 * Initializes the scrollback buffer entry.
 *
 * @param entry Scrollback buffer entry.
 * @return 0 if okay. Negative value if could not initialize.
 */
int scrollback_buffer_entry_init(scrollback_buffer_entry_t *entry);



/**
 * Inserts a new character into the line at the given cursor position. The
 * new character will be placed into index @c cursor in the line and all
 * subsequent characters will be shifted right (position incremented) by one.
 *
 * @param entry Scrollback buffer entry.
 * @param cursor Position in the line at which to insert.
 * @param data New char to insert into the line.
 * @return 0 if okay. Negative value if could not insert.
 */
int scrollback_buffer_entry_insert(scrollback_buffer_entry_t *entry, int cursor, char data);



/**
 * Deletes the character in the given position in the line and shifts
 * all subsequent characters left (decrements position) by one.
 *
 * @param entry Scrollback buffer entry.
 * @param cursor Position in the line at which to delete.
 * @return 0 if okay. Negative value if could not delete.
 */
int scrollback_buffer_entry_delete(scrollback_buffer_entry_t *entry, int cursor);



/**
 * Sets the line stored in given entry to new line.
 *
 * @param entry Scrollback buffer entry.
 * @param line String representing new line to be stored.
 * @return 0 if okay. Negative value if could not set new line.
 */
int scrollback_buffer_entry_set_new_line(scrollback_buffer_entry_t *entry, char *line);



/**
 * Sets the entry in use.
 *
 * @param entry Scrollback buffer entry.
 * @return 0 if okay. Negative value if could not set in use.
 */
int scrollback_buffer_entry_set_in_use(scrollback_buffer_entry_t *entry);



/**
 * Sets the entry free.
 *
 * @param entry Scrollback buffer entry.
 * @return 0 if okay. Negative value if could not set free.
 */
int scrollback_buffer_entry_set_free(scrollback_buffer_entry_t *entry);



/**
 * Returns whether the entry is in use.
 *
 * @param entry Scrollback buffer entry. 
 * @return true if in use, false otherwise.
 */
bool scrollback_buffer_entry_is_in_use(scrollback_buffer_entry_t *entry);







/**
 * @typedef current_line_t
 *
 * Structure used for holding the current line
 * being edited on the line discipline.
 */
typedef struct
{
	/**
	 * Actual text of the command entered.
	 */
    char line[MAX_LINE_SIZE];

    /**
     * Index of the final character of the command + 1
     */
    int end_index;

    /**
     * Position in the current buffer entry at which to
     * display the terminal cursor.
     */
    int cursor;

} current_line_t;



/**
 * Sets the cursor to the given position.
 *
 * @param line Current line being edited.
 * @param cursor_position Position to set the cursor to. Must be in [0,end_index].
 * @return 0 if okay. Negative value if could not set cursor to position.
 */
int line_set_cursor(current_line_t *line, int cursor_position);



/**
 * Moves the cursor left by 1 if not at beginning of line.
 *
 * @param line Current line being edited.
 * @return 0 if okay. Negative value if could not move cursor left.
 */
int line_move_cursor_left(current_line_t *line);



/**
 * Moves the cursor right by 1 if not at end of line.
 *
 * @param line Current line being edited.
 * @return 0 if okay. Negative value if could not move cursor right.
 */
int line_move_cursor_right(current_line_t *line);



/**
 * Initialize the line.
 *
 * @param line Current line being edited.
 * @return 0 if okay. Negative value if could not init.
 */
int line_init(current_line_t *line);



/**
 * Inserts a new character into the line at the current cursor position. The
 * new character will be placed into index @c cursor in the line and all
 * subsequent characters will be shifted right (position incremented) by one.
 *
 * @param line Current line being edited.
 * @param data New char to insert into the line.
 * @return 0 if okay. Negative value if could not insert.
 */
int line_insert(current_line_t *line, char data);



/**
 * Deletes the character in the given position in the line and shifts
 * all subsequent characters left (decrements position) by one.
 *
 * @param line Current line being edited.
 * @return 0 if okay. Negative value if could not delete.
 */
int line_delete(current_line_t *line);






/**
 * @typedef scrollback_buffer_t
 *
 * The scrollback buffer. Used for command history in the
 * line discipline for the miniOS command line.
 */
typedef struct
{
	/**
	 * Array of buffer entries that stores the command history.
	 */
    scrollback_buffer_entry_t buffer[SCROLLBACK_BUFFER_NUM_ENTRIES];

    /**
     * Number of current entry being displayed. NOT THE SAME as
     * the index, which is current%SCROLLBACK_BUFFER_NUM_ENTRIES.
     * This number is incremented on reception of down arrow key
     * and decremented on reception of up arrow key. This variable
     * cannot be less than 0, greater than @c latest, or less than
     * @c latest - SCROLLBACK_BUFFER_NUM_ENTRIES.
     */
    int current;

    /**
     * Number of latest entry inserted. NOT THE SAME as
     * the index, which is latest%SCROLLBACK_BUFFER_NUM_ENTRIES.
     * Incremented when return key is pressed. NEVER decremented.
     */
    int latest;

} scrollback_buffer_t;


/**
 * Converts from the current buffer entry
 * number to the index into the table.
 */
#define CURRENT_INDEX(_buffer)      ((_buffer)->current%SCROLLBACK_BUFFER_NUM_ENTRIES)


/**
 * Converts from the latest buffer entry
 * number to its index into the table.
 */
#define LATEST_INDEX(_buffer)       ((_buffer)->latest%SCROLLBACK_BUFFER_NUM_ENTRIES)




/**
 * Clears/initializes the scrollback buffer.
 *
 * @param buffer Scrollback buffer in use by line discipline.
 * @return 0 if okay. Negative value
 */
int scrollback_buffer_clear(scrollback_buffer_t *buffer);



/**
 * Sets the @c current member to the next entry in the scrollback buffer.
 *
 * @param buffer Scrollback buffer.
 * @return 0 if okay. Negative value if could not move to next entry.
 */
int scrollback_buffer_set_current_to_next_entry(scrollback_buffer_t *buffer);



/**
 * Sets the @c current member to the previous entry in the scrollback buffer.
 *
 * @param buffer Scrollback buffer.
 * @return 0 if okay. Negative value if could not move to previous entry.
 */
int scrollback_buffer_set_current_to_previous_entry(scrollback_buffer_t *buffer);



/**
 * Sets the @c latest member to the next entry in the scrollback buffer.
 *
 * @param buffer Scrollback buffer.
 * @return 0 if okay. Negative value if could not move to next entry.
 */
int scrollback_buffer_set_latest_to_next_entry(scrollback_buffer_t *buffer);



/**
 * Moves current entry to the given entry number. Number passed must
 * be in the range [latest-SCROLLBACK_BUFFER_NUM_ENTRIES+1, latest].
 *
 * @param buffer Scrollback buffer.
 * @param entry_number Number of the entry to set current to.
 * @return 0 if okay. Negative value if ccould not move to given entry.
 */
int scrollback_buffer_set_current_entry(scrollback_buffer_t *buffer, int entry_number);



/**
 * Returns pointer to the current entry in the scrollback buffer.
 *
 * @param buffer Scrollback buffer.
 * @return Pointer to current entry. NULL if error.
 */
scrollback_buffer_entry_t *scrollback_buffer_get_current_entry(scrollback_buffer_t *buffer);



/**
 * Returns pointer to the latest entry in the scrollback buffer.
 *
 * @param buffer Scrollback buffer.
 * @return Pointer to the current entry. NULL if error.
 */
scrollback_buffer_entry_t *scrollback_buffer_get_latest_entry(scrollback_buffer_t *buffer);



/**
 * Returns pointer to the entry specified by the given entry number. Number passed must
 * be in the range [latest-SCROLLBACK_BUFFER_NUM_ENTRIES+1, latest].
 *
 * @param buffer Scrollback buffer.
 * @param entry_number Number of entry to get.
 * @return Pointer to given entry. NULL if error.
 */
scrollback_buffer_entry_t *scrollback_buffer_get_entry(scrollback_buffer_t *buffer, int entry_number);



/**
 * 
 * 
 */
//int scrollback_buffer_scroll_back(scrollback_buffer_t *buffer);



/**
 * 
 * 
 */
//int scrollback_buffer_scroll_forward(scrollback_buffer_t *buffer);



/**
 * 
 * 
 */
//int scrollback_buffer_process_enter(scrollback_buffer_t *buffer);





#endif
