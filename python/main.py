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

 Firmware requirements:
    Micropython with Pimoroni Picographics library

 Hardare requirements:
    Raspberry Pi Pico-W
    1.3" SPI Round LCD Screen (240x240)

 Default screen wiring:
    CS to GP17
    SCK to GP18
    MOSI to GP19
    DC to GP16
    BL to GP20

 By           - Matthew Page
 Credit       - Everyone who came before and wrote a how to guide
 Version      - 0.2
 Release date - 33rd December 2022
"""
import math
import random
import utime
import network
import ntptime
import _thread
from picographics import PicoGraphics, DISPLAY_ROUND_LCD_240X240, PEN_P8

display = PicoGraphics(display=DISPLAY_ROUND_LCD_240X240, pen_type=PEN_P8, rotate=90)

# General settings and constant(ishes)
WIFI_SSID = "network"
WIFI_PASSWORD = "password"
NIGHT_MODE = False
WIDTH = display.get_bounds()[0]
HEIGHT = display.get_bounds()[1]
MIDX = int(WIDTH/2)
MIDY = int(WIDTH/2)
FPS = 25
BG = display.create_pen(90, 25, 70)
PURPLE = display.create_pen(255, 50, 255)
GREEN = display.create_pen(50, 255, 50)
BLACK = display.create_pen(0, 0, 0)
STARS_COLOUR = display.create_pen(220, 200, 220)
STARS_TOTAL = 200
STARS_SPEED_MAX = 25
DEFAULT_NOTIFICATION_DELAY = 2

# Default alarms (Hours, Minutes, Seconds, Message)
alarms = ((8, 30, 0, "Time to get up!"), (12, 0, 0, "Lunch time!"), (17, 0, 0, "Time to go home!"), (22, 30, 0, "Time to go to bed!"))

# Dim the display if in night mode - this could be triggered by a light sensor
if NIGHT_MODE:
    display.set_backlight(0.3)
else:
    display.set_backlight(1.0)

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
    """Show an alarm message on the display
    text: The text to show"""
    for x in range(0, 5):
        notification(text, PURPLE, 0.5)
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

    def move(self, WIDTH, HEIGHT):
        """Move the star and rebirth if off screen
        Thread Bug! For some reasons I keep getting HEIGHT undefined, but the other globals work?
        WIDTH: The width of the display
        HEIGHT: The height of the display"""

        self.x += self.dx / 10
        self.y += self.dy / 10
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
    while True:
        for star in stars:
            star.move(WIDTH, HEIGHT)
        utime.sleep(1 / FPS)

# Main Program
notification("Starting up!", PURPLE)

# Get the time from NTP
setNtpTime(WIFI_SSID, WIFI_PASSWORD)

# Create some stars
stars = []
for i in range(0, STARS_TOTAL):
    stars.append(Star())

# Move the stars in core1 with a new thread
core1 = _thread.start_new_thread(moveStars, ())

# Main Loop
while True:

    # Time in seconds
    seconds = utime.time()

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

    # Draw the stars that have been moved in core1
    for star in stars:
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

    # Draw the time
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
