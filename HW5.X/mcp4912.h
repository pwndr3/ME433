#include "nu32dip.h"
#include "spi.h"
#ifndef DEF_MCP4912
#define DEF_MCP4912

// Functions
void set_voltage_A(unsigned short val);
void set_voltage_B(unsigned short val);

#define CS_PIN LATBbits.LATB2

#endif // DEF_MCP4912