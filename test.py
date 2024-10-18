import pyttsx3
import speech_recognition as sr
import pyaudio

# Test Pyttsx3 (text-to-speech)
engine = pyttsx3.init()
engine.say("Hello, I am your AI assistant.")
engine.runAndWait()

# Test Speech Recognition
recognizer = sr.Recognizer()
with sr.Microphone() as source:
    print("Say something...")
    audio = recognizer.listen(source)
    try:
        print("You said: " + recognizer.recognize_google(audio))
    except sr.UnknownValueError:
        print("Sorry, I did not understand that.")
    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))
