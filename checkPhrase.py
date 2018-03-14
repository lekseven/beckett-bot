
# -*- coding: utf8 -*-
import data

def checkWord(base,word):
	# check pattern, where word = base(known) + ending(unknown)
	if word == base: return True
	if word.find(base) != 0: return False 
	ending = word[len(base):]
	return ending in data.dataEndings

def findKey(word):
	for key, bases in data.dataKeys.items():
		for base in bases:
			if checkWord(base,word): return key
	return False

def checkArgs(args):
	for word in args:
		found_key = findKey(word)
		if found_key: return found_key
    
    
