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

global submenu
global menu_pos
submenu = [menu]
menu_pos = []

global pos
global cursor_pos
pos = 0
cursor_pos = 0

def menu_back():
    global submenu
    global menu_pos
    global pos
    global cursor_pos
    submenu.pop()
    current_menu_pos = menu_pos.pop()
    pos = current_menu_pos[0]
    cursor_pos = current_menu_pos[1]

menu_functions = {
    "back": menu_back,
    "backlight_on": lcd.backlight_on,
    "backlight_off": lcd.backlight_off
}


async def menu_control():
    global submenu
    global menu_pos
    global pos
    global cursor_pos
    while True:
        lcd.move_to(0, cursor_pos)
        lcd.putchar(">")
        lcd.move_to(1, 0)
        lcd.putstr(submenu[-1][pos]["name"])
        lcd.move_to(1, 1)
        lcd.putstr(submenu[-1][pos + 1]["name"])
        input = await keypad.get_input()

        if (int(input) == 8):
            cursor_pos += 1

        if (int(input) == 2):
            cursor_pos -= 1

        if (int(input) == 5):
            if (("children" in submenu[-1][pos + cursor_pos].keys()) and (len(submenu[-1][pos + cursor_pos]["children"]) > 0)):
                submenu.append(submenu[-1][pos + cursor_pos]["children"])
                menu_pos.append([pos, cursor_pos])
                pos = 0
                cursor_pos = 0
            elif (("function" in submenu[-1][pos + cursor_pos].keys()) and (len(submenu[-1][pos + cursor_pos]["function"]) > 0)):
                for function in (submenu[-1][pos + cursor_pos]["function"]):
                    menu_functions[function]()



        if (cursor_pos > 1):
            pos += 1
            cursor_pos = 1

        if (cursor_pos < 0):
            pos -= 1
            cursor_pos = 0

        if (pos + cursor_pos >= len(submenu[-1])):
            pos = 0
            cursor_pos = 0

        if (pos + cursor_pos < 0):
            pos = len(submenu[-1]) - 2
            cursor_pos = 1

        lcd.clear()


loop = uasyncio.get_event_loop()

loop.create_task(menu_control())

loop.run_forever()