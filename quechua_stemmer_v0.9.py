#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import sys
import re

nominal_suffixes = {
	1:["chá", "cha", "chu", "ču", "chuch", "chus", "chusinam", "má", "m", "mi", "qa", "ri", "si", "ŝi", "ŝ", "s", "yá", "hina"], # before removing 'ŝ'/'s', test 'paŝ'/'pas'
	2:["pas", "paŝ"],
	3:["wan"],
	4:["kama", "man", "manta", "n", "p", "pa", "pi", "paq", "rayku", "kta", "ta", "piwan"], # before removing 'pa', test 'sapa' #before removing 'kta' test 'chik' [Genitive Cuzco/Bolivia : #before removing 'q' test 'niyuq', 'yuq', 'ni', 'niraq']
	5:["kuna", "kunaq", "kunag", "pura"],
	6:["n", "nchik", "nčik", "nchis", "nku", "y", "yki", "ykichik", "ykichis"],
	7:["sapa", "yuq", "niq", "llanti", "nti", "niqlla", "yuqlla"],
	8:["cha", "su", "ŝu", "niraq", "ni", "ñi"],
	9:["pti", "spa", "ŝpa", "sqa", "ŝqa", "šqa","na", "stin", "q", "qi","y"] # deverbal noun -> go to verbal suffixes 12
}

verbal_suffixes = {
	1:["chá", "cha", "chu", "ču", "chuch", "chus", "chusinam", "má", "m", "mi", "qa", "ri", "si", "ŝi", "ŝ", "s", "yá", "hina"], 
		# before removing 'qa', test 'sqa' 
		# before removing 'ŝ'/'s', test 'paŝ'/'pas'
	2:["taq"],
	3:["hina", "puni", "pas", "paŝ", "ña", "raq"], # cumulative
	4:["chwan"], # go to 11
	5:["man"],
	6:["n", "nchik", "nčik", "nchis", "nku", "y", "yki", "ykichik", "ykichis", "ykichiq"], # before removing 'n', test 'sun'
	7:["chik", "ku"],
	8:["yman", "sun", "ŝun", "waq", "sqayki", "saq", "nqa", "y", "chun"], # go to 11
	9:["chun", "ni",  "ñi", "nki", "n", "nchik", "nčik", "y", "sunki", "yki"],
	10:["rqa", "sqa", "ŝqa", "šqa"],
	11:["chka"],
	12:["su", "ŝu", "wa"],
	13:["lla"],
	14:["tamu","mu", "ku", "pu"], # cumulative mu - ku -pu #before removing 'ku', test 'paku' and 'yku'
	15:["chi"],
	16:["paku", "ysi", "rpari"],
	17:["yku", "rqu"], # cumulative
	18:["lli", "ya", "ymana"], # verbalizers (on nominal root), end of parsing #before removing 'ya', test 'qya, raya, naya, paya'
	19:["qya", "raya", "ykacha", "kacha", "rari", "na", "naya", "pa", "paya"],
	20:["tya", "pya", "ri"]
}


def multiple_stems(string, cur_len, suffixes, ordered):
	for suf in suffixes:
		if string.endswith(suf):
			if suf == 'ku' and string.endswith(('yku', 'paku')):
				return (string, cur_len)
			l = len(suf)
			if len(string)-l > 2:
				string = string[:-l]
				cur_len -= l
				if not ordered:
					suffixes.remove(suf)
					(string, cur_len) = multiple_stems(string, cur_len, suffixes, False)
					break
			else:
				return (string, cur_len-l)

	return (string, cur_len)


def stemmer(word):

	L = len(word)

