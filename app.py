import json
import logging
import re

import pymorphy2
from flask import Flask, request


morph = pymorphy2.MorphAnalyzer()
app = Flask(__name__)


logging.basicConfig(level=logging.DEBUG)


# Задаем параметры приложения Flask.
@app.route("/", methods=['POST'])
def main():
    # Функция получает тело запроса и возвращает ответ.
    logging.info('Request: %r', request.json)

    response = switch_state(request.json)
    response = {
        'version': request.json['version'],
        'session': request.json['session'],
        'response': {
            'end_session': False,
            'text': response['text'],
        }
    }

    logging.info('Response: %r', response)

    return json.dumps(
        response,
        ensure_ascii=False,
        indent=2
    )


profiles = {}
sessions = {}


def switch_state(request):
    user_id = request['session']['user_id']
    if user_id not in profiles:
        profiles[user_id] = {}
    profile = request['profile'] = profiles[user_id]

    utterance = request['utterance'] = request['request']['original_utterance']
    words = request['words'] = re.findall(r'\w+', utterance, flags=re.UNICODE)
    request['lemmas'] = [morph.parse(word)[0].normal_form for word in words]

    session_id = request['session']['session_id']
    if session_id not in sessions:
        state = sessions[session_id] = collect_profile(profile)
        response = state.send(None)
    else:
        state = sessions[session_id]
        response = state.send(request)

    return response


def collect_profile(profile):
    req = yield {'text': 'Кого ты ищешь - девушку или парня?'}
    while True:
        lemmas = req['lemmas']

        if any(w in lemmas for w in ['парень', 'молодой', 'мч', 'мужчина', 'мальчик']):
            gender = 'male'
            break
        elif any(w in lemmas for w in ['девушка', 'женщина', 'тёлка', 'телок', 'девочка']):
            gender = 'female'
            break

        req = yield {'text': 'Скажи или слово "девушка", или слово "парень"'}
    profile['gender'] = gender

    req = yield {'text': 'Сколько тебе лет?'}
    while True:
        utterance = req['utterance']

        if not re.fullmatch(r'\d+', utterance):
            req = yield {'text': 'Назови число'}
            continue
        age = int(utterance)

        if age < 18:
            yield {'text': 'Навык доступен только для людей не младше 18 лет :('}
            return
        if age > 100:
            yield {'text': 'Некорректный возраст, назови возраст ещё раз'}
            continue
        break
    profile['age'] = age

    req = yield {'text': 'В каком городе ты живёшь?'}
    utterance = req['utterance']
    # TODO: Проверить город
    profile['city'] = utterance
