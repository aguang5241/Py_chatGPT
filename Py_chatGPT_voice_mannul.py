import os, time
import openai
import wave
import struct
import whisper
import pyaudio
import threading
from gtts import gTTS
from pynput import keyboard
from playsound import playsound

class Recorder():
    def __init__(self, format, chunk, channels, rate):
        self.FORMAT = format
        self.CHUNK = chunk
        self.CHANNELS = channels
        self.RATE = rate
        self._running = False
        self._frames = []
        self.recBegin =0
        self.recTime =0  

    def start(self):
        print('\033[93m' + 'Start recording...' + '\033[0m')
        threading._start_new_thread(self.__record, ())
        self._running = True

    def __record(self):
        self.recBegin = time.time()
        self._frames = []

        p = pyaudio.PyAudio()
        stream = p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        frames_per_buffer=self.CHUNK)
        while(self._running):
            data = stream.read(self.CHUNK)
            self._frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

    def stop(self):
        self._running = False
        self.recTime = time.time() - self.recBegin
        print('\033[93m' + 'Stop recording... Record time: %d s' % self.recTime + '\033[0m')
        self.save(user_mp3)

    def save(self, fileName):   
        p = pyaudio.PyAudio()
        wf = wave.open(fileName, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self._frames))
        wf.close()
        p.terminate()

def on_keyPress(key):
    try:
        # press SPACE to start recording, press SPACE again to stop recording
        if key == keyboard.Key.space:
            if recorder._running:
                recorder.stop()
                return False
            else:
                recorder.start()
    except Exception as e: 
        print(e)
   
if __name__ == "__main__":
    # Format
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    INITIAL_SECONDS = 2
    TOLLERANCE = 100
    LANGUAGE = 'en'

    # Get current time and only keep the numbers
    now = time.strftime('%H%M%S', time.localtime())
    assi_mp3 = 'assistant.mp3'
    user_mp3 = 'user.mp3'

    # To choose if you want to continue a previous chat or start a new one
    while True:
        choice = input('Enter the name of the file you want to continue or enter "new" to start a new chat: ')
        if choice == 'new':
            chatlog = f'chatlog_{now}.txt'
            break
        elif os.path.isfile(choice):
            chatlog = choice
            break
        else:
            print('File does not exist. Please try again.')
    
    openai.api_key_path = os.path.join(os.path.dirname(__file__), 'openai_api_key.txt')

    greeting = 'Welcome to the chatGPT. How can I help you?'
    print('\033[94m' + 'Assistant: ' + greeting + '\033[0m')

    tts = gTTS('Welcome to the chatGPT. How can I help you?', lang=LANGUAGE, slow=False)
    tts.save(assi_mp3)
    playsound(assi_mp3)
    
    while True:
        print('\033[92m' + 'Press SPACE to start recording, press SPACE again to stop recording.' + '\033[0m')
        recorder = Recorder(format=FORMAT, chunk=CHUNK, channels=CHANNELS, rate=RATE)
        keyboard_listener = keyboard.Listener(on_press=on_keyPress)
        with keyboard_listener:
            keyboard_listener.join()
    
        # Speech to text
        model = whisper.load_model('base')
        result = model.transcribe(user_mp3, fp16=False)
        user = result['text']
        print(user)

        with open(chatlog, 'a') as f:
            f.write('user: ' + user + '\n')

        messages = []
        with open(chatlog, 'r') as f:
            content = f.readlines()
            content = [x.strip() for x in content]

        for line in content:
            if line.startswith('user'):
                messages.append({"role": "user", "content": line[5:]})
            elif line.startswith('assistant'):
                messages.append({"role": "assistant", "content": line[11:]})

        completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
        assistant = completion['choices'][0]['message']['content']
        with open(chatlog, 'a') as f:
            f.write('assistant: ' + assistant + '\n')

        # print assistant response in blue
        print('\033[94m' + 'Assistant: ' + assistant + '\033[0m')

        # Convert text to speech
        tts = gTTS(assistant, lang=LANGUAGE)
        tts.save(assi_mp3)
        playsound(assi_mp3)

