from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtCore import QThread, pyqtSignal
from recorder_ui import Ui_MainWindow as RecorderUI
import pyaudio, time, struct, os, wave

class My_Recorder(QMainWindow):
    def __init__(self):
        super(My_Recorder, self).__init__()
        self.ui = RecorderUI()
        self.ui.setupUi(self)
        self.is_recording = False
        self.format = pyaudio.paInt16
        self.chunk = 1024
        self.channel = 1
        self.rate = 44100
        self.seconds = 5
        self.user_mp3 = '/Users/aguang/Coding/Py_chatGPT/recorder.mp3'
        self.ui.pushButton.clicked.connect(self.record)

    def record(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=self.format, channels=self.channel, rate=self.rate, input=True, frames_per_buffer=self.chunk)
        print('Recording...')

        frames = []
        for i in range(0, int(self.rate / self.chunk * self.seconds)):
            data = stream.read(self.chunk)
            frames.append(data)

            data_int = struct.unpack(str(2*self.chunk) +'B', data)
            data_avg=sum(data_int)/len(data_int)

            self.ui.statusbar.showMessage('i: ' + str(i) + ', avg: ' + str(data_avg))

        stream.stop_stream()
        stream.close()
        p.terminate()

        p = pyaudio.PyAudio()
        # Delete the existing .mp3 file
        if os.path.exists(self.user_mp3):
            # print('Deleting the existing user.mp3 file...')
            os.remove(self.user_mp3)
        wf = wave.open(self.user_mp3, 'wb')
        wf.setnchannels(self.channel)
        wf.setsampwidth(p.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(frames))
        wf.close()
        p.terminate()


if __name__ == '__main__':
    app = QApplication([])
    window = My_Recorder()
    window.show()
    app.exec_()



