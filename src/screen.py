import contextlib

import board
from adafruit_character_lcd.character_lcd_rgb_i2c import Character_LCD_RGB_I2C

LCD_COLUMNS = 16
LCD_ROWS = 2

@contextlib.contextmanager
def open_screen():
    i2c = board.I2C()
    screen = Character_LCD_RGB_I2C(i2c, LCD_COLUMNS, LCD_ROWS)
    screen.display = True
    screen.color = [100,100,100]
    try:
        yield screen
    finally:
        screen.clear()
        screen.display = False
        screen.color = [0,0,0]
