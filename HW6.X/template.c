#include "nu32dip.h" // constants, functions for startup and UART
#include "mcp23008.h"
#include <math.h>

void wait(float waitMs);

int main(void) {
  NU32DIP_Startup(); // cache on, interrupts on, LED/button init, UART init
  i2c_master_setup();
  
  // Init chip
  mcp23008_init(0x7F);

  // State machine to limit I2C communication
  char buttonVal = 0, flagChange = 0;
  
  while (1) {
    // Heartbeat - flash yellow
    NU32DIP_YELLOW = ~NU32DIP_YELLOW;
    
    // Get pins, turn on blue light if button pressed
    unsigned char pins = mcp23008_get_pins();
    if (pins & 0x01 && buttonVal == 0) {
        buttonVal = 1;
        flagChange = 1;
    } else if (!(pins & 0x01) && buttonVal == 1) {
        buttonVal = 0;
        flagChange = 1;
    }
        
    if (flagChange) {
        flagChange = 0;
        
        if (buttonVal)
            mcp23008_set_pins(0x00); // Turn on
        else 
            mcp23008_set_pins(0x80); // Turn off
    }
    
    wait(1000.0f/5);
  }
}
	
void wait(float waitMs) {
    unsigned long t = _CP0_GET_COUNT(); 
    while(_CP0_GET_COUNT() < t + 24000*waitMs){}
}
