#include "font.h"
#include "ssd1306.h"

void drawChar(unsigned char x, unsigned char y, unsigned char character) {
    // Draw single character as pixel position x,y
    char char_idx = character - 0x20; // First character is SPACE 0x20
    
    unsigned char xi, yi;
    for (xi = x; xi < x + CHAR_WIDTH; xi++) {
        char col = ASCII[char_idx][xi - x];
        for (yi = y; yi < y + CHAR_HEIGHT; yi++) {
            // Draw one pixel at a time
            char color = (col & (1 << (yi - y))) != 0;
            ssd1306_drawPixel(xi, yi, color);
        }
    }
}

void drawString(unsigned char x, unsigned char y, unsigned char string[]) {
    // Draw string starting at pixel x,y
    unsigned char xi, i;
    for (xi = x, i = 0; string[i] != '\0'; xi += CHAR_WIDTH, i++) {
        drawChar(xi, y, string[i]);
    }
}

void drawMessage(unsigned char line, unsigned char message[]) {
    // Draw left-justified message on line 0 to 3
    drawString(0, line * CHAR_HEIGHT, message);
}

void drawMessageRight(unsigned char line, unsigned char message[]) {
    // Draw right-justified message on line 0 to 3 
    drawString((MAX_CHARS_PER_ROW - strlen(message)) * CHAR_WIDTH, line * CHAR_HEIGHT, message);
}