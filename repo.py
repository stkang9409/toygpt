import data
import data_ko
import random


def defined_topics(lang='ko'):
    if lang == 'ko':
        return data_ko.situations.keys()

    return data.situations.keys()


def get_situations(topic, lang='ko'):
    if lang == 'ko':
        return data_ko.situations[topic]

    return data.situations[topic]


def get_opponent(lang='ko'):
    if lang == 'ko':
        opponent = data_ko.opponents
    else:
        opponent = data.opponents

    return opponent[random.randint(0, len(opponent) - 1)]
