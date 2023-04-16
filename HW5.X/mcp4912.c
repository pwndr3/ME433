#include "mcp4912.h"

void set_voltage(int ch, unsigned short val) {
    // ch = 0: A, ch = 1: B
    // val: [0, 1023]
    unsigned short command = 0;
    
    // Channel
    command |= (ch & 0x1) << 15;
    
    // Buffered, gain = 1, active
    command |= 0b111 << 12;
    
    // Voltage value
    command |= (val & 0x3FF) << 2;
    
    // Send 16-bit command
    CS_PIN = 0;
    spi_io(command);
    CS_PIN = 1;
}

void set_voltage_A(unsigned short val) {
    set_voltage(0, val);
}

void set_voltage_B(unsigned short val) {
    set_voltage(1, val);
}