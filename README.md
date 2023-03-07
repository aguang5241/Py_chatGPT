# Py_chatGPT
Python-based chatbot using chatGPT API, supporting both text-based and voice-based chatting.   

[***Bilibili***](https://www.bilibili.com/video/BV1554y1u75j/?share_source=copy_web&vd_source=52c5fec8348a24e00d38c36bc12b5a7d)     

[***YouTube***](https://youtu.be/H9Ss8RYrTw8)

## Introduction
1. ***Py_chatGPT_text.py***
* Communicate with the chatbot by typing.
* Can save/load the chat history.

2. ***Py_chatGPT_voice.py***
* Real-time communication with the chatbot by voice.
* Can save/load the chat history.
* Based on the Google Text-to-Speech API and the Whisper Speech-to-Text API.

## Getting Started
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
    python3 Py_chatGPT_voice.py
    ```
4. Enjoy!
