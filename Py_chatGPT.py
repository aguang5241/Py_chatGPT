import openai
import os, time

# Get current time and only keep the numbers
now = time.strftime('%H%M%S', time.localtime())

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

while True:
    user = input('User: ')
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