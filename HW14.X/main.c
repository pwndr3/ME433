#include "nu32dip.h" // constants, functions for startup and UART
#include <math.h>

#define LOOP_FREQ (0.25)

#define PWM_MIN 1470 // 0 deg
#define PWM_MAX 7800 // 195 deg

#define MAX(A, B) ((A > B) ? A : B)
#define MIN(A, B) ((A > B) ? B : A)

int deg_to_pwm(int deg) {
    return (PWM_MAX - PWM_MIN) * MAX(0, MIN(195, deg)) / 195 + PWM_MIN;
}

int main(void) {
    NU32DIP_Startup(); // cache on, interrupts on, LED/button init, UART init
    
    // Set RC servo PWM
    RPB7Rbits.RPB7R = 0b0101;
    TRISBbits.TRISB7 = 1;
    
    T2CONbits.TCKPS = 0b100; // Timer2 prescaler N=16 (1:16)
    PR2 = 59999;             // period = (PR2+1) * N * (1/48000000) = 20 ms
    TMR2 = 0;                // initial TMR2 count is 0
    OC1CONbits.OCM = 0b110;  // PWM mode without fault pin; other OC1CON bits are defaults
    OC1CONbits.OCTSEL = 0;   // Use timer2
    OC1RS = 4500;            // duty cycle = OC1RS/(PR2+1) = 25%
    OC1R = 4500;             // initialize before turning OC1 on; afterward it is read-only
    T2CONbits.ON = 1;        // turn on Timer2
    OC1CONbits.ON = 1;       // turn on OC1
    
    int flag = 0;
    while (1) {
        _CP0_SET_COUNT(0);
        
        if (flag = ~flag)
            OC1RS = deg_to_pwm(45);
        else
            OC1RS = deg_to_pwm(135);
        
        // Wait before updating
        while (_CP0_GET_COUNT() < 48000000 / 2 / LOOP_FREQ);
    }
}

