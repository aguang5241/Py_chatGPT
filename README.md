# Py_chatGPT
Python-based chatbot using chatGPT API, supporting both text-based and voice-based chatting.   

[***Bilibili***](https://www.bilibili.com/video/BV1zs4y157am/?vd_source=99d1cb91e2f7dd90ccd34800244e2bb8)     

[***Youtube***](https://youtu.be/iyeYOZbsM9c)

## Software
Download the least version from the [***release page***](https://github.com/aguang5241/Py_chatGPT/releases), please STAR ⭐️ this repo if you like it.
* ***MacOS***   
<div align=left><img src='https://raw.githubusercontent.com/aguang5241/Py_chatGPT/main/res/interface_mac.png' alt='' width='700'/></div>   

* ***Windows***
<div align=left><img src='https://raw.githubusercontent.com/aguang5241/Py_chatGPT/main/res/interface_win.png' alt='' width='700'/></div>

👉🏻 ***Note:*** If there is no sound, you may need to install the [***FLAC***](https://xiph.org/flac/download.html) command line tool.   

## Source Code
### Introduction
1. ***Py_chatGPT_text.py***
* Communicate with the chatbot by typing.
* Can save/load the chat history.

2. ***Py_chatGPT_voice_auto.py***
* Will automatically start and stop the recording based on the voice activity.
* Real-time communication with the chatbot by voice.
* Can save/load the chat history.
* Based on the Google Text-to-Speech API and the Whisper Speech-to-Text API.

3. ***Py_chatGPT_voice_manual.py (Recommended)***
* Need to manually start and stop the recording.
* Real-time communication with the chatbot by voice.
* Can save/load the chat history.
* Based on the Google Text-to-Speech API and the Whisper Speech-to-Text API.

### Getting Started
1. Prepare your own chatGPT api key and save it in the `openai_api_key.txt` file
2. Install the dependencies
    ```bash
    pip install -r requirements.txt
    ```
3. Run the program you want
    ```bash
    python3 Py_chatGPT_text.py
    ``` 
    or
    ```bash
    python3 Py_chatGPT_voice_auto.py
    ```
    or
    ```bash
    python3 Py_chatGPT_voice_manual.py
    ```
4. Enjoy!

👉🏻 ***Note:*** the python version version I used is 3.9.6, different versions may have different results.
