"""
  ____            _    _                 ____ _            _
 |  _ \  ___  ___| | _| |_ ___  _ __    / ___| | ___   ___| | __
 | | | |/ _ \/ __| |/ / __/ _ \| '_ \  | |   | |/ _ \ / __| |/ /
 | |_| |  __/\__ \   <| || (_) | |_) | | |___| | (_) | (__|   <
 |____/ \___||___/_|\_\\__\___/| .__/   \____|_|\___/ \___|_|\_\
                               |_|

 Raspberry Pi Pico-W desktop clock

 Buzzer and musical tones

 Inspired by https://www.tomshardware.com/how-to/buzzer-music-raspberry-pi-pico

"""
from machine import Pin, PWM
from utime import sleep

"""Note lengths in beats
SB - Semibreve (whole note)
M - Minim (half note)
C - Crotchet (quarter note)
Q - Quaver (eighth note)
SQ - Semi-quaver (sixteenth note)
"""
NOTE_SB = 4
NOTE_M = 2
NOTE_C = 1
NOTE_Q = 0.5
NOTE_SQ = 0.25

# Musical tones in Hz
TONES = {
    "B0": 31, "C1": 33, "CS1": 35, "D1": 37, "DS1": 39, "E1": 41, "F1": 44, "FS1": 46, "G1": 49, "GS1": 52, "A1": 55, "AS1": 58, "B1": 62,
    "C2": 65, "CS2": 69, "D2": 73, "DS2": 78, "E2": 82, "F2": 87, "FS2": 93, "G2": 98, "GS2": 104, "A2": 110, "AS2": 117, "B2": 123,
    "C3": 131, "CS3": 139, "D3": 147, "DS3": 156, "E3": 165, "F3": 175, "FS3": 185, "G3": 196, "GS3": 208, "A3": 220, "AS3": 233, "B3": 247,
    "C4": 262, "CS4": 277, "D4": 294, "DS4": 311, "E4": 330, "F4": 349, "FS4": 370, "G4": 392, "GS4": 415, "A4": 440, "AS4": 466, "B4": 494,
    "C5": 523, "CS5": 554,"D5": 587, "DS5": 622, "E5": 659, "F5": 698, "FS5": 740, "G5": 784, "GS5": 831, "A5": 880, "AS5": 932, "B5": 988,
    "C6": 1047, "CS6": 1109, "D6": 1175, "DS6": 1245, "E6": 1319, "F6": 1397, "FS6": 1480, "G6": 1568, "GS6": 1661, "A6": 1760, "AS6": 1865, "B6": 1976,
    "C7": 2093, "CS7": 2217, "D7": 2349, "DS7": 2489, "E7": 2637, "F7": 2794, "FS7": 2960, "G7": 3136, "GS7": 3322, "A7": 3520, "AS7": 3729, "B7": 3951,
    "C8": 4186, "CS8": 4435, "D8": 4699, "DS8": 4978
}

# Beats per minute
BPM = 120

# Pause between notes
PAUSE = 0.01

"""Song to play - Happy Birthday"""
SONG = (
    ("C4", NOTE_Q), ("C4", NOTE_Q), ("D4", NOTE_C), ("C4", NOTE_C), ("F4", NOTE_C), ("E4", NOTE_M),
    ("C4", NOTE_Q), ("C4", NOTE_Q), ("D4", NOTE_C), ("C4", NOTE_C), ("G4", NOTE_C), ("F4", NOTE_M),
    ("C4", NOTE_Q), ("C4", NOTE_Q), ("C5", NOTE_C), ("A5", NOTE_C), ("F4", NOTE_C),
    ("E4", NOTE_C), ("D4", NOTE_C), ("B5", NOTE_Q), ("B5", NOTE_Q), ("A5", NOTE_C),
    ("F4", NOTE_C), ("G4", NOTE_C),  ("F4", NOTE_M)
)

class Buzzer():
    """Class to handle the buzzer.
    pin - The pin the buzzer is connected to"""
    def __init__(self, pin):
        self.pin = Pin(pin)
        self.pwm = PWM(self.pin)
        self.pwm.freq(500)
        self.pwm.duty_u16(0)

    def playNote(self, note):
        """Plays a note using the buzzer
        note - A tuple of the note to play and the length of the note"""
        if (note[0] == "R"):
            self.pwm.duty_u16(0)
        else:
            self.pwm.duty_u16(1000)
            self.pwm.freq(TONES[note[0]])

        sleep((60 / BPM) * note[1])
        self.pwm.duty_u16(0)
        sleep(PAUSE)

    def playSong(self):
        """Plays a song using the buzzer
        song - A tuple of notes to play"""
        for note in SONG:
            self.playNote(note)

        self.pwm.duty_u16(0)

    def alert(self):
        """Plays an alert sound using the buzzer"""
        self.pwm.duty_u16(1000)
        for x in range(500, 900, 3):
            self.pwm.freq(x)
            sleep(0.01)
        self.pwm.duty_u16(0)

    def beep(self):
        """Plays a beep sound using the buzzer"""
        self.playNote(("B5", NOTE_SQ))
        self.playNote(("D5", NOTE_SQ))

    def yes(self):
        """Plays a yes sound using the buzzer"""
        self.playNote(("C5", NOTE_SQ))

    def no(self):
        """Plays a no sound using the buzzer"""
        self.playNote(("E4", NOTE_SQ))
        self.playNote(("C4", NOTE_SQ))
