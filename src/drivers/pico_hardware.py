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

def blink_led(count=1, duration_ms=100, delay_ms=None):
    assert type(count) == int
    assert type(duration_ms) == int
    if delay_ms == None:
        delay_ms = duration_ms
    assert type(delay_ms) == int

    try:
        while count:
            turn_led_on()
            time.sleep_ms(duration_ms)
            turn_led_off()
            if count == 1:
                break
            time.sleep_ms(delay_ms)
            count -= 1
    finally:
        if get_led_value():
            turn_led_off()


# onboard boot select button
def poll_bootsel_till_released(timeout_ms=None, press_callback=None, release_callback=None):
    pressed_duration_us = None
    pressed_since_us = None
    pressed_sleeptime_us = 25000
    unpressed_sleeptime_us = 100000

    if timeout_ms:
        timeout_ms = time.ticks_ms() + int(timeout_ms)

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
                if timeout_ms and time.ticks_ms() >= timeout_ms:
                    break
                time.sleep_us(unpressed_sleeptime_us)
            else:
                pressed_duration_us = time.ticks_us() - pressed_since_us
                if release_callback:
                    release_callback()
                break

    return pressed_duration_us


def poll_bootsel(timeout_s=None):
    PRESS_TYPES = (None, "unknown", "short", "double", "long")

    pressed_us = poll_bootsel_till_released(timeout_s*1000)

    if not pressed_us:
        # no press is None
        pressed_type = None

    elif pressed_us < 0.5 * 10**6:
        pressed_again_us = poll_bootsel_till_released(500)

        # a single <0.5s press is "short"
        if not pressed_again_us:
            pressed_type = "short"

        # another <0.5s press is "double"
        elif pressed_again_us < 0.5 * 10**6:
            pressed_type = "double"

        # anything else is unknown
        else:
            pressed_type = "unknown"

    elif 3 * 10**6 < pressed_us < 5 * 10**6:
        # a 3-5s press is "long"
        pressed_type = "long"

    else:
        # anything else is unknown
        pressed_type = "unknown"

    assert pressed_type in PRESS_TYPES

    return pressed_type
    

# user-added piezo speaker
class Piezo:
    def __init__(self, pin, duty=2**8):
        self.pwm = machine.PWM(machine.Pin(int(pin)))
        self.duty = int(duty)

    def tone(self, freq, duration_ms, duty=None):
        assert type(freq) == int
        assert type(duration_ms) == int
        if duty == None:
           duty = self.duty
        assert type(duty) == int

        try:
            self.pwm.freq(freq)
            self.pwm.duty_u16(duty)
            time.sleep_ms(duration_ms)
        finally:
            self.quiet()

    def setDuty(self, duty):
        self.duty = int(duty)

    def quiet(self):
        self.pwm.duty_u16(0)

    def die(self):
        self.pwm.deinit()


#
# example usage: feedback to user via led/piezo
#

# _buzzer = None
_buzzer = Piezo(15, 1024)

def alert(count=10, interval_ms=100, audible=_buzzer, hilo=False):
    '''
    blinks the led count times for interval_ms;
    ... may play alternating lo/hi tones to piezo
    '''
    LOW_TONE = 400
    HIGH_TONE = 800
    if hilo:
       LOW_TONE, HIGH_TONE = HIGH_TONE, LOW_TONE
    assert type(count) == int
    assert type(interval_ms) == int
    try:
        for i in range(count):
            toggle_led()
            if audible and _buzzer:
                _buzzer.tone(LOW_TONE if i%2==0 else HIGH_TONE, interval_ms)
            else:
                time.sleep_ms(interval_ms)
    finally:
        turn_led_off()
        if audible and _buzzer:
            _buzzer.die()


ack_short_press = lambda: alert(2, 100)
ack_double_press = lambda: alert(2, 100, hilo=True)
ack_long_press = lambda: alert(2, 500)
nack_press = lambda: alert(6, 300, hilo=True)
