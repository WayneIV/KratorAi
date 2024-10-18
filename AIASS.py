import datetime
import wikipedia
import smtplib
import requests
import json
import sqlite3
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from cryptography.fernet import Fernet
from langdetect import detect
from googletrans import Translator
from apscheduler.schedulers.background import BackgroundScheduler
import time
import re
import pyttsx3
import speech_recognition as sr



class AI_Assistant:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        self.voice = self.engine.getProperty('voices')[0]  # Default voice (can be customized)
        self.engine.setProperty('voice', self.voice.id)
        self.engine.setProperty('rate', 150)  # Set speech rate (can be customized)
        
        # Initialize API keys and email credentials (use environment variables for better security)
        self.weather_api_key = "your_weather_api_key_here"  # Replace with a valid API key
        self.email_sender = "your_email_here@gmail.com"  # Replace with your email
        self.db_connection = sqlite3.connect('assistant_data.db')
        self.db_cursor = self.db_connection.cursor()
        self.key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.key)
        self.scheduler = BackgroundScheduler()
        self.init_db()

    def init_db(self):
        """Initialize SQLite Database for storing tasks and reminders"""
        try:
            self.db_cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        task TEXT NOT NULL,
                                        status TEXT NOT NULL,
                                        due_date TEXT,
                                        priority INTEGER DEFAULT 3
                                      )''')
            self.db_cursor.execute('''CREATE TABLE IF NOT EXISTS notes (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        note TEXT NOT NULL
                                      )''')
            self.db_connection.commit()
        except sqlite3.Error as e:
            print(f"Error initializing database: {e}")
            self.speak("Failed to initialize the database.")

    def encrypt_message(self, message):
        """Encrypts sensitive information like email password"""
        encrypted_message = self.cipher_suite.encrypt(message.encode())
        return encrypted_message

    def decrypt_message(self, encrypted_message):
        """Decrypts sensitive information"""
        decrypted_message = self.cipher_suite.decrypt(encrypted_message)
        return decrypted_message.decode()

    def speak(self, text):
        """Function to give voice feedback"""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Error in speech synthesis: {e}")
            self.speak("There was an issue with the voice feedback.")

    def listen(self):
        """Function to capture user's speech via microphone"""
        with sr.Microphone() as source:
            try:
                print("Listening...")
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source)
                command = self.recognizer.recognize_google(audio).lower()
                print(f"You said: {command}")
                return command
            except sr.UnknownValueError:
                self.speak("Sorry, I did not understand that.")
            except sr.RequestError:
                self.speak("Sorry, I'm having trouble with the speech service.")
            except Exception as e:
                self.speak("An error occurred while listening.")
                print(f"Error in listening: {e}")
            return None

    def detect_language(self, text):
        """Detects the language of the command"""
        try:
            return detect(text)
        except Exception as e:
            print(f"Error detecting language: {e}")
            return 'en'

    def translate_command(self, command, target_language='en'):
        """Translates commands to English if needed"""
        try:
            translator = Translator()
            translated = translator.translate(command, dest=target_language)
            return translated.text
        except Exception as e:
            print(f"Error translating command: {e}")
            self.speak("Error translating the command.")
            return command

    def execute_command(self, command):
        """Function to execute commands based on voice input"""
        language = self.detect_language(command)
        print(f"Detected language: {language}")
        
        if language != 'en':
            command = self.translate_command(command)

        if 'hello' in command:
            self.speak("Hello, how can I assist you today?")
        elif 'search' in command:
            query = command.replace('search', '').strip()
            self.speak(f"Searching for {query}")
            kit.search(query)
        elif 'wikipedia' in command:
            query = command.replace('wikipedia', '').strip()
            self.speak(f"Fetching information from Wikipedia about {query}")
            info = wikipedia.summary(query, sentences=2)
            self.speak(info)
        elif 'open' in command:
            website = command.replace('open', '').strip()
            self.speak(f"Opening {website}")
            webbrowser.open(f"http://{website}")
        elif 'time' in command:
            time = datetime.datetime.now().strftime("%H:%M")
            self.speak(f"The current time is {time}")
        elif 'date' in command:
            date = datetime.datetime.now().strftime("%B %d, %Y")
            self.speak(f"Today's date is {date}")
        elif 'play music' in command:
            self.speak("Playing music for you.")
            os.system("start music.mp3")  # Adjust for your media player setup
        elif 'weather' in command:
            city = command.replace('weather in', '').strip()
            self.speak(f"Fetching weather details for {city}")
            self.get_weather(city)
        elif 'send email' in command:
            self.send_email_flow()
        elif 'reminder' in command:
            self.set_reminder_flow()
        elif 'add task' in command:
            self.add_task_flow()
        elif 'list tasks' in command:
            self.list_tasks()
        elif 'notes' in command:
            self.manage_notes(command)
        elif 'prioritize' in command:
            self.prioritize_task(command)
        elif 'personalize' in command:
            self.personalize_assistant()
        elif 'exit' in command or 'quit' in command:
            self.speak("Goodbye!")
            exit()
        else:
            self.speak("I'm sorry, I didn't understand the command. Please try again.")

    def get_weather(self, city):
        """Fetches weather information for a given city using an API"""
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.weather_api_key}&units=metric"
            response = requests.get(url)
            data = response.json()
            if data.get("cod") != 200:
                self.speak(f"Could not retrieve weather for {city}. Please try again later.")
            else:
                temp = data["main"]["temp"]
                weather_desc = data["weather"][0]["description"]
                self.speak(f"The current weather in {city} is {weather_desc} with a temperature of {temp}°C.")
        except Exception as e:
            self.speak("Failed to retrieve weather data. Please check your internet connection.")
            print(f"Error fetching weather: {e}")

    def send_email_flow(self):
        """Flow to handle sending emails"""
        self.speak("Who would you like to send the email to?")
        recipient = self.listen()
        self.speak("What should I say in the email?")
        message_body = self.listen()
        self.send_email(recipient, message_body)

    def send_email(self, recipient, body):
        """Sends an email using SMTP"""
        msg = MIMEMultipart()
        msg['From'] = self.email_sender
        msg['To'] = recipient
        msg['Subject'] = "AI Assistant Email"
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.email_sender, self.decrypt_message(b"your_encrypted_email_password"))  # Decrypt password
            text = msg.as_string()
            server.sendmail(self.email_sender, recipient, text)
            server.quit()
            self.speak(f"Email sent to {recipient}")
        except Exception as e:
            self.speak(f"Failed to send email. Error: {e}")

    def set_reminder_flow(self):
        """Flow to handle setting reminders"""
        self.speak("What is your reminder?")
        reminder = self.listen()
        self.speak("When should I remind you? (Please say the date and time in the format 'YYYY-MM-DD HH:MM')")
        reminder_time = self.listen()
        self.set_reminder(reminder, reminder_time)

    def set_reminder(self, reminder, reminder_time):
        """Sets a reminder for the user"""
        try:
            reminder_time = datetime.datetime.strptime(reminder_time, '%Y-%m-%d %H:%M')
            wait_time = (reminder_time - datetime.datetime.now()).total_seconds()
            if wait_time < 0:
                self.speak("Reminder time is in the past.")
                return

            time.sleep(wait_time)
            self.speak(f"Reminder: {reminder}")
        except Exception as e:
            self.speak("Failed to set reminder.")
            print(f"Error setting reminder: {e}")

    def prioritize_task(self, command):
        """Allows user to prioritize a task by modifying its priority"""
        task_id = re.search(r"\d+", command)
        if task_id:
            task_id = int(task_id.group(0))
            self.speak(f"Setting priority for task ID {task_id}. Please specify priority (1 to 5)")
            priority = self.listen()
            try:
                self.db_cursor.execute("UPDATE tasks SET priority = ? WHERE id = ?", (priority, task_id))
                self.db_connection.commit()
                self.speak(f"Task ID {task_id} updated with priority {priority}.")
            except sqlite3.Error as e:
                self.speak(f"Failed to set priority for task {task_id}.")
                print(f"Error updating priority: {e}")

    def personalize_assistant(self):
        """Personalize the assistant with a custom wake word"""
        self.speak("What would you like to call me?")
        wake_word = self.listen()
        self.speak(f"Thank you! You can now call me {wake_word}.")
        # Update wake word in settings or save it for future reference.

# Initialize and start assistant
if __name__ == "__main__":
    assistant = AI_Assistant()
    assistant.speak("Hello, I am your personal assistant. How may I help you today?")
    
    while True:
        command = assistant.listen()
        if command:
            assistant.execute_command(command)
