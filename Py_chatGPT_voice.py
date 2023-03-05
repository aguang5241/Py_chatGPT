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

# Recording the environment for 1 second to set the threshold
warning_message = 'Please remain silent for 5 second to allow the program to detect the environment volume.'
print('\033[91m' + warning_message + '\033[0m')
pa = pyaudio.PyAudio()
stream = pa.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
env = []
for i in range(0, int(RATE / CHUNK * 5)):
    data = stream.read(CHUNK)
    data_int = struct.unpack(str(2*CHUNK) +'B', data)
    avg_data=sum(data_int)/len(data_int)
    env.append(avg_data)
    # print the remain seconds and refresh using flush in red
    print('\033[91m' + 'Remaining: ' + str(int(5 - i / 43)) + ' seconds' + '\033[0m', end='\r', flush=True)

threshold = sum(env)/len(env) * 1.4
if threshold < 10.0:
    print('No voice detected. Please check your microphone.')
    exit()
else:
    # print('Environment volume: ' + str(threshold))
    pass

while True:
    # Start recording
    pa = pyaudio.PyAudio()
    stream = pa.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    print('Recording...')

    frames = []
    for i in range(0, int(RATE / CHUNK * INITIAL_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    i = 0
    while True:
        # Converting chunk data into integers
        data = stream.read(CHUNK)
        data_int = struct.unpack(str(2*CHUNK) +'B', data)
        # Finding average intensity per chunk
        avg_data=sum(data_int)/len(data_int)
        # print and refresh using flush
        # print('Speaking volume: ' + str(avg_data), end='\r', flush=True)
        # Recording chunk data
        frames.append(data)
        # if avg_data samller than THRESHOLD for TOLLERANCE times, stop recording
        if avg_data < threshold:
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
    tts = gTTS(assistant, lang=LANGUAGE)
    tts.save(assi_mp3)
    playsound(assi_mp3)