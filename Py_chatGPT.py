
import openai
import os, sys, getopt


openai.api_key_path = os.path.join(os.path.dirname(__file__), 'openai_api_key.txt')

if os.path.exists('chatlog.txt'):
    os.remove('chatlog.txt')

while True:
    user = input('I: ')
    with open('chatlog.txt', 'a') as f:
        f.write('user: ' + user + '\n')

    messages = []
    with open('chatlog.txt', 'r') as f:
        content = f.readlines()
        content = [x.strip() for x in content]

    for line in content:
        if line.startswith('user'):
            messages.append({"role": "user", "content": line[5:]})
        elif line.startswith('assistant'):
            messages.append({"role": "assistant", "content": line[11:]})

    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    assistant = completion['choices'][0]['message']['content']
    with open('chatlog.txt', 'a') as f:
        f.write('assistant: ' + assistant + '\n')

    print('Assistant: ' + assistant)