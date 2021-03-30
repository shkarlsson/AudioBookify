#%%
import pdfreader
import re
from spellchecker import SpellChecker
import os
import pyttsx3
from time import sleep

# %%
VOICE_NAME = 'Karen'
FILE_SPLIT_DELIMITER = 'Chapter '
root_dir = os.path.dirname(os.path.abspath(__file__))+'/'
filename = [f for f in os.listdir(root_dir+'pdf') if '.pdf' in f[-4:]][0] #Gets the first pdf file in this directory
fd = open(root_dir + 'pdf/' + filename, "rb")
viewer = pdfreader.SimplePDFViewer(fd)
test = input(f'Test different voices? (y) (Else I will go with {VOICE_NAME})') == 'y'

#%% Reading pdf and saving to string.
i = 0
end_reached = False
s = ''
while not end_reached:
	try:
		i += 1
		print(f'\rReading page number {i}...', end='')
		viewer.navigate(i)
		viewer.render()
		s += ''.join(viewer.canvas.strings)
	except:
		end_reached = True

print(f'Done. {len(s)} characters have been read.')
# %% Cleaning up string.
s2 = re.sub('The Metamorphosis of Prime Intellect: Chapter 1http://www.kuro5hin.org/prime-intellect/mopiall.html[0-9]+ of 13423/03/08 23:03', ' ', s)

s2 = re.sub('(?<=[a-z])(?=[A-Z])',' ',s2) #Separating chapter title endings from begining of chapter text
s2 = re.sub('  \* (?=Chapter .+:   )','\n\n',s2) #Spacing chapter beginnings
s2 = re.sub('(?<=(\.|\?|\!))(?=\"?[A-z])',' ', s2) #Adding missing spaces after sentences
#s2 = re.sub('(?<=(\.|\?|\!))(?=\"[A-z])')
s2 = re.sub('(?<=(\,|\;))(?=[A-z])',' ', s2) #Adding missing spaces in sentences
s2 = re.sub('(\*|\>)', '\n- ', s2) #Standardizing dialogue character
s2 = re.sub('(?<=\")(?=\")', '\n ', s2) # Spacing dialogue
s2 = s2.replace(',"', '",')
#s2 = re.sub('(?<=- )(.+)\"', r'\1',s2)

names = ['caroline', 'timothy', 'mamba', 'glasslike']
names += [n+'s' for n in names]
spell = SpellChecker()
spell.word_frequency.load_words(names)


#Doing a bit of complicated text cleanup of mess caused by pdfreader not interpreting linebreaks as anything.

def get_most_probably_split(word):
	max_prob = 0
	max_prob_i = 0
	max_p1, max_p2 = 0, 0
	for i in range(len(word)):	
		w1 = re.sub('[^a-zA-Z]+', '', word[:i]).lower()
		w2 = re.sub('[^a-zA-Z]+', '', word[i:]).lower()
		p1, p2 = spell.word_probability(w1), spell.word_probability(w2)
		prob = min(p1,p2) * 9**99 + min(len(w1), len(w2))
		if prob > max_prob:
			max_prob = prob
			max_prob_i = int(i)
			max_p1, max_p2 = p1, p2
	#print(clean_word, '--->',clean_word[:max_prob_i], clean_word[max_prob_i:])
	#print(word, '--->',word[:max_prob_i], word[max_prob_i:], '(', f'{max_p1:.0e}', f'{max_p2:.0e}', ')', i)
	return [word[:max_prob_i], word[max_prob_i:]]


s3 = []
for word in s2.split(' '):
	clean_word = re.sub('[^a-zA-Z]+', '', word).lower()
	if len(clean_word) > 0:
		if '-' in word[:-1]:
			hyphen_word = []
			for sub_word in word.split('-'):
				clean_sub_word = re.sub('[^a-zA-Z]+', '', sub_word).lower()
				if len(clean_sub_word) > 0:
					if spell.word_probability(clean_sub_word) == 0:
						hyphen_word.append(' '.join(get_most_probably_split(sub_word)))
					else:
						hyphen_word.append(sub_word)
				else:
					hyphen_word.append(sub_word)
			hyphen_word = '-'.join(hyphen_word)
			s3 += [hyphen_word]
		else:
			if spell.word_probability(clean_word) == 0:
				s3 += get_most_probably_split(word)
			else:
				s3 += [word]
	else:
		s3 += [word]


txt = ' '.join(s3)
f = open(root_dir + 'txt/' + filename[:-4] + '.txt', "w")
f.write(txt)
f.close()

# %% Exporting to mp3

engine = pyttsx3.init()

if test == True:
	voices = engine.getProperty('voices')
	for voice in voices:
		engine.setProperty('voice', voice.id)
		#engine.say(txt[100:400])
		engine.save_to_file(txt[200:1000],root_dir + 'test/' + voice.name + '.mp3')
		engine.runAndWait()
		sleep(1)

else:
	voice = [v for v in engine.getProperty('voices') if v.name == VOICE_NAME][0]
	engine.setProperty('voice', voice.id)
	d = root_dir + 'mp3/' + filename[:-4] + '_' + VOICE_NAME.lower() + '.mp3'
	engine.save_to_file(txt, d)
	engine.runAndWait()
	engine.stop()

print('Done!')
# %%
