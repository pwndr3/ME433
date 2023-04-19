#include "mcp23008.h"

void mcp23008_init(unsigned char io) {
    // Assign input/output pins
    // 0: output, 1: input
    
    // Start bit
    i2c_master_start();
    // Device opcode
    i2c_master_send(MCP23008_ADDRESS << 1); // Write to register
    // Register address
    i2c_master_send(MCP23008_IODIR);
    // IO config
    i2c_master_send(io);
    // Stop
    i2c_master_stop();
    
    // Set byte operation
    // Start bit
    i2c_master_start();
    // Device opcode
    i2c_master_send(MCP23008_ADDRESS << 1); // Write to register
    // Register address
    i2c_master_send(MCP23008_IOCON);
    // IO config
    i2c_master_send(0b110110); // SEQOP disabled
    // Stop
    i2c_master_stop();
    
    // Set to poll from GPIO register --- very specific to this assignment
    // Start bit
    i2c_master_start();
    // Device opcode
    i2c_master_send(MCP23008_ADDRESS << 1); // Write to register
    // Register address
    i2c_master_send(MCP23008_IODIR);
    // Stop
    i2c_master_stop();
}

void mcp23008_set_pins(unsigned char pins) {
    // Start bit
    i2c_master_start();
    // Device opcode
    i2c_master_send(MCP23008_ADDRESS << 1); // Write to register
    // Register address
    i2c_master_send(MCP23008_GPIO);
    // IO config
    i2c_master_send(pins);
    // Stop
    i2c_master_stop();
}

unsigned char mcp23008_get_pins() {
    // Start bit
    i2c_master_start();
    // Device opcode
    i2c_master_send(MCP23008_ADDRESS << 1 | 1); // Read from register
    // IO config
    unsigned char pins = i2c_master_recv();
    // Stop
    i2c_master_ack(1); // NACK
    i2c_master_stop();
    
    return pins;
}