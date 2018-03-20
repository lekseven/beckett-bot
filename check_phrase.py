# -*- coding: utf8 -*-
import data


def check_word(base, word):
    # check pattern, where word = base(known) + ending(unknown)
    if word == base:
        return True
    if word.find(base) != 0:
        return False
    ending = word[len(base):]
    return ending in data.dataEndings


def find_key(word):
    for key, bases in data.dataKeys.items():
        for base in bases:
            if check_word(base, word):
                return key
    return False


def check_args(args):
    for word in args:
        found_key = find_key(word)
        if found_key and found_key in data.responsesData:
            return found_key
    return False