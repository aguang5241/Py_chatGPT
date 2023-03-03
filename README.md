# Py_chatGPT
Python-based chatbot using chatGPT API, supporting both text-based and voice-based chatting.

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
