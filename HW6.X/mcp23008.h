#ifndef DEF_MCP23008
#define DEF_MCP23008

#include "nu32dip.h"
#include "i2c_master_noint.h"

#define MCP23008_ADDRESS 0b0100000

#define MCP23008_IODIR 0x00
#define MCP23008_IPOL 0x01
#define MCP23008_GPINTEN 0x02
#define MCP23008_DEFVAL 0x03
#define MCP23008_INTCON 0x04
#define MCP23008_IOCON 0x05
#define MCP23008_GPPU 0x06
#define MCP23008_INTF 0x07
#define MCP23008_INTCAP 0x08
#define MCP23008_GPIO 0x09
#define MCP23008_OLAT 0x0A

void mcp23008_init(unsigned char io);
void mcp23008_set_pins(unsigned char pins);
unsigned char mcp23008_get_pins();

#endif // DEF_MCP23008