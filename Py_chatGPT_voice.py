import os, time
import openai
import pyaudio
import wave
import struct
import whisper
from gtts import gTTS
from playsound import playsound

# Format
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44400
INITIAL_SECONDS = 2
THRESHOLD = 100
TOLLERANCE = 50

# Get current time and only keep the numbers
now = time.strftime('%H%M%S', time.localtime())
assi_mp3 = f'assistant_{now}.mp3'
user_mp3 = f'user_{now}.mp3'

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

tts = gTTS('Welcome to the chatGPT. How can I help you?', lang='en', slow=False)
tts.save(assi_mp3)
playsound(assi_mp3)

while True:
    # Start recording
    pa = pyaudio.PyAudio()
    stream = pa.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    print('Recording...')

    frames = []
    seconds = INITIAL_SECONDS
    for i in range(0, int(RATE / CHUNK * seconds)):
        data = stream.read(CHUNK)
        frames.append(data)

    i = 0
    while True:
        # Converting chunk data into integers
        data = stream.read(CHUNK)
        data_int = struct.unpack(str(2*CHUNK) +'B', data)
        # Finding average intensity per chunk
        avg_data=sum(data_int)/len(data_int)
        # print(str(avg_data))
        # Recording chunk data
        frames.append(data)
        # if avg_data samller than THRESHOLD for TOLLERANCE times, stop recording
        if avg_data < THRESHOLD:
            i += 1
            if i > TOLLERANCE:
                break

    stream.stop_stream()
    stream.close()
    pa.terminate()

    sf = wave.open(user_mp3, 'wb')
    sf.setnchannels(CHANNELS)
    sf.setsampwidth(pa.get_sample_size(FORMAT))
    sf.setframerate(RATE)
    sf.writeframes(b''.join(frames))
    sf.close()

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
    tts = gTTS(assistant, lang='en')
    tts.save(assi_mp3)
    playsound(assi_mp3)