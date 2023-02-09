from buzzer import Buzzer
from utime import sleep

buzzer = Buzzer(15)

buzzer.alert()
sleep(2)
buzzer.beep()
sleep(2)
buzzer.yes()
sleep(2)
buzzer.no()
sleep(2)
buzzer.playSong()