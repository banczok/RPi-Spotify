import datetime
import shutil
import sys
import threading
import time

import requests
from PyQt5 import QtWidgets, uic
from PyQt5.Qt import *
from PyQt5.QtGui import *

import songInfo as sI
import spotifyHandle


class NewThread(threading.Thread):
    isRunning = False

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.start()
        self._is_running = True

    def run(self):
        print("Starting " + self.name)
        if self.name == "Thread-1":
            while True:
                refresh()

        elif self.name == "Thread-2":
            # gpio.gpioListener()
            pass
        else:
            time.sleep(1)
            while True:
                marquee()


def marquee():
    time.sleep(0.18)
    if len(sI.songInfo.title) > 20:
        if sI.songInfo.marqueeIndex == 0:
            Ui.updateGUI.title.setText(sI.songInfo.title)
            time.sleep(15)

        if sI.songInfo.marqueeIndex <= len(sI.songInfo.title):
            Ui.updateGUI.title.setText(sI.songInfo.title[sI.songInfo.marqueeIndex:])

        sI.songInfo.marqueeIndex += 1

        if sI.songInfo.marqueeIndex > len(sI.songInfo.title):
            Ui.updateGUI.title.setText(sI.songInfo.marquee[sI.songInfo.marqueeIndex2:])

            if sI.songInfo.marqueeIndex2 == 30:
                time.sleep(20)

            sI.songInfo.marqueeIndex2 += 1

            if sI.songInfo.marqueeIndex2 > len(sI.songInfo.marquee):
                sI.songInfo.marqueeIndex2 = 0
    else:
        print("Killing thread")
        sys.exit()


def refresh():
    artist, title, isPlaying, url, actual, duration = spotifyHandle.getSongInfo()
    if title != sI.songInfo.title or artist != sI.songInfo.artist or isPlaying != sI.songInfo.isPlaying:
        sI.songInfo.title = title
        sI.songInfo.artist = artist
        sI.songInfo.url = url
        sI.songInfo.isPlaying = isPlaying
        sI.songInfo.duration = duration
        sI.songInfo.marqueeIndex = 0
        sI.songInfo.marqueeIndex2 = 0
        sI.songInfo.marquee = ' ' * 30 + title + ' ' * 15

        if threading.active_count() < 4 and len(title) > 20:
            NewThread()

        Ui.refreshImage(Ui.updateGUI)
        Ui.refreshArtistAndTitle(Ui.updateGUI, (artist, title))
        Ui.refreshButton(Ui.updateGUI)

    Ui.updateSlider(Ui.updateGUI, (actual, duration))
    time.sleep(1)


def nextTrack(event):
    spotifyHandle.next_track()


def prevTrack(event):
    spotifyHandle.prev_track()


class Ui(QMainWindow):
    updateGUI = None

    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('gui.ui', self)
        self.offset = None

        self.setWindowTitle("Spotify Widget")
        self.setWindowIcon(QIcon("img\\icon.ico"))
        self.setMouseTracking(True)
        QFontDatabase.addApplicationFont("img/Montserrat-SemiBold.ttf")
        self.setWindowFlags(Qt.FramelessWindowHint)
        Ui.updateGUI = self

        self.nextTrackButton = self.findChild(QLabel, 'next')
        self.nextTrackButton.mousePressEvent = nextTrack

        self.prevTrackButton = self.findChild(QLabel, 'prev')
        self.prevTrackButton.mousePressEvent = prevTrack

        self.playButton = self.findChild(QLabel, 'play')
        self.playButton.mousePressEvent = self.playPause

        self.title = self.findChild(QLabel, "title")
        self.title.setFont(QFont("Montserrat-SemiBold"))

        self.artist = self.findChild(QLabel, "artist")
        self.artist.setFont(QFont("Montserrat-SemiBold"))

        self.cover = self.findChild(QLabel, 'cover')

        self.exitButton = self.findChild(QLabel, 'exit')
        self.exitButton.mousePressEvent = self.exitApp

        self.miniButton = self.findChild(QLabel, 'mini')
        self.miniButton.mousePressEvent = self.minimizeApp

        self.status = self.findChild(QSlider, 'status')
        self.status.mousePressEvent = self.onClickSliderPosition

        self.durationTime = self.findChild(QLabel, 'finTime')
        self.actualTime = self.findChild(QLabel, 'actTime')

        # style sheet
        self.playButton.setStyleSheet("QLabel{background-color: #d4d4d4} QLabel::hover{background-color: white}")
        self.prevTrackButton.setStyleSheet("QLabel{background-color: #858585} QLabel::hover{background-color: #f2f2f2}")
        self.nextTrackButton.setStyleSheet("QLabel{background-color: #858585} QLabel::hover{background-color: #f2f2f2}")
        self.exitButton.setStyleSheet("QLabel::hover{background-color: #c93434;} ")
        self.mini.setStyleSheet("QLabel::hover{background-color: #858585;}")
        self.artist.setStyleSheet("color: #858585; font: 9pt")
        self.title.setStyleSheet("color: #f2f2f2; font: 18pt")

        self.show()

    def onClickSliderPosition(self, event):
        x = event.pos().manhattanLength()
        value = round((100 * x / self.status.width()) - 5)
        duration = sI.songInfo.duration
        spotifyHandle.seekToPosition(value / 100 * duration)

    def updateSlider(self, value):
        actual = round(value[0] / 1000)
        duration = round(value[1] / 1000)

        actualTime = str(datetime.timedelta(seconds=actual))[2:]
        durationTime = str(datetime.timedelta(seconds=duration))[2:]

        self.actualTime.setText(actualTime)
        self.durationTime.setText(durationTime)

        self.status.setMaximum(duration)
        self.status.setValue(actual)

    def exitApp(self, event):
        self.close()

    def minimizeApp(self, event):
        self.showNormal()
        self.showMinimized()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.pos()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.pos() - self.offset)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.offset = None
        super().mouseReleaseEvent(event)

    def playPause(self, event):
        spotifyHandle.pause_play(sI.songInfo.isPlaying)
        self.refreshButton()

    def refreshButton(self):
        if sI.songInfo.isPlaying:
            self.playButton.setPixmap(QPixmap('img/pause.png'))
        else:
            self.playButton.setPixmap(QPixmap('img/play.png'))

    def refreshArtistAndTitle(self, value):
        self.artist.setText(' '.join(map(str, value[0])))
        self.title.setText(value[1])

    def refreshImage(self):
        image_url = sI.songInfo.url
        filename = "img/cover.jpg"
        r = requests.get(image_url, stream=True)
        if r.status_code == 200:
            r.raw.decode_content = True

            with open(filename, 'wb') as f:
                shutil.copyfileobj(r.raw, f)

            path = 'img/cover.jpg'
        else:
            path = 'img/no-cover.png'

        self.cover.setPixmap(QPixmap(path))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    gui = Ui()
    NewThread()
    NewThread()
    sys.exit(app.exec_())
