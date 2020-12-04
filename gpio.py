import time

import RPi.GPIO as GPIO

import main
import spotifyHandle


class pinNumbers:
    nextTrack = 5
    prevTrack = 6
    playPause = 12


def gpioListener():
    GPIO.setwarnings(False)

    # use gpio numbers
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(pinNumbers.nextTrack, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(pinNumbers.prevTrack, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(pinNumbers.playPause, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    time.sleep(2)

    while True:
        if GPIO.input(pinNumbers.nextTrack) == GPIO.HIGH:
            spotifyHandle.next_track()

        if GPIO.input(pinNumbers.prevTrack) == GPIO.HIGH:
            spotifyHandle.prev_track()

        if GPIO.input(pinNumbers.playPause) == GPIO.HIGH:
            spotifyHandle.pause_play(main.songInfo.isPlaying)

        time.sleep(.5)

