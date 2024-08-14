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
profiles = None

with open("menu.json") as f:
    menu = json.load(f)["children"]

with open("profiles.json") as f:
    profiles = json.load(f)["profiles"]
    profiles.append({"name": "Back"})


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

def clear_vars():
    global submenu
    global menu_pos
    global pos
    global cursor_pos
    submenu = [menu]
    menu_pos = []
    pos = 0
    cursor_pos = 0

menu_functions = {
    "back": menu_back,
    "backlight_on": lcd.backlight_on,
    "backlight_off": lcd.backlight_off,
    "clear_vars": clear_vars
}

process_status = "profile_select"

async def menu_control():
    global submenu
    global menu_pos
    global pos
    global cursor_pos
    global process_status
    while True:
        if (process_status == "main_menu"):
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
            update_menu()
            
        else:
            await uasyncio.sleep_ms(0)

async def profile_select_menu():
    global menu_pos
    global pos
    global cursor_pos
    global process_status
    while True:
        if (process_status == "profile_select"):
            lcd.move_to(0, cursor_pos)
            lcd.putchar(">")
            lcd.move_to(1, 0)
            lcd.putstr(profiles[pos]["name"])
            lcd.move_to(1, 1)
            lcd.putstr(profiles[pos + 1]["name"])
            input = await keypad.get_input()

            if (int(input) == 8):
                cursor_pos += 1

            if (int(input) == 2):
                cursor_pos -= 1

            if (int(input) == 5):
                if (profiles[pos + cursor_pos]["name"] == "Back"):
                    process_status = "main_menu"
                else:
                    lcd.clear()
                    lcd.move_to(0, 0)
                    lcd.putstr(profiles[pos + cursor_pos]["name"])
                    lcd.move_to(0, 1)
                    lcd.putstr("A:Start, B:Exit")
                    input = await keypad.get_input()
                    if (input == 'A'):
                        #placeholder
                    elif (input == 'B')


            update_menu()

        else:
            await uasyncio.sleep_ms(0)


def update_menu():
    global pos
    global cursor_pos
    
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



menu_loop = uasyncio.get_event_loop()
menu_loop.create_task(menu_control())
menu_loop.create_task(profile_select_menu())
menu_loop.run_forever()