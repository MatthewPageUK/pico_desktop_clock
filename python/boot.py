"""
boot.py: Initialization of the board at power-on/hard-reset
 - restore saved time if available.
 - save time every second using timer.
"""
from ustruct import (pack, unpack)
r=machine.RTC()

# Restore clock save or set sane default value if no save
try:
    with open("hwclock.save","rb") as fr: r.datetime(unpack("<8I",fr.read()))
except (OSError,ValueError) as e:
    r.datetime((2023, 2, 9, 4, 13, 59, 0, 0))

# function to save the RTC 
def rtSaverCallback(t):
    with open("hwclock.save","w") as fw: fw.write(pack("<8I",*(r.datetime())))

# periodic firing of the function every 1000ms (longer or shorter as required)
rtsaver = machine.Timer(mode=machine.Timer.PERIODIC, period=1000, callback=rtSaverCallback)
