import time
import rp2
import machine


# onboard LED
def get_led_value():
    return machine.Pin("LED", machine.Pin.OUT).value()

def turn_led_on():
    machine.Pin("LED", machine.Pin.OUT).value(1)

def turn_led_off(): 
    machine.Pin("LED", machine.Pin.OUT).value(0)

def toggle_led():
    machine.Pin("LED", machine.Pin.OUT).toggle()


# onboard boot select button
def poll_bootsel_till_released(timeout_s=None, press_callback=None, release_callback=None):
    pressed_duration_us = None
    pressed_since_us = None
    pressed_sleeptime_us = 25000
    unpressed_sleeptime_us = 100000

    if timeout_s:
        timeout_s += time.time()

    while True:
        pressed = rp2.bootsel_button()
        if pressed:
            if not pressed_since_us:
                pressed_since_us = time.ticks_us()
                if press_callback:
                    press_callback()
            time.sleep_us(pressed_sleeptime_us)
        else:
            if not pressed_since_us:
                if timeout_s and time.time() > timeout_s:
                    break
                time.sleep_us(unpressed_sleeptime_us)
            else:
                pressed_duration_us = time.ticks_us() - pressed_since_us
                if release_callback:
                    release_callback()
                break

    return pressed_duration_us
