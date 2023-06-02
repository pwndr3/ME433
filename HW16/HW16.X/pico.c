#include "pico.h"

void setup_pico() {
    __builtin_disable_interrupts();
    
     //UART2 pins
    TRISBbits.TRISB8 = 1;
    TRISBbits.TRISB9 = 0;
    
    U2RXRbits.U2RXR = 0b0100; // Set B8 to U2RX
    RPB9Rbits.RPB9R = 0b0010; // Set B9 to U2TX

    // turn on UART2 without an interrupt
    U2MODEbits.BRGH = 0; // set baud to NU32_DESIRED_BAUD
    U2BRG = ((NU32DIP_SYS_FREQ / PICO_BAUD) / 16) - 1;

    // 8 bit, no parity bit, and 1 stop bit (8N1 setup)
    U2MODEbits.PDSEL = 0;
    U2MODEbits.STSEL = 0;

    // configure TX & RX pins as output & input pins
    U2STAbits.UTXEN = 1;
    U2STAbits.URXEN = 1;
    // configure without hardware flow control
    U2MODEbits.UEN = 0;

    // enable the uart
    U2MODEbits.ON = 1;
    
    __builtin_enable_interrupts();
}

void read_pico(char * message, int maxLength) {
    char data = 0;
    int complete = 0, num_bytes = 0;
    // loop until you get a '\r' or '\n'
    while (!complete) {
        if (U2STAbits.URXDA) { // if data is available
            data = U2RXREG; // read the data
            if ((data == '\n') || (data == '\r')) {
                complete = 1;
            } else {
                message[num_bytes] = data;
                ++num_bytes;
                // roll over if the array is too small
                if (num_bytes >= maxLength) {
                    num_bytes = 0;
                }
            }
        }
    }
    // end the string
    message[num_bytes] = '\0';
}

void write_pico(const char * string) {
    while (*string != '\0') {
        while (U2STAbits.UTXBF) {
            ; // wait until tx buffer isn't full
        }
        U2TXREG = *string;
        ++string;
    }
}