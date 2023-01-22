"""
  ____            _    _                 ____ _            _
 |  _ \  ___  ___| | _| |_ ___  _ __    / ___| | ___   ___| | __
 | | | |/ _ \/ __| |/ / __/ _ \| '_ \  | |   | |/ _ \ / __| |/ /
 | |_| |  __/\__ \   <| || (_) | |_) | | |___| | (_) | (__|   <
 |____/ \___||___/_|\_\\__\___/| .__/   \____|_|\___/ \___|_|\_\
                               |_|

 Raspberry Pi Pico-W desktop clock

 Displays a clock on the LCD screen with an animated starfield background
 Connects to a WiFi network to get the time from an NTP server
 Displays alarms and notifications at set times
 Plays musical alarms
 Snooze feature (coming soon)

 Firmware requirements:
    Micropython with Pimoroni Picographics library

 Hardare requirements:
    Raspberry Pi Pico-W
    1.3" SPI Round LCD Screen (240x240)
    2 x momentary push buttons (Omron type B3F with long extension)
    1 x buzzer

 Default screen wiring:
    CS to GP17
    SCK to GP18
    MOSI to GP19
    DC to GP16
    BL to GP20

 Button Wiring
    Button 1 to GP0
    Button 2 to GP1
    GND to any ground pin (3)

 Buzzer Wiring
    Positive to GP15
    Negative to any ground pin (18)

 By           - Matthew Page
 Credit       - Everyone who came before and wrote a how to guide
 Version      - 0.2
 Release date - 22nd January 2023
"""
import math
import random
import utime
import network
import ntptime
import _thread
from machine import Pin, PWM
from picographics import PicoGraphics, DISPLAY_ROUND_LCD_240X240, PEN_P8

display = PicoGraphics(display=DISPLAY_ROUND_LCD_240X240, pen_type=PEN_P8, rotate=90)

# General settings and constant(ishes)
NTP = True                          # Enable NTP time sync
WIFI_SSID = "network"               # WiFi network name
WIFI_PASSWORD = "password"          # WiFi network password
THEME = "RED"                       # Filament colour used to print the case
MULTICORE = True                    # Enable multicore - sometimes buggy
NIGHT_MODE = False                  # Default to day mode
WIDTH = display.get_bounds()[0]     # Screen width
HEIGHT = display.get_bounds()[1]    # Screen height
MIDX = int(WIDTH/2)                 # Middle of the screen
MIDY = int(WIDTH/2)                 # Middle of the screen
FPS = 25                            # Target frame rate
if THEME == "PURPLE":               # Purple case
    PURPLE = display.create_pen(255, 50, 255)
elif THEME == "RED":                # Red case
    PURPLE = display.create_pen(255, 50, 50)
