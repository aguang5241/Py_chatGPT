/Users/aguang/Library/Python/3.9/lib/python/site-packages
/Users/aguang/Library/Python/3.9/lib/python/site-packages/whisper/assets/multilingual/*.json

datas = [('/Users/aguang/Library/Python/3.9/lib/python/site-packages/whisper/assets/mel_filters.npz', './whisper/assets')]
python examples/pytorch/translation/run_translation.py --model_name_or_path t5-small --dataset_name wmt16 --dataset_config ro-en ...,

pyinstaller -F --add-binary "./ffmpeg:." Super_Assistant.py

/Users/aguang/Coding/Py_chatGPT/python_venv/lib/python3.9/site-packages/ffmpeg/_run.py
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