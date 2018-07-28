import json
import logging
import os
import re
import threading
import random

import pymorphy2
from flask import Flask, request

from match import get_match_score
from utils import CityRepository, filter_stop_words


PROFILE_FILE = 'profiles.json'


morph = pymorphy2.MorphAnalyzer()
app = Flask(__name__)

city_repository = CityRepository()


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
    response = state.send(request)

    return response


def collect_profile():
    profile = {}

    text = random.choice(['Привет! Кого ты ищешь - девушку или парня?',
                          'Привет, кого будем искать? Девушку или парня?'])
    req = yield {'text': text}
    while True:
        lemmas = req['lemmas']

        if any(w in lemmas for w in ['парень', 'молодой', 'мч', 'мужчина', 'мальчик']):
            gender = 'female'
            break
        elif any(w in lemmas for w in ['девушка', 'женщина', 'тёлка', 'телок', 'девочка']):
            gender = 'male'
            break

        req = yield {'text': 'Скажи или слово "девушка", или слово "парень"'}
    profile['gender'] = gender

    text = random.choice(['Я смогу тебе помочь! Как тебя зовут?',
                          'Отлично! Назови свое имя.'])
    req = yield {'text': text}
    profile['name'] = req['lemmas'][-1]

    text = random.choice(['Сколько тебе лет?',
                          'Назови свой возраст.'])
    req = yield {'text': text}
    while True:
        utterance = req['utterance']

        if not re.fullmatch(r'\d+', utterance):
            req = yield {'text': 'Назови число'}
            continue
        age = int(utterance)

        if age < 18:
            req = yield {'text': 'Навык доступен только для людей не младше 18 лет, сорри :(',
                         'end_session': True}
            return
        if age > 100:
            req = yield {'text': 'Некорректный возраст, назови возраст ещё раз'}
            continue
        break
    profile['age'] = age

    req = yield {'text': 'А в каком городе ты живёшь?'}
    while True:
        utterance = req['utterance']

        if city_repository.try_get_city(utterance) is not None:
            break

        req = yield {'text': 'Я не знаю такого города. Назови город ещё раз.'}
    profile['city'] = utterance

    req = yield {'text': 'Расскажи, где ты работаешь или учишься?'}
    profile['occupation'] = filter_stop_words(req['lemmas'])

    req = yield {'text': 'Чем ты занимаешься в свободное время? Какие у тебя хобби?'}
    profile['hobbies'] = filter_stop_words(req['lemmas'])

    req = yield {'text': 'Какую музыку ты слушаешь? Назови пару исполнителей.'}
    profile['music'] = filter_stop_words(req['lemmas'])

    req = yield {'text': 'Отлично! Тебе осталось сообщить свой номер телефона. Начинай с "восьмёрки". ' +
                         'Я проигнорирую все слова в твоей фразе, кроме чисел.'}
    while True:
        utterance = req['utterance']
        phone = re.sub(r'\D', r'', utterance)

        req = yield {'text': 'Я правильно распознала твой номер телефона?'}
        lemmas = req['lemmas']

        if any(w in lemmas for w in ['да', 'правильно']):
            break

        req = yield {'text': 'Скажи свой номер ещё раз'}
    profile['phone'] = phone

    user_id = req['session']['user_id']
    with profile_lock:
        profiles[user_id] = profile
        with open('profiles.json', 'w') as f:
            json.dump(profiles, f)

    candidates = [value for id, value in profiles.items()
                  if user_id != id and get_match_score(profile, value) > 0]
    if not candidates:
        if gender == 'male':
            text = 'Ура, я добавила тебя в базу! ' + \
                   'Как только навыком воспользуется подходящая тебе девушка, я сообщу ей твои контакты!'
        else:
            text = 'Ура, я добавила тебя в базу! ' + \
                   'Как только навыком воспользуется подходящий тебе парень, я сообщу ему твои контакты!'
        req = yield {'text': text, 'end_session': True}
        return

    best_candidate = max(candidates, key=lambda value: get_match_score(profile, value))
    if gender == 'male':
        text = 'Кажется, я знаю одну девушку, которая может тебе понравиться. Её зовут {}, ей {}. ' \
               'Ты можешь позвонить ей по номеру: {}'.format(
            best_candidate['name'], best_candidate['age'], best_candidate['phone'])
    else:
        text = 'Кажется, я знаю одного парня, который может тебе понравиться. Его зовут {}, ему {}. ' \
               'Ты можешь позвонить ему по номеру: {}'.format(
            best_candidate['name'], best_candidate['age'], best_candidate['phone'])
    req = yield {'text': text, 'end_session': True}
