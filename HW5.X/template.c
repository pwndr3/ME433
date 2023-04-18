#include "nu32dip.h" // constants, functions for startup and UART
#include "mcp4912.h"
#include <math.h>

void wait(float waitMs);

int main(void) {
  // Generate sine wave and store in array
  int numPoints = 100;
  unsigned short sineWave[numPoints]; // 2 Hz
  unsigned short triangleWave[numPoints]; // 1 Hz
  
  // Sine wave
  for (int i = 0; i < numPoints; i++)
      sineWave[i] = (unsigned short)(512*sin(2 * ((double)i/numPoints) * 2 * M_PI) + 512) % 1024;

  // Triangle wave
  int middlePoint = (int)(numPoints / 2);
  for (int i = 0; i < middlePoint; i++)
      triangleWave[i] = (unsigned short)(((double)i/middlePoint) * 1024) % 1024;
  for (int i = middlePoint; i < numPoints; i++)
      triangleWave[i] = (unsigned short)(1023 - ((double)(i - middlePoint)/(numPoints - middlePoint)) * 1024) % 1024;

  NU32DIP_Startup(); // cache on, interrupts on, LED/button init, UART init
  initSPI();
  int i = 0;

  while (1) {
    set_voltage_A(sineWave[i++]);
    set_voltage_B(triangleWave[i++]);
    
    if (i >= numPoints)
        i = 0;
    
    wait(1000.0f/numPoints);
  }
}
	
void wait(float waitMs) {
    unsigned long t = _CP0_GET_COUNT(); 
    while(_CP0_GET_COUNT() < t + 48000*waitMs){}
}
