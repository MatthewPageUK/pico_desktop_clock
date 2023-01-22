# Raspberry Pi Pico Desktop Clock with Round LCD

A little desktop clock with round display for Raspberry Pi Pico, or could be coded to do and be anything you want.

* Acquires current time from NTP
* Customisable alarms with snooze feature
* Buzzer to play musical alarms

### Latest
* 21 Jan 2023 - Version 2 - new design, added buttons, buzzer and alarms
* 20 Jan 2023 - Moved the star movement to core1, added simple alarms, a night mode ready for a light sensor, ASCII art and got the AI to write some comments for me.
* 30 Dec 2022 - Fixed some time and code issues

### Version 2
https://user-images.githubusercontent.com/46349796/213926866-4d1f6632-3ad6-42b0-ba31-92c4016c5022.mp4

### Hardare requirements:
* Raspberry Pi Pico-W
* 1.3" SPI Round LCD Screen (240x240)
* 2 x momentary push buttons (Omron type B3F with long extension)
* Buzzer

## Round LCD 1.3" SPI
https://thepihut.com/products/1-3-spi-colour-round-lcd-240x240-breakout

## Pico W
https://thepihut.com/products/raspberry-pi-pico-w

## LCD Wiring
* 3-5V to any 5V or 3V pin
* CS to GP17
* SCK to GP18
* MOSI to GP19
* DC to GP16
* BL to GP20
* GND to any ground pin

### Button Wiring
* Button 1 to GP0
* Button 2 to GP1
* GND to any ground pin (3)

### Buzzer Wiring
* Positive to GP15
* Negative to any ground pin (18)

![IMG_20230121_194446](https://user-images.githubusercontent.com/46349796/213927016-2a4e380b-3378-4212-a818-23bbc12693c3.jpg)

![IMG_20230121_203929](https://user-images.githubusercontent.com/46349796/213927093-d79e3fc7-9ae3-4553-a282-4f1663df9421.jpg)

## Python MModules
Installed MicroPython with Pimoroni graphics via Thonny

https://github.com/pimoroni/pimoroni-pico/tree/main/micropython/modules/picographics

## Printing
Printed on an Ender 3 Neo v2 with standard settings and PLA filament. (Nasty top layer)

![IMG_20230122_133425](https://user-images.githubusercontent.com/46349796/213927059-f73bd700-8a8c-4ec3-a36d-c6ac833bc317.jpg)

![Desktop Clock v2 v10](https://user-images.githubusercontent.com/46349796/213927189-6ac83479-3f26-4988-8e9f-f5b01f33679a.png)

# Bugs
* Multicore seems to crash alot, especially with the IRQ buttons..
Freeware - use as you wish
