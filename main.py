import machine
from machine import I2C, Pin, ADC
import time
import math
import uasyncio

import ujson as json

from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd
import keypad
import hwtone

#import network

lcd_i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
LCD_I2C_ADDR = lcd_i2c.scan()[0]
lcd = I2cLcd(lcd_i2c, LCD_I2C_ADDR, 2, 16)
lcd.clear()

led = Pin("LED", Pin.OUT)

ntc = ADC(Pin(27))
ntc_beta = 3950

relay = Pin(28, Pin.OUT)
relay.off()

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

'''
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
'''

global rtc
rtc = machine.RTC()

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

def draw_menu(l1text, l2text, cursor_position_draw):
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
    process_status = "main_menu"

def clear_vars():
    global submenu
    global menu_pos
    global pos
    global cursor_pos
    submenu = [menu]
    menu_pos = []
    pos = 0
    cursor_pos = 0

def zfl(s, width):
    return '{:0>{w}}'.format(s, w=width)

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
            draw_menu(submenu[-1][pos]["name"], submenu[-1][pos + 1]["name"], cursor_pos)
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


async def run_profile(profile):
    lcd.clear()
    for obj in profile:
        if (obj["type"] == "heat"):
            relay.on()
            lcd.clear()
            lcd.move_to(0, 0)
            lcd.putstr("Heating->")
            lcd.putstr(str(obj["temp"]))
            lcd.putstr("C")
            while ((1 / (math.log(1 / (65535.0 / ntc.read_u16() - 1)) / ntc_beta + 1.0 / 298.15) - 273.15) < obj["temp"]):
                lcd.move_to(0,1)
                lcd.putstr(zfl(str(round(1 / (math.log(1 / (65535.0 / ntc.read_u16() - 1)) / ntc_beta + 1.0 / 298.15) - 273.15)), 3))
                lcd.putstr("C")
                await uasyncio.sleep_ms(0)
        if (obj["type"] == "hold"):
            start_time = time.time()
            lcd.clear()
            lcd.move_to(0, 0)
            lcd.putstr("Holding ")
            lcd.putstr(zfl(str(obj["temp"]), 3))
            lcd.putstr("C ")
            lcd.move_to(5, 1)
            lcd.putstr(zfl(str(obj["time"]), 3))
            lcd.putstr("s")
            while (time.time() - start_time < obj["time"]):
                current_temp = round(1 / (math.log(1 / (65535.0 / ntc.read_u16() - 1)) / ntc_beta + 1.0 / 298.15) - 273.15)
                time_passed = time.time() - start_time
                lcd.move_to(0,1)
                lcd.putstr(zfl(str(current_temp), 3))
                lcd.putstr("C")
                lcd.move_to(5, 1)
                lcd.putstr(zfl(str(obj["time"] - time_passed), 3))
                if (time_passed % 7 == 0):
                    print(current_temp)
                    print(obj["temp"])
                    if (current_temp > obj["temp"]):
                        relay.off()
                    elif (current_temp < obj["temp"]):
                        relay.on()
                
                await uasyncio.sleep_ms(200)

        if (obj["type"] == "cool"):
            relay.on()
            lcd.clear()
            lcd.move_to(0, 0)
            lcd.putstr("Cooling->")
            lcd.putstr(str(obj["temp"]))
            lcd.putstr("C")
            while ((1 / (math.log(1 / (65535.0 / ntc.read_u16() - 1)) / ntc_beta + 1.0 / 298.15) - 273.15) > obj["temp"]):
                lcd.move_to(0,1)
                lcd.putstr(zfl(str(round(1 / (math.log(1 / (65535.0 / ntc.read_u16() - 1)) / ntc_beta + 1.0 / 298.15) - 273.15)), 3))
                lcd.putstr("C")
                await uasyncio.sleep_ms(0)
    
    relay.off()
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("Reflow Complete")
    buzzer_task = uasyncio.get_event_loop().create_task(hwtone.timer_buzzer())
    while True:
        await keypad.get_input()
        buzzer_task.cancel()
        break



async def profile_select_menu():
    global menu_pos
    global pos
    global cursor_pos
    global process_status
    while True:
        if (process_status == "profile_select"):
            draw_menu(profiles[pos]["name"], profiles[pos + 1]["name"], cursor_pos)
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
                        await run_profile(profiles[pos + cursor_pos]["profile"])
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

'''
async def connect(network_id):
    global wlan
    print("connecting to network " + networks[network_id]["ssid"])
    wlan.connect(networks[0]["ssid"], networks[network_id]["pass"])
    wlan.ifconfig()
    while wlan.isconnected() == False:
        led.toggle()
        await uasyncio.sleep_ms(100)
    print("connected")
    led.on()
'''

menu_loop = uasyncio.new_event_loop()
'''
if (len(networks) > 0):
    menu_loop.create_task(connect(0))
'''
menu_loop.create_task(menu_control())
menu_loop.create_task(profile_select_menu())

menu_loop.run_forever()