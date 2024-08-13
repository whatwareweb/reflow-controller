import machine
from machine import I2C, Pin

import uasyncio

import json

from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd

import keypad


lcd_i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
LCD_I2C_ADDR = lcd_i2c.scan()[0]
lcd = I2cLcd(lcd_i2c, LCD_I2C_ADDR, 2, 16)


menu = None

with open("menu.json") as f:
    menu = json.load(f)["children"]

current_menu = menu
submenu = [menu]

pos = 0
cursor_pos = 0


async def menu_control():
    global pos
    global cursor_pos
    global current_menu
    global submenu
    while True:
        lcd.move_to(0, cursor_pos)
        lcd.putchar(">")
        lcd.move_to(1, 0)
        lcd.putstr(current_menu[pos]["name"])
        lcd.move_to(1, 1)
        lcd.putstr(current_menu[pos + 1]["name"])
        input = await keypad.get_input()

        if int(input) == 8:
            cursor_pos += 1

        if int(input) == 2:
            cursor_pos -= 1

        if int(input) == 5:
            print(current_menu[pos + cursor_pos]["children"])
            print(current_menu[pos + cursor_pos])
            if len(current_menu[pos + cursor_pos]["children"]) > 0:
                current_menu = current_menu[pos + cursor_pos]["children"]
                pos = 0
                cursor_pos = 0

        if cursor_pos > 1:
            pos += 1
            cursor_pos = 1

        if cursor_pos < 0:
            pos -= 1
            cursor_pos = 0

        if pos + cursor_pos >= len(current_menu):
            pos = 0
            cursor_pos = 0

        if pos + cursor_pos < 0:
            pos = len(current_menu) - 2
            cursor_pos = 1

        lcd.clear()


loop = uasyncio.get_event_loop()

loop.create_task(menu_control())

loop.run_forever()
