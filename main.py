from machine import Pin
import network
from utime import ticks_ms, ticks_add, ticks_diff
from PiicoDev_Unified import sleep_ms
from PiicoDev_SSD1306 import create_PiicoDev_SSD1306
from PiicoDev_RGB import PiicoDev_RGB
from PiicoDev_Buzzer import PiicoDev_Buzzer
from PiicoDev_CAP1203 import PiicoDev_CAP1203
from PiicoDev_VEML6040 import PiicoDev_VEML6040
from http_server import Server
import _thread

led = Pin("LED", Pin.OUT)
display = create_PiicoDev_SSD1306()
leds = PiicoDev_RGB()
buzz = PiicoDev_Buzzer(volume=1)
touch = PiicoDev_CAP1203()
color_sensor = PiicoDev_VEML6040()

notes = {'C4':262,
         'Db':277,
         'D' :294,
         'Eb':311,
         'E' :330,
         'F' :349,
         'Gb':370,
         'G' :392,
         'Ab':415,
         'A' :440,
         'Bb':466,
         'B' :494,
         'C5':523,
         'rest':0, # zero Hertz is the same as no tone at all
         }

g_color = ''
g_hue = ''
g_lock = _thread.allocate_lock()

def main():
    connect_to_wifi()

    _thread.start_new_thread(main_loop, [])

    server_loop()

def connect_to_wifi():
    nic = network.WLAN(network.WLAN.IF_STA)
    nic.active(True)
    nic.connect('<>', '<>')
    attempts = 0
    while not nic.isconnected():
        if attempts > 3:
            raise(Exception('could not connect to wifi'))
        sleep_ms(400)
        attempts += 1
    print('connected to wifi!')
    print(nic.ifconfig())

def server_loop():
    def get_color_hue_fn():
        with g_lock:
            return (g_color, g_hue)
        
    server = Server(get_color_hue_fn)

    while True:
        server.accept()

def main_loop():
    global g_hue
    global g_color

    interval = 1
    prev_note = 'rest'
    hue = ''
    color = ''
    next_color_read = 0
    next_led_off = 0

    while True:
        now = ticks_ms()

        (did_read, next_color_read, _hue, _color) = read_color_sensor(now, next_color_read)

        if did_read:
            hue = _hue
            color = _color
            with g_lock:
                g_hue = _hue
                g_color = _color

        next_led_off = set_led(now, did_read, next_led_off)

        # read touch button
        (note, leds_state, tone) = read_buttons_for_tone()

        # buzz a tone
        prev_note = buzz_tone(prev_note, note, tone)

        # print to the screen
        show_display_message(note, color, hue)


        # toggle peripheral led
        set_led_array(leds_state)

        sleep_ms(interval)


def read_color_sensor(now, next_color_read):
    color_read_interval = 500

    if ticks_diff(next_color_read, now) < 0:
        hue = color_sensor.readHSV()['hue']
        color = color_sensor.classifyHue()
        next_color_read = ticks_add(now, color_read_interval)
        return (True, next_color_read, hue, color)
    return (False, next_color_read, 0, '')

def set_led(now, on, next_led_off):
    led_interval = 50

    if on:
        next_led_off = ticks_add(now, led_interval)
        led.high()
    elif ticks_diff(next_led_off, now) < 0:
        led.low()

    return next_led_off

def read_buttons_for_tone():
    status = touch.read()
    note = 'rest'
    leds_state = [ 0, 0, 0 ]
    if status[1]:
        note = 'C4'
        leds_state = [ 1, 0, 0 ]
    elif status[2]:
        note = 'E'
        leds_state = [ 0, 1, 0 ]
    elif status[3]:
        note = 'G'
        leds_state = [ 0, 0, 1, ]

    tone = notes[note]

    return (note, leds_state, tone)

def buzz_tone(prev_note, note, tone):
    if prev_note != note:
        buzz.tone(tone)
        return note

    return prev_note

def show_display_message(note, color, hue):
    text = "{0}: {1:.0f}".format(color, hue)
    if note != 'rest':
        text = note
    display.fill(0)
    display.text(text, 20, 35, 1)
    display.show()

def set_led_array(leds_state):
    leds.setPixel(0, [ 0, leds_state[0] * 255, 0 ] )
    leds.setPixel(1, [ leds_state[1] * 255, 0, 0 ])
    leds.setPixel(2, [ 0, 0, leds_state[2] * 255])
    leds.show()

main()