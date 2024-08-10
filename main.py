import machine
from machine import I2C, Pin

import uasyncio

from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd

import keypad
from keypad import get_input

lcd_i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
LCD_I2C_ADDR = lcd_i2c.scan()[0]
lcd = I2cLcd(lcd_i2c, LCD_I2C_ADDR, 2, 16)

lcd.putstr("Hello world!")

print(get_input())