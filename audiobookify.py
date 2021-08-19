# %% 
# The pdf that this thing has been delevoped on can be found here: https://ia903205.us.archive.org/11/items/prime_intellect/prime_intellect.pdf

import pdfreader
import re
from spellchecker import SpellChecker
import os
import pyttsx3
from time import sleep

# %% Settings

TEST = False # Change to True if you want to save sample mp3s of all available voices on your system.
VOICE_NAME = 'Karen' # Choose which voice to use. If TEST == True, then a sample of all available voices on your system will be saved to the project location when you run the script. After listening in, you can make your pick and assign VOICE_NAME.
root_dir = os.path.dirname(os.path.abspath(__file__))+'/'
filename = [f for f in os.listdir(root_dir) if '.pdf' in f[-4:]][0] # Gets the first pdf file in the project directory. 
fd = open(root_dir + filename, "rb")
viewer = pdfreader.SimplePDFViewer(fd)

#%% Reading pdf and saving to txt file.
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

f = open(root_dir + filename[:-4] + '_direct_read.txt', "w")
f.write(s)
f.close()

# %% Cleaning up string. (This is adapted for one specific pdf and need to be adapted according to the pdf you use as input.)
s2 = re.sub('The Metamorphosis of Prime Intellect: Chapter 1http://www.kuro5hin.org/prime-intellect/mopiall.html[0-9]+ of 13423/03/08 23:03', ' ', s)

s2 = re.sub('(?<=[a-z])(?=[A-Z])',' ', s2) # Separating chapter title endings from begining of chapter text
s2 = re.sub('  \* (?=Chapter .+:   )',' \n\n', s2) # Spacing chapter beginnings
s2 = re.sub('(?<=(\.|\?|\!))(?=\"?[A-z])',' ', s2) # Adding missing spaces after sentences
s2 = re.sub('(?<=(\,|\;))(?=[A-z])',' ', s2) # Adding missing spaces in sentences
s2 = re.sub('(\*|\>)', '\n- ', s2) # Standardizing dialogue character
s2 = re.sub('(?<=\")(?=\")', ' \n', s2) # Spacing dialogue

s2 = re.sub(',\"', '\",', s2) # Relocating quotes that ended up on wrong sides of commas
s2 = re.sub('\? \"(?=[A-Z])','\?\" ', s2)  # Relocating quotes that ended up on wrong sides of spaces

names = ['caroline', 'timothy', 'mamba', 'glasslike'] # These are some words that occur in the book that SpellChecker doesn't recognize. Do adjust according to the source pdf.
names += [n+'s' for n in names] # Adding possesives
spell = SpellChecker()
spell.word_frequency.load_words(names)

# Doing a bit of complicated text cleanup of mess caused by pdfreader not interpreting linebreaks as anything.

def get_most_probable_split(word):
	# This tests all ways of splitting a word into two and returns the most likely split as a list with lengt 2.
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
	return [word[:max_prob_i], word[max_prob_i:]]

# Splitting inacurately joined words with the help of SpellChecker...
wrong_word_prob_cutoff = 10 ** (-7)

def double_word_splitter(word,sep):
	# This splits words that use some kind of separator, runs get_most_probable_split() on each sub-word, and then joins the words together again with the original separator.
	d_w = []
	for sub_word in word.split(sep):
		clean_sub_word = re.sub('[^a-zA-Z]+', '', sub_word).lower()
		if len(clean_sub_word) > 0:
			if spell.word_probability(clean_sub_word) <= wrong_word_prob_cutoff:
				d_w.append(' '.join(get_most_probable_split(sub_word)))
			else:
				d_w += [sub_word]
		else:
			d_w.append(sub_word)
	d_w = sep.join(d_w)
	return [d_w]

s3 = []
for word in s2.split(' '): # Looping through all the words in the book.
	clean_word = re.sub('[^a-zA-Z]+', '', word).lower()
	if len(clean_word) > 0:
		# Dealing with words with hyphens
		if '-' in word[:-1]:
			s3 += double_word_splitter(word,'-')
		elif '_' in word[:-1]:
			s3 += double_word_splitter(word,'_')
		# Dealing with non-hyphen words
		else:
			if spell.word_probability(clean_word) <= wrong_word_prob_cutoff:
				s3 += get_most_probable_split(word)
			else:
				s3 += [word]
	else:
		s3 += [word]


txt = ' '.join(s3)
f = open(root_dir + filename[:-4] + '.txt', "w")
f.write(txt)
f.close()

# %% Exporting to mp3

engine = pyttsx3.init()

if TEST:
	voices = engine.getProperty('voices')
	for voice in voices:
		engine.setProperty('voice', voice.id)
		engine.save_to_file(txt[200:1000],root_dir + 'test_' + voice.name + '.mp3')
		engine.runAndWait()
		sleep(1)

else:
	voice = [v for v in engine.getProperty('voices') if v.name == VOICE_NAME][0]
	engine.setProperty('voice', voice.id)
	d = root_dir + filename[:-4] + '_' + VOICE_NAME.lower() + '.mp3'
	engine.save_to_file(txt, d)
	engine.runAndWait()
	engine.stop()

print('Done!')
# %%
