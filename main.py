import datetime
import shutil
import sys
import threading
import time

import requests
from PyQt5 import QtWidgets, uic
from PyQt5.Qt import *
from PyQt5.QtGui import *

import spotifyHandle


class songInfo:
    artist = ""
    title = ""
    isPlaying = ""
    url = ""
    duration = 0


class NewThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.start()

    def run(self):
        print("Starting " + self.name)
        while True:
            refresh()


def refresh():
    title, artist, isPlaying, url, actual, duration = spotifyHandle.getSongInfo()
    if title != songInfo.title or artist != songInfo.artist or isPlaying != songInfo.isPlaying:
        songInfo.title = title
        songInfo.artist = artist
        songInfo.isPlaying = isPlaying
        songInfo.url = url
        songInfo.duration = duration
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
        self.setWindowFlags(Qt.FramelessWindowHint)
        Ui.updateGUI = self

        self.nextTrackButton = self.findChild(QLabel, 'next')
        self.nextTrackButton.mousePressEvent = nextTrack

        self.prevTrackButton = self.findChild(QLabel, 'prev')
        self.prevTrackButton.mousePressEvent = prevTrack

        self.playButton = self.findChild(QLabel, 'play')
        self.playButton.mousePressEvent = self.playPause

        self.title = self.findChild(QLabel, "title")
        self.artist = self.findChild(QLabel, "artist")
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
        self.status.setStyleSheet(self.stylesheet())
        self.exitButton.setStyleSheet("QLabel::hover{background-color: #c93434;} ")
        self.mini.setStyleSheet("QLabel::hover{background-color: #858585;}")
        self.artist.setStyleSheet("color: #858585; font: 9pt")
        self.title.setStyleSheet("color: #f2f2f2; font: 18pt")

        self.show()

    def stylesheet(self):
        return """
            QSlider::groove:horizontal:hover {
                background: red;
                height: 10px;
            }
    
            QSlider::groove:horizontal {
                background: #858585;
                border: 1px solid;
                height: 5px;
                
            }

            QSlider::sub-page:horizontal {
                background: #858585;
                height: 5px;
                
            }

            QSlider::add-page:horizontal {
                background: #484848;
                height: 5px;

            }
        """

    def onClickSliderPosition(self, event):
        x = event.pos().manhattanLength()
        value = round((99 * x / self.status.width()) - 5)
        duration = songInfo.duration

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
        spotifyHandle.pause_play(songInfo.isPlaying)
        self.refreshButton()

    def refreshButton(self):
        if songInfo.isPlaying:
            self.playButton.setPixmap(QPixmap('img\\pause.png'))
        else:
            self.playButton.setPixmap(QPixmap('img\\play.png'))

    def refreshArtistAndTitle(self, value):
        self.artist.setText(' '.join(map(str, value[1])))
        self.title.setText(value[0])

    def refreshImage(self):
        image_url = songInfo.url
        filename = "img\\cover.jpg"
        r = requests.get(image_url, stream=True)
        if r.status_code == 200:
            r.raw.decode_content = True

            with open(filename, 'wb') as f:
                shutil.copyfileobj(r.raw, f)

            path = 'img\\cover.jpg'
        else:
            path = 'img\\no-cover.png'

        self.cover.setPixmap(QPixmap(path))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    gui = Ui()
    NewThread()
    sys.exit(app.exec_())
