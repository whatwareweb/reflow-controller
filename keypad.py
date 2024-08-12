import machine
from machine import Pin

import uasyncio

keyMatrix = [
    ["1", "2", "3", "A"],
    ["4", "5", "6", "B"],
    ["7", "8", "9", "C"],
    ["*", "0", "#", "D"]
]

col_pins = [9, 8, 7, 6]
row_pins = [13, 12, 11, 10]

row = []
col = []

for item in row_pins:
    row.append(machine.Pin(item,machine.Pin.OUT))
for item in col_pins:
    col.append(machine.Pin(item,machine.Pin.IN,machine.Pin.PULL_DOWN))



def scan_keypad():
    keys = []

    for row_key in range(len(row)):
        row[row_key].value(1)
        for colKey in range(len(col)):
            if col[colKey].value() == 1:
                key = keyMatrix[row_key][colKey]
                keys.append(key)
        row[row_key].value(0)
    
    return keys


async def wait_for_no_input():
    while len(scan_keypad()) > 0:
        await uasyncio.sleep_ms(0)

async def wait_for_input():
    while len(scan_keypad()) < 1:
        await uasyncio.sleep_ms(0)

    return scan_keypad()

async def get_input():
    await wait_for_no_input()
    keys = await wait_for_input()
    await wait_for_no_input()
    return keys[0]