import os
import speech_recognition as sr
from os import path
from pocketsphinx import LiveSpeech, get_model_path

# model_path = get_model_path()

# speech = LiveSpeech(
#     verbose=False,
#     sampling_rate=16000,
#     buffer_size=2048,
#     no_search=False,
#     full_utt=False,
#     hmm=os.path.join(model_path, 'en-us'),
#     lm=os.path.join(model_path, 'en-us.lm.bin'),
#     dic=os.path.join(model_path, 'cmudict-en-us.dict')
# )

for index, name in enumerate(sr.Microphone.list_microphone_names()):
    print("Microphone with name \"{1}\" found for `Microphone(device_index={0})`".format(index, name))

r = sr.Recognizer()
with sr.Microphone(device_index=0) as source:
    print("say something")
    audio = r.listen(source)

try:
    print("Sphinx thinks you said " + r.recognize_sphinx(audio))
except sr.UnknownValueError:
    print("Sphinx could not understand audio")
except sr.RequestError as e:
    print("Sphinx error; {0}".format(e))
AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "male.wav")
# AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "french.aiff")
# AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "chinese.flac")


# use the audio file as the audio source
r = sr.Recognizer()
r.dynamic_energy_threshold = True
with sr.AudioFile(AUDIO_FILE) as source:
    # r.adjust_for_ambient_noise(source=source, duration=0.25)
    audio = r.record(source)  # read the entire audio file

# recognize speech using Sphinx
try:
    print("Sphinx thinks you said - " + r.recognize_sphinx(audio))
except sr.UnknownValueError:
    print("Sphinx could not understand audio")
except sr.RequestError as e:
    print("Sphinx error; {0}".format(e))
