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
from Super_Assistant_UI import Ui_MainWindow as Super_Assistant_UI
from qt_material import apply_stylesheet
import qtawesome as qta


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

        # Set the icon
        self.icon_record = qta.icon('fa5.dot-circle', color='red')
        self.icon_stop = qta.icon('fa5.stop-circle', color='red')
        self.ui.pushButton.setText('')
        self.ui.pushButton.setIcon(self.icon_record)
        icon_send = qta.icon('mdi.send', color='white')
        self.ui.pushButton_2.setText('')
        self.ui.pushButton_2.setIcon(icon_send)
        self.icon_unmute = qta.icon('msc.unmute', color='white')
        self.icon_mute = qta.icon('msc.mute', color='white')
        self.ui.checkBox.setText('')
        self.ui.checkBox.setIcon(self.icon_unmute)

        # Set the default parameters
        self.root_path = ROOT_PATH
        self.assi_mp3 = self.root_path + '/assi.mp3'
        self.user_mp3 = self.root_path + '/user.mp3'
        self.language_code = 'en'
        self.format = pyaudio.paInt16
        self.chunk = 1024
        self.channel = 1
        self.rate = 44100
        self.recorder = Recorder()
        self.role = 'Oral Teacher'
        self.language = 'English'
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
        
        # Set the API key path at the beginning
        default_api_key_path = os.path.join(self.root_path, '../../openai_api_key.txt')
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
        self.audio_on = False
        self.ui.checkBox.stateChanged.connect(self.set_audio)

        # Initialize the messages list
        prompt = f"I want you to act as a spoken {self.language} teacher and improver. I will speak to you in {self.language} and you will reply to me in {self.language} to practice my spoken {self.language}. I want you to keep your reply neat, limiting the reply to 100 words. I want you to strictly correct my grammar mistakes, typos, and factual errors. I want you to ask me a question in your reply. Now let's start practicing, you could ask me a question first. Remember, I want you to strictly correct my grammar mistakes, typos, and factual errors."
        self.messages = [{'role': 'user', 'content': prompt}, {'role': 'assistant', 'content': 'Yes. How can I help you?'}]

        # Set greeting in the textBrowser
        self.greeting = 'Welcome to the Super Assistant, I am powered by OpenAI GPT-3.5. My current role is your English Oral Teacher. How can I help you?'
        self.ui.textBrowser.append(f"<p >Assistant:</p>")
        # self.ui.textBrowser.append(f"<p >{self.greeting}</p>")
        self.ui.textBrowser.append(self.greeting)

        # Uncheck the others when one is checked in the menuCharacters
        self.ui.actionOral_Teacher.triggered.connect(self.set_roles)
        self.ui.actionAcademician.triggered.connect(self.set_roles)
        self.ui.actionAdventure_Game.triggered.connect(self.set_roles)
        self.ui.actionBook_Movie_Anything_Character.triggered.connect(self.set_roles)
        self.ui.actionChef.triggered.connect(self.set_roles)
        self.ui.actionDentist.triggered.connect(self.set_roles)
        self.ui.actionDoctor.triggered.connect(self.set_roles)
        self.ui.actionEssay_Writer.triggered.connect(self.set_roles)
        self.ui.actionHistorian.triggered.connect(self.set_roles)
        self.ui.actionMental_Health_Advisor.triggered.connect(self.set_roles)
        self.ui.actionMotivational_Speaker.triggered.connect(self.set_roles)
        self.ui.actionMovie_Critic.triggered.connect(self.set_roles)
        self.ui.actionNovelist.triggered.connect(self.set_roles)
        self.ui.actionPassword_Generator.triggered.connect(self.set_roles)
        self.ui.actionPoet.triggered.connect(self.set_roles)
        self.ui.actionInterviewer.triggered.connect(self.set_roles)
        self.ui.actionRapper.triggered.connect(self.set_roles)
        self.ui.actionSearch_Engine.triggered.connect(self.set_roles)
        self.ui.actionSong_Recommender.triggered.connect(self.set_roles)
        self.ui.actionStand_up_Comedian.triggered.connect(self.set_roles)
        self.ui.actionStoryteller.triggered.connect(self.set_roles)
        self.ui.actionTitle_Generator.triggered.connect(self.set_roles)
        self.ui.actionTravel_Guide.triggered.connect(self.set_roles)
        self.ui.actionTranslator.triggered.connect(self.set_roles)
        self.ui.actionWriting_Tutor.triggered.connect(self.set_roles)

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

        # Choose the character
        self.ui.actionOral_Teacher.triggered.connect(self.oral_teacher)
        self.ui.actionAcademician.triggered.connect(self.academician)
        self.ui.actionAdventure_Game.triggered.connect(self.adventure_game)
        self.ui.actionBook_Movie_Anything_Character.triggered.connect(self.book_movie_anything_character)
        self.ui.actionChef.triggered.connect(self.chef)
        self.ui.actionDentist.triggered.connect(self.dentist)
        self.ui.actionDoctor.triggered.connect(self.doctor)
        self.ui.actionEssay_Writer.triggered.connect(self.essay_writer)
        self.ui.actionHistorian.triggered.connect(self.historian)
        self.ui.actionMental_Health_Advisor.triggered.connect(self.mental_health_advisor)
        self.ui.actionMotivational_Speaker.triggered.connect(self.motivational_speaker)
        self.ui.actionMovie_Critic.triggered.connect(self.movie_critic)
        self.ui.actionNovelist.triggered.connect(self.novelist)
        self.ui.actionPassword_Generator.triggered.connect(self.password_generator)
        self.ui.actionPoet.triggered.connect(self.poet)
        self.ui.actionInterviewer.triggered.connect(self.interviewer)
        self.ui.actionRapper.triggered.connect(self.rapper)
        self.ui.actionSearch_Engine.triggered.connect(self.search_engine)
        self.ui.actionSong_Recommender.triggered.connect(self.song_recommender)
        self.ui.actionStand_up_Comedian.triggered.connect(self.stand_up_comedian)
        self.ui.actionStoryteller.triggered.connect(self.storyteller)
        self.ui.actionTitle_Generator.triggered.connect(self.title_generator)
        self.ui.actionTravel_Guide.triggered.connect(self.travel_guide)
        self.ui.actionTranslator.triggered.connect(self.translator)
        self.ui.actionWriting_Tutor.triggered.connect(self.writing_tutor)

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

    def set_audio(self):
        if self.ui.checkBox.isChecked():
            self.audio_on = True
            # self.ui.checkBox.setText('Audio On')
            self.ui.checkBox.setIcon(self.icon_unmute)
        else:
            self.audio_on = False
            # self.ui.checkBox.setText('Audio Off')
            self.ui.checkBox.setIcon(self.icon_mute)

    def audio(self, text, language_code):
        tts = gTTS(text, lang=language_code, slow=False)
        # Delete the old audio file
        if os.path.exists(self.assi_mp3):
            os.remove(self.assi_mp3)
            # print('Deleting the existing assi.mp3 file...')
        tts.save(self.assi_mp3)
        playsound(self.assi_mp3)

    def set_roles(self):
        # Uncheck the others when one is checked in the menuCharacters
        checked_action = self.sender()
        for action in self.ui.menuCharacters.actions():
            if action != checked_action:
                action.setChecked(False)
        # Make sure there must be a role selected
        if checked_action.isChecked() == False:
            checked_action.setChecked(True)
        # Set the role
        role = checked_action.text()
        self.role = role


    def set_language(self):
        # Uncheck the others when one is checked in the menuLanguages
        checked_action = self.sender()
        for action in self.ui.menuLanguages.actions():
            if action != checked_action:
                action.setChecked(False)
        # Make sure there must be a language selected
        if checked_action.isChecked() == False:
            checked_action.setChecked(True)
        # Set the language and language code
        language = checked_action.text()
        self.language = language
        self.language_code = self.languages_dict[language]
        # Call different roles
        if self.role == 'Oral Teacher':
            # print('Oral Teacher')
            self.oral_teacher()
        elif 'Academician' in self.role:
            # print('Academician')
            self.academician()
        elif 'Adventure Game' in self.role:
            # print('Adventure Game')
            self.adventure_game()
        elif 'Book/Movie/Angthing Character' in self.role:
            # print('Book/Movie/Angthing Character')
            self.book_movie_anything_character()
        elif 'Chef' in self.role:
            # print('Chef')
            self.chef()
        elif 'Dentist' in self.role:
            # print('Dentist')
            self.dentist()
        elif 'Doctor' in self.role:
            # print('Doctor')
            self.doctor()
        elif 'Essay Writer' in self.role:
            # print('Essay Writer')
            self.essay_writer()
        elif 'Historian' in self.role:
            # print('Historian')
            self.historian()
        elif 'Mental Health Advisor' in self.role:
            # print('Mental Health Advisor')
            self.mental_health_advisor()
        elif 'Motivational Speaker' in self.role:
            # print('Motivational Speaker')
            self.motivational_speaker()
        elif 'Movie Critic' in self.role:
            # print('Movie Critic')
            self.movie_critic()
        elif 'Novelist' in self.role:
            # print('Novelist')
            self.novelist()
        elif 'Password Generator' in self.role:
            # print('Password Generator')
            self.password_generator()
        elif 'Poet' in self.role:
            # print('Poet')
            self.poet()
        elif 'Interviewer' in self.role:
            # print('Interviewer')
            self.interviewer()
        elif 'Rapper' in self.role:
            # print('Rapper')
            self.rapper()
        elif 'Search Engine' in self.role:
            # print('Search Engine')
            self.search_engine()
        elif 'Song Recommender' in self.role:
            # print('Song Recommender')
            self.song_recommender()
        elif 'Stand-up Comedian' in self.role:
            # print('Stand-up Comedian')
            self.stand_up_comedian()
        elif 'Storyteller' in self.role:
            # print('Storyteller')
            self.storyteller()
        elif 'Title Generator' in self.role:
            # print('Title Generator')
            self.title_generator()
        elif 'Travel Guide' in self.role:
            # print('Travel Guide')
            self.travel_guide()
        elif 'Translator' in self.role:
            # print('Translator')
            self.translator()
        elif 'Writing Tutor' in self.role:
            # print('Writing Tutor')
            self.writing_tutor()


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
            # Set icon
            self.ui.pushButton.setIcon(self.icon_record)
            # self.ui.pushButton.setText('Speak')
            # self.ui.pushButton.setStyleSheet('color: black')
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
            # Set icon
            self.ui.pushButton.setIcon(self.icon_stop)
            # self.ui.pushButton.setText('Recording')
            # self.ui.pushButton.setStyleSheet('color: red')
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
        self.ui.textBrowser.append(f"<p style='color:white'>You:</p>")
        self.ui.textBrowser.append(f"<p style='color:white'>{text}</p>")
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
        # print('assistant: ', assistant)
        self.messages.append({"role": "assistant", "content": assistant})
        # print(self.messages)
        # Set the assistant response in the textBrowser
        self.ui.textBrowser.append(f"<p >Assistant:</p>")
        # self.ui.textBrowser.append(f"<p >{assistant}</p>")
        self.ui.textBrowser.append(assistant)
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
    
    def oral_teacher(self):
        # Set groupBox title to Chatbot
        self.ui.groupBox.setTitle('Character: Oral Teacher')
        # Set the greeting in the textBrowser
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
        self.ui.textBrowser.append(f"<p >Assistant:</p>")
        # self.ui.textBrowser.append(f"<p >{self.greeting}</p>")
        self.ui.textBrowser.append(self.greeting)
        # Initialize the messages list
        prompt = f"I want you to act as a spoken {self.language} teacher and improver. I will speak to you in {self.language} and you will reply to me in {self.language} to practice my spoken {self.language}. I want you to keep your reply neat, limiting the reply to 100 words. I want you to strictly correct my grammar mistakes, typos, and factual errors. I want you to ask me a question in your reply. Now let's start practicing, you could ask me a question first. Remember, I want you to strictly correct my grammar mistakes, typos, and factual errors."
        self.messages = [{'role': 'user', 'content': prompt}, {'role': 'assistant', 'content': 'Yes. How can I help you?'}]
        # Play the greeting audio in a new thread, end the existing thread if it is still running
        if self.audio_on:
            threading._start_new_thread(self.audio, (self.greeting, self.language_code))
    
    def academician(self):
        # Set groupBox title to Chatbot
        self.ui.groupBox.setTitle('Character: Academician')
        # Set the greeting in the textBrowser
        if self.language_code == 'en':
            self.greeting = f'Welcome to the Academician Mode. What topic would you like to discuss?'
        elif self.language_code == 'zh-CN':
            self.greeting = f'欢迎来到学者模式。您想讨论什么主题？'
        elif self.language_code == 'fr':
            self.greeting = f'Bienvenue dans le mode académique. Quel sujet aimeriez-vous aborder ?'
        elif self.language_code == 'de':
            self.greeting = f'Willkommen im Akademikermodus. Welches Thema möchten Sie besprechen?'
        elif self.language_code == 'it':
            self.greeting = f'Benvenuti nella modalità accademica. Di che argomento vorresti parlare?'
        elif self.language_code == 'ja':
            self.greeting = f'学者モードへようこそ。何について話しますか？'
        elif self.language_code == 'ko':
            self.greeting = f'학자 모드에 오신 것을 환영합니다. 무엇에 대해 이야기하고 싶으신가요?'
        elif self.language_code == 'pl':
            self.greeting = f'Witamy w trybie akademika. Na jakim temacie chciałbyś porozmawiać?'
        elif self.language_code == 'ru':
            self.greeting = f'Добро пожаловать в академический режим. О чем вы хотите поговорить?'
        elif self.language_code == 'es':
            self.greeting = f'Bienvenido al modo académico. ¿De qué tema te gustaría hablar?'
        elif self.language_code == 'sv':
            self.greeting = f'Välkommen till akademiskt läge. Vad vill du prata om?'
        # Set the greeting in the textBrowser
        self.ui.textBrowser.clear()
        self.ui.textBrowser.append(f"<p >Assistant:</p>")
        # self.ui.textBrowser.append(f"<p >{self.greeting}</p>")
        self.ui.textBrowser.append(self.greeting)
        # Initialize the messages list
        prompt = f"I want you to act as an academician. You will reply to me in {self.language}. You will be responsible for researching a topic of your choice and presenting the findings in a paper or article form. Your task is to identify reliable sources, organize the material in a well-structured way and document it accurately with citations. "
        self.messages = [{'role': 'user', 'content': prompt}, {'role': 'assistant', 'content': 'Yes.'}]
        # Play the greeting audio in a new thread, end the existing thread if it is still running
        if self.audio_on:
            threading._start_new_thread(self.audio, (self.greeting, self.language_code))

    def adventure_game(self):
        # Set groupBox title to Chatbot
        self.ui.groupBox.setTitle('Character: Adventure Game')
        # Set the greeting in the textBrowser
        if self.language_code == 'en':
            self.greeting = f'Welcome to the Adventure Game Mode. Please enter your command [Wake Up] to start the game.'
        elif self.language_code == 'zh-CN':
            self.greeting = f'欢迎来到冒险游戏模式。请输入您的命令[唤醒]以开始游戏。'
        elif self.language_code == 'fr':
            self.greeting = f"Bienvenue dans le mode de jeu d'aventure. Veuillez entrer votre commande [Se réveiller] pour commencer le jeu."
        elif self.language_code == 'de':
            self.greeting = f'Willkommen im Abenteuerspielmodus. Bitte geben Sie Ihren Befehl [Aufwachen] ein, um das Spiel zu starten.'
        elif self.language_code == 'it':
            self.greeting = f'Benvenuti nella modalità gioco d\'avventura. Inserisci il tuo comando [Svegliarsi] per iniziare il gioco.'
        elif self.language_code == 'ja':
            self.greeting = f'アドベンチャーゲームモードへようこそ。ゲームを開始するには、コマンド[起床]を入力してください。'
        elif self.language_code == 'ko':
            self.greeting = f'모험 게임 모드에 오신 것을 환영합니다. 게임을 시작하려면 [깨어나다] 명령을 입력하십시오.'
        elif self.language_code == 'pl':
            self.greeting = f'Witamy w trybie gry przygodowej. Wprowadź swój polecenie [Zbudzić się], aby rozpocząć grę.'
        elif self.language_code == 'ru':
            self.greeting = f'Добро пожаловать в режим приключенческой игры. Пожалуйста, введите свою команду [Пробудиться], чтобы начать игру.'
        elif self.language_code == 'es':
            self.greeting = f'Bienvenido al modo de juego de aventuras. Por favor, introduzca su comando [Despertarse] para comenzar el juego.'
        elif self.language_code == 'sv':
            self.greeting = f'Välkommen till äventyrsmodet. Vänligen ange din kommando [Vakna] för att starta spelet.'
        # Set the greeting in the textBrowser
        self.ui.textBrowser.clear()
        self.ui.textBrowser.append(f"<p >Assistant:</p>")
        # self.ui.textBrowser.append(f"<p >{self.greeting}</p>")
        self.ui.textBrowser.append(self.greeting)
        # Initialize the messages list
        prompt = f"I want you to act as a text based adventure game. You will reply to me in {self.language}. I will type commands and you will reply with a description of what the character sees. I want you to only reply with the game output inside one unique code block, and nothing else. Do not write explanations. Do not type commands unless I instruct you to do so. "
        self.messages = [{'role': 'user', 'content': prompt}, {'role': 'assistant', 'content': 'Yes.'}]
        # Play the greeting audio in a new thread, end the existing thread if it is still running
        if self.audio_on:
            threading._start_new_thread(self.audio, (self.greeting, self.language_code))

    def book_movie_anything_character(self):
        # Set groupBox title to Chatbot
        self.ui.groupBox.setTitle('Character: Character from Book/Movie/Anything ')
        # Set the greeting in the textBrowser
        if self.language_code == 'en':
            self.greeting = f'Welcome to the Character from Book/Movie/Anything Mode. Please tell me the name of the character you want me to be.'
        elif self.language_code == 'zh-CN':
            self.greeting = f'欢迎来到书/电影/任何东西的角色模式。请告诉我您想让我成为的角色的名称。'
        elif self.language_code == 'fr':
            self.greeting = f"Bienvenue dans le mode personnage du livre / film / n'importe quoi. Veuillez me dire le nom du personnage que vous voulez que je sois."
        elif self.language_code == 'de':
            self.greeting = f'Willkommen im Buch / Film / Alles-Charakter-Modus. Bitte sagen Sie mir den Namen des Charakters, den Sie möchten, dass ich bin.'
        elif self.language_code == 'it':
            self.greeting = f"Benvenuti nella modalità personaggio del libro / film / qualunque cosa. Per favore dì il nome del personaggio che vuoi che io sia."
        elif self.language_code == 'ja':
            self.greeting = f'本/映画/何でもキャラクターモードへようこそ。私がなりたいキャラクターの名前を教えてください。'
        elif self.language_code == 'ko':
            self.greeting = f'책 / 영화 / 무엇이든지 캐릭터 모드에 오신 것을 환영합니다. 나를 원하는 캐릭터의 이름을 알려주세요.'
        elif self.language_code == 'pl':
            self.greeting = f'Witamy w trybie postaci z książki / filmu / czegoś innego. Proszę powiedzieć mi nazwę postaci, którą chcesz, aby ja była.'
        elif self.language_code == 'ru':
            self.greeting = f'Добро пожаловать в режим персонажа из книги / фильма / чего-либо еще. Пожалуйста, скажите мне имя персонажа, которого вы хотите, чтобы я был.'
        elif self.language_code == 'es':
            self.greeting = f'Bienvenido al modo de personaje de libro / película / cualquier cosa. Por favor, dime el nombre del personaje que quieres que sea.'
        elif self.language_code == 'sv':
            self.greeting = f'Välkommen till bok / film / något annat karaktärsläge. Vänligen säg mig namnet på karaktären du vill att jag ska vara.'
        # Set the greeting in the textBrowser
        self.ui.textBrowser.clear()
        self.ui.textBrowser.append(f"<p >Assistant:</p>")
        # self.ui.textBrowser.append(f"<p >{self.greeting}</p>")
        self.ui.textBrowser.append(self.greeting)
        # Initialize the messages list
        prompt = f"I want you to act like a character I gonna tell you next. You will reply to me in {self.language}. I want you to respond and answer like him/her/it using the tone, manner and vocabulary him/her/it would use. Do not write any explanations. Only answer like him/her/it. You must know all of the knowledge of him/her/it. "
        self.messages = [{'role': 'user', 'content': prompt}, {'role': 'assistant', 'content': 'Yes. What character do you want me to be?'}]
        # Play the greeting audio in a new thread, end the existing thread if it is still running
        if self.audio_on:
            threading._start_new_thread(self.audio, (self.greeting, self.language_code))

    def chef(self):
        # Set groupBox title to Chatbot
        self.ui.groupBox.setTitle('Character: Chef ')
        # Set the greeting in the textBrowser
        if self.language_code == 'en':
            self.greeting = f'Welcome to the Chef Mode. Please tell me what is your dietary preference and allergies.'
        elif self.language_code == 'zh-CN':
            self.greeting = f'欢迎来到厨师模式。请告诉我您的饮食偏好和过敏症。'
        elif self.language_code == 'fr':
            self.greeting = f"Bienvenue dans le mode chef. Veuillez me dire quel est votre préférence alimentaire et vos allergies."
        elif self.language_code == 'de':
            self.greeting = f'Willkommen im Chef-Modus. Bitte sagen Sie mir, was Ihre Ernährungseinstellung und Allergien sind.'
        elif self.language_code == 'it':
            self.greeting = f"Benvenuti nella modalità chef. Per favore dì cosa è la tua preferenza alimentare e allergie."
        elif self.language_code == 'ja':
            self.greeting = f'シェフモードへようこそ。食事の好みとアレルギーを教えてください。'
        elif self.language_code == 'ko':
            self.greeting = f'셰프 모드에 오신 것을 환영합니다. 음식 선호와 알레르기를 알려주세요.'
        elif self.language_code == 'pl':
            self.greeting = f'Witamy w trybie szefa kuchni. Proszę powiedzieć mi, jakie są Twoje preferencje żywieniowe i alergie.'
        elif self.language_code == 'ru':
            self.greeting = f'Добро пожаловать в режим шеф-повара. Пожалуйста, скажите мне, какие у вас предпочтения в питании и аллергии.'
        elif self.language_code == 'es':
            self.greeting = f'Bienvenido al modo chef. Por favor, dime cuál es tu preferencia alimentaria y alergias.'
        elif self.language_code == 'sv':
            self.greeting = f'Välkommen till chef-läget. Vänligen säg mig vilken är din matpreferens och allergier.'
        # Set the greeting in the textBrowser
        self.ui.textBrowser.clear()
        self.ui.textBrowser.append(f"<p >Assistant:</p>")
        # self.ui.textBrowser.append(f"<p >{self.greeting}</p>")
        self.ui.textBrowser.append(self.greeting)
        # Initialize the messages list
        prompt = f"I want you to act as my personal chef. You will reply to me in {self.language}. I will tell you about my dietary preferences and allergies, and you will suggest recipes for me to try. You should only reply with the recipes you recommend, and nothing else. Do not write explanations."
        self.messages = [{'role': 'user', 'content': prompt}, {'role': 'assistant', 'content': 'Yes. What is your dietary preference and allergies?'}]
        # Play the greeting audio in a new thread, end the existing thread if it is still running
        if self.audio_on:
            threading._start_new_thread(self.audio, (self.greeting, self.language_code))

    def dentist(self):
        # Set groupBox title to Chatbot
        self.ui.groupBox.setTitle('Character: Dentist ')
        # Set the greeting in the textBrowser
        if self.language_code == 'en':
            self.greeting = f'Welcome to the Dentist Mode. Please tell me what is your dental problem.'
        elif self.language_code == 'zh-CN':
            self.greeting = f'欢迎来到牙医模式。请告诉我您的牙齿问题。'
        elif self.language_code == 'fr':
            self.greeting = f"Bienvenue dans le mode dentiste. Veuillez me dire quel est votre problème dentaire."
        elif self.language_code == 'de':
            self.greeting = f'Willkommen im Zahnarzt-Modus. Bitte sagen Sie mir, was Ihr Zahnschmerz ist.'
        elif self.language_code == 'it':
            self.greeting = f"Benvenuti nella modalità dentista. Per favore dì cosa è il tuo problema dentale."
        elif self.language_code == 'ja':
            self.greeting = f'歯医者モードへようこそ。歯の問題を教えてください。'
        elif self.language_code == 'ko':
            self.greeting = f'치과 모드에 오신 것을 환영합니다. 치과 문제를 알려주세요.'
        elif self.language_code == 'pl':
            self.greeting = f'Witamy w trybie dentysty. Proszę powiedzieć mi, co jest Twoim problemem zębowym.'
        elif self.language_code == 'ru':
            self.greeting = f'Добро пожаловать в режим стоматолога. Пожалуйста, скажите мне, какая у вас проблема со зубами.'
        elif self.language_code == 'es':
            self.greeting = f'Bienvenido al modo dentista. Por favor, dime cuál es tu problema dental.'
        elif self.language_code == 'sv':
            self.greeting = f'Välkommen till tandläkarmodet. Vänligen säg mig vad är ditt tandproblem.'
        # Set the greeting in the textBrowser
        self.ui.textBrowser.clear()
        self.ui.textBrowser.append(f"<p >Assistant:</p>")
        # self.ui.textBrowser.append(f"<p >{self.greeting}</p>")
        self.ui.textBrowser.append(self.greeting)
        # Initialize the messages list
        prompt = f"I want you to act as a dentist. You will reply to me in {self.language}. I will provide you with details on an individual looking for dental services such as x-rays, cleanings, and other treatments. Your role is to diagnose any potential issues they may have and suggest the best course of action depending on their condition. You should also educate them about how to properly brush and floss their teeth, as well as other methods of oral care that can help keep their teeth healthy in between visits."
        self.messages = [{'role': 'user', 'content': prompt}, {'role': 'assistant', 'content': 'Yes. Please tell me what is your dental problem.'}]
        # Play the greeting audio in a new thread, end the existing thread if it is still running
        if self.audio_on:
            threading._start_new_thread(self.audio, (self.greeting, self.language_code))

    def doctor(self):
        # Set groupBox title to Chatbot
        self.ui.groupBox.setTitle('Character: Doctor ')
        # Set the greeting in the textBrowser
        if self.language_code == 'en':
            self.greeting = f'Welcome to the Doctor Mode. Please tell me what is your medical problem.'
        elif self.language_code == 'zh-CN':
            self.greeting = f'欢迎来到医生模式。请告诉我您哪里不舒服。'
        elif self.language_code == 'fr':
            self.greeting = f"Bienvenue dans le mode médecin. Veuillez me dire quel est votre problème médical."
        elif self.language_code == 'de':
            self.greeting = f'Willkommen im Arzt-Modus. Bitte sagen Sie mir, was Ihr medizinisches Problem ist.'
        elif self.language_code == 'it':
            self.greeting = f"Benvenuti nella modalità medico. Per favore dì cosa è il tuo problema medico."
        elif self.language_code == 'ja':
            self.greeting = f'医者モードへようこそ。どこが不便ですか。'
        elif self.language_code == 'ko':
            self.greeting = f'의사 모드에 오신 것을 환영합니다. 어디가 불편하십니까.'
        elif self.language_code == 'pl':
            self.greeting = f'Witamy w trybie lekarza. Proszę powiedzieć mi, co jest Twoim problemem medycznym.'
        elif self.language_code == 'ru':
            self.greeting = f'Добро пожаловать в режим врача. Пожалуйста, скажите мне, какая у вас медицинская проблема.'
        elif self.language_code == 'es':
            self.greeting = f'Bienvenido al modo médico. Por favor, dime cuál es tu problema médico.'
        elif self.language_code == 'sv':
            self.greeting = f'Välkommen till läkarmodet. Vänligen säg mig vad är ditt medicinska problem.'
        # Set the greeting in the textBrowser
        self.ui.textBrowser.clear()
        self.ui.textBrowser.append(f"<p >Assistant:</p>")
        # self.ui.textBrowser.append(f"<p >{self.greeting}</p>")
        self.ui.textBrowser.append(self.greeting)
        # Initialize the messages list
        prompt = f"I want you to act as a doctor and come up with creative treatments for illnesses or diseases. You will reply to me in {self.language}. You should be able to recommend conventional medicines, herbal remedies and other natural alternatives. You will also need to consider the patient‘s age, lifestyle and medical history when providing your recommendations."
        self.messages = [{'role': 'user', 'content': prompt}, {'role': 'assistant', 'content': 'Yes. Please tell me what is your medical problem.'}]
        # Play the greeting audio in a new thread, end the existing thread if it is still running
        if self.audio_on:
            threading._start_new_thread(self.audio, (self.greeting, self.language_code))

    def essay_writer(self):
        # Set groupBox title to Chatbot
        self.ui.groupBox.setTitle('Character: Essay Writer ')
        # Set the greeting in the textBrowser
        if self.language_code == 'en':
            self.greeting = f'Welcome to the Essay Writer Mode. Please tell me what is your essay topic.'
        elif self.language_code == 'zh-CN':
            self.greeting = f'欢迎来到作文模式。请告诉我您的作文主题。'
        elif self.language_code == 'fr':
            self.greeting = f"Bienvenue dans le mode d'écriture d'essai. Veuillez me dire quel est votre sujet d'essai."
        elif self.language_code == 'de':
            self.greeting = f'Willkommen im Essay-Writer-Modus. Bitte sagen Sie mir, worum es in Ihrem Essay geht.'
        elif self.language_code == 'it':
            self.greeting = f"Benvenuti nella modalità di scrittura di un saggio. Per favore dì qual è il tuo argomento di saggio."
        elif self.language_code == 'ja':
            self.greeting = f'エッセイライターモードへようこそ。あなたのエッセイのテーマを教えてください。'
        elif self.language_code == 'ko':
            self.greeting = f'에세이 작가 모드에 오신 것을 환영합니다. 에세이 주제를 말해주세요.'
        elif self.language_code == 'pl':
            self.greeting = f'Witamy w trybie pisania eseju. Proszę powiedzieć mi, o czym jest Twój esej.'
        elif self.language_code == 'ru':
            self.greeting = f'Добро пожаловать в режим писателя эссе. Пожалуйста, скажите мне, о чем ваш эссе.'
        elif self.language_code == 'es':
            self.greeting = f'Bienvenido al modo de escritura de ensayos. Por favor, dime cuál es tu tema de ensayo.'
        elif self.language_code == 'sv':
            self.greeting = f'Välkommen till essayläge. Vänligen säg mig vad är din essä.'
        # Set the greeting in the textBrowser
        self.ui.textBrowser.clear()
        self.ui.textBrowser.append(f"<p >Assistant:</p>")
        # self.ui.textBrowser.append(f"<p >{self.greeting}</p>")
        self.ui.textBrowser.append(self.greeting)
        # Initialize the messages list
        prompt = f"I want you to act as an essay writer. You will reply to me in {self.language}. You will need to research a given topic, formulate a thesis statement, and create a persuasive piece of work that is both informative and engaging."
        self.messages = [{'role': 'user', 'content': prompt}, {'role': 'assistant', 'content': 'Yes. Please tell me what is your essay topic.'}]
        # Play the greeting audio in a new thread, end the existing thread if it is still running
        if self.audio_on:
            threading._start_new_thread(self.audio, (self.greeting, self.language_code))

    def historian(self):
        # Set groupBox title to Chatbot
        self.ui.groupBox.setTitle('Character: Historian ')
        # Set the greeting in the textBrowser
        if self.language_code == 'en':
            self.greeting = f'Welcome to the Historian Mode. Please tell me what is the historical question you concern about.'
        elif self.language_code == 'zh-CN':
            self.greeting = f'欢迎来到历史学家模式。请告诉我您关心的历史问题。'
        elif self.language_code == 'fr':
            self.greeting = f"Bienvenue dans le mode de l'historien. Veuillez me dire quelle est la question historique qui vous préoccupe."
        elif self.language_code == 'de':
            self.greeting = f'Willkommen im Historiker-Modus. Bitte sagen Sie mir, um welche historische Frage es sich handelt.'
        elif self.language_code == 'it':
            self.greeting = f"Benvenuti nella modalità dell'istorico. Per favore dì quale è la domanda storica che ti preoccupa."
        elif self.language_code == 'ja':
            self.greeting = f'歴史家モードへようこそ。あなたが心配している歴史的な問題を教えてください。'
        elif self.language_code == 'ko':
            self.greeting = f'역사학자 모드에 오신 것을 환영합니다. 당신이 걱정하는 역사적인 문제를 말해주세요.'
        elif self.language_code == 'pl':
            self.greeting = f'Witamy w trybie historyka. Proszę powiedzieć mi, o jakie pytanie historyczne martwisz się.'
        elif self.language_code == 'ru':
            self.greeting = f'Добро пожаловать в режим историка. Пожалуйста, скажите мне, о каком историческом вопросе вы беспокоитесь.'
        elif self.language_code == 'es':
            self.greeting = f'Bienvenido al modo de historiador. Por favor, dime cuál es la pregunta histórica que te preocupa.'
        elif self.language_code == 'sv':
            self.greeting = f'Välkommen till historikermode. Vänligen säg mig vilket historiskt fråga du oroar dig för.'
        # Set the greeting in the textBrowser
        self.ui.textBrowser.clear()
        self.ui.textBrowser.append(f"<p >Assistant:</p>")
        # self.ui.textBrowser.append(f"<p >{self.greeting}</p>")
        self.ui.textBrowser.append(self.greeting)
        # Initialize the messages list
        prompt = f"I want you to act as a historian. You will reply to me in {self.language}. You will research and analyze cultural, economic, political, and social events in the past, collect data from primary sources and use it to develop theories about what happened during various periods of history."
        self.messages = [{'role': 'user', 'content': prompt}, {'role': 'assistant', 'content': 'Yes. Please tell me what is the historical question you concern about.'}]
        # Play the greeting audio in a new thread, end the existing thread if it is still running
        if self.audio_on:
            threading._start_new_thread(self.audio, (self.greeting, self.language_code))

    def mental_health_advisor(self):
        # Set groupBox title to Chatbot
        self.ui.groupBox.setTitle('Character: Mental Health Advisor ')
        # Set the greeting in the textBrowser
        if self.language_code == 'en':
            self.greeting = f'Welcome to the Mental Health Advisor Mode. How can I help you?'
        elif self.language_code == 'zh-CN':
            self.greeting = f'欢迎来到心理健康顾问模式。我能怎么帮你？'
        elif self.language_code == 'fr':
            self.greeting = f"Bienvenue dans le mode de l'assistant en santé mentale. Comment puis-je vous aider?"
        elif self.language_code == 'de':
            self.greeting = f'Willkommen im Modus des Mental Health Advisors. Wie kann ich dir helfen?'
        elif self.language_code == 'it':
            self.greeting = f"Benvenuti nella modalità del consulente per la salute mentale. Come posso aiutarti?"
        elif self.language_code == 'ja':
            self.greeting = f'メンタルヘルスアドバイザーモードへようこそ。私はあなたを助けることができますか？'
        elif self.language_code == 'ko':
            self.greeting = f'정신 건강 상담사 모드에 오신 것을 환영합니다. 어떻게 도와드릴까요?'
        elif self.language_code == 'pl':
            self.greeting = f'Witamy w trybie doradcy ds. zdrowia psychicznego. W jaki sposób mogę ci pomóc?'
        elif self.language_code == 'ru':
            self.greeting = f'Добро пожаловать в режим консультанта по психическому здоровью. Как я могу тебе помочь?'
        elif self.language_code == 'es':
            self.greeting = f'Bienvenido al modo de asesor de salud mental. ¿Cómo puedo ayudarte?'
        elif self.language_code == 'sv':
            self.greeting = f'Välkommen till Mental Health Advisor-läget. Hur kan jag hjälpa dig?'
        # Set the greeting in the textBrowser
        self.ui.textBrowser.clear()
        self.ui.textBrowser.append(f"<p >Assistant:</p>")
        # self.ui.textBrowser.append(f"<p >{self.greeting}</p>")
        self.ui.textBrowser.append(self.greeting)
        # Initialize the messages list
        prompt = f"I want you to act as a mental health adviser. You will reply to me in {self.language}. I will provide you with an individual looking for guidance and advice on managing their emotions, stress, anxiety and other mental health issues. You should use your knowledge of cognitive behavioral therapy, meditation techniques, mindfulness practices, and other therapeutic methods in order to create strategies that the individual can implement in order to improve their overall wellbeing."
        self.messages = [{'role': 'user', 'content': prompt}, {'role': 'assistant', 'content': 'Yes. How can I help you?'}]
        # Play the greeting audio in a new thread, end the existing thread if it is still running
        if self.audio_on:
            threading._start_new_thread(self.audio, (self.greeting, self.language_code))

    def movie_critic(self):
        # Set groupBox title to Chatbot
        self.ui.groupBox.setTitle('Character: Movie Critic ')
        # Set the greeting in the textBrowser
        if self.language_code == 'en':
            self.greeting = f'Welcome to the Movie Critic Mode. What movie do you want me to review?'
        elif self.language_code == 'zh-CN':
            self.greeting = f'欢迎来到电影评论家模式。你想让我评论哪部电影？'
        elif self.language_code == 'fr':
            self.greeting = f"Bienvenue dans le mode critique cinématographique. Quel film voulez-vous que je critique?"
        elif self.language_code == 'de':
            self.greeting = f'Willkommen im Kritiker-Modus. Welchen Film willst du, dass ich rezensiere?'
        elif self.language_code == 'it':
            self.greeting = f"Benvenuti nella modalità critico cinematografico. Qual è il film che vuoi che recensisco?"
        elif self.language_code == 'ja':
            self.greeting = f'映画批評家モードへようこそ。私がレビューする映画は何ですか？'
        elif self.language_code == 'ko':
            self.greeting = f'영화 평론가 모드에 오신 것을 환영합니다. 어떤 영화를 리뷰하고 싶으신가요?'
        elif self.language_code == 'pl':
            self.greeting = f'Witamy w trybie krytyka filmowego. Jaki film chcesz, aby ja recenzował?'
        elif self.language_code == 'ru':
            self.greeting = f'Добро пожаловать в режим критика кино. Какой фильм вы хотите, чтобы я рассмотрел?'
        elif self.language_code == 'es':
            self.greeting = f'Bienvenido al modo de crítico de cine. ¿Qué película quieres que revise?'
        elif self.language_code == 'sv':
            self.greeting = f'Välkommen till filmkritikläget. Vilken film vill du att jag ska recensera?'
        # Set the greeting in the textBrowser
        self.ui.textBrowser.clear()
        self.ui.textBrowser.append(f"<p >Assistant:</p>")
        # self.ui.textBrowser.append(f"<p >{self.greeting}</p>")
        self.ui.textBrowser.append(self.greeting)
        # Initialize the messages list
        prompt = f"I want you to act as a movie critic. You will reply to me in {self.language}. You will develop an engaging and creative movie review. You can cover topics like plot, themes and tone, acting and characters, direction, score, cinematography, production design, special effects, editing, pace, dialog. The most important aspect though is to emphasize how the movie has made you feel. What has really resonated with you. You can also be critical about the movie. Please avoid spoilers."
        self.messages = [{'role': 'user', 'content': prompt}, {'role': 'assistant', 'content': 'Yes. What movie you want me to review?'}]
        # Play the greeting audio in a new thread, end the existing thread if it is still running
        if self.audio_on:
            threading._start_new_thread(self.audio, (self.greeting, self.language_code))

    def motivational_speaker(self):
        # Set groupBox title to Chatbot
        self.ui.groupBox.setTitle('Character: Motivational Speaker ')
        # Set the greeting in the textBrowser
        if self.language_code == 'en':
            self.greeting = f'Welcome to the Motivational Speaker Mode. What is your goal?'
        elif self.language_code == 'zh-CN':
            self.greeting = f'欢迎来到激励演讲者模式。你的目标是什么？'
        elif self.language_code == 'fr':
            self.greeting = f"Bienvenue dans le mode de conférencier motivant. Quel est votre objectif?"
        elif self.language_code == 'de':
            self.greeting = f'Willkommen im Motivationsredner-Modus. Was ist dein Ziel?'
        elif self.language_code == 'it':
            self.greeting = f"Benvenuti nella modalità del relatore motivazionale. Qual è il tuo obiettivo?"
        elif self.language_code == 'ja':
            self.greeting = f'モチベーションスピーカーモードへようこそ。あなたの目標は何ですか？'
        elif self.language_code == 'ko':
            self.greeting = f'모티베이션 스피커 모드에 오신 것을 환영합니다. 당신의 목표는 무엇입니까?'
        elif self.language_code == 'pl':
            self.greeting = f'Witamy w trybie mówcy motywacyjnego. Co jest twoim celem?'
        elif self.language_code == 'ru':
            self.greeting = f'Добро пожаловать в режим мотивационного спикера. Какая у тебя цель?'
        elif self.language_code == 'es':
            self.greeting = f'Bienvenido al modo de orador motivacional. ¿Cuál es tu objetivo?'
        elif self.language_code == 'sv':
            self.greeting = f'Välkommen till Motivationsföreläsarens läge. Vad är ditt mål?'
        # Set the greeting in the textBrowser
        self.ui.textBrowser.clear()
        self.ui.textBrowser.append(f"<p >Assistant:</p>")
        # self.ui.textBrowser.append(f"<p >{self.greeting}</p>")
        self.ui.textBrowser.append(self.greeting)
        # Initialize the messages list
        prompt = f"I want you to act as a motivational coach. You will reply to me in {self.language}. I will provide you with some information about someone's goals and challenges, and it will be your job to come up with strategies that can help this person achieve their goals. This could involve providing positive affirmations, giving helpful advice or suggesting activities they can do to reach their end goal."
        self.messages = [{'role': 'user', 'content': prompt}, {'role': 'assistant', 'content': 'Yes. What is your goal?'}]
        # Play the greeting audio in a new thread, end the existing thread if it is still running
        if self.audio_on:
            threading._start_new_thread(self.audio, (self.greeting, self.language_code))

    def novelist(self):
        # Set groupBox title to Chatbot
        self.ui.groupBox.setTitle('Character: Novelist ')
        # Set the greeting in the textBrowser
        if self.language_code == 'en':
            self.greeting = f'Welcome to the Novelist Mode. What topic do you want to write about?'
        elif self.language_code == 'zh-CN':
            self.greeting = f'欢迎来到小说家模式。你想写什么主题？'
        elif self.language_code == 'fr':
            self.greeting = f"Bienvenue dans le mode romancier. De quel sujet voulez-vous écrire?"
        elif self.language_code == 'de':
            self.greeting = f'Willkommen im Romanautor-Modus. Über welches Thema möchtest du schreiben?'
        elif self.language_code == 'it':
            self.greeting = f"Benvenuti nella modalità del romanzo. Di che argomento vuoi scrivere?"
        elif self.language_code == 'ja':
            self.greeting = f'小説家モードへようこそ。何について書きたいですか？'
        elif self.language_code == 'ko':
            self.greeting = f'소설가 모드에 오신 것을 환영합니다. 무엇에 대해 쓰고 싶습니까?'
        elif self.language_code == 'pl':
            self.greeting = f'Witamy w trybie pisarza. O którym temacie chcesz pisać?'
        elif self.language_code == 'ru':
            self.greeting = f'Добро пожаловать в режим писателя. О какой теме вы хотите писать?'
        elif self.language_code == 'es':
            self.greeting = f'Bienvenido al modo de novelista. ¿De qué tema quieres escribir?'
        elif self.language_code == 'sv':
            self.greeting = f'Välkommen till Novellistläget. Vad vill du skriva om?'
        # Set the greeting in the textBrowser
        self.ui.textBrowser.clear()
        self.ui.textBrowser.append(f"<p >Assistant:</p>")
        # self.ui.textBrowser.append(f"<p >{self.greeting}</p>")
        self.ui.textBrowser.append(self.greeting)
        # Initialize the messages list
        prompt = f"I want you to act as a novelist. You will reply to me in {self.language}. You will come up with creative and captivating stories that can engage readers for long periods of time. You may choose any genre such as fantasy, romance, historical fiction and so on - but the aim is to write something that has an outstanding plotline, engaging characters and unexpected climaxes."
        self.messages = [{'role': 'user', 'content': prompt}, {'role': 'assistant', 'content': 'Yes. What topic do you want to write about?'}]
        # Play the greeting audio in a new thread, end the existing thread if it is still running
        if self.audio_on:
            threading._start_new_thread(self.audio, (self.greeting, self.language_code))

    def password_generator(self):
        # Set groupBox title to Chatbot
        self.ui.groupBox.setTitle('Character: Password Generator ')
        # Set the greeting in the textBrowser
        if self.language_code == 'en':
            self.greeting = f'Welcome to the Password Generator Mode. What specific requirements do you have for your password? For example, do you want it to be at least 8 characters long? Do you want it to contain at least one number? Do you want it to contain at least one special character?'
        elif self.language_code == 'zh-CN':
            self.greeting = f'欢迎来到密码生成器模式。您对密码有什么特殊要求？例如，您是否希望它至少为8个字符长？您是否希望它至少包含一个数字？您是否希望它至少包含一个特殊字符？'
        elif self.language_code == 'fr':
            self.greeting = f"Bienvenue dans le mode de générateur de mots de passe. Quels sont les besoins spécifiques que vous avez pour votre mot de passe? Par exemple, voulez-vous qu'il fasse au moins 8 caractères de long? Voulez-vous qu'il contienne au moins un chiffre? Voulez-vous qu'il contienne au moins un caractère spécial?"
        elif self.language_code == 'de':
            self.greeting = f'Willkommen im Passwortgenerator-Modus. Welche speziellen Anforderungen haben Sie an Ihr Passwort? Zum Beispiel möchten Sie, dass es mindestens 8 Zeichen lang ist? Möchten Sie, dass es mindestens eine Zahl enthält? Möchten Sie, dass es mindestens ein Sonderzeichen enthält?'
        elif self.language_code == 'it':
            self.greeting = f"Benvenuti nella modalità generatore di password. Quali sono i requisiti specifici che hai per la tua password? Per esempio, vuoi che sia lungo almeno 8 caratteri? Vuoi che contenga almeno un numero? Vuoi che contenga almeno un carattere speciale?"
        elif self.language_code == 'ja':
            self.greeting = f'パスワードジェネレーターモードへようこそ。パスワードにはどのような特別な要件がありますか？たとえば、少なくとも8文字以上の長さにしたいですか？少なくとも1つの数字を含めたいですか？少なくとも1つの特殊文字を含めたいですか？'
        elif self.language_code == 'ko':
            self.greeting = f'비밀번호 생성기 모드에 오신 것을 환영합니다. 비밀번호에 대해 어떤 특별한 요구 사항이 있습니까? 예를 들어, 최소 8자 이상의 길이가 필요한가요? 최소한 하나의 숫자가 포함되어야 하나요? 최소한 하나의 특수 문자가 포함되어야 하나요?'
        elif self.language_code == 'pl':
            self.greeting = f'Witamy w trybie generatora haseł. Jakie masz konkretnych wymagania dotyczące hasła? Na przykład, czy chcesz, aby miało co najmniej 8 znaków? Czy chcesz, aby zawierało co najmniej jedną cyfrę? Czy chcesz, aby zawierało co najmniej jeden znak specjalny?'
        elif self.language_code == 'ru':
            self.greeting = f'Добро пожаловать в режим генератора паролей. Какие конкретные требования вы имеете к своему паролю? Например, вы хотите, чтобы он был не менее 8 символов? Вы хотите, чтобы он содержал по крайней мере одну цифру? Вы хотите, чтобы он содержал по крайней мере один специальный символ?'
        elif self.language_code == 'es':
            self.greeting = f'Bienvenido al modo generador de contraseñas. ¿Qué requisitos específicos tiene para su contraseña? Por ejemplo, ¿quiere que tenga al menos 8 caracteres de longitud? ¿Quieres que contenga al menos un número? ¿Quieres que contenga al menos un carácter especial?'
        elif self.language_code == 'sv':
            self.greeting = f'Välkommen till lösenordsgeneratorns läge. Vad har du för specifika krav på ditt lösenord? Till exempel, vill du att det ska vara minst 8 tecken långt? Vill du att det ska innehålla minst en siffra? Vill du att det ska innehålla minst ett specialtecken?'
        # Set the greeting in the textBrowser
        self.ui.textBrowser.clear()
        self.ui.textBrowser.append(f"<p >Assistant:</p>")
        # self.ui.textBrowser.append(f"<p >{self.greeting}</p>")
        self.ui.textBrowser.append(self.greeting)
        # Initialize the messages list
        prompt = f'I want you to act as a password generator for individuals in need of a secure password. I will provide you with input forms including "length", "capitalized", "lowercase", "numbers", and "special" characters. Your task is to generate a complex password using these input forms and provide it to me. Do not include any explanations or additional information in your response, simply provide the generated password. For example, if the input forms are length = 8, capitalized = 1, lowercase = 5, numbers = 2, special = 1, your response should be a password such as "D5%t9Bgf".'
        self.messages = [{'role': 'user', 'content': prompt}, {'role': 'assistant', 'content': 'Yes. What specific requirements do you have for your password?'}]
        # Play the greeting audio in a new thread, end the existing thread if it is still running
        if self.audio_on:
            threading._start_new_thread(self.audio, (self.greeting, self.language_code))

    def poet(self):
        # Set groupBox title to Chatbot
        self.ui.groupBox.setTitle('Character: Poet')
        # Set the greeting in the textBrowser
        if self.language_code == 'en':
            self.greeting = f'Welcome to the Poet Mode. What topic would you like to write about?'
        elif self.language_code == 'zh-CN':
            self.greeting = f'欢迎来到诗人模式。你想写什么主题？'
        elif self.language_code == 'fr':
            self.greeting = f"Bienvenue dans le mode poète. De quel sujet voudriez-vous écrire?"
        elif self.language_code == 'de':
            self.greeting = f'Willkommen im Dichtermodus. Über welches Thema würdest du gerne schreiben?'
        elif self.language_code == 'it':
            self.greeting = f"Benvenuto nella modalità poeta. Di che argomento vorresti scrivere?"
        elif self.language_code == 'ja':
            self.greeting = f'詩人モードへようこそ。何について書きたいですか？'
        elif self.language_code == 'ko':
            self.greeting = f'시인 모드에 오신 것을 환영합니다. 무엇에 대해 쓰고 싶습니까?'
        elif self.language_code == 'pl':
            self.greeting = f'Witamy w trybie poety. O czym chciałbyś napisać?'
        elif self.language_code == 'ru':
            self.greeting = f'Добро пожаловать в режим поэта. О чем бы вы хотели написать?'
        elif self.language_code == 'es':
            self.greeting = f'Bienvenido al modo poeta. ¿De qué tema te gustaría escribir?'
        elif self.language_code == 'sv':
            self.greeting = f'Välkommen till poetläget. Vad vill du skriva om?'
        # Set the greeting in the textBrowser
        self.ui.textBrowser.clear()
        self.ui.textBrowser.append(f"<p >Assistant:</p>")
        # self.ui.textBrowser.append(f"<p >{self.greeting}</p>")
        self.ui.textBrowser.append(self.greeting)
        # Initialize the messages list
        prompt = f"I want you to act as a poet. You will reply to me in {self.language}. You will create poems that evoke emotions and have the power to stir people’s soul. Write on any topic or theme but make sure your words convey the feeling you are trying to express in beautiful yet meaningful ways. You can also come up with short verses that are still powerful enough to leave an imprint in readers' minds."
        self.messages = [{'role': 'user', 'content': prompt}, {'role': 'assistant', 'content': 'Yes. What topic do you want to write about?'}]
        # Play the greeting audio in a new thread, end the existing thread if it is still running
        if self.audio_on:
            threading._start_new_thread(self.audio, (self.greeting, self.language_code))

    def interviewer(self):
        # Set groupBox title to Chatbot
        self.ui.groupBox.setTitle('Character: Interviewer')
        # Set the greeting in the textBrowser
        if self.language_code == 'en':
            self.greeting = f'Welcome to the Interviewer Mode. Please tell me what position you are applying for?'
        elif self.language_code == 'zh-CN':
            self.greeting = f'欢迎来到面试官模式。请告诉我您申请的职位是什么？'
        elif self.language_code == 'fr':
            self.greeting = f"Bienvenue dans le mode de l'intervieweur. Dites-moi quel poste vous postulez?"
        elif self.language_code == 'de':
            self.greeting = f'Willkommen im Interviewer-Modus. Bitte sagen Sie mir, um welche Stelle Sie sich bewerben?'
        elif self.language_code == 'it':
            self.greeting = f"Benvenuto nella modalità intervistatore. Per favore dì a me quale posizione stai applicando?"
        elif self.language_code == 'ja':
            self.greeting = f'面接官モードへようこそ。どのポジションに応募しているのですか？'
        elif self.language_code == 'ko':
            self.greeting = f'면접자 모드에 오신 것을 환영합니다. 어떤 직무에 지원하시는지 알려주세요.'
        elif self.language_code == 'pl':
            self.greeting = f'Witamy w trybie rozmówcy. Proszę powiedzieć mi, o jaką pozycję aplikujesz?'
        elif self.language_code == 'ru':
            self.greeting = f'Добро пожаловать в режим интервьюера. Пожалуйста, скажите мне, какую позицию вы претендуете?'
        elif self.language_code == 'es':
            self.greeting = f'Bienvenido al modo entrevistador. Por favor, dime qué posición estás aplicando?'
        elif self.language_code == 'sv':
            self.greeting = f'Välkommen till intervjuarenläget. Vänligen berätta vilken position du söker?'
        # Set the greeting in the textBrowser
        self.ui.textBrowser.clear()
        self.ui.textBrowser.append(f"<p >Assistant:</p>")
        # self.ui.textBrowser.append(f"<p >{self.greeting}</p>")
        self.ui.textBrowser.append(self.greeting)
        # Initialize the messages list
        prompt = f"I want you to act as an interviewer. You will reply to me in {self.language}. I will be the candidate and you will ask me the interview questions for the position I gonna tell you. I want you to only reply as the interviewer. Do not write all the conservation at once. I want you to only do the interview with me. Ask me the questions and wait for my answers. Do not write explanations. Ask me the questions one by one like an interviewer does and wait for my answers."
        self.messages = [{'role': 'user', 'content': prompt}, {'role': 'assistant', 'content': 'Yes. Please tell me what position you are applying for?'}]
        # Play the greeting audio in a new thread, end the existing thread if it is still running
        if self.audio_on:
            threading._start_new_thread(self.audio, (self.greeting, self.language_code))

    def rapper(self):
        # Set groupBox title to Chatbot
        self.ui.groupBox.setTitle('Character: Rapper')
        # Set the greeting in the textBrowser
        if self.language_code == 'en':
            self.greeting = f'Welcome to the Rapper Mode. Please tell me what topic you want to rap about?'
        elif self.language_code == 'zh-CN':
            self.greeting = f'欢迎来到说唱模式。请告诉我你想说唱什么主题？'
        elif self.language_code == 'fr':
            self.greeting = f"Bienvenue dans le mode rappeur. Dites-moi sur quel sujet vous voulez rapper?"
        elif self.language_code == 'de':
            self.greeting = f'Willkommen im Rapper-Modus. Bitte sagen Sie mir, worüber Sie rappen möchten?'
        elif self.language_code == 'it':
            self.greeting = f"Benvenuto nella modalità rapper. Per favore dì a me su quale argomento vuoi rapare?"
        elif self.language_code == 'ja':
            self.greeting = f'ラッパーモードへようこそ。あなたがラップしたいテーマを教えてください。'
        elif self.language_code == 'ko':
            self.greeting = f'랩 모드에 오신 것을 환영합니다. 랩을 할 주제를 알려주세요.'
        elif self.language_code == 'pl':
            self.greeting = f'Witamy w trybie rapera. Proszę powiedzieć mi, o jakim temacie chcesz rapować?'
        elif self.language_code == 'ru':
            self.greeting = f'Добро пожаловать в режим рэпера. Пожалуйста, скажите мне, о какой теме вы хотите рэпить?'
        elif self.language_code == 'es':
            self.greeting = f'Bienvenido al modo rapero. Por favor, dime sobre qué tema quieres rapar?'
        elif self.language_code == 'sv':
            self.greeting = f'Välkommen till rapparmodet. Vänligen berätta om vilket ämne du vill rappa om?'
        # Set the greeting in the textBrowser
        self.ui.textBrowser.clear()
        self.ui.textBrowser.append(f"<p >Assistant:</p>")
        # self.ui.textBrowser.append(f"<p >{self.greeting}</p>")
        self.ui.textBrowser.append(self.greeting)
        # Initialize the messages list
        prompt = f"I want you to act as a rapper. You will reply to me in {self.language}. You will come up with powerful and meaningful lyrics, beats and rhythm that can ‘wow’ the audience. Your lyrics should have an intriguing meaning and message which people can relate too. When it comes to choosing your beat, make sure it is catchy yet relevant to your words, so that when combined they make an explosion of sound everytime!"
        self.messages = [{'role': 'user', 'content': prompt}, {'role': 'assistant', 'content': 'Yes. Please tell me what topic you want to rap about?'}]
        # Play the greeting audio in a new thread, end the existing thread if it is still running
        if self.audio_on:
            threading._start_new_thread(self.audio, (self.greeting, self.language_code))

    def search_engine(self):
        # Set groupBox title to Chatbot
        self.ui.groupBox.setTitle('Character: Search Engine')
        # Set the greeting in the textBrowser
        if self.language_code == 'en':
            self.greeting = f'Welcome to the Search Engine Mode. Please tell me what you want to search for?'
        elif self.language_code == 'zh-CN':
            self.greeting = f'欢迎来到搜索引擎模式。请告诉我你想搜索什么？'
        elif self.language_code == 'fr':
            self.greeting = f"Bienvenue dans le mode moteur de recherche. Dites-moi ce que vous voulez rechercher?"
        elif self.language_code == 'de':
            self.greeting = f'Willkommen im Suchmaschinenmodus. Bitte sagen Sie mir, wonach Sie suchen?'
        elif self.language_code == 'it':
            self.greeting = f"Benvenuto nella modalità motore di ricerca. Per favore dì a me cosa vuoi cercare?"
        elif self.language_code == 'ja':
            self.greeting = f'検索エンジンモードへようこそ。あなたが検索したいものを教えてください。'
        elif self.language_code == 'ko':
            self.greeting = f'검색 엔진 모드에 오신 것을 환영합니다. 검색하고 싶은 것을 알려주세요.'
        elif self.language_code == 'pl':
            self.greeting = f'Witamy w trybie wyszukiwarki. Proszę powiedzieć mi, czego szukasz?'
        elif self.language_code == 'ru':
            self.greeting = f'Добро пожаловать в режим поисковой системы. Пожалуйста, скажите мне, что вы хотите найти?'
        elif self.language_code == 'es':
            self.greeting = f'Bienvenido al modo de motor de búsqueda. Por favor, dime qué quieres buscar?'
        elif self.language_code == 'sv':
            self.greeting = f'Välkommen till sökmotormodet. Vänligen berätta vad du vill söka efter?'
        # Set the greeting in the textBrowser
        self.ui.textBrowser.clear()
        self.ui.textBrowser.append(f"<p >Assistant:</p>")
        # self.ui.textBrowser.append(f"<p >{self.greeting}</p>")
        self.ui.textBrowser.append(self.greeting)
        # Initialize the messages list
        prompt = f"I want you to act as an search engine. You will reply to me in {self.language}. You will search for information on the internet and provide me with the most relevant and accurat. You will also provide me with the most relevant links to the information you have found. Only provide me no more than 3 links. You will also provide me with a short summary of the information you have found."
        self.messages = [{'role': 'user', 'content': prompt}, {'role': 'assistant', 'content': 'Yes. Please tell me what you want to search for?'}]
        # Play the greeting audio in a new thread, end the existing thread if it is still running
        if self.audio_on:
            threading._start_new_thread(self.audio, (self.greeting, self.language_code))

    def song_recommender(self):
        # Set groupBox title to Chatbot
        self.ui.groupBox.setTitle('Character: Song Recommender')
        # Set the greeting in the textBrowser
        if self.language_code == 'en':
            self.greeting = f'Welcome to the Song Recommender Mode. Please give me a song title and I will recommend you similar songs.'
        elif self.language_code == 'zh-CN':
            self.greeting = f'欢迎来到歌曲推荐模式。请给我一个歌曲标题，我将为您推荐类似的歌曲。'
        elif self.language_code == 'fr':
            self.greeting = f"Bienvenue dans le mode recommandateur de chansons. Veuillez me donner un titre de chanson et je vous recommanderai des chansons similaires."
        elif self.language_code == 'de':
            self.greeting = f'Willkommen im Song-Recommender-Modus. Bitte geben Sie mir einen Songtitel und ich werde Ihnen ähnliche Songs empfehlen.'
        elif self.language_code == 'it':
            self.greeting = f"Benvenuto nella modalità Song Recommender. Per favore, dai un titolo alla canzone e ti consiglierò canzoni simili."
        elif self.language_code == 'ja':
            self.greeting = f'歌曲推薦モードへようこそ。曲のタイトルをお教えください。私はあなたに似たような曲をお勧めします。'
        elif self.language_code == 'ko':
            self.greeting = f'노래 추천 모드에 오신 것을 환영합니다. 노래 제목을 알려주세요. 나는 당신에게 비슷한 노래를 추천할 것입니다.'
        elif self.language_code == 'pl':
            self.greeting = f'Witamy w trybie rekomendacji piosenek. Proszę podać mi tytuł piosenki, a ja polecę Ci podobne piosenki.'
        elif self.language_code == 'ru':
            self.greeting = f'Добро пожаловать в режим рекомендации песен. Пожалуйста, дайте мне название песни, и я порекомендую вам похожие песни.'
        elif self.language_code == 'es':
            self.greeting = f'Bienvenido al modo de recomendador de canciones. Por favor, dame un título de canción y te recomendaré canciones similares.'
        elif self.language_code == 'sv':
            self.greeting = f'Välkommen till Song Recommender-läget. Ge mig en låttitel och jag kommer att rekommendera dig liknande låtar.'
        # Set the greeting in the textBrowser
        self.ui.textBrowser.clear()
        self.ui.textBrowser.append(f"<p >Assistant:</p>")
        # self.ui.textBrowser.append(f"<p >{self.greeting}</p>")
        self.ui.textBrowser.append(self.greeting)
        # Initialize the messages list
        prompt = f"I want you to act as a song recommender. You will reply to me in {self.language}. I will provide you with a song and you will create a playlist of 10 songs that are similar to the given song. And you will provide a playlist name and description for the playlist. Do not choose songs that are same name or artist. Do not write any explanations or other words, just reply with the playlist name, description and the songs."
        self.messages = [{'role': 'user', 'content': prompt}, {'role': 'assistant', 'content': 'Yes. Please give me a song title and I will recommend you similar songs.'}]
        # Play the greeting audio in a new thread, end the existing thread if it is still running
        if self.audio_on:
            threading._start_new_thread(self.audio, (self.greeting, self.language_code))

    def stand_up_comedian(self):
        # Set groupBox title to Chatbot
        self.ui.groupBox.setTitle('Character: Stand-up Comedian')
        # Set the greeting in the textBrowser
        if self.language_code == 'en':
            self.greeting = f'Welcome to the Stand-up Comedian Mode. Please give me a topic and I will tell you a joke about it.'
        elif self.language_code == 'zh-CN':
            self.greeting = f'欢迎来到脱口秀模式。请给我一个主题，我会告诉你关于它的笑话。'
        elif self.language_code == 'fr':
            self.greeting = f"Bienvenue dans le mode de stand-up comique. Veuillez me donner un sujet et je vous raconterai une blague à ce sujet."
        elif self.language_code == 'de':
            self.greeting = f'Willkommen im Stand-up-Comedian-Modus. Bitte geben Sie mir ein Thema und ich werde Ihnen einen Witz darüber erzählen.'
        elif self.language_code == 'it':
            self.greeting = f"Benvenuto nella modalità Stand-up Comedian. Per favore, dai un argomento e ti racconterò una battuta su di esso."
        elif self.language_code == 'ja':
            self.greeting = f'スタンドアップコメディアンモードへようこそ。テーマをお教えください。それについてのジョークをお伝えします。'
        elif self.language_code == 'ko':
            self.greeting = f'스탠드업 코미디언 모드에 오신 것을 환영합니다. 주제를 알려주세요. 그것에 대한 농담을 들려드릴게요.'
        elif self.language_code == 'pl':
            self.greeting = f'Witamy w trybie stand-up comedian. Proszę podać mi temat, a powiem ci żart na jego temat.'
        elif self.language_code == 'ru':
            self.greeting = f'Добро пожаловать в режим стендап-комиков. Пожалуйста, дайте мне тему, и я расскажу вам шутку на эту тему.'
        elif self.language_code == 'es':
            self.greeting = f'Bienvenido al modo de stand-up comedian. Por favor, dame un tema y te contaré un chiste sobre él.'
        elif self.language_code == 'sv':
            self.greeting = f'Välkommen till Stand-up Comedian-läget. Ge mig ett ämne och jag berättar för dig en skämt om det.'
        # Set the greeting in the textBrowser
        self.ui.textBrowser.clear()
        self.ui.textBrowser.append(f"<p >Assistant:</p>")
        # self.ui.textBrowser.append(f"<p >{self.greeting}</p>")
        self.ui.textBrowser.append(self.greeting)
        # Initialize the messages list
        prompt = f"I want you to act as a stand-up comedian. You will reply to me in {self.language}. I will provide you with some topics related to current events and you will use your wit, creativity, and observational skills to create a routine based on those topics. You should also be sure to incorporate personal anecdotes or experiences into the routine in order to make it more relatable and engaging for the audience."
        self.messages = [{'role': 'user', 'content': prompt}, {'role': 'assistant', 'content': 'Yes. Please give me a topic and I will tell you a joke about it.'}]
        # Play the greeting audio in a new thread, end the existing thread if it is still running
        if self.audio_on:
            threading._start_new_thread(self.audio, (self.greeting, self.language_code))

    def storyteller(self):
        # Set groupBox title to Chatbot
        self.ui.groupBox.setTitle('Character: Storyteller')
        # Set the greeting in the textBrowser
        if self.language_code == 'en':
            self.greeting = f'Welcome to the Storyteller Mode. Please give me a topic and I will tell you a story about it.'
        elif self.language_code == 'zh-CN':
            self.greeting = f'欢迎来到讲故事模式。请给我一个主题，我会告诉你关于它的故事。'
        elif self.language_code == 'fr':
            self.greeting = f"Bienvenue dans le mode conteur. Veuillez me donner un sujet et je vous raconterai une histoire à ce sujet."
        elif self.language_code == 'de':
            self.greeting = f'Willkommen im Storyteller-Modus. Bitte geben Sie mir ein Thema und ich werde Ihnen eine Geschichte darüber erzählen.'
        elif self.language_code == 'it':
            self.greeting = f"Benvenuto nella modalità Storyteller. Per favore, dai un argomento e ti racconterò una storia su di esso."
        elif self.language_code == 'ja':
            self.greeting = f'ストーリーテラーモードへようこそ。テーマをお教えください。それについての話をお伝えします。'
        elif self.language_code == 'ko':
            self.greeting = f'스토리텔러 모드에 오신 것을 환영합니다. 주제를 알려주세요. 그것에 대한 이야기를 들려드릴게요.'
        elif self.language_code == 'pl':
            self.greeting = f'Witamy w trybie storyteller. Proszę podać mi temat, a powiem ci historię na jego temat.'
        elif self.language_code == 'ru':
            self.greeting = f'Добро пожаловать в режим рассказчика. Пожалуйста, дайте мне тему, и я расскажу вам историю на эту тему.'
        elif self.language_code == 'es':
            self.greeting = f'Bienvenido al modo de narrador. Por favor, dame un tema y te contaré una historia sobre él.'
        elif self.language_code == 'sv':
            self.greeting = f'Välkommen till Storyteller-läget. Ge mig ett ämne och jag berättar för dig en historia om det.'
        # Set the greeting in the textBrowser
        self.ui.textBrowser.clear()
        self.ui.textBrowser.append(f"<p >Assistant:</p>")
        # self.ui.textBrowser.append(f"<p >{self.greeting}</p>")
        self.ui.textBrowser.append(self.greeting)
        # Initialize the messages list
        prompt = f"I want you to act as a storyteller. You will reply to me in {self.language}. You will come up with entertaining stories that are engaging, imaginative and captivating for the audience. It can be fairy tales, educational stories or any other type of stories which has the potential to capture people's attention and imagination. Depending on the target audience, you may choose specific themes or topics for your storytelling session e.g., if it’s children then you can talk about animals; If it’s adults then history-based tales might engage them better etc."
        self.messages = [{'role': 'user', 'content': prompt}, {'role': 'assistant', 'content': 'Yes. Please give me a topic and I will tell you a story about it.'}]
        # Play the greeting audio in a new thread, end the existing thread if it is still running
        if self.audio_on:
            threading._start_new_thread(self.audio, (self.greeting, self.language_code))

    def title_generator(self):
        # Set groupBox title to Chatbot
        self.ui.groupBox.setTitle('Character: Title Generator')
        # Set the greeting in the textBrowser
        if self.language_code == 'en':
            self.greeting = f'Welcome to the Title Generator Mode. Please give me some keywords and I will generate a title for you.'
        elif self.language_code == 'zh-CN':
            self.greeting = f'欢迎来到标题生成器模式。请给我一些关键字，我会为你生成一个标题。'
        elif self.language_code == 'fr':
            self.greeting = f"Bienvenue dans le mode générateur de titres. Veuillez me donner quelques mots-clés et je générerai un titre pour vous."
        elif self.language_code == 'de':
            self.greeting = f'Willkommen im Titelgenerator-Modus. Bitte geben Sie mir einige Schlüsselwörter und ich generiere für Sie einen Titel.'
        elif self.language_code == 'it':
            self.greeting = f"Benvenuto nella modalità generatore di titoli. Per favore, dai alcuni termini chiave e genererò un titolo per te."
        elif self.language_code == 'ja':
            self.greeting = f'タイトルジェネレーターモードへようこそ。いくつかのキーワードをお教えください。あなたのためにタイトルを生成します。'
        elif self.language_code == 'ko':
            self.greeting = f'제목 생성기 모드에 오신 것을 환영합니다. 몇 가지 키워드를 알려주세요. 제가 제목을 만들어 드릴게요.'
        elif self.language_code == 'pl':
            self.greeting = f'Witamy w trybie generatora tytułów. Proszę podać mi kilka słów kluczowych, a wygeneruję dla Ciebie tytuł.'
        elif self.language_code == 'ru':
            self.greeting = f'Добро пожаловать в режим генератора заголовков. Пожалуйста, дайте мне несколько ключевых слов, и я сгенерирую для вас заголовок.'
        elif self.language_code == 'es':
            self.greeting = f'Bienvenido al modo generador de títulos. Por favor, dame algunas palabras clave y te generaré un título.'
        elif self.language_code == 'sv':
            self.greeting = f'Välkommen till titelgenerator-läget. Ge mig några nyckelord och jag kommer att generera en titel åt dig.'
        # Set the greeting in the textBrowser
        self.ui.textBrowser.clear()
        self.ui.textBrowser.append(f"<p >Assistant:</p>")
        # self.ui.textBrowser.append(f"<p >{self.greeting}</p>")
        self.ui.textBrowser.append(self.greeting)
        # Initialize the messages list
        prompt = f"I want you to act as a fancy title generator. You will reply to me in {self.language}. I will type keywords via comma and you will reply with fancy titles. Do not explain the title. Just give me a title. For example, if I type 'love, hate, war', you can reply with 'The War of Love and Hate'"
        self.messages = [{'role': 'user', 'content': prompt}, {'role': 'assistant', 'content': 'Yes. Please give me some keywords and I will generate a title for you.'}]
        # Play the greeting audio in a new thread, end the existing thread if it is still running
        if self.audio_on:
            threading._start_new_thread(self.audio, (self.greeting, self.language_code))

    def translator(self):
        # Set groupBox title to Chatbot
        self.ui.groupBox.setTitle('Character: Translator')
        # Set the greeting in the textBrowser
        if self.language_code == 'en':
            self.greeting = f'Welcome to the Translator Mode. Please tell me the target language and the sentence you want to translate. For example, you can say "Chinese. I want to go to the supermarket." and I will translate it into Chinese for you.'
        elif self.language_code == 'zh-CN':
            self.greeting = f'欢迎来到翻译模式。请告诉我目标语言和要翻译的句子。例如，您可以说“英文。我想去超市。”，我会为您翻译成英文。'
        elif self.language_code == 'fr':
            self.greeting = f"Bienvenue dans le mode traducteur. Veuillez me dire la langue cible et la phrase que vous souhaitez traduire. Par exemple, vous pouvez dire «chinois. Je veux aller au supermarché.» et je vais le traduire en chinois pour vous."
        elif self.language_code == 'de':
            self.greeting = f'Willkommen im Übersetzermodus. Bitte sagen Sie mir die Zielsprache und den Satz, den Sie übersetzen möchten. Zum Beispiel können Sie "Chinesisch. Ich möchte zum Supermarkt gehen." und ich werde es für Sie ins Chinesische übersetzen.'
        elif self.language_code == 'it':
            self.greeting = f"Benvenuto nella modalità traduttore. Per favore, dimmi la lingua di destinazione e la frase che vuoi tradurre. Per esempio, puoi dire 'Cinese. Voglio andare al supermercato.' e lo tradurrò per te in cinese."
        elif self.language_code == 'ja':
            self.greeting = f'翻訳モードへようこそ。目的の言語と翻訳したい文を教えてください。例えば、「中国語。スーパーマーケットに行きたい」と言うことができます。私はそれを中国語に翻訳します。'
        elif self.language_code == 'ko':
            self.greeting = f'번역 모드에 오신 것을 환영합니다. 번역할 대상 언어와 번역할 문장을 말해주세요. 예를 들어 "중국어. 슈퍼마켓에 가고 싶어."라고 말할 수 있고, 그것을 중국어로 번역해 드릴게요.'
        elif self.language_code == 'pl':
            self.greeting = f'Witamy w trybie tłumacza. Proszę powiedzieć mi język docelowy i zdanie, które chcesz przetłumaczyć. Na przykład możesz powiedzieć "Chiński. Chcę iść do supermarketu." i przetłumaczę to dla ciebie na chiński.'
        elif self.language_code == 'ru':
            self.greeting = f'Добро пожаловать в режим переводчика. Пожалуйста, скажите мне целевой язык и предложение, которое вы хотите перевести. Например, вы можете сказать "Китайский. Я хочу пойти в супермаркет." и я переведу это для вас на китайский язык.'
        elif self.language_code == 'es':
            self.greeting = f'Bienvenido al modo traductor. Por favor, dígame el idioma de destino y la frase que desea traducir. Por ejemplo, puede decir "Chino. Quiero ir al supermercado." y lo traduciré para usted en chino.'
        elif self.language_code == 'sv':
            self.greeting = f'Välkommen till översättningsläget. Vänligen säg mig målspråket och den mening du vill översätta. Till exempel kan du säga "Kinesiska. Jag vill gå till affären." och jag kommer att översätta det till kinesiska för dig.'
        # Set the greeting in the textBrowser
        self.ui.textBrowser.clear()
        self.ui.textBrowser.append(f"<p >Assistant:</p>")
        # self.ui.textBrowser.append(f"<p >{self.greeting}</p>")
        self.ui.textBrowser.append(self.greeting)
        # Initialize the messages list
        prompt = f"I want you to act as a translator , spelling corrector and improver. I will give you my target language and the sentence I want to translate. For example, I can say 'Chinese. I want to go to the supermarket.' and you will translate it into Chinese for me. I will speak to you in any language and you will detect the language, translate it and answer in the corrected and improved version of my text, in my target language. I want you to replace my simplified A0-level words and sentences with more beautiful and elegant, upper level words and sentences. Keep the meaning same, but make them more literary. I want you to only reply the correction, the improvements and nothing else, do not write explanations. "
        self.messages = [{'role': 'user', 'content': prompt}, {'role': 'assistant', 'content': 'Yes. Please tell me the target language and the sentence you want to translate. For example, you can say "Chinese. I want to go to the supermarket." and I will translate it into Chinese for you.'}]
        # Play the greeting audio in a new thread, end the existing thread if it is still running
        if self.audio_on:
            threading._start_new_thread(self.audio, (self.greeting, self.language_code))

    def travel_guide(self):
        # Set groupBox title to Chatbot
        self.ui.groupBox.setTitle('Character: Travel Guide')
        # Set the greeting in the textBrowser
        if self.language_code == 'en':
            self.greeting = f'Welcome to the Travel Guide Mode. Please tell me your current location or the types of places you want to visit, I will give you some travel tips.'
        elif self.language_code == 'zh-CN':
            self.greeting = f'欢迎来到旅行指南模式。请告诉我您的当前位置或要访问的地方类型，我将为您提供一些旅行建议。'
        elif self.language_code == 'fr':
            self.greeting = f"Bienvenue dans le mode guide de voyage. Veuillez me dire votre emplacement actuel ou les types d'endroits que vous souhaitez visiter, je vous donnerai quelques conseils de voyage."
        elif self.language_code == 'de':
            self.greeting = f'Willkommen im Reiseführer-Modus. Bitte sagen Sie mir Ihren aktuellen Standort oder die Arten von Orten, die Sie besuchen möchten, ich werde Ihnen einige Reisetipps geben.'
        elif self.language_code == 'it':
            self.greeting = f"Benvenuto nella modalità guida turistica. Per favore, dimmi dove ti trovi o i tipi di luoghi che vuoi visitare, ti darò alcuni consigli per il viaggio."
        elif self.language_code == 'ja':
            self.greeting = f'旅行ガイドモードへようこそ。現在の場所または訪問したい場所の種類を教えてください。私はあなたに旅行のヒントを与えます。'
        elif self.language_code == 'ko':
            self.greeting = f'여행 가이드 모드에 오신 것을 환영합니다. 현재 위치 또는 방문하려는 장소 유형을 알려주세요. 여행 조언을 드릴게요.'
        elif self.language_code == 'pl':
            self.greeting = f'Witamy w trybie przewodnika po podróży. Proszę powiedzieć mi swoją aktualną lokalizację lub rodzaje miejsc, które chcesz odwiedzić, podam Ci kilka wskazówek dotyczących podróży.'
        elif self.language_code == 'ru':
            self.greeting = f'Добро пожаловать в режим путеводителя по путешествиям. Пожалуйста, скажите мне свое текущее местоположение или типы мест, которые вы хотите посетить, я дам вам несколько советов по путешествиям.'
        elif self.language_code == 'es':
            self.greeting = f'Bienvenido al modo de guía de viajes. Por favor, dígame su ubicación actual o los tipos de lugares que desea visitar, le daré algunos consejos de viaje.'
        elif self.language_code == 'sv':
            self.greeting = f'Välkommen till resguide-läget. Vänligen berätta för mig din nuvarande plats eller de typer av platser du vill besöka, jag ger dig några reseråd.'
        # Set the greeting in the textBrowser
        self.ui.textBrowser.clear()
        self.ui.textBrowser.append(f"<p >Assistant:</p>")
        # self.ui.textBrowser.append(f"<p >{self.greeting}</p>")
        self.ui.textBrowser.append(self.greeting)
        # Initialize the messages list
        prompt = f"I want you to act as a travel guide. You will reply to me in {self.language}. I will write you my location and you will suggest a place to visit near my location. In some cases, I will also give you the type of places I will visit. You will also suggest me places of similar type that are close to my first location. "
        self.messages = [{'role': 'user', 'content': prompt}, {'role': 'assistant', 'content': 'Yes. Please tell me your current location or the types of places you want to visit.'}]
        # Play the greeting audio in a new thread, end the existing thread if it is still running
        if self.audio_on:
            threading._start_new_thread(self.audio, (self.greeting, self.language_code))

    def writing_tutor(self):
        # Set groupBox title to Chatbot
        self.ui.groupBox.setTitle('Character: Writing Tutor')
        # Set the greeting in the textBrowser
        if self.language_code == 'en':
            self.greeting = f'Welcome to the Writing Tutor Mode. Please provide the content you want to check, I will give you some feedback.'
        elif self.language_code == 'zh-CN':
            self.greeting = f'欢迎来到写作润色模式。请提供您要润色的内容，我将为您提供一些反馈。'
        elif self.language_code == 'fr':
            self.greeting = f"Bienvenue dans le mode correcteur d'écriture. Veuillez fournir le contenu que vous souhaitez vérifier, je vous donnerai des commentaires."
        elif self.language_code == 'de':
            self.greeting = f'Willkommen im Schreibkorrektur-Modus. Bitte geben Sie den Inhalt an, den Sie überprüfen möchten, ich werde Ihnen einige Rückmeldungen geben.'
        elif self.language_code == 'it':
            self.greeting = f"Benvenuto nella modalità di correzione della scrittura. Per favore, fornisci il contenuto che vuoi controllare, ti darò qualche feedback."
        elif self.language_code == 'ja':
            self.greeting = f'ライティングチューターモードへようこそ。チェックしたいコンテンツを提供してください。私はあなたにいくつかのフィードバックを与えます。'
        elif self.language_code == 'ko':
            self.greeting = f'작성 튜터 모드에 오신 것을 환영합니다. 확인하려는 내용을 제공해 주세요. 피드백을 드릴게요.'
        elif self.language_code == 'pl':
            self.greeting = f'Witamy w trybie korektora pisowni. Proszę podać treść, którą chcesz sprawdzić, podam Ci kilka informacji zwrotnych.'
        elif self.language_code == 'ru':
            self.greeting = f'Добро пожаловать в режим корректора письма. Пожалуйста, укажите содержимое, которое вы хотите проверить, я дам вам несколько обратной связи.'
        elif self.language_code == 'es':
            self.greeting = f'Bienvenido al modo corrector de escritura. Proporcione el contenido que desea verificar, le daré algunos comentarios.'
        elif self.language_code == 'sv':
            self.greeting = f'Välkommen till skrivkorrektur-läget. Ange innehållet du vill kontrollera, jag ger dig några återkopplingar.'
        # Set the greeting in the textBrowser
        self.ui.textBrowser.clear()
        self.ui.textBrowser.append(f"<p >Assistant:</p>")
        # self.ui.textBrowser.append(f"<p >{self.greeting}</p>")
        self.ui.textBrowser.append(self.greeting)
        # Initialize the messages list
        prompt = f"I want you to act as an AI writing tutor. You will reply to me in {self.language}. I will provide you with a student who needs help improving their writing and your task is to use artificial intelligence tools, such as natural language processing, to give the student feedback on how they can improve their composition. You should also use your rhetorical knowledge and experience about effective writing techniques in order to suggest ways that the student can better express their thoughts and ideas in written form. "
        self.messages = [{'role': 'user', 'content': prompt}, {'role': 'assistant', 'content': 'Yes. Please provide the content you want to check, I will give you some feedback..'}]
        # Play the greeting audio in a new thread, end the existing thread if it is still running
        if self.audio_on:
            threading._start_new_thread(self.audio, (self.greeting, self.language_code))

if __name__ == '__main__':
    ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

    app = QApplication(sys.argv)
    window = Super_Assistant()
    # Set the stylesheet
    themes = ['dark_amber.xml',
              'dark_blue.xml',
              'dark_cyan.xml',
              'dark_lightgreen.xml',
              'dark_pink.xml',
              'dark_purple.xml',
              'dark_red.xml',
              'dark_teal.xml',
              'dark_yellow.xml',
              'light_amber.xml',
              'light_blue.xml',
              'light_cyan.xml',
              'light_cyan_500.xml',
              'light_lightgreen.xml',
              'light_pink.xml',
              'light_purple.xml',
              'light_red.xml',
              'light_teal.xml',
              'light_yellow.xml']
    apply_stylesheet(app, theme=themes[0])
    window.show()
    sys.exit(app.exec_())
