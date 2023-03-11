import os, sys, time
import openai
import wave
import speech_recognition as sr
import pyaudio
import threading
import webbrowser
from gtts import gTTS
from playsound import playsound
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtCore import QThread, pyqtSignal
from Super_Assistant_UI_win import Ui_MainWindow as Super_Assistant_UI


class Call_ChatGPT(QThread):
    signal_assistant = pyqtSignal(str)

    def __init__(self, parent=None, messages=None):
        super().__init__(parent)
        self.parent = parent
        self.messages = messages

    def run(self):
        try:
            completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=self.messages)
            # Get the assistant response
            assistant = completion['choices'][0]['message']['content']
            self.signal_assistant.emit(assistant)
        except Exception as e:
            self.signal_assistant.emit(str(e))

class Call_Speech_Recogizer(QThread):
    signal_user = pyqtSignal(str)

    def __init__(self, parent=None, user_mp3=None, language_code=None):
        super().__init__(parent)
        self.parent = parent
        self.user_mp3 = user_mp3
        self.language_code = language_code

    def run(self):
        r = sr.Recognizer()
        with sr.AudioFile(self.user_mp3) as source:
            audio = r.record(source)

        # Using Google Speech Recognition
        try:
            user = r.recognize_google(audio_data=audio, language=self.language_code)
        except Exception as e:
            user = str(e)

        # # Using Whisper Speech Recognition
        # try:
        #     user = r.recognize_whisper(audio_data=audio)
        # except Exception as e:
        #     user = ''

        self.signal_user.emit(user)

