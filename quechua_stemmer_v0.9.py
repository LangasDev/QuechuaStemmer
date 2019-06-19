#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import sys
import re
import os.path
from pathlib import Path


nominal_suffixes = {
	1:["chá", "cha", "chu", "ču", "chuch", "chus", "chusinam", "má", "m", "mi", "qa", "ri", "si", "ŝi", "ŝ", "s", "yá"], # before removing 'ŝ'/'s', test 'paŝ'/'pas'
	2:["ña", "hina", "pis", "pas", "paŝ", "puni"], # cumulative
	3:["wan"],
	4:["kama", "man", "manta", "n", "p", "pa", "pi", "paq", "rayku", "kta", "ta", "piwan"], # before removing 'pa', test 'sapa' 'chik' [Genitive Cuzco/Bolivia : #before removing 'q' test 'niyuq', 'yuq', 'ni', 'niraq']
	5:["kuna", "kunaq", "kunag", "pura"],
	6:["n", "nchik", "nčik", "nchis", "nku", "y", "yki", "ykichik", "ykichis"],
	7:["sapa", "yuq", "niq", "llanti", "nti", "niqlla", "yuqlla"],
	8:["su", "ŝu", "niraq", "ni", "ñi"],
	9:["cha", "pti", "spa", "ŝpa", "sqa", "ŝqa", "šqa","na", "stin", "qi","q","y"]
}


verbal_suffixes = {
	1:["chá", "cha", "chu", "ču", "chuch", "chus", "chusinam", "má", "m", "mi", "qa", "ri", "si", "ŝi", "ŝ", "s", "yá", "hina"], 
		# before removing 'qa', test 'sqa' 
		# before removing 'ŝ'/'s', test 'paŝ'/'pas'
	2:["taq"],
	3:["hina", "puni", "pis", "pas", "paŝ", "ña", "raq"], # cumulative
	4:["chwan"], # go to 11
	5:["man"],
	6:["n", "nchik", "nčik", "nchis", "nku", "y", "yki", "ykichik", "ykichis", "ykichiq"], # before removing 'n', test 'sun'
	7:["chik", "ku"],
	8:["yman", "sun", "ŝun", "waq", "sqayki", "saq", "ŝaq", "nqa", "y", "chun"], # go to 11
	9:["chun", "ni",  "ñi", "nki", "n", "nchik", "nčik", "y", "sunki", "yki"],
	10:["rqa", "sqa", "ŝqa", "šqa"],
	11:["chka"],
	12:["su", "ŝu", "wa"],
	13:["lla"],
	14:["tamu","mu", "ku", "pu"], # cumulative mu - ku -pu #before removing 'ku', test 'paku' and 'yku'
	15:["chi"],
	16:["paku", "ysi", "rpari"],
	17:["naku", "yku", "rqu"], # cumulative
	18:["qya", "raya", "ykacha", "kacha", "rari", "na", "naya", "pa", "paya"],
	19:["cha","lli", "ya", "ymana"], # verbalizers (on nominal root), end of parsing #before removing 'ya', test 'qya, raya, naya, paya'
	20:["ri"]
}

V = ['a', 'i', 'u', 'e', 'o']
C = ['ĉ', 'č', 'h', 'k', 'l', 'm', 'n', 'ñ', 'o', 'p','q', 'r','s', 'ŝ', 't', 'w', 'y']
ngrams = ['ch', 'll', 'sh', "ch'", "chh", "t'","th", "tt", "p'", "ph", "pp", "q'", 'qh', 'qq', "k'", "kh"]

# Compute the phonological pattern
def get_phon_pattern(string):
	for n in ngrams:
		string = string.replace(n, 'C')
		
	characters = list(string)
	
	scheme = ''
	for c in characters:
		if c in V:
			scheme += 'V'
		else:
			scheme += 'C'
	
	return scheme
	
# For the roots with 2 syllables, the scheme should be (C)V(C)-CV	
def is_accurate_scheme(string):
	if ( string == 'VCV' or string == 'CVCV' 
		or string == 'VCCV' or string=='CVCCV' ):
		return True
	else:
		return False
	

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


def stemmer(word, dico):

	L = len(word)

# Try nominal stemming	
	i=1
	current_len = L
	current_word = word

	
	while i < 10 and current_len > 4:
		for suf in nominal_suffixes[i]:
			if current_word.endswith(suf):
				if suf=='hina' and current_word.endswith('-hina'):
					#stem_history = "|-hina" + stem_history
					current_word = current_word[:-5]
					current_len -= 5
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
				if current_len - l > 3 and not is_accurate_scheme(get_phon_pattern(current_word)):
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

# General case 
	current_len = L
	current_word = word
	i=1
	while i < 21 and current_len > 4:
		if i==3 or i == 18:
			(current_word,current_len) = multiple_stems(current_word, current_len, verbal_suffixes[i], False)
		elif i==14:
			(current_word,current_len) = multiple_stems(current_word, current_len, verbal_suffixes[i], True)
		
		else:
			for suf in verbal_suffixes[i]:
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
				
					if current_len - l > 2:
						current_word = current_word[:-l]
						current_len -= l
						
						if i==4 or i==8:
							i=10
						
						elif i==19:
							scheme = get_phon_pattern(current_word)
							if is_accurate_scheme(scheme):
								return (word, current_word, 'N', scheme)
							else:
								return (word, current_word, 'N', '')
							
		i += 1

	verbal_root = current_word

# Choose between the roots
	
	scheme_nom = get_phon_pattern(nominal_root)
	
	if is_accurate_scheme(scheme_nom):
		if nominal_root in dico:
			return (word, nominal_root, dico[nominal_root], scheme_nom)
		else:
			return (word, nominal_root, 'N', scheme_nom)
	else:
		
		scheme_verb = get_phon_pattern(verbal_root)
		if is_accurate_scheme(scheme_verb):
			if verbal_root in dico:
				return (word, verbal_root, dico[verbal_root], scheme_verb)
			else:
				return (word, verbal_root, 'V', scheme_verb)
		
		else:
			if len(nominal_root) <= len(verbal_root):
					return (word, nominal_root, 'N', "")
			else:
					return (word, verbal_root, 'V', "")
	

if __name__ == '__main__':
	
	if len(sys.argv) != 2:
		print ('Usage : python quechua_stemmer.py infile')
		sys.exit()
	else:
		filename = sys.argv[1]
		
		dic = {}
		dir_path = Path(os.path.dirname(os.path.realpath(__file__)))
		path_dict = dir_path / "lexicon_pos.txt"

		if os.path.exists(path_dict):
			que_lexicon_f = open(path_dict, 'r')
			for lines in que_lexicon_f:
				entry, pos = lines.strip('\n').split('\t')
				dic[entry] = pos
		
		with open(filename) as f:
			for line in f:
				word = line.strip('\n')
				res = stemmer(word, dic)
				print(res[0]+'\t'+res[1]+'\t'+res[2]+'\t'+res[3])