# Try nominal stemming	
	i=1
	current_len = L
	current_word = word
	
	stem_history = ""
	
	dico = {}
	que_lexicon_f = open('lexicon_pos.txt', 'r')
	for lines in que_lexicon_f:
		entry, pos = lines.split('\t')
		dico[entry] = pos
	
	if current_word in dico:
		return (word, current_word, dico[current_word])
	
	deverbal_root = "" #For deverbal nouns 
	
	while i < 10 and current_len > 4:
		for suf in nominal_suffixes[i]:
			if current_word.endswith(suf):
				if suf=='hina' and current_word.endswith('-hina'):
					stem_history = "|-hina" + stem_history
					return current_word[:-5]
				if i==1:
					if suf == 's' or suf == 'ŝ':
						if current_word.endswith(('paŝ','pas')):
							current_word = current_word[:-3]
							current_len -= 3
							i = 2
							break
						elif current_word.endswith(('ykichis', 'nchis')):
							i = 5
							break
					elif suf =='qa' and current_word.endswith(('sqa', 'ŝqa', 'šqa')):
						i=8
						break
				elif i==4:
					if suf == 'pa':
						if current_word.endswith('sapa') and current_len > 6:
							current_word = current_word[:-4]
							current_len -= 4
							i = 7
							break
						elif current_word.endswith(('spa', 'ŝpa')):
							i = 8
							break
					elif suf == 'kta':
						if current_word.endswith('nchikta'):
							current_word = current_word[:-7]
							current_len -= 5
							i = 6
							break
						elif current_word.endswith('nčikta'):
							current_word = current_word[:-6]
							current_len -= 4
							i = 6
							break
						elif current_word.endswith('ykichikta'):
							current_word = current_word[:-9]
							current_len -= 7
							i = 6
							break

				l = len(suf)
				if current_len - l > 2:
					current_word = current_word[:-l]
					current_len -= l
					
					if i==9:
						deverbal_root = current_word
					
					#Testing if word is in Spanish
					#nomreg = r"\b"+ re.escape(current_word)+r"\b"
					#if re.search(nomreg, es_dict):
					#	return (word, current_word, 'E')
		i+=1
	

	nominal_root = current_word
	
# Try verbal stemming

	#""" Case of the deverbal nouns """
	if deverbal_root != "":
		i = 12
		while i < 19 and current_len > 4:
			for suf in verbal_suffixes[i]:
				if i==14:
					(current_word,current_len) = multiple_stems(current_word, current_len, verbal_suffixes[i], True)
				elif i==18:
					(current_word,current_len) = multiple_stems(current_word, current_len, verbal_suffixes[i], False)
				else:
					if current_word.endswith(suf):
						l = len(suf)
					elif i==19 and suf=='ya':
						if current_word.endswith(('qya','raya','naya','paya')):
								break
								
						if current_len - l > 2:
							current_word = current_word[:-l]
							current_len -= l
							break
			i += 1
		
		deverbal_root = current_word
		
	#""" General case """
	current_len = L
	current_word = word
	i=1
	while i < 21 and current_len > 4:
		for suf in verbal_suffixes[i]:
			if i==3 or i == 18:
				(current_word,current_len) = multiple_stems(current_word, current_len, verbal_suffixes[i], False)
			elif i==14:
				(current_word,current_len) = multiple_stems(current_word, current_len, verbal_suffixes[i], True)
		
			else:
				if current_word.endswith(suf):
					l = len(suf)
					if i==1:
						if suf=='ŝ' or suf=='s':
							if current_word.endswith(('paŝ', 'pas')):
								current_word = current_word[:-3]
								current_len -= 3
								i=2
								break
							elif current_word.endswith('ykichis'):
								current_word = current_word[:-7]
								current_len -= 7
								i = 5
								break
						elif suf=='qa':
							if current_word.endswith(('ŝqa', 'sqa', 'rqa')):
								i=9
								break
				
					elif i==6 and suf == 'n':
						if current_word.endswith(('sun', 'ŝun')):
							i=7
							break
								
					elif i==19 and suf=='ya':
						if current_word.endswith(('qya','raya','naya','paya')):
							break
				
					if current_len - l > 2:
						current_word = current_word[:-l]
						current_len -= l
						
						if i==4 or i==8:
							i=10
						
						elif i==19:
							return (word, current_word, 'N')
							
		i += 1

	verbal_root = current_word

# Choose between the roots
	if (deverbal_root != "") and (len(deverbal_root) < len(verbal_root)):
		verbal_root = deverbal_root

	if len(nominal_root) <= len(verbal_root):
		return (word, nominal_root, 'N')
	else:
		return (word, verbal_root, 'V')
	

if __name__ == '__main__':
	
	if len(sys.argv) != 2:
		print ('Usage : python quechua_stemmer.py infile')
		sys.exit()
	else:
		filename = sys.argv[1]
		with open(filename) as f:
			for line in f:
				word = line.strip('\n')
				res = stemmer(word)
				print(res[0]+'\t'+res[1]+'\t'+res[2])

