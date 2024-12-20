#ifndef NT7603_DRIVER_H
#define NT7603_DRIVER_H


/**
 * @file NT7603_Driver.h
 *
 * Driver for the Novatek NT7603 LCD Display
 * driver. For more information on definitions
 * in this file see the NT7603 datasheet.
 */


#include <stdbool.h>
#include <stdint.h>

#include <proc/PIC32MX/p32mx795f512l.h>


// opcodes for NT7603 instructions. These are used in API
// functions
#define NT7603_DISPLAY_CLEAR_INSTRUCTION            0x01
#define NT7603_CURSOR_HOME_INSTRUCTION              0x02
#define NT7603_ENTRY_MODE_SET_INSTRUCTION           0x04
#define NT7603_DISPLAY_ON_INSTRUCTION               0x08
#define NT7603_DISPLAY_SHIFT_INSTRUCTION            0x10
#define NT7603_FUNCTION_SET_INSTRUCTION             0x20
#define NT7603_CG_RAM_ADDRESS_SET_INSTRUCTION       0x40
#define NT7603_DD_RAM_ADDRESS_SET_INSTRUCTION       0x80




/**********************************
 * Macros for setting NT7603 Pins *
 **********************************/


/**
 * Data bus register (DB0-DB7) maps to RE0-RE7 on the
 * PIC32. To set REx for output, write a 0 to the corresponding
 * bit in TRISE (i.e. TRISEx). To set REx for input, write a
 * 1 to TRISEx.
 */
#define NT7603_DATA_BUS_REGISTER_WRITE(_data)       \
            TRISE = 0xFF00;                         \
            LATE = _data


#define NT7603_DATA_BUS_REGISTER_READ(_value)       \
            TRISE = 0x00FF;                         \
            _value = PORTE



/**
 * Register select input on NT7603 maps to RB15 on the PIC32.
 */
#define NT7603_REGISTER_SELECT_WRITE(_bit)      \
            TRISBbits.TRISB15 = 0;              \
            LATBbits.LATB15 = _bit


/**
 * Enable input on NT7603 maps to RD4 on PIC32
 */
#define NT7603_ENABLE()         \
        TRISDbits.TRISD4 = 0;   \
        LATDbits.LATD4 = 1


#define NT7603_DISABLE()        \
        TRISDbits.TRISD4 = 0;   \
        LATDbits.LATD4 = 0


/**
 * Sets the NT7603 into read mode by writing
 * a 1 to the R/W input, which maps to RD5 on
 * the PIC32.
 */
#define NT7603_SET_READ_MODE()          \
        TRISDbits.TRISD5 = 0;           \
        LATDbits.LATD5 = 1


/**
 * Sets the NT7603 into write mode by writing
 * a 0 to the R/W input, which maps to RD5 on
 * the PIC32.
 */
#define NT7603_SET_WRITE_MODE()         \
        TRISDbits.TRISD5 = 0;           \
        LATDbits.LATD5 = 0




/******************************
 * Functions implementing the *
 * instruction set for NT7603 *
 ******************************/


/**
 * Clear the LCD display.
 */
void NT7603_clear_display();


/**
 * Reset the cursor to the home position.
 * This is the top left corner of the LCD
 * display.
 */
void NT7603_cursor_home();


/**
 * Sets the entry mode of the display. This determines
 * the behavior of the display after each read/write.
 *
 * @param increment Bool. If true, increment (shift right by on position)
 *                  the cursor after each read/write to the display.
 * @param display_shift Bool. If true sets display shift mode.
 */
void NT7603_set_entry_mode(bool increment, bool display_shift);


/**
 * Turns the LCD display on and configures the cursor functionality.
 *
 * @param display_on Bool. Whether to turn the display on.
 * @param cursor_display_on Bool. Whether to the cursor is visible
 *                          on the LCD display.
 * @param cursor_blink_on Bool. Whether the cursor is blinking.
 */
void NT7603_turn_display_on(bool display_on, bool cursor_display_on, bool cursor_blink_on);


/**
 * Shifts the display. What this actually mean I have no idea.
 *
 * @param shift_right Bool. If true, shift display right.
 */
void NT7603_shift_display(bool shift_right);


/**
 * Moves the cursor to one place either right or left.
 *
 * @param move_right Bool. If true, move cursor right.
 */
void NT7603_move_cursor(bool move_right);


/**
 * Sets the functionality of the NT7603.
 *
 * @param is_8_bit If true, the data bus register is 8-bits.
 * @param dual_line If true, sets the display in dual-line mode.
 * @param display_size If 1, sets char size to be 5x10 dots. If 0,
 *        sets it to be 5x8.
 */
void NT7603_function_set(bool is_8_bit, bool dual_line, uint8_t display_size);


/**
 * Sets the address counter to a character generator
 * RAM address.
 *
 * @param address The address in the character generator RAM.
 */
void NT7603_set_CG_RAM_address(uint8_t address);


/**
 * Sets the address counter to a display data RAM address.
 *
 * @param address Address to be set.
 */
void NT7603_set_DD_RAM_address(uint8_t address);


/**
 * Reads the busy flag and the address counter.
 *
 * @param[out] busy_flag Function stores bisy flag in LSB of this param.
 * @param[out] address_counter Function stores address counter in this param.
 */
void NT7603_read_busy_flag_and_address_counter(uint8_t *busy_flag, uint8_t *address_counter);


/**
 * Writes the data to the current address counter.
 *
 * @param data Data to be written.
 */
void NT7603_write_data(uint8_t data);


/**
 * Reads data from the current address counter.
 *
 * @return Data read from the NT7603.
 */
uint8_t NT7603_read_data();



/*********************************
 * API functions. These exist
 * at a higher level than the
 * instruction set implementation
 * functions
 *********************************/



void NT7603_initialize();


void NT7603_write_string(char *string);


#endif