BG = display.create_pen(90, 25, 70)
GREEN = display.create_pen(50, 255, 50)
BLACK = display.create_pen(0, 0, 0)
STARS_COLOUR = display.create_pen(220, 200, 220)
STARS_TOTAL = 200                   # Number of stars to show
STARS_SPEED_MAX = 25                # Max speed of stars
DEFAULT_NOTIFICATION_DELAY = 2      # Time notifications are displayed for
BUZZER_PIN = 15                     # Buzzer GPIO pin
BUZZER_TONES = {"B0": 31, "C1": 33, "CS1": 35, "D1": 37, "DS1": 39, "E1": 41, "F1": 44, "FS1": 46, "G1": 49, "GS1": 52, "A1": 55, "AS1": 58, "B1": 62, "C2": 65, "CS2": 69, "D2": 73, "DS2": 78, "E2": 82, "F2": 87, "FS2": 93, "G2": 98, "GS2": 104, "A2": 110, "AS2": 117, "B2": 123, "C3": 131, "CS3": 139, "D3": 147, "DS3": 156, "E3": 165, "F3": 175, "FS3": 185, "G3": 196, "GS3": 208, "A3": 220, "AS3": 233, "B3": 247, "C4": 262, "CS4": 277, "D4": 294, "DS4": 311, "E4": 330, "F4": 349, "FS4": 370, "G4": 392, "GS4": 415, "A4": 440, "AS4": 466, "B4": 494, "C5": 523, "CS5": 554,"D5": 587, "DS5": 622, "E5": 659, "F5": 698, "FS5": 740, "G5": 784, "GS5": 831, "A5": 880, "AS5": 932, "B5": 988, "C6": 1047, "CS6": 1109, "D6": 1175, "DS6": 1245, "E6": 1319, "F6": 1397, "FS6": 1480, "G6": 1568, "GS6": 1661, "A6": 1760, "AS6": 1865, "B6": 1976, "C7": 2093, "CS7": 2217, "D7": 2349, "DS7": 2489, "E7": 2637, "F7": 2794, "FS7": 2960, "G7": 3136, "GS7": 3322, "A7": 3520, "AS7": 3729, "B7": 3951, "C8": 4186, "CS8": 4435, "D8": 4699, "DS8": 4978}
ALARM_SONG = ("C4", "C4", "D4", "C4", "F4", "E4", "C4", "C4", "D4", "C4", "G4", "F4", "C4", "C4", "C5", "A4", "F4", "E4", "D4", "B4", "B4", "A4", "F4", "G4", "F4", "P", "P")
BUTTON1_PIN = 0                     # Button 1 GPIO pin
BUTTON2_PIN = 1                     # Button 2 GPIO pin

def playsong(song):
    global alarmActive
    """Plays a song using the buzzer
    https://www.tomshardware.com/how-to/buzzer-music-raspberry-pi-pico
    song - A tuple of notes to play"""
    for i in range(len(song)):
        if not alarmActive:
            break
        if (song[i] == "P"):
            buzzer.duty_u16(0)
        else:
            buzzer.duty_u16(1000)
            buzzer.freq(BUZZER_TONES[song[i]])
        utime.sleep(0.3)
    buzzer.duty_u16(0)

def notification(text, colour, delay = DEFAULT_NOTIFICATION_DELAY, background = BG):
    """Show a notification on the display
    text: The text to show
    colour: The colour of the text
    delay: The delay in seconds before clearing the screen
    background: The background colour"""
    display.set_pen(background)
    display.clear()
    display.set_pen(colour)
    display.text(text, int((WIDTH - display.measure_text(text, 2)) / 2), 110, 200, 2)
    display.update()
    utime.sleep(delay)

def showAlarm(text):
    """Show an alarm message on the display and play a song while the alarm is active
    text: The text to show"""
    global alarmActive

    if not alarmActive:
        alarmActive = True
        while alarmActive:
            if alarmActive:
                notification(text, PURPLE, 0.5)
            if alarmActive:
                playsong(ALARM_SONG)
            if alarmActive:
                notification(text, BG, 0.5, PURPLE)

def setNtpTime(ssid, password):
    """Connect to the WIFI and get the time from NTP
    ssid: The WIFI SSID
    password: The WIFI password"""

    notification("Setting time...", GREEN)

    # Connect to WIFI
    wifiNetwork = network.WLAN(network.STA_IF)
    wifiNetwork.active(True)
    wifiNetwork.connect(ssid, password)

    notification("Connecting to WIFI...", GREEN)
    wifiCount = 1

    # Wait for connection
    while wifiNetwork.status() != network.STAT_GOT_IP:
        notification("Connecting... {c}".format(c=wifiCount), GREEN, 1)
        wifiCount += 1

    # Get time from NTP
    notification("Getting NTP time", GREEN)
    ntptime.settime()

    # Disconnect from WIFI
    wifiNetwork.disconnect()
    wifiNetwork.active(False)
    notification("Done", PURPLE)

    return True

