#include "nu32dip.h" // constants, functions for startup and UART
#include "i2c_master_noint.h"
#include "mpu6050.h"
#include <stdio.h>

void blink(int, int); // blink the LEDs function

int main(void) {
    NU32DIP_Startup(); // cache on, interrupts on, LED/button init, UART init
    init_mpu6050();
	
	// char array for the raw data
    uint8_t raw_data[IMU_ARRAY_LEN];
    char message[256];
            
	// floats to store the data
    float ax, ay, az;
    float gx, gy, gz;
    float temp;
	
	if (!whoami()) {
        NU32DIP_WriteUART1("Wrong chip!");
        
        // if whoami is not 0x68, stuck in loop with LEDs on
        while(1);
    }

	// wait to print until you get a newline
    char m_in[100];
    NU32DIP_ReadUART1(m_in,100);

    while (1) {
		// use core timer for exactly 100Hz loop
        _CP0_SET_COUNT(0);
        blink(1, 5);

        // read IMU
        burst_read_mpu6050(raw_data);
        
		// convert data
        ax = conv_xXL(raw_data);
        ay = conv_yXL(raw_data);
        az = conv_zXL(raw_data);
        
        gx = conv_xG(raw_data);
        gy = conv_xG(raw_data);
        gz = conv_xG(raw_data);
        
        temp = conv_temp(raw_data);

        // 1) PRINT DATA
        /*
        sprintf(message, "ACCEL: %.2f %.2f %.2f\r\n", ax, ay, az);
        NU32DIP_WriteUART1(message);
        sprintf(message, "GYRO: %.2f %.2f %.2f\r\n", gx, gy, gz);
        NU32DIP_WriteUART1(message);
        sprintf(message, "TEMP: %.2f C\r\n", temp);
        NU32DIP_WriteUART1(message);
        NU32DIP_WriteUART1("===============================\r\n");
        */
        
        // 2) SEND TO PLOT
        sprintf(message, "%.2f\r\n", ax);
        NU32DIP_WriteUART1(message);
        
        while (_CP0_GET_COUNT() < 48000000 / 2 / 100) {
        }
    }
}

// blink the LEDs
void blink(int iterations, int time_ms) {
    int i;
    unsigned int t;
    for (i = 0; i < iterations; i++) {
        NU32DIP_GREEN = 0; // on
        NU32DIP_YELLOW = 1; // off
        t = _CP0_GET_COUNT(); // should really check for overflow here
        // the core timer ticks at half the SYSCLK, so 24000000 times per second
        // so each millisecond is 24000 ticks
        // wait half in each delay
        while (_CP0_GET_COUNT() < t + 12000 * time_ms) {
        }

        NU32DIP_GREEN = 1; // off
        NU32DIP_YELLOW = 0; // on
        t = _CP0_GET_COUNT(); // should really check for overflow here
        while (_CP0_GET_COUNT() < t + 12000 * time_ms) {
        }
    }
}

