
#include <proc/p32mx170f256b.h>

// initialize SPI1
void initSPI() {
    // B14 is SCK1 (default)
    
    // B11 is SDI1, B1 is SDO1
    RPB1Rbits.RPB1R = 0b0011;
    SDI1Rbits.SDI1R = 0b0011;
    
    // B2 is CS
    LATBbits.LATB2 = 1;
    
    // Two LEDS (B4 B5), SDO & CS (B1 B2)
    TRISBCLR = 0b110110;

    // setup SPI1
    SPI1CON = 0; // turn off the spi module and reset it
    SPI1BUF; // clear the rx buffer by reading from it
    SPI1BRG = 1; // 1000 for 24kHz, 1 for 12MHz; // baud rate to 10 MHz [SPI1BRG = (48000000/(2*desired))-1]
    SPI1STATbits.SPIROV = 0; // clear the overflow bit
    SPI1CONbits.CKE = 1; // data changes when clock goes from hi to lo (since CKP is 0)
    SPI1CONbits.MSTEN = 1; // master operation
    SPI1CONbits.MODE16 = 1;
    SPI1CONbits.ON = 1; // turn on spi 
}


// send a byte via spi and return the response
unsigned short spi_io(unsigned short o) {
  SPI1BUF = o;
  while(SPI1STATbits.SPIBUSY) { // wait to receive the byte
    ;
  }
  return SPI1BUF;
}