from machine import Pin
from time import sleep

led = Pin("LED", Pin.OUT)

from PiicoDev_SSD1306 import create_PiicoDev_SSD1306
from PiicoDev_RGB import PiicoDev_RGB

display = create_PiicoDev_SSD1306()
leds = PiicoDev_RGB()

i = 0
while True:
    # toggle system led
    led.toggle()

    # print the counter
    display.fill(1)
    display.text(str(i), 50, 35, 0)
    display.show()

    # toggle peripheral led
    leds.setPixel(0, [ 0, (i % 2) * 255, 0 ] )
    leds.show()

    sleep(0.5)

    i += 1