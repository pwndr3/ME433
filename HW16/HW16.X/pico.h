#ifndef PICO_H
#define PICO_H

#include "nu32dip.h"

void setup_pico();
void read_pico(char * message, int maxLength);
void write_pico(const char * string);

#endif // PICO_H
