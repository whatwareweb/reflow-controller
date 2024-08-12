import machine
from machine import I2C, Pin

import uasyncio

from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd

import keypad

from menu import Menu

lcd_i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
LCD_I2C_ADDR = lcd_i2c.scan()[0]
lcd = I2cLcd(lcd_i2c, LCD_I2C_ADDR, 2, 16)

async def set_char():
    while True:
        char = await keypad.get_input()


loop = uasyncio.get_event_loop()

loop.create_task(set_char())

loop.run_forever()