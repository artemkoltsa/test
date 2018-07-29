import logging
import random
import threading
from werkzeug.local import LocalProxy

import flask


logging.basicConfig(level=logging.DEBUG)


request = LocalProxy(lambda: flask.g.request)


class AliceSkill(flask.Flask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._sessions = {}
        self._session_lock = threading.RLock()

        @self.before_request
        def save_request():
            flask.g.request = flask.request.json

    def script(self, generator):
        @self.route("/", methods=['POST'])
        def handle_post():
            logging.info('Request: %r', request)

            content = self._switch_state(generator)
            response = {
                'version': request['version'],
                'session': request['session'],
                'response': content,
            }

            logging.info('Response: %r', response)
            return flask.jsonify(response)

        return generator

    def _switch_state(self, generator):
        session_id = request['session']['session_id']
        with self._session_lock:
            if session_id not in self._sessions:
                state = self._sessions[session_id] = generator()
            else:
                state = self._sessions[session_id]
        content = next(state)

        return content


def say(*texts, **response_kwargs):
    response = response_kwargs
    response['text'] = random.choice(texts)
    if 'end_session' not in response:
        response['end_session'] = False
    return response
