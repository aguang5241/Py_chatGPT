# Py_chatGPT
Python-based chatbot using chatGPT API, supporting both text-based and voice-based chatting.   

👉🏻 --- [***Youtube***](https://youtu.be/jsRzKgakH5g)  
👉🏻 --- [***Zhihu***](https://www.zhihu.com/zvideo/1619295745764544513)   
👉🏻 --- [***Bilibili***](https://www.bilibili.com/video/BV1654y1M7By/)   

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

## Source Code Introduction
* ***Py_chatGPT/***
    * ***Py_chatGPT_text.py***
        * Communicate with the chatbot by typing.
        * Can save/load the chat history.

    * ***Py_chatGPT_voice_auto/mannual.py***
        * Real-time communication with the chatbot by voice.
        * Can save/load the chat history.
        * Based on the Google Text-to-Speech API and the Whisper Speech-to-Text API.
        * `Py_chatGPT_voice_auto.py` will automatically start and stop the recording based on the voice activity.
        * `Py_chatGPT_voice_manual.py` need user to manually start and stop the recording.
    
    * ***openai_api_key.txt***
        * The chatGPT API key.
        * You can get your own chatGPT API key from [***here***](https://platform.openai.com).

    * ***requirements.txt***
        * The dependencies of the software.

    * ***Py_chatGPT.md***
        * Instructions for running the source code.

* ***Super_Assistant/***
    * ***Super_Assistant.py***
        * The main program of the software.
        * The GUI is based on the PyQt5 library.
        * The voice recognition is based on the Google Text-to-Speech and Speech-to-Text API.
        * The chatbot is based on the chatGPT API.
    * ***Super_Assitant_UI(_win).ui/py***
        * The UI files of the software and the converted python files for MacOS and Windows.
        * The UI is based on the Qt Designer.
    * ***Super_Assistant.md/spec***
        * The command line and the spec file for building the software using [***PyInstaller***](https://www.pyinstaller.org/)