class Recorder():
    def __init__(self):
        self.format = pyaudio.paInt16
        self.chunk = 1024
        self.channel = 1
        self.rate = 44100
        self.frames = []
        self.running = False

        self.user_mp3 = ROOT_PATH + '/user.mp3'

    def start(self):
        threading._start_new_thread(self.record, ())
        self.running = True

    def record(self):
        self.frames = []
        p = pyaudio.PyAudio()
        stream = p.open(format=self.format,
                        channels=self.channel,
                        rate=self.rate,
                        input=True,
                        frames_per_buffer=self.chunk)
        while(self.running):
            data = stream.read(self.chunk)
            self.frames.append(data)
            # print('Recording...')
        stream.stop_stream()
        stream.close()
        p.terminate()

    def stop(self):
        self.running = False
        self.save(self.user_mp3)

    def save(self, fileName):
        p = pyaudio.PyAudio()
        wf = wave.open(fileName, 'wb')
        wf.setnchannels(self.channel)
        wf.setsampwidth(p.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        p.terminate()

class Super_Assistant(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Super_Assistant_UI()
        self.ui.setupUi(self)

        self.root_path = ROOT_PATH

        # self.ui.textBrowser.append(f"<p style='color:red'>Root path: {self.root_path}</p>")

        self.assi_mp3 = self.root_path + '/assi.mp3'
        self.user_mp3 = self.root_path + '/user.mp3'
        self.language_code = 'en'
        self.format = pyaudio.paInt16
        self.chunk = 1024
        self.channel = 1
        self.rate = 44100
        self.recorder = Recorder()
        self.languages_dict = {'Chinese': 'zh-CN', 
                               'English': 'en', 
                               'French': 'fr', 
                               'German': 'de', 
                               'Italian': 'it', 
                               'Japanese': 'ja', 
                               'Korean': 'ko', 
                               'Polish': 'pl', 
                               'Russian': 'ru', 
                               'Spanish': 'es', 
                               'Swedish': 'sv'}

        # Initialize the messages list
        self.messages = [{'role': 'user', 'content': 'From now on, your role is my Oral English Teacher. Please keep your responses as short as possible. And you should stop and correct me at any time once you find my grammar is wrong.'}, {'role': 'assistant', 'content': 'Yes.'}]
        
        # Set the API key path at the beginning
        default_api_key_path = os.path.join(self.root_path, '../openai_api_key.txt')
        if os.path.exists(default_api_key_path):
            self.api_key_path = default_api_key_path
            self.ui.statusbar.showMessage('API key file detected, ready to use...')
            self.ui.actionMy_API_Key.setText('My API Key: ' + self.api_key_path)
            openai.api_key_path = self.api_key_path
        else:
            self.ui.statusbar.showMessage('Please select the API key file path in the Settings menu...')
            self.ui.actionMy_API_Key.setText('Select...')

        # Set the API key path manually
        self.ui.actionMy_API_Key.triggered.connect(self.set_api_key_path)

        # Set audio on/off status
        self.audio_on = True
        self.ui.checkBox.stateChanged.connect(self.set_audio)

        # Set greeting in the textBrowser
        self.greeting = 'Welcome to the Super Assistant, I am powered by OpenAI GPT-3.5. My current role is your English Oral Teacher. How can I help you?'
        self.ui.textBrowser.append(f"<p style='color:blue'>Assistant:</p>")
        self.ui.textBrowser.append(f"<p style='color:blue'>{self.greeting}</p>")

        # Uncheck the others when one is checked in the menuRoles
        self.ui.actionAisearch.triggered.connect(self.uncheck_roles)
        self.ui.actionChatbot.triggered.connect(self.uncheck_roles)
        self.ui.actionOral_Teacher.triggered.connect(self.uncheck_roles)

        # Uncheck the others when one is checked in the menuLanguages
        self.ui.actionChinese.triggered.connect(self.uncheck_languages)
        self.ui.actionEnglish.triggered.connect(self.uncheck_languages)
        self.ui.actionFrench.triggered.connect(self.uncheck_languages)
        self.ui.actionGerman.triggered.connect(self.uncheck_languages)
        self.ui.actionItalian.triggered.connect(self.uncheck_languages)
        self.ui.actionJapanese.triggered.connect(self.uncheck_languages)
        self.ui.actionKorean.triggered.connect(self.uncheck_languages)
        self.ui.actionPolish.triggered.connect(self.uncheck_languages)
        self.ui.actionRussian.triggered.connect(self.uncheck_languages)
        self.ui.actionSpanish.triggered.connect(self.uncheck_languages)
        self.ui.actionSwedish.triggered.connect(self.uncheck_languages)

        # Set the language and enter the Oral Teacher mode
        self.ui.actionChinese.triggered.connect(self.set_language)
        self.ui.actionEnglish.triggered.connect(self.set_language)
        self.ui.actionFrench.triggered.connect(self.set_language)
        self.ui.actionGerman.triggered.connect(self.set_language)
        self.ui.actionItalian.triggered.connect(self.set_language)
        self.ui.actionJapanese.triggered.connect(self.set_language)
        self.ui.actionKorean.triggered.connect(self.set_language)
        self.ui.actionPolish.triggered.connect(self.set_language)
        self.ui.actionRussian.triggered.connect(self.set_language)
        self.ui.actionSpanish.triggered.connect(self.set_language)
        self.ui.actionSwedish.triggered.connect(self.set_language)

        # Enter the Chatbot mode
        self.ui.actionChatbot.triggered.connect(self.chatbot)

        # Enter the Aisearch mode
        self.ui.actionAisearch.triggered.connect(self.aisearch)

        # Visit my GitHub
        self.ui.actionGithub.triggered.connect(self.github)

        # Send me email in actionFeedback
        self.ui.actionFeedback.triggered.connect(self.feedback)

        # Get the text from the lineEdit by pressing Enter or clicking the pushButton_2
        self.ui.lineEdit.returnPressed.connect(self.get_text)
        self.ui.pushButton_2.clicked.connect(self.get_text)

        # Get the text by speaking
        self.ui.pushButton.clicked.connect(self.start_or_stop)

        # Save the chatlog to a txt file
        self.ui.actionSave.triggered.connect(self.save_chatlog)

        # Load the chatlog from a txt file
        self.ui.actionLoad.triggered.connect(self.load_chatlog)

    def uncheck_roles(self):
        checked_action = self.sender()
        for action in self.ui.menuRoles.actions():
            if action != checked_action:
                action.setChecked(False)
    
    def uncheck_languages(self):
        checked_action = self.sender()
        for action in self.ui.menuLanguages.actions():
            if action != checked_action:
                action.setChecked(False)

    def set_audio(self):
        if self.ui.checkBox.isChecked():
            self.audio_on = True
            self.ui.checkBox.setText('Audio On')
        else:
            self.audio_on = False
            self.ui.checkBox.setText('Audio Off')

    def set_language(self):
        # Set groupBox title to Oral Teacher
        self.ui.groupBox.setTitle('Role: Oral Teacher')
        # Set the language code
        checked_action = self.sender()
        language = checked_action.text()
        self.language_code = self.languages_dict[language]
        if self.language_code == 'en':
            self.greeting = f'Welcome to the Oral Teacher Mode. I will help you to improve your oral English. How can I help you?'
        elif self.language_code == 'zh-CN':
            self.greeting = f'欢迎来到口语教师模式。我将帮助您提高您的汉语口语。我能帮到您什么？'
        elif self.language_code == 'fr':
            self.greeting = f"Bienvenue dans le mode professeur d'expression orale. Je vais vous aider à améliorer votre français oral. Comment puis-je vous aider ?"
        elif self.language_code == 'de':
            self.greeting = f'Willkommen im Modus Mundlicher Lehrer. Ich werde Ihnen helfen, Ihr mündliches Deutsch zu verbessern. Wie kann ich Ihnen helfen?'
        elif self.language_code == 'it':
            self.greeting = f"Benvenuti nella modalità insegnante di conversazione. Ti aiuterò a migliorare il tuo italiano parlato. Come posso aiutarvi?"
        elif self.language_code == 'ja':
            self.greeting = f'口頭教師モードへようこそ。私はあなたの日本語の口頭を改善するのを手伝います。どうすればいいですか？'
        elif self.language_code == 'ko':
            self.greeting = f'반갑습니다. 저는 당신의 한국어의 말하기를 향상시키는 데 도움이 될 것입니다. 어떻게 도와드릴까요?'
        elif self.language_code == 'pl':
            self.greeting = f'Witamy w trybie nauczyciela mówienia. Pomogę Ci poprawić twoje mówienie po polsku. W czym mogę pomóc?'
        elif self.language_code == 'ru':
            self.greeting = f'Добро пожаловать в режим устного учителя. Я помогу вам улучшить ваше устное русское. Как я могу помочь?'
        elif self.language_code == 'es':
            self.greeting = f'Bienvenido al modo de profesor oral. Te ayudaré a mejorar tu español hablado. ¿Cómo puedo ayudarte?'
        elif self.language_code == 'sv':
            self.greeting = f'Välkommen till tallärarläget. Jag kommer att hjälpa dig att förbättra ditt talade svenska. Hur kan jag hjälpa dig?'
        # Set the greeting in the textBrowser
        self.ui.textBrowser.clear()
        self.ui.textBrowser.append(f"<p style='color:blue'>Assistant:</p>")
        self.ui.textBrowser.append(f"<p style='color:blue'>{self.greeting}</p>")
        # Initialize the messages list
        self.messages = [{'role': 'user', 'content': f'From now on, your role is my Oral {language} Teacher. Please keep your responses as short as possible. And you should stop and correct me at any time once you find my grammar is wrong.'}, {'role': 'assistant', 'content': 'Yes.'}]

        # Play the greeting audio in a new thread, end the existing thread if it is still running
        if self.audio_on:
            threading._start_new_thread(self.audio, (self.greeting, self.language_code))

    def audio(self, text, language_code):
        tts = gTTS(text, lang=language_code, slow=False)
        # Delete the old audio file
        if os.path.exists(self.assi_mp3):
            os.remove(self.assi_mp3)
            # print('Deleting the existing assi.mp3 file...')
        tts.save(self.assi_mp3)
        playsound(self.assi_mp3)

    def chatbot(self):
        # Initialize the messages list
        self.messages = [{'role': 'user', 'content': 'From now on, your role is my Chatbot. Please keep your responses as short as possible.'}, {'role': 'assistant', 'content': 'Yes.'}]
        # Set groupBox title to Chatbot
        self.ui.groupBox.setTitle('Role: Chatbot')
        # Set the greeting in the textBrowser
        if self.language_code == 'en':
            self.greeting = f'Welcome to the Chatbot Mode. How can I help you?'
        elif self.language_code == 'zh-CN':
            self.greeting = f'欢迎来到聊天机器人模式。我能帮到您什么？'
        elif self.language_code == 'fr':
            self.greeting = f"Bienvenue dans le mode chatbot. Comment puis-je vous aider ?"
        elif self.language_code == 'de':
            self.greeting = f'Willkommen im Chatbot-Modus. Wie kann ich Ihnen helfen?'
        elif self.language_code == 'it':
            self.greeting = f"Benvenuti nella modalità chatbot. Come posso aiutarvi?"
        elif self.language_code == 'ja':
            self.greeting = f'チャットボットモードへようこそ。どうすればいいですか？'
        elif self.language_code == 'ko':
            self.greeting = f'반갑습니다. 어떻게 도와드릴까요?'
        elif self.language_code == 'pl':
            self.greeting = f'Witamy w trybie chatbot. W czym mogę pomóc?'
        elif self.language_code == 'ru':
            self.greeting = f'Добро пожаловать в режим чат-бота. Как я могу помочь?'
        elif self.language_code == 'es':
            self.greeting = f'Bienvenido al modo chatbot. ¿Cómo puedo ayudarte?'
        elif self.language_code == 'sv':
            self.greeting = f'Välkommen till chattbotläget. Hur kan jag hjälpa dig?'
        self.ui.textBrowser.clear()
        self.ui.textBrowser.append(f"<p style='color:blue'>Assistant:</p>")
        self.ui.textBrowser.append(f"<p style='color:blue'>{self.greeting}</p>")
        # Play the greeting audio in a new thread, end the existing thread if it is still running
        if self.audio_on:
            threading._start_new_thread(self.audio, (self.greeting, self.language_code))
    
    def aisearch(self):
        # Initialize the messages list
        self.messages = [{'role': 'user', 'content': 'From now on, your role is my AI Search Engine. Please attach the supporting links to your responses.'}, {'role': 'assistant', 'content': 'Yes.'}]
        # Set groupBox title to Aisearch
        self.ui.groupBox.setTitle('Role: AI Search')
        # Set the greeting in the textBrowser
        if self.language_code == 'en':
            self.greeting = f'Welcome to the AI Search Mode. How can I help you?'
        elif self.language_code == 'zh-CN':
            self.greeting = f'欢迎来到AI搜索模式。我能帮到您什么？'
        elif self.language_code == 'fr':
            self.greeting = f'Bienvenue dans le mode de recherche AI. Comment puis-je vous aider ?'
        elif self.language_code == 'de':
            self.greeting = f'Willkommen im AI-Suchmodus. Wie kann ich Ihnen helfen?'
        elif self.language_code == 'it':
            self.greeting = f'Benvenuti nella modalità di ricerca AI. Come posso aiutarvi?'
        elif self.language_code == 'ja':
            self.greeting = f'AI検索モードへようこそ。どうすればいいですか？'
        elif self.language_code == 'ko':
            self.greeting = f'AI 검색 모드에 오신 것을 환영합니다. 어떻게 도와드릴까요?'
        elif self.language_code == 'pl':
            self.greeting = f'Witamy w trybie wyszukiwania AI. W czym mogę pomóc?'
        elif self.language_code == 'ru':
            self.greeting = f'Добро пожаловать в режим поиска AI. Как я могу помочь?'
        elif self.language_code == 'es':
            self.greeting = f'Bienvenido al modo de búsqueda AI. ¿Cómo puedo ayudarte?'
        elif self.language_code == 'sv':
            self.greeting = f'Välkommen till AI-sökläget. Hur kan jag hjälpa dig?'
        self.ui.textBrowser.clear()
        self.ui.textBrowser.append(f"<p style='color:blue'>Assistant:</p>")
        self.ui.textBrowser.append(f"<p style='color:blue'>{self.greeting}</p>")
        # Play the greeting audio in a new thread, end the existing thread if it is still running
        if self.audio_on:
            threading._start_new_thread(self.audio, (self.greeting, self.language_code))

    def set_api_key_path(self):
        # Open a file dialog to select the API key path using the QFileDialog
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.AnyFile)
        # file_dialog.setFilter(QFileDialog.Files)
        file_dialog.setNameFilter('Text files (*.txt)')
        file_dialog.setViewMode(QFileDialog.Detail)
        file_dialog.setAcceptMode(QFileDialog.AcceptOpen)
        file_dialog.setWindowTitle('Select the API key file')
        file_dialog.setLabelText(QFileDialog.Accept, 'Select')
        file_dialog.setLabelText(QFileDialog.Reject, 'Cancel')
        if file_dialog.exec_():
            # Get the API key path
            self.api_key_path = file_dialog.selectedFiles()[0]
            # Update the actionMy_API_Key text
            self.ui.actionMy_API_Key.setText('API Key Path: ' + self.api_key_path)
            # Update the statusbar
            self.ui.statusbar.showMessage('API key file detected, ready to use...')
            # Update the openai.api_key_path
            openai.api_key_path = self.api_key_path
    
    def github(self):
        webbrowser.open('https://github.com/aguang5241')

    def feedback(self):
        webbrowser.open('mailto:guangchen5241@gmail.com')

    def start_or_stop(self):
        if self.recorder.running:
            print('Stop recording')
            # Stop recording
            self.recorder.stop()
            self.rec_end = time.time()
            self.ui.pushButton.setText('Speak')
            # Show the pushButton text in black
            self.ui.pushButton.setStyleSheet('color: black')
            self.ui.statusbar.showMessage('Recording stopped, record time: ' + str(round(self.rec_end - self.rec_begin, 2)) + 's')
            # Using QThread to run self.set_text()
            self.call_speech_recognizer_thread = Call_Speech_Recogizer(parent=None, user_mp3=self.user_mp3, language_code=self.language_code)
            self.call_speech_recognizer_thread.start()
            self.call_speech_recognizer_thread.signal_user.connect(self.set_text)
        else:
            print('Start recording')
            # Start recording
            self.recorder.start()
            self.rec_begin = time.time()
            self.ui.pushButton.setText('Recording')
            self.ui.pushButton.setStyleSheet('color: red')
            self.ui.statusbar.showMessage('Recording started, press the button again to stop recording')

    def set_text(self, user):
        # Set the text in the lineEdit
        self.ui.lineEdit.setText(user)

    def get_text(self):
        text = self.ui.lineEdit.text()
        # print('text: ', text)
        # If there is no text or only spaces, do nothing and return
        if not text or text.isspace():
            return
        self.ui.lineEdit.clear()
        self.ui.textBrowser.append(f"<p style='color:black'>You:</p>")
        self.ui.textBrowser.append(f"<p style='color:black'>{text}</p>")
        # Scroll to the bottom of the textBrowser
        self.ui.textBrowser.verticalScrollBar().setValue(self.ui.textBrowser.verticalScrollBar().maximum())
        # Add the text to the messages list
        self.messages.append({"role": "user", "content": text})
        # print(self.messages)
        # Call self.send_text() in a new thread
        # threading._start_new_thread(self.send_text, ())

        # Using QThread to call self.send_text()
        self.call_chatgpt_thread = Call_ChatGPT(parent=None, messages=self.messages)
        self.call_chatgpt_thread.start()
        self.call_chatgpt_thread.signal_assistant.connect(self.send_text)

    def send_text(self, assistant):
        self.messages.append({"role": "assistant", "content": assistant})
        # print(self.messages)
        # Set the assistant response in the textBrowser
        self.ui.textBrowser.append(f"<p style='color:blue'>Assistant:</p>")
        self.ui.textBrowser.append(f"<p style='color:blue'>{assistant}</p>")
        # Scroll to the bottom of the textBrowser
        self.ui.textBrowser.verticalScrollBar().setValue(self.ui.textBrowser.verticalScrollBar().maximum())
        # Play the assistant audio in a new thread
        if self.audio_on:
            threading._start_new_thread(self.audio, (assistant, self.language_code))
    
    def save_chatlog(self):
        # Open a file dialog to select the save path using the QFileDialog
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.AnyFile)
        # file_dialog.setFilter(QFileDialog.Files)
        file_dialog.setNameFilter('Text files (*.txt)')
        file_dialog.setViewMode(QFileDialog.Detail)
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setWindowTitle('Select the save path')
        file_dialog.setLabelText(QFileDialog.Accept, 'Save')
        file_dialog.setLabelText(QFileDialog.Reject, 'Cancel')
        save_path = file_dialog.getSaveFileName(self, 'Save File', '', 'Text files (*.txt)')
        if save_path[0]:
            # Save the chatlog
            with open(save_path[0], 'w') as f:
                f.write(self.ui.textBrowser.toPlainText())
            # Update the statusbar
            self.ui.statusbar.showMessage('Chatlog saved in ' + save_path[0])
    
    def load_chatlog(self):
        # Open a file dialog to select the chatlog file using the QFileDialog
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter('Text files (*.txt)')
        file_dialog.setViewMode(QFileDialog.Detail)
        file_dialog.setAcceptMode(QFileDialog.AcceptOpen)
        file_dialog.setWindowTitle('Select the chatlog file')
        file_dialog.setLabelText(QFileDialog.Accept, 'Select')
        file_dialog.setLabelText(QFileDialog.Reject, 'Cancel')
        chatlog_path = file_dialog.getOpenFileName(self, 'Open File', '', 'Text files (*.txt)')
        if chatlog_path[0]:
            # Load the chatlog
            with open(chatlog_path[0], 'r') as f:
                content = f.readlines()
                content = [x.strip() for x in content]
            for line in content:
                if line.startswith('You:'):
                    self.messages.append({"role": "user", "content": line[4:]})
                elif line.startswith('Assistant:'):
                    self.messages.append({"role": "assistant", "content": line[11:]})
            self.ui.statusbar.showMessage(f'Chatlog {chatlog_path[0]} loaded, ready to continue the conversation')

if __name__ == '__main__':
    ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

    app = QApplication(sys.argv)
    window = Super_Assistant()
    window.show()
    sys.exit(app.exec_())
