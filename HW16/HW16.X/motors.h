#ifndef MOTORS_H
#define MOTORS_H

#include "nu32dip.h"

#define LEFT_MOTOR 0
#define RIGHT_MOTOR 1

#define FORWARD 0
#define BACKWARD 1

#define PHASE_MOTOR_LEFT LATBbits.LATB0
#define PHASE_MOTOR_RIGHT LATBbits.LATB1

void setup_motors();
void set_motor_speed(int motor, int direction, float speed);

#endif // MOTORS_H