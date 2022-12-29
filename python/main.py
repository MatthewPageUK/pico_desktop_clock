import math
import random
import machine
import utime
import network
import ntptime
from picographics import PicoGraphics, DISPLAY_ROUND_LCD_240X240, PEN_P8

WIFI_SSID = "yournetwork"
WIFI_PASSWORD = "yourpassword"

display = PicoGraphics(display=DISPLAY_ROUND_LCD_240X240, pen_type=PEN_P8, rotate=90)
display.set_backlight(1.0)

WIDTH, HEIGHT = display.get_bounds()
MIDX = int(WIDTH/2)
MIDY = int(WIDTH/2)
FPS = 25
BG = display.create_pen(90, 25, 70)
PURPLE = display.create_pen(255, 50, 255)
GREEN = display.create_pen(50, 255, 50)
BLACK = display.create_pen(0, 0, 0)
STARS_TOTAL = 150
STARS_SPEED_MAX = 50
STARS_COLOUR = display.create_pen(220, 200, 220)
DEFAULT_NOTIFICATION_DELAY = 0

# Show a notification on the display
def notification(text, colour, delay = DEFAULT_NOTIFICATION_DELAY, background = BG):
    display.set_pen(background)
    display.clear()
    display.set_pen(colour)
    display.text(text, int((WIDTH - display.measure_text(text, 2)) / 2), 110, 200, 2)
    display.update()
    utime.sleep(delay)

# Show an alarm message
def alarm(text):
    for x in range(0, 5):
        notification(text, PURPLE, 0.5)
        notification(text, BG, 0.5, PURPLE)

# Connect to WiFi and get time
def setNtpTime(ssid, password):
    notification("Setting time...", GREEN)

    wifiNetwork = network.WLAN(network.STA_IF)
    wifiNetwork.active(True)
    wifiNetwork.connect(ssid, password)

    notification("Connecting to WIFI...", GREEN)
    wifiCount = 1
    while wifiNetwork.status() != network.STAT_GOT_IP:
        notification("Connecting... {c}".format(c=wifiCount), GREEN, 1)
        wifiCount += 1

    notification("Getting NTP time", GREEN)
    ntptime.settime()

    wifiNetwork.disconnect()
    wifiNetwork.active(False)
    notification("Done", PURPLE)

    return True

# Draw an outer ring
def drawRing(value, distance, intervals = 60, small = 3, large = 6, inner = 1):
    for dot in range(0, intervals):
        angle = math.pi * 2 * (dot / intervals) - math.pi / 2
        x = int(MIDX + math.cos(angle) * distance)
        y = int(MIDY + math.sin(angle) * distance)

        if dot >= value:
            colour = GREEN
        else:
            colour = PURPLE

        if dot == value:
            radius = large
        else:
            radius = small

        display.set_pen(colour)
        display.circle(x, y, radius)
        display.set_pen(BG)
        display.circle(x, y, inner)

# Draw a hand on the clock face
def drawHand(value, distance, intervals = 60):
    display.set_pen(GREEN)
    angle = math.pi * 2 * (value / intervals) - math.pi / 2
    x = int(MIDX + math.cos(angle) * distance)
    y = int(MIDY + math.sin(angle) * distance)
    display.line(MIDX, MIDY, x, y)

# A star class
class Star:
    def __init__(self, x = MIDX, y = MIDY, r = 1, dx = 0, dy = 0):
        self.x = x
        self.y = y
        self.r = r
        self.dx = dx
        self.dy = dy
        self.rebirth()

    # Move star and rebirth if off screen
    def move(self):
        self.x += self.dx / 10
        self.y += self.dy / 10
        if self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT:
            self.rebirth()
    # Draw star on the display
    def draw(self):
        display.set_pen(STARS_COLOUR)
        display.circle(int(self.x), int(self.y), int(self.r))

    # Rebirth the star in the middle with random vector
    def rebirth(self):
        self.x = MIDX
        self.y = MIDY
        self.dx = random.randint(0, STARS_SPEED_MAX * 2) - STARS_SPEED_MAX
        self.dy = random.randint(0, STARS_SPEED_MAX * 2) - STARS_SPEED_MAX

notification("Starting up!", PURPLE)

# Get the time
setNtpTime(WIFI_SSID, WIFI_PASSWORD)

# Create some stars
stars = []
for i in range(0, STARS_TOTAL):
    stars.append(Star())

# Main Loop
while True:

    # Time in seconds
    seconds = utime.time()

    # Clock seconds, minutes and hours
    clock_seconds = seconds % (24 * 3600)
    clock_hours = clock_seconds // 3600
    clock_seconds %= 3600
    clock_minutes = clock_seconds // 60
    clock_seconds %= 60
    if clock_hours > 12:
        clock_hours -= 12

    # Show an alarm
    # if int(clock_seconds) == 45:
    #    alarm('I am alarming')

    # Clear the screen
    display.set_pen(BG)
    display.clear()

    # Move and draw the stars
    for star in stars:
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
