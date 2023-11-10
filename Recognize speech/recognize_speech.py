import speech_recognition as sr
import nltk
from nltk.tokenize import sent_tokenize
nltk.download('punkt')

def recognize_speech_from_audio(audio_file):

    r = sr.Recognizer()

    with sr.AudioFile(audio_file) as source:
        audio_data = r.record(source)

    transcript = r.recognize_sphinx(audio_data)

    sentences = sent_tokenize(transcript)

    with open(f"{audio_file}.txt", "w") as file:
        for sentence in sentences:
            file.write(sentence + "\n")
