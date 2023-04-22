#include "nu32dip.h" // constants, functions for startup and UART
#include "i2c_master_noint.h"
#include "mpu6050.h"
#include "ssd1306.h"
#include "font.h"
#include <stdio.h>

void blink(int, int); // blink the LEDs function

int main(void) {
    NU32DIP_Startup(); // cache on, interrupts on, LED/button init, UART init
    init_mpu6050();
    ssd1306_setup();
	
	// char array for the raw data
    uint8_t raw_az[2];
    char message[256];
            
	// floats to store the data
    float az, fps;

    while (1) {
        _CP0_SET_COUNT(0);

        // read IMU
        raw_az[0] = read_byte_I2C1(IMU_ADDR, ACCEL_XOUT_H);
        raw_az[1] = read_byte_I2C1(IMU_ADDR, ACCEL_XOUT_L);
                
		// convert data to float
        az = (signed short)(raw_az[0] << 8 | raw_az[1])*0.000061;
        
        sprintf(message, "ACCEL Z: %+.2f g", az);
        drawMessage(0, message);
        ssd1306_update();
        
        // Get FPS
        fps = (48000000.0f / 2) / _CP0_GET_COUNT();
        sprintf(message, "FPS: %.2f", fps);
        drawMessageRight(3, message);
    }
}