def drawRing(value, distance, intervals = 60, small = 3, large = 6, inner = 1):
    """Draw an outer ring on the clock face
    value: The value to show
    distance: The distance from the centre
    intervals: The number of intervals
    small: The size of the small dots
    large: The size of the large dots
    inner: The size of the inner dot circle"""

    for dot in range(0, intervals):

        # Calculate the position of the dot
        angle = math.pi * 2 * (dot / intervals) - math.pi / 2
        x = int(MIDX + math.cos(angle) * distance)
        y = int(MIDY + math.sin(angle) * distance)

        # Set the colour and radius of the dot
        if dot >= value:
            colour = GREEN
        else:
            colour = PURPLE

        if dot == value:
            radius = large
        else:
            radius = small

        # Draw the dot
        display.set_pen(colour)
        display.circle(x, y, radius)
        display.set_pen(BG)
        display.circle(x, y, inner)

def drawHand(value, distance, intervals = 60):
    """Draw a hand on the clock face
    value: The hand position
    distance: The distance from the centre
    intervals: The number of intervals"""

    display.set_pen(GREEN)

    # Calculate the position of the hand
    angle = math.pi * 2 * (value / intervals) - math.pi / 2
    x = int(MIDX + math.cos(angle) * distance)
    y = int(MIDY + math.sin(angle) * distance)

    # Draw the hand
    display.line(MIDX, MIDY, x, y)

class Star:
    """A star class
    x: The x position
    y: The y position
    r: The radius
    dx: The x velocity
    dy: The y velocity"""

    def __init__(self, x = MIDX, y = MIDY, r = 1, dx = 0, dy = 0):
        self.x = x
        self.y = y
        self.r = r
        self.dx = dx
        self.dy = dy
        self.rebirth()

    def move(self):
        """Move the star and rebirth if off screen"""

        # Increase the speed of the stars as the clock ticks
        speed = 15 - (clock_seconds % 60) // 4
        self.x += self.dx / speed
        self.y += self.dy / speed
        if self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT:
            self.rebirth()

    def draw(self):
        """Draw the star on the display"""
        display.set_pen(STARS_COLOUR)
        display.circle(int(self.x), int(self.y), int(self.r))

    def rebirth(self):
        """Rebirth the star in the middle with random vector"""
        self.x = MIDX
        self.y = MIDY
        self.dx = random.randint(0, STARS_SPEED_MAX * 2) - STARS_SPEED_MAX
        self.dy = random.randint(0, STARS_SPEED_MAX * 2) - STARS_SPEED_MAX

def moveStars():
    """Move the stars in a loop - runs as process in core 1 """
    global restartCore1
    try:
        restartCore1 = False
        while True:
            for star in stars:
                star.move()
            utime.sleep(1 / FPS)
    # Sometimes a thread is left running, so catch the error and restart
    # Only happens when you're stopping and starting the program
    except Exception as e:
        print("Restaring core1: {e}".format(e=e))
        restartCore1 = True
        _thread.exit()

def button1Handler(pin):
    """Button 1 IRQ handler - cancels the alarm or toggles Night Mode"""
    global alarmActive, NIGHT_MODE, button1Debounce, seconds

    # Check the time the button was last pressed, debounce
    if button1Debounce == 0 or seconds - button1Debounce > 1:
        button1Debounce = seconds

        if alarmActive:
            alarmActive = False
            print("Alarm cancelled")
        else:
            NIGHT_MODE = not NIGHT_MODE

def button2Handler(pin):
    """Button 2 IRQ handler - snoozes the alarm"""
    global alarmActive, button2Debounce, seconds

    # Check the time the button was last pressed, debounce
    if button2Debounce == 0 or seconds - button2Debounce > 1:
        button2Debounce = seconds

        alarmActive = False
        print("Snoozed")

# Debounce the IRQ buttons, this stores the last time they were pressed
button1Debounce = 0
button2Debounce = 0

