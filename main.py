import machine
from machine import I2C, Pin

import time

import uasyncio

import json

from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd

import keypad

import network


lcd_i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
LCD_I2C_ADDR = lcd_i2c.scan()[0]
lcd = I2cLcd(lcd_i2c, LCD_I2C_ADDR, 2, 16)


menu = None
profiles = None
networks = None

with open("menu.json") as f:
    menu = json.load(f)["children"]

with open("profiles.json") as f:
    profiles = json.load(f)["profiles"]
    profiles.append({"name": "Back"})

with open("networks.json") as f:
    networks = json.load(f)["networks"]


global submenu
global menu_pos
submenu = [menu]
menu_pos = []

global pos
global cursor_pos
pos = 0
cursor_pos = 0

global process_status
process_status = "profile_select"

def draw_screen(l1text, l2text, cursor_position_draw):
    lcd.move_to(0, cursor_position_draw)
    lcd.putchar(">")
    lcd.move_to(1, 0)
    lcd.putstr(l1text)
    lcd.move_to(1, 1)
    lcd.putstr(l2text)


def menu_back():
    global submenu
    global menu_pos
    global pos
    global cursor_pos
    submenu.pop()
    current_menu_pos = menu_pos.pop()
    pos = current_menu_pos[0]
    cursor_pos = current_menu_pos[1]

def select_profile():
    global process_status
    process_status = "profile_select"

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
    "select_profile": select_profile,
    "backlight_on": lcd.backlight_on,
    "backlight_off": lcd.backlight_off,
    "clear_vars": clear_vars
}

async def menu_control():
    global submenu
    global menu_pos
    global pos
    global cursor_pos
    global process_status
    while True:
        if (process_status == "main_menu"):
            draw_screen(submenu[-1][pos]["name"], submenu[-1][pos + 1]["name"], cursor_pos)
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
            update_menu(len(submenu[-1]))
            
        else:
            await uasyncio.sleep_ms(0)

async def profile_select_menu():
    global menu_pos
    global pos
    global cursor_pos
    global process_status
    while True:
        if (process_status == "profile_select"):
            draw_screen(profiles[pos]["name"], profiles[pos + 1]["name"], cursor_pos)
            input = await keypad.get_input()

            if (int(input) == 8):
                cursor_pos += 1

            if (int(input) == 2):
                cursor_pos -= 1

            if (int(input) == 5):
                if (profiles[pos + cursor_pos]["name"] == "Back"):
                    process_status = "main_menu"
                    clear_vars()
                else:
                    lcd.clear()
                    lcd.move_to(0, 0)
                    lcd.putstr(profiles[pos + cursor_pos]["name"])
                    lcd.move_to(0, 1)
                    lcd.putstr("A:Start, B:Exit")
                    input = await keypad.get_input()
                    if (input == 'A'):
                        pass
                    elif (input == 'B'):
                        process_status = "main_menu"
                        clear_vars()

            update_menu(len(profiles))

        else:
            await uasyncio.sleep_ms(0)


def update_menu(length):
    global pos
    global cursor_pos
    
    if (cursor_pos > 1):
        pos += 1
        cursor_pos = 1

    if (cursor_pos < 0):
        pos -= 1
        cursor_pos = 0

    if (pos + cursor_pos >= length):
        pos = 0
        cursor_pos = 0

    if (pos + cursor_pos < 0):
        pos = length - 2
        cursor_pos = 1

    lcd.clear()


async def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    print("connecting to network " + networks[0]["ssid"])
    wlan.connect(networks[0]["ssid"], networks[0]["pass"])
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        await uasyncio.sleep_ms(200)
    print(wlan.ifconfig())


menu_loop = uasyncio.get_event_loop()
menu_loop.create_task(connect())
menu_loop.create_task(menu_control())
menu_loop.create_task(profile_select_menu())
menu_loop.run_forever()