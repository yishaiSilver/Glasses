import gtts
import playsound

mp3_file_number = 0

def sound(first_sentence):
	global mp3_file_number

	tts = gtts.gTTS(text=first_sentence, lang='en', slow=False)
	print('beginning audio generation')
	tts.save("./sounds/speech_ouput_{}.mp3".format(mp3_file_number))
	print('audio generated.')
  
	playsound.playsound("./sounds/speech_ouput_{}.mp3".format(mp3_file_number))

	mp3_file_number += 1

def initSound():
	tts = gtts.gTTS(text="initializing Google text to speech.", lang='en', slow=False)
	tts.save("gtts_init.mp3".format(mp3_file_number))