# Main Program
restartCore1 = MULTICORE
notification("Starting up!", PURPLE)

# Setup the buttons
button1 = Pin(BUTTON1_PIN, Pin.IN, Pin.PULL_UP)
button2 = Pin(BUTTON2_PIN, Pin.IN, Pin.PULL_UP)

# Setup button 1 and 2 with and IRQ handler
# This is all very buggy and results in random freezes
button1.irq(trigger=Pin.IRQ_FALLING, handler=button1Handler)
button2.irq(trigger=Pin.IRQ_FALLING, handler=button2Handler)

# Set up the buzzer
buzzer = PWM(Pin(BUZZER_PIN))
buzzer.freq(500)
buzzer.duty_u16(0)

# Default alarms (Hours, Minutes, Seconds, Message)
alarms = ((8, 30, 0, "Time to get up!"), (12, 0, 0, "Lunch time!"), (17, 30, 0, "Time to go home!"), (21, 10, 0, "Time to go to bed!"))
alarmActive = False

# Get the time from NTP
if NTP:
    setNtpTime(WIFI_SSID, WIFI_PASSWORD)

# Create some stars
stars = []
for i in range(0, STARS_TOTAL):
    stars.append(Star())

startTime = utime.time()

# Main Loop
while True:

    # Time in seconds
    seconds = utime.time()

    # Dim the display if in night mode - this could be triggered by a light sensor
    if NIGHT_MODE:
        display.set_backlight(0.3)
    else:
        display.set_backlight(1.0)

    # If we need to start / restart core1 thread, do it, but wait a sec for the thread to die
    if MULTICORE and restartCore1:
        utime.sleep(0.5)
        try:
            # Move the stars in core1 with a new thread
            core1 = _thread.start_new_thread(moveStars, ())
        except Exception as e:
            print("core1 failed: {e}".format(e=e))

    # Show a test alarm 5 seconds after startup
    if seconds - startTime == 5:
        showAlarm("This is an alarm!")

    # Clock seconds, minutes and hours
    clock_seconds = seconds % (24 * 3600)
    clock_hours24 = clock_seconds // 3600
    clock_seconds %= 3600
    clock_minutes = clock_seconds // 60
    clock_seconds %= 60
    if clock_hours24 > 12:
        clock_hours = clock_hours24 - 12
    else:
        clock_hours = clock_hours24

    # Check for alarms
    for alarm in alarms:
        if alarm == (clock_hours24, clock_minutes, clock_seconds, alarm[3]):
            showAlarm(alarm[3])

    # Clear the screen
    display.set_pen(BG)
    display.clear()

    # Draw the stars that have been moved in core1, or move them if not using multicore
    for star in stars:
        if not MULTICORE:
            star.move()
        star.draw()

    # Draw the rings
    drawRing(clock_hours, 70, intervals = 12, small = 6, large = 8, inner = 2)
    drawRing(clock_minutes, 85)
    drawRing(clock_seconds, 100)

    # Draw the hands
    drawHand(clock_seconds, 90)
    drawHand(clock_minutes, 75)
    drawHand(clock_hours, 60, 12)

    # Draw the black hole
    display.set_pen(BLACK)
    display.circle(120, 120, 10)

    # Draw the time in a box
    display.set_pen(GREEN)
    text = "{clock_hours:d}:{clock_minutes:02d}:{clock_seconds:02d}".format(clock_hours=clock_hours, clock_minutes=clock_minutes, clock_seconds=clock_seconds)
    twidth = display.measure_text(text, 2)
    xpos = int((WIDTH - twidth) / 2)

    display.set_pen(BG)
    display.rectangle(xpos - 2, 85 - 2, twidth + 4, 20)

    display.set_pen(GREEN)
    display.text(text, xpos, 85, 0, 2)

    # Update the display
    display.update()

    # Sleep a while
    utime.sleep(1 / FPS)
