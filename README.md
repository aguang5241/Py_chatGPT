# Py_chatGPT
Python-based chatbot using chatGPT API, supporting both text-based and voice-based chatting.   

👉🏻 --- [***Bilibili***](https://www.bilibili.com/video/BV1654y1M7By/)   
👉🏻 --- [***Youtube***](https://youtu.be/iyeYOZbsM9c)  

## Software
Download the least version from the [***release page***](https://github.com/aguang5241/Py_chatGPT/releases), please STAR ⭐️ this repo if you like it.

* ***MacOS***   
<div align=left><img src='https://raw.githubusercontent.com/aguang5241/Py_chatGPT/main/res/interface_mac.png' alt='' width='700'/></div>   

* ***Windows***
<div align=left><img src='https://raw.githubusercontent.com/aguang5241/Py_chatGPT/main/res/interface_win.png' alt='' width='700'/></div>

👉🏻 ***Note:*** 
* If there is no sound, you may need to install the [***FLAC***](https://xiph.org/flac/download.html) command line tool and add it to the system path.

* For MacOS users:

    * If you cannot open the `Super_Assistant.app` file, you may need to do the following steps:
        1. After downloading the `Super_Assistant.app.zip` file, unzip it with `Unarchiver`. ***Note:*** Please do not use the `Archive Utility`, that will cause the `Super_Assistant.app` file to be damaged.
        2. The first time you run the `Super_Assistant.app` file, you may see the following error message `"Super_Assistant" cannot be opened`.
        3. Go to Terminal and run the following command:
        ```bash
        xattr -d com.apple.quarantine /path/to/Super_Assistant.app
        ```
        4. Then you can run the `Super_Assistant.app`.
        5. If you get the error message `FLAC conversion utility not available - consider installing the FLAC command line application by running apt-get install flac or your operating system's equivalent` when you are recording, you may download and use `Super_Assistant` Unix executable file instead.

    * If you cannot open the `Super_Assistant` Unix executable file, you may need to do the following steps:
        1. The first time you run the `Super_Assistant` Unix executable file, you may see the following error message `"Super_Assistant" cannot be opened because it is from an unidentified developer`. Go to `System Preferences -> Security & Privacy -> General -> Open Anyway`. After that you may see the following error message `macOS cannot verify the developer of “Super_Assistant”. Are you sure you want to open it?`, please click `Cancel`.
        2. Then go to Terminal and run the following command:
            ```bash
            chmod +x /path/to/Super_Assistant
            ```
        3. Then you can run the `Super_Assistant` Unix executable file.

## Source Code
### Introduction
* ***script/***
    * ***Py_chatGPT_text.py***
        * Communicate with the chatbot by typing.
        * Can save/load the chat history.

    * ***Py_chatGPT_voice_auto/mannual.py***
        * Real-time communication with the chatbot by voice.
        * Can save/load the chat history.
        * Based on the Google Text-to-Speech API and the Whisper Speech-to-Text API.
        * `Py_chatGPT_voice_auto.py` will automatically start and stop the recording based on the voice activity.
        * `Py_chatGPT_voice_manual.py` need user to manually start and stop the recording.

* ***software/***
    * ***Super_Assistant.py***
        * The main program of the software.
        * The GUI is based on the PyQt5 library.
        * The voice recognition is based on the Google Text-to-Speech and Speech-to-Text API.
        * The chatbot is based on the chatGPT API.
    * ***Super_Assitant_UI(_win).ui/py***
        * The UI files of the software and the converted python files for MacOS and Windows.
        * The UI is based on the Qt Designer.
    * ***Super_Assistant.md | Super_Assistant.spec***
        * The pyinstaller command file and the pyinstaller configuration file.
    

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
