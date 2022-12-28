import time
import math
import random
import machine
from picographics import PicoGraphics, DISPLAY_ROUND_LCD_240X240, PEN_P8

display = PicoGraphics(display=DISPLAY_ROUND_LCD_240X240, pen_type=PEN_P8, rotate=90)
display.set_backlight(1.0)

WIDTH, HEIGHT = display.get_bounds()
MIDX = int(WIDTH/2)
MIDY = int(HEIGHT/2)
FPS = 25
BG = display.create_pen(90, 25, 70)
PURPLE = display.create_pen(255, 50, 255)
GREEN = display.create_pen(50, 255, 50)
BLACK = display.create_pen(0, 0, 0)
STARS_TOTAL = 150
STARS_SPEED_MAX = 50
STARS_COLOUR = display.create_pen(220, 200, 220)

class Star:
    def __init__(self, x, y, r, dx, dy, pen):
        self.x = x
        self.y = y
        self.r = r
        self.dx = dx
        self.dy = dy
        self.pen = pen

# Create some stars
stars = []
for i in range(0, STARS_TOTAL):
    dx = random.randint(0, STARS_SPEED_MAX * 2) - STARS_SPEED_MAX
    dy = random.randint(0, STARS_SPEED_MAX * 2) - STARS_SPEED_MAX
    stars.append(Star(MIDX, MIDY, 1, dx, dy, STARS_COLOUR))

# Main Loop
while True:

    # Time in seconds
    seconds = time.time()

    # Clock seconds, minutes and hours
    clock_seconds = seconds % (24 * 3600)
    clock_hours = clock_seconds // 3600
    clock_seconds %= 3600
    clock_minutes = clock_seconds // 60
    clock_seconds %= 60
    if clock_hours > 12:
        clock_hours -= 12

    # Clear the screen
    display.set_pen(BG)
    display.clear()

    # Move and draw the stars
    for star in stars:
        star.x += star.dx / 10
        star.y += star.dy / 10
        if star.x < 0 or star.x > WIDTH or star.y < 0 or star.y > HEIGHT:
            star.x = MIDX
            star.y = MIDY
            star.dx = random.randint(0, STARS_SPEED_MAX * 2) - STARS_SPEED_MAX
            star.dy = random.randint(0, STARS_SPEED_MAX * 2) - STARS_SPEED_MAX

        display.set_pen(star.pen)
        display.circle(int(star.x), int(star.y), int(star.r))

    # Draw the hours ring
    for dot in range(0, 12):
        s1 = dot / 12
        angle = math.pi * 2 * s1 - math.pi / 2
        x = MIDX + math.cos(angle) * 70
        y = MIDY + math.sin(angle) * 70

        if dot >= clock_hours:
            display.set_pen(GREEN)
        else:
            display.set_pen(PURPLE)

        if dot == clock_hours:
            display.circle(int(x), int(y), 6)
        else:
            display.circle(int(x), int(y), 3)

        display.set_pen(BG)
        display.circle(int(x), int(y), 1)

    # Draw the minutes ring
    for dot in range(0, 60):
        s1 = dot / 60
        angle = math.pi * 2 * s1 - math.pi / 2
        x = MIDX + math.cos(angle) * 85
        y = MIDY + math.sin(angle) * 85

        if dot >= clock_minutes:
            display.set_pen(GREEN)
        else:
            display.set_pen(PURPLE)

        if dot == clock_minutes:
            display.circle(int(x), int(y), 6)
        else:
            display.circle(int(x), int(y), 3)

        display.set_pen(BG)
        display.circle(int(x), int(y), 1)

    # Draw the seconds ring
    for dot in range(0, 60):
        s1 = dot / 60
        angle = math.pi * 2 * s1 - math.pi / 2
        x = MIDX + math.cos(angle) * 100
        y = MIDY + math.sin(angle) * 100

        if dot >= clock_seconds:
            display.set_pen(GREEN)
        else:
            display.set_pen(PURPLE)

        if dot == clock_seconds:
            display.circle(int(x), int(y), 6)
        else:
            display.circle(int(x), int(y), 3)

        display.set_pen(BG)
        display.circle(int(x), int(y), 1)

    # Draw the seconds hand
    display.set_pen(GREEN)
    s1 = clock_seconds / 60
    angle = math.pi * 2 * s1 - math.pi / 2
    x = MIDX + math.cos(angle) * 90
    y = MIDY + math.sin(angle) * 90
    display.line(MIDX, MIDY, int(x), int(y))

    # Draw the minutes hand
    s1 = clock_minutes / 60
    angle = math.pi * 2 * s1 - math.pi / 2
    x = MIDX + math.cos(angle) * 75
    y = MIDY + math.sin(angle) * 75
    display.line(MIDX, MIDY, int(x), int(y))

    # Draw the hours hand
    s1 = clock_hours / 12
    angle = math.pi * 2 * s1 - math.pi / 2
    x = MIDX + math.cos(angle) * 60
    y = MIDY + math.sin(angle) * 60
    display.line(MIDX, MIDY, int(x), int(y))

    # Draw the black hole
    display.set_pen(BLACK)
    display.circle(120, 120, 10)

    # Draw the time
    display.set_pen(GREEN)
    text = "{clock_hours}:{clock_minutes}:{clock_seconds}".format(clock_hours=clock_hours, clock_minutes=clock_minutes, clock_seconds=clock_seconds)
    width = display.measure_text(text, 2)
    xpos = int( (240 - width) / 2)

    display.set_pen(BG)
    display.rectangle(xpos-2, 75-2, width + 4, 20)

    display.set_pen(GREEN)
    display.text(text, xpos, 75, 0, 2)

    # Update the display
    display.update()

    # Sleep a while
    time.sleep(1 / FPS)