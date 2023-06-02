#include "nu32dip.h" // constants, functions for startup and UART
#include "pico.h"
#include "motors.h"
#include <math.h>

#define LOOP_FREQ 10

// IMAGE PROCESSING ON PICO
// PID ON PIC 

int main(void) {
    NU32DIP_Startup(); // cache on, interrupts on, LED/button init, UART init
    
    setup_motors();
    setup_pico();
    
    char message[100];
    int motor, direction;
    float speed;
    while (1) {
        _CP0_SET_COUNT(0);

        //write_pico("Test\r\n");
        
        read_pico(message, 100);
        sscanf(message, "%d %d %f", &motor, &direction, &speed);
        set_motor_speed(motor, direction, speed);
        
        /*
        NU32DIP_ReadUART1(message, 99);
        NU32DIP_WriteUART1("Received\r\n");
        
        sscanf(message, "%d %d %f", &motor, &direction, &speed);
        
        set_motor_speed(motor, direction, speed);
        */
        
        // Wait before updating
        while (_CP0_GET_COUNT() < 48000000 / 2 / LOOP_FREQ);
    }
}

