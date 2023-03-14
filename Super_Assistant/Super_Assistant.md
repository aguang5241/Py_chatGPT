## Pyinstaller command
* For Whispers
pyinstaller -F -w --add-data '/Users/aguang/Coding/Py_chatGPT/py_venv_whisper/lib/python3.9/site-packages/whisper/assets/gpt2/*.txt:./whisper/assets/gpt2' --add-data '/Users/aguang/Coding/Py_chatGPT/py_venv_whisper/lib/python3.9/site-packages/whisper/assets/gpt2/*json:./whisper/assets/gpt2' --add-data '/Users/aguang/Coding/Py_chatGPT/py_venv_whisper/lib/python3.9/site-packages/whisper/assets/multilingual/*json:./whisper/assets/multilingual' --add-data '/Users/aguang/Coding/Py_chatGPT/py_venv_whisper/lib/python3.9/site-packages/whisper/assets/multilingual/*txt:./whisper/assets/multilingual' --add-data '/Users/aguang/Coding/Py_chatGPT/py_venv_whisper/lib/python3.9/site-packages/whisper/assets/*npz:./whisper/assets' --copy-metadata 'tqdm' --copy-metadata 'regex' --copy-metadata 'requests' --copy-metadata 'packaging' --copy-metadata 'filelock' --copy-metadata 'numpy' --copy-metadata 'tokenizers' --copy-metadata 'torch' Super_Assistant.py

* For Google
pyinstaller -F -w Super_Assistant.py