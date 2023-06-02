#include "motors.h"

#define PR2_MAX 2400

void setup_motors() {
    // Timer init
    T2CONbits.TCKPS = 0b0;   // Timer2 prescaler N=1 (1:1)
    PR2 = PR2_MAX - 1;       // period = (PR2+1) * N * (1/48000000) = 1/20 kHz
    TMR2 = 0;                // initial TMR2 count is 0
    
    // Motor 1
    RPA0Rbits.RPA0R = 0b0101;
    TRISAbits.TRISA0 = 0;
    
    OC1CONbits.OCM = 0b110;  // PWM mode without fault pin; other OC1CON bits are defaults
    OC1CONbits.OCTSEL = 0;   // Use timer2
    OC1RS = 0;               // duty cycle = OC1RS/(PR2+1) = 25%
    OC1R = 0;                // initialize before turning OC1 on; afterward it is read-only
    
    TRISBbits.TRISB0 = 0;
    PHASE_MOTOR_LEFT = 1;
    
    // Motor 2
    RPA1Rbits.RPA1R = 0b0101;
    TRISAbits.TRISA1 = 0;
    
    OC2CONbits.OCM = 0b110;  // PWM mode without fault pin; other OC1CON bits are defaults
    OC2CONbits.OCTSEL = 0;   // Use timer2
    OC2RS = 0;               // duty cycle = OC1RS/(PR2+1) = 25%
    OC2R = 0;                // initialize before turning OC1 on; afterward it is read-only
    
    TRISBbits.TRISB1 = 0;
    PHASE_MOTOR_RIGHT = 1;
    
    // Turn on
    T2CONbits.ON = 1;        // turn on Timer2
    OC1CONbits.ON = 1;       // turn on OC1
    OC2CONbits.ON = 1;       // turn on OC2
}

void set_motor_speed(int motor, int direction, float speed) {
    /* 
     * motor: LEFT_MOTOR/RIGHT_MOTOR
     * direction: FORWARD/BACKWARD
     * speed: float between 0 and 1
     */
    if (direction != FORWARD && direction != BACKWARD)
        return; // Invalid direction
    if (speed < 0.0f || speed > 1.0f)
        return; // Invalid speed
    
    switch(motor) {
        case LEFT_MOTOR:
            PHASE_MOTOR_LEFT = direction;
            OC1RS = (int)(PR2_MAX * speed);
            break;
        case RIGHT_MOTOR:
            PHASE_MOTOR_RIGHT = direction;
            OC2RS = (int)(PR2_MAX * speed);
            break;
    }
}