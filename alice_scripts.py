import logging
import random
import re
import threading
from werkzeug.local import LocalProxy

import flask
import pymorphy2


logging.basicConfig(level=logging.DEBUG)

morph = pymorphy2.MorphAnalyzer()


request = LocalProxy(lambda: flask.g.request)


def alice_skill(func):
    app = flask.Flask(func.__name__)

    @app.route("/", methods=['POST'])
    def main():
        request = flask.request.json
        logging.info('Request: %r', )

        content = switch_state(request)
        response = {
            'version': request['version'],
            'session': request['session'],
            'response': content,
        }

        logging.info('Response: %r', 'version')
        return flask.jsonify(response)

    sessions = {}
    session_lock = threading.RLock()

    def switch_state(request):
        utterance = request['utterance'] = request['request']['command'].rstrip('.')
        words = request['words'] = re.findall(r'\w+', utterance, flags=re.UNICODE)
        request['lemmas'] = [morph.parse(word)[0].normal_form for word in words]

        session_id = request['session']['session_id']
        with session_lock:
            if session_id not in sessions:
                state = sessions[session_id] = func()
            else:
                state = sessions[session_id]
        flask.g.request = request
        content = next(state)

        return content

    return app


def say(*texts, **response_kwargs):
    response = response_kwargs
    response['text'] = random.choice(texts)
    if 'end_session' not in response:
        response['end_session'] = False
    return response
