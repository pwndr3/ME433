#include "nu32dip.h" // constants, functions for startup and UART
#include <math.h>

void wait(float waitMs);

int main(void) {
  // Generate sine wave and store in array
  int numPoints = 100;
  double sinewave[numPoints];
  
  for (int i = 0; i < numPoints; i++) {
      sinewave[i] = (3.3/2) * sin(((double)i/numPoints) * 2 * M_PI) + (3.3/2);
  }
  
  char message[100]; // Huge to prevent overflow, although this is not 100% bullet proof
  
  NU32DIP_Startup(); // cache on, interrupts on, LED/button init, UART init
  while (1) {
	if (!NU32DIP_USER){
		// Read out sine array
        for (int i = 0; i < numPoints; i++) {
            sprintf(message, "%f\n", sinewave[i]);
            NU32DIP_WriteUART1(message);
            
            wait(1000.0f/numPoints);
        }
	}
  }
}
	
void wait(float waitMs) {
    unsigned long t = _CP0_GET_COUNT(); 
    // the core timer ticks at half the SYSCLK, so 24000000 times per second
    // so each millisecond is 24000 ticks
    while(_CP0_GET_COUNT() < t + 24000*waitMs){}
}
