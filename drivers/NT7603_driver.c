
#include "NT7603_Driver.h"



void NT7603_clear_display()
{
    // set up operation by setting R/W pin to 0 and RS pin to 0
    NT7603_SET_WRITE_MODE();
    NT7603_REGISTER_SELECT_WRITE(0);
    
    // display clear instruction requires no arguments
    NT7603_DATA_BUS_REGISTER_WRITE(NT7603_DISPLAY_CLEAR_INSTRUCTION);
    
    // pulse enable pin and wait for long enough for operation to
    // complete. May change this from empty for loop to something
    // else in the future
    NT7603_ENABLE();
    for(int i = 0; i < 50000; i++);
    NT7603_DISABLE();
}



void NT7603_cursor_home()
{
    // set up operation by setting R/W and RS pins to 0
    NT7603_REGISTER_SELECT_WRITE(0);
    NT7603_SET_WRITE_MODE();
    
    // write instruction to instruction reg
    NT7603_DATA_BUS_REGISTER_WRITE(NT7603_CURSOR_HOME_INSTRUCTION);
    
    // pulse enable and wait
    NT7603_ENABLE();
    for(int i = 0; i < 50000; i++);
    NT7603_DISABLE();
}


void NT7603_set_entry_mode(bool increment, bool display_shift)
{
    uint8_t instruction;
    
    // set up operation by setting R/W and RS pins to 0
    NT7603_REGISTER_SELECT_WRITE(0);
    NT7603_SET_WRITE_MODE();
    
    // OR bitmask to insert argument fields into instruction
    instruction = NT7603_ENTRY_MODE_SET_INSTRUCTION | ((increment & 0x1) << 1) | (display_shift & 0x1);
    NT7603_DATA_BUS_REGISTER_WRITE(instruction);
    
    // pulse enable and wait
    NT7603_ENABLE();
    for(int i = 0; i < 5000; i++);
    NT7603_DISABLE();
}


void NT7603_turn_display_on(bool display_on, bool cursor_display_on, bool cursor_blink_on)
{
    uint8_t instruction;
    
    // set up operation by setting R/W and RS pins to 0
    NT7603_REGISTER_SELECT_WRITE(0);
    NT7603_SET_WRITE_MODE();
    
    // OR bitmask inserts args into instruction
    instruction = NT7603_DISPLAY_ON_INSTRUCTION         | 
                    ((display_on & 0x1) << 2)           |
                    ((cursor_display_on & 0x1) << 1)    |
                    (cursor_blink_on & 0x1);
    
    NT7603_DATA_BUS_REGISTER_WRITE(instruction);
    
    // pulse enable and wait
    NT7603_ENABLE();
    for(int i = 0; i < 5000; i++);
    NT7603_DISABLE();
}


void NT7603_shift_display(bool shift_right)
{
    uint8_t instruction;
    
    // set up operation by setting R/W and RS pins to 0
    NT7603_REGISTER_SELECT_WRITE(0);
    NT7603_SET_WRITE_MODE();
    
    instruction = NT7603_DISPLAY_SHIFT_INSTRUCTION | (1 << 3) | ((shift_right & 0x1) << 2);
    NT7603_DATA_BUS_REGISTER_WRITE(instruction);
    
    // pulse enable and wait
    NT7603_ENABLE();
    for(int i = 0; i < 5000; i++);
    NT7603_DISABLE();
}


void NT7603_move_cursor(bool move_right)
{
    uint8_t instruction;
    
    // set up operation by setting R/W and RS pins to 0
    NT7603_REGISTER_SELECT_WRITE(0);
    NT7603_SET_WRITE_MODE();
    
    // move_cursor and shift_display share same opcode
    instruction = NT7603_DISPLAY_SHIFT_INSTRUCTION | ((move_right & 0x1) << 2);
    NT7603_DATA_BUS_REGISTER_WRITE(instruction);
    
    // pulse enable and wait
    NT7603_ENABLE();
    for(int i = 0; i < 5000; i++);
    NT7603_DISABLE();
}


void NT7603_function_set(bool is_8_bit, bool dual_line, uint8_t display_size)
{
    uint8_t instruction;
    
    // set up operation by setting R/W and RS pins to 0
    NT7603_REGISTER_SELECT_WRITE(0);
    NT7603_SET_WRITE_MODE();
    
    instruction = NT7603_FUNCTION_SET_INSTRUCTION   |
                    ((is_8_bit & 0x1) << 4)         |
                    ((dual_line & 0x1) << 3)        |
                    ((display_size & 0x1) << 2);
    
    
    NT7603_DATA_BUS_REGISTER_WRITE(instruction);
    
    // pulse enable and wait
    NT7603_ENABLE();
    for(int i = 0; i < 5000; i++);
    NT7603_DISABLE();
}


void NT7603_set_CG_RAM_address(uint8_t address)
{
    uint8_t instruction;
    
    // set up operation by setting R/W and RS pins to 0
    NT7603_REGISTER_SELECT_WRITE(0);
    NT7603_SET_WRITE_MODE();
    
    instruction = NT7603_CG_RAM_ADDRESS_SET_INSTRUCTION | (address & 0x3f);
    NT7603_DATA_BUS_REGISTER_WRITE(instruction);
    
    // pulse enable and wait
    NT7603_ENABLE();
    for(int i = 0; i < 5000; i++);
    NT7603_DISABLE();
}


void NT7603_set_DD_RAM_address(uint8_t address)
{
    uint8_t instruction;
    
    // set up operation by setting R/W and RS pins to 0
    NT7603_REGISTER_SELECT_WRITE(0);
    NT7603_SET_WRITE_MODE();
    
    instruction = NT7603_DD_RAM_ADDRESS_SET_INSTRUCTION | (address & 0x7f);
    NT7603_DATA_BUS_REGISTER_WRITE(instruction);
    
    // pulse enable and wait
    NT7603_ENABLE();
    for(int i = 0; i < 5000; i++);
    NT7603_DISABLE();
}


void NT7603_read_busy_flag_and_address_counter(uint8_t *busy_flag, uint8_t *address_counter)
{
    uint8_t data;
    
    NT7603_REGISTER_SELECT_WRITE(0);
    NT7603_SET_READ_MODE();
    
    // pulse enable and wait
    NT7603_ENABLE();
    for(int i = 0; i < 5000; i++);
    NT7603_DISABLE();
    
    NT7603_DATA_BUS_REGISTER_READ(data);
    
    *address_counter = (data & 0x7f);
    *busy_flag = ((data >> 7) & 0x1);
}


void NT7603_write_data(uint8_t data)
{
    NT7603_REGISTER_SELECT_WRITE(1);
    NT7603_SET_WRITE_MODE();
    NT7603_DATA_BUS_REGISTER_WRITE(data);
    
    // pulse enable and wait
    NT7603_ENABLE();
    for(int i = 0; i < 500; i++);
    NT7603_DISABLE();
}


uint8_t NT7603_read_data()
{
    uint8_t retval;
    
    NT7603_REGISTER_SELECT_WRITE(1);
    NT7603_SET_READ_MODE();
    
    // pulse enable and wait
    NT7603_ENABLE();
    for(int i = 0; i < 5000; i++);
    NT7603_DISABLE();
    
    NT7603_DATA_BUS_REGISTER_READ(retval);
    
    return retval;
}


void NT7603_write_string(char *string)
{
    for(int i = 0; string[i] != 0; i++)
    {
        NT7603_write_data(string[i]);
    }
}


