from machine import Pin


from utime import ticks_ms, ticks_add, ticks_diff
from PiicoDev_Unified import sleep_ms
from PiicoDev_SSD1306 import create_PiicoDev_SSD1306
from PiicoDev_RGB import PiicoDev_RGB
from PiicoDev_Buzzer import PiicoDev_Buzzer
from PiicoDev_CAP1203 import PiicoDev_CAP1203
from PiicoDev_VEML6040 import PiicoDev_VEML6040

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

interval = 1
prev_note = 'rest'
color_read_interval = 500
hue = ''
color = ''
next_color_read = 0
led_interval = 50
next_led_off = 0

while True:
    now = ticks_ms()

    # read the color sensor
    if ticks_diff(next_color_read, now) < 0:
        hue = color_sensor.readHSV()['hue']
        color = color_sensor.classifyHue()
        next_color_read = ticks_add(now, color_read_interval)
        set_led = True

    # set LED if we want to
    if set_led:
        next_led_off = ticks_add(now, led_interval)
        led.high()
        set_led = False
    elif ticks_diff(next_led_off, now) < 0:
        led.low()

    # read touch button
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

    # buzz a tone
    if prev_note != note:
        buzz.tone(tone)
        prev_note = note

    # print to the screen
    text = "{0}: {1:.0f}".format(color, hue)
    if note != 'rest':
        text = note
    display.fill(0)
    display.text(text, 20, 35, 1)
    display.show()


     # toggle peripheral led
    leds.setPixel(0, [ 0, leds_state[0] * 255, 0 ] )
    leds.setPixel(1, [ leds_state[1] * 255, 0, 0 ])
    leds.setPixel(2, [ 0, 0, leds_state[2] * 255])
    leds.show()

    sleep_ms(interval)