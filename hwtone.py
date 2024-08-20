# code in this file modified from https://www.instructables.com/Respberry-Pi-Pico-W-Generating-Tones-With-Programm/

import rp2
import machine
from machine import Pin
import uasyncio


@rp2.asm_pio(
    set_init=rp2.PIO.OUT_LOW,
    in_shiftdir=rp2.PIO.SHIFT_LEFT,
    out_shiftdir=rp2.PIO.SHIFT_LEFT,
)

def wave_prog():
    pull(block)
    mov(x, osr)         # waveCount
    pull(block)
    label("loop")
    mov(y, osr)         # halfWaveNumCycles
    set(pins, 1)        # high
    label("high")
    jmp(y_dec, "high")
    mov(y, osr)         # halfWaveNumCycles
    set(pins, 0)        # low
    label("low")
    jmp(y_dec, "low")
    jmp(x_dec, "loop")

# the clock frequency of Raspberry Pi Pico is 125MHz; 1953125 is 125MHz / 64
sm = rp2.StateMachine(0, wave_prog, freq=1953125, set_base=Pin(2)) 
sm.active(1)

def HWPlayTone(freq: int, duration: int):
    # count 1 cycle for jmp() ==> 1 cycle per half wave ==> 2 cycles per wave
    halfWaveNumCycles = round(1953125.0 / freq / 2)
    waveCount = round(duration * freq / 1000.0)
    sm.put(waveCount)
    sm.put(halfWaveNumCycles)

async def timer_buzzer():
    while True:
        HWPlayTone(1000, 500)
        await uasyncio.sleep(1)