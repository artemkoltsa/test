import json
import logging
import os
import re
import threading
import random

import flask
import pymorphy2
from flask import Flask, request
from werkzeug.local import LocalProxy

from match import get_match_score
from utils import NamedEntitiesRepository, filter_stop_words


PROFILE_FILE = 'profiles.json'


morph = pymorphy2.MorphAnalyzer()
app = Flask(__name__)

names_repository = NamedEntitiesRepository()


logging.basicConfig(level=logging.DEBUG)


@app.route("/", methods=['POST'])
def main():
    logging.info('Request: %r', request.json)

    result = switch_state(request.json)
    response = {
        'version': request.json['version'],
        'session': request.json['session'],
        'response': {
            'end_session': result.get('end_session', False),
            'text': result['text'],
        }
    }

    logging.info('Response: %r', response)

    return json.dumps(
        response,
        ensure_ascii=False,
        indent=2
    )


def load_profiles():
    if not os.path.isfile(PROFILE_FILE):
        return {}

    with open(PROFILE_FILE) as f:
        return json.load(f)


profiles = load_profiles()
profile_lock = threading.RLock()

sessions = {}
session_lock = threading.RLock()


def switch_state(request):
    utterance = request['utterance'] = request['request']['command'].rstrip('.')
    words = request['words'] = re.findall(r'\w+', utterance, flags=re.UNICODE)
    request['lemmas'] = [morph.parse(word)[0].normal_form for word in words]

    session_id = request['session']['session_id']
    with session_lock:
        if session_id not in sessions:
            state = sessions[session_id] = collect_profile()
            request = None
        else:
            state = sessions[session_id]
    flask.g.input = request
    response = next(state)

    return response


input = LocalProxy(lambda: flask.g.input)


def say(*texts, end_session=False):
    return {'text': random.choice(texts), 'end_session': end_session}


def collect_profile():
    profile = {}

    yield say('Привет! Кого ты ищешь - девушку или парня?',
              'Привет, кого будем искать? Девушку или парня?')
    while True:
        lemmas = input['lemmas']

        if any(w in lemmas for w in ['парень', 'молодой', 'мч', 'мужчина', 'мальчик']):
            gender = 'female'
            break
        elif any(w in lemmas for w in ['девушка', 'женщина', 'тёлка', 'телок', 'девочка']):
            gender = 'male'
            break

        yield say('Скажи или слово "девушка", или слово "парень"')
    profile['gender'] = gender

    yield say('Я смогу тебе помочь! Как тебя зовут?',
              'Отлично! Назови свое имя.')

    while True:
        utterance = input['utterance']
        name = names_repository.try_get_name(utterance)
        if name is not None:
            break

        yield say('Первый раз слышу такое имя. Назови как в паспорте написано.')

    profile['name'] = name

    yield say('Сколько тебе лет?', 'Назови свой возраст.')
    while True:
        utterance = input['utterance']

        if not re.fullmatch(r'\d+', utterance):
            yield say('Назови число')
            continue
        age = int(utterance)

        if age < 18:
            yield say('Навык доступен только для людей не младше 18 лет, сорри :(',
                      end_session=True)
            return
        if age > 100:
            yield say('Выглядишь моложе. Назови свой настоящий возраст :)')
            continue
        break
    profile['age'] = age

    yield say('А в каком городе ты живёшь?')
    while True:
        utterance = input['utterance']

        if names_repository.try_get_city(utterance) is not None:
            break

        yield say('Я не знаю такого города. Назови его полное название.')
    profile['city'] = utterance

    yield say('Расскажи, где ты работаешь или учишься?')
    profile['occupation'] = filter_stop_words(input['lemmas'])

    yield say('Чем ты занимаешься в свободное время? Какие у тебя хобби?')
    profile['hobbies'] = filter_stop_words(input['lemmas'])

    yield say('Какую музыку ты слушаешь? Назови пару исполнителей.')
    profile['music'] = filter_stop_words(input['lemmas'])

    candidates = [value for id, value in profiles.items()
                  if get_match_score(profile, value) > 0]
    if not candidates:
        yield say('Отлично! Тебе осталось сообщить свой номер телефона. Начинай с "восьмёрки". ' +
                  'Я проигнорирую все слова в твоей фразе, кроме чисел.')
        while True:
            utterance = input['utterance']
            phone = re.sub(r'\D', r'', utterance)

            yield say('Я правильно распознала твой номер телефона?')
            lemmas = input['lemmas']

            if any(w in lemmas for w in ['да', 'правильно']):
                break

            yield say('Скажи свой номер ещё раз')
        profile['phone'] = phone

        session_id = input['session']['session_id']
        with profile_lock:
            profiles[session_id] = profile
            with open('profiles.json', 'w') as f:
                json.dump(profiles, f)

        if gender == 'male':
            text = 'Ура, я добавила тебя в базу! ' + \
                   'Как только навыком воспользуется подходящая тебе девушка, я сообщу ей твои контакты!'
        else:
            text = 'Ура, я добавила тебя в базу! ' + \
                   'Как только навыком воспользуется подходящий тебе парень, я сообщу ему твои контакты!'
        yield say(text, end_session=True)
        return

    best_candidate = max(candidates, key=lambda value: get_match_score(profile, value))
    if gender == 'male':
        text = 'Кажется, я знаю одну девушку, которая может тебе понравиться. Её зовут {}, ей {}. ' \
               'Ты можешь позвонить ей по номеру: {}.'.format(
            best_candidate['name'].capitalize(), best_candidate['age'], best_candidate['phone'])
    else:
        text = 'Кажется, я знаю одного парня, который может тебе понравиться. Его зовут {}, ему {}. ' \
               'Ты можешь позвонить ему по номеру: {}.'.format(
            best_candidate['name'].capitalize(), best_candidate['age'], best_candidate['phone'])

    commons = set(profile['hobbies']) & set(best_candidate['hobbies'])
    if commons:
        text += '\n\nУ вас есть общие хобби: {}.'.format(', '.join(commons))

    commons = set(profile['music']) & set(best_candidate['music'])
    if commons:
        text += '\n\nВы любите одну и ту же музыку, например: {}.'.format(', '.join(commons))

    yield say(text, end_session=True)
