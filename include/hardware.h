#ifndef HARDWARE_H
#define HARDWARE_H

/**
 * @file hardware.h
 *
 * This file is essentially a high-level Hardware Abstraction
 * Layer (HAL) for the hardware-independent parts of the OS.
 * This will include functions and definitions that are common
 * to all hardware and are necessary for even arch-independent
 * code to know about, or that the user might want to know.
 */


int get_system_clock_frequency();
int get_peripheral_bus_frequency();
int get_usb_clock_frequency();


#endif