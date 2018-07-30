import json
import logging
import os
import re
import threading

from alice_scripts import Skill, request, say, suggest
from match import get_match_score
from utils import NamedEntitiesRepository, filter_stop_words


logging.basicConfig(level=logging.DEBUG)

skill = Skill(__name__)


@skill.script
def run_script():
    profile = {
        'gender': (yield from ask_gender()),
        'name': (yield from ask_name()),
        'age': (yield from ask_age()),
        'city': (yield from ask_city()),
    }
    yield from add_tags(profile)

    candidates = [value for id, value in profiles.items()
                  if get_match_score(profile, value) > 0]
    if not candidates:
        profile['phone'] = yield from ask_phone()
        yield from add_to_db(profile)
        return

    best_candidate = max(candidates, key=lambda value: get_match_score(profile, value))
    yield from show_match(profile, best_candidate)


def ask_gender():
    yield say('Привет! Кого ты ищешь - девушку или парня?',
              'Привет, кого будем искать? Девушку или парня?',
              suggest('Девушку', 'Парня'))
    while True:
        if request.has_lemmas('парень', 'человек', 'мч', 'мужчина'):
            return 'female'
        if request.has_lemmas('девушка', 'женщина'):
            return 'male'

        yield say('Скажи или слово "девушка", или слово "парень"',
                  suggest('Девушка', 'Парень'))


names_repository = NamedEntitiesRepository()


def ask_name():
    yield say('Я смогу тебе помочь! Как тебя зовут?',
              'Отлично! Назови свое имя.')
    while True:
        name = names_repository.try_get_name(request.command)
        if name is not None:
            return name

        yield say('Первый раз слышу такое имя. Назови как в паспорте написано.')


def ask_age():
    yield say('Сколько тебе лет?', 'Назови свой возраст.')
    while True:
        if not re.fullmatch(r'\d+', request.command):
            yield say('Назови число')
            continue
        age = int(request.command)

        if age < 18:
            yield say('Навык доступен только для людей не младше 18 лет, сорри :(',
                      end_session=True)
            return None
        if age > 100:
            yield say('Выглядишь моложе. Назови свой настоящий возраст :)')
            continue
        return age


def ask_city():
    yield say('А в каком городе ты живёшь?')
    while True:
        if names_repository.try_get_city(request.command) is not None:
            return request.command

        yield say('Я не знаю такого города. Назови его полное название.')


def add_tags(profile):
    yield say('Расскажи, где ты работаешь или учишься?')
    profile['occupation'] = filter_stop_words(request.lemmas)

    yield say('Чем ты занимаешься в свободное время? Какие у тебя хобби?')
    profile['hobbies'] = filter_stop_words(request.lemmas)

    yield say('Какую музыку ты слушаешь? Назови пару исполнителей.')
    profile['music'] = filter_stop_words(request.lemmas)


def ask_phone():
    yield say('Отлично! Тебе осталось сообщить свой номер телефона. Начинай с "восьмёрки". ' +
              'Я проигнорирую все слова в твоей фразе, кроме чисел.')
    while True:
        phone = re.sub(r'\D', r'', request.command)

        yield say('Я правильно распознала твой номер телефона?',
                  suggest('Правильно', 'Давай ещё раз'))
        if request.has_lemmas('да', 'правильно'):
            return phone

        yield say('Скажи свой номер ещё раз')


def add_to_db(profile):
    session_id = request.session_id
    with profile_lock:
        profiles[session_id] = profile
        with open('profiles.json', 'w') as f:
            json.dump(profiles, f)

    if profile['gender'] == 'male':
        text = 'Ура, я добавила тебя в базу! ' + \
               'Как только навыком воспользуется подходящая тебе девушка, я сообщу ей твои контакты!'
    else:
        text = 'Ура, я добавила тебя в базу! ' + \
               'Как только навыком воспользуется подходящий тебе парень, я сообщу ему твои контакты!'
    yield say(text, end_session=True)


def show_match(profile, best_candidate):
    if profile['gender'] == 'male':
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


PROFILE_FILE = 'profiles.json'


def load_profiles():
    if not os.path.isfile(PROFILE_FILE):
        return {}

    with open(PROFILE_FILE) as f:
        return json.load(f)


profiles = load_profiles()
profile_lock = threading.RLock()
