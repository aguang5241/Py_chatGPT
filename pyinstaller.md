
pyinstaller -F -w --add-data '/Users/aguang/Coding/Py_chatGPT/py_venv/lib/python3.9/site-packages/whisper/assets/gpt2/*.txt:./whisper/assets/gpt2' --add-data '/Users/aguang/Coding/Py_chatGPT/py_venv/lib/python3.9/site-packages/whisper/assets/gpt2/*json:./whisper/assets/gpt2' --add-data '/Users/aguang/Coding/Py_chatGPT/py_venv/lib/python3.9/site-packages/whisper/assets/multilingual/*json:./whisper/assets/multilingual' --add-data '/Users/aguang/Coding/Py_chatGPT/py_venv/lib/python3.9/site-packages/whisper/assets/multilingual/*txt:./whisper/assets/multilingual' --add-data '/Users/aguang/Coding/Py_chatGPT/py_venv/lib/python3.9/site-packages/whisper/assets/*npz:./whisper/assets' --copy-metadata 'tqdm' --copy-metadata 'regex' --copy-metadata 'requests' --copy-metadata 'packaging' --copy-metadata 'filelock' --copy-metadata 'numpy' --copy-metadata 'tokenizers' --copy-metadata 'torch' Super_Assistant.py

* `_run.pu`
```python
    # Absolute path to ffmpeg
    import os, sys
    current_path = os.path.dirname(sys.argv[0])
    if 'Contents' in current_path:
        root_path = current_path.split('/Contents')[0]
    else:
        root_path = os.path.join(current_path, 'Super_Assistant.app')
    ffmpeg_path = os.path.join(root_path, 'Contents', 'MacOS', 'ffmpeg')

    # root_path  = current_path
    # ffmpeg_path = os.path.join(root_path, 'ffmpeg')
    
    if args[0] == 'ffmpeg':
        args[0] = args[0].replace('ffmpeg', ffmpeg_path)
    print('AGUANG args: ', args)

    return subprocess.Popen(
        args, stdin=stdin_stream, stdout=stdout_stream, stderr=stderr_stream
    )
```