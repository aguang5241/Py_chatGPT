from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtCore import QThread, pyqtSignal
from recorder_ui import Ui_MainWindow as RecorderUI
import pyaudio, time, struct

class Recorder(QThread):
    signal_frames = pyqtSignal(list)
    signal_detection = pyqtSignal(str)

    def __init__(self, parent=None, is_recording=None):
        super().__init__(parent)
        self.parent = parent
        self.is_recording = is_recording
        self.format = pyaudio.paInt16
        self.chunk = 1024
        self.channel = 1
        self.rate = 44100

    def run(self):
        frames = []
        p = pyaudio.PyAudio()
        stream = p.open(format=self.format,
                        channels=self.channel,
                        rate=self.rate,
                        input=True,
                        frames_per_buffer=self.chunk)
        i = 0
        while(self.is_recording):
            data = stream.read(self.chunk)
            data_int = struct.unpack(str(2*self.chunk) +'B', data)
            data_avg=sum(data_int)/len(data_int)
            frames.append(data)

            i += 1
            detection = 'i: ' + str(i) + ', avg: ' + str(data_avg)
            self.signal_detection.emit(detection)
        stream.stop_stream()
        stream.close()
        p.terminate()
        self.signal_frames.emit(frames)

    def stop(self):
        self.is_recording = False

class My_Recorder(QMainWindow):
    def __init__(self):
        super(My_Recorder, self).__init__()
        self.ui = RecorderUI()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.start_or_stop)
        self.is_recording = False

    def start_or_stop(self):
        if self.ui.pushButton.text() == 'Recording':
            # Stop recording
            self.is_recording = False
            self.recorder.stop()
            self.rec_end = time.time()
            self.ui.pushButton.setText('Speak')
            # Show the pushButton text in black
            self.ui.pushButton.setStyleSheet('color: black')
            self.ui.statusbar.showMessage('Recording stopped, record time: ' + str(round(self.rec_end - self.rec_begin, 2)) + 's')
        else:
            # Start recording
            self.is_recording = True
            self.rec_begin = time.time()
            self.ui.pushButton.setText('Recording')
            # Show the pushButton text in red
            self.ui.pushButton.setStyleSheet('color: red')
            self.ui.statusbar.showMessage('Recording started, press the button again to stop recording')

            self.recorder = Recorder(parent=None, is_recording=self.is_recording)
            # Using QThread to record the audio
            self.recorder.start()
            self.recorder.signal_frames.connect(self.speech_to_text)
            self.recorder.signal_detection.connect(self.detection)

    def speech_to_text(self, frames):
        self.frames = frames
        print('frames received: ', len(self.frames))
        
        # analyze the frames to see if there is any sound
        import numpy as np
        analysis = np.frombuffer(b''.join(self.frames), dtype=np.int16)
        
        self.ui.textBrowser.clear()
        self.ui.textBrowser.append(f"<p style='color:blue'>frame length: {len(self.frames)}</p>")
        self.ui.textBrowser.append(f"<p style='color:blue'>frame max: {analysis.max()}</p>")
        self.ui.textBrowser.append(f"<p style='color:blue'>frame min: {analysis.min()}</p>")
        self.ui.textBrowser.append(f"<p style='color:blue'>frame mean: {analysis.mean()}</p>")
        self.ui.textBrowser.append(f"<p style='color:blue'>frame std: {analysis.std()}</p>")

    def detection(self, detection):
        self.ui.statusbar.showMessage('Recording, detection: ' + detection)


if __name__ == '__main__':
    app = QApplication([])
    window = My_Recorder()
    window.show()
    app.exec_()



