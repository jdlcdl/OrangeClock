"""
brainstorm:
   Polling the bootsel_button and lighting the onboard led

   When the pico is doing nothing else, it takes about 25-30us to
   set led Pin value to that of rp2.bootsel_button() and store a timestamp,
   therefore sleeping for 25-30ms between polling would imply that the
   pico is idle for all but 1/1000th of its cycles.  To me, this means even 
   polling could be very responsive to button presses and releases (10-40/s)

   Still, setting irqs on the rising and falling edges with a timer seems
   the better way (but not sure yet how to do it with the bootsel_button).
"""

import time
import rp2
import machine

led = machine.Pin("LED", machine.Pin.OUT)
def turn_led_on(): led.value(1)
def turn_led_off(): led.value(0)

def poll_bootsel_till_released(timeout=None, press_callback=None, release_callback=None):
    pressed_duration = None
    pressed_since = None
    pressed_sleeptime = 25000
    unpressed_sleeptime = 100000
    if timeout:
        timeout += time.time()
    
    while True:
        pressed = rp2.bootsel_button()

        if pressed:
            if not pressed_since:
                pressed_since = time.ticks_us()
                if press_callback:
                    press_callback()
            time.sleep_us(pressed_sleeptime)
        else:
            if not pressed_since:
                if timeout and time.time() > timeout:
                    break
                time.sleep_us(unpressed_sleeptime)
            else:
                pressed_duration = time.ticks_us() - pressed_since
                if release_callback:
                    release_callback()
                break
    return pressed_duration

if __name__ == '__main__':
    
    while True:
        pressed = poll_bootsel_till_released(30, turn_led_on, turn_led_off)
        if pressed:
            print("bootsel_button pressed for {:0.3f}s".format(pressed/10**6))
        else:
            print("bootsel_button was not pressed")

