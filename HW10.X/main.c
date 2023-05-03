#include "nu32dip.h" // constants, functions for startup and UART
#include "ws2812b.h"
#include <math.h>

#define NUM_LEDS 5
#define HUE_STEP 5
#define LOOP_FREQ 30

#define SATURATION 1
#define BRIGHTNESS 1

int main(void) {
    NU32DIP_Startup(); // cache on, interrupts on, LED/button init, UART init
    ws2812b_setup();
    
    wsColor c[NUM_LEDS];
    float hue = 0.0f;
    
    while (1) {
        _CP0_SET_COUNT(0);
        
        // Build color array
        for (int i = 0; i < NUM_LEDS; i++) {
            c[i] = HSBtoRGB(fmod(hue + i * HUE_STEP, 360), SATURATION, BRIGHTNESS); 
        }
        
        hue += HUE_STEP;
        
        if (hue >= 360.0f)
            hue -= 360.0f;
        
        // Set color
        ws2812b_setColor(c, NUM_LEDS);
        
        // Wait before updating colors
        while (_CP0_GET_COUNT() < 48000000 / 2 / LOOP_FREQ);
    }
}

