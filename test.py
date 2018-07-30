from alice_scripts import Skill, request, say, suggest


skill = Skill(__name__)


@skill.script
def run_script():
    yield say('Привет! Загадайте число от 1 до 100, а я его отгадаю. '
              'Скажите, когда будете готовы.')

    lo = 1
    hi = 100
    while lo < hi:
        middle = (lo + hi) // 2
        yield say('Ваше число больше {}?'.format(middle),
                  'Правда ли, что число больше {}?'.format(middle),
                  suggest('Да', 'Нет'))

        while True:
            if request.has_lemmas('нет', 'не'):
                hi = middle
                break
            elif request.has_lemmas('да', 'ага'):
                lo = middle + 1
                break
            else:
                yield say('Я не поняла ваш ответ. Скажите "да" или "нет"',
                          suggest('Да', 'Нет'))

    yield say('Думаю, вы загадали число {}!'.format(lo),
              end_session=True)
