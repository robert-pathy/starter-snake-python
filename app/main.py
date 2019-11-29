import json
import os
import random
import bottle

from random import randint
import numpy as np
import tflearn
import math
from tflearn.layers.core import input_data, fully_connected
from tflearn.layers.estimator import regression
from statistics import mean
from collections import Counter

from api import ping_response, start_response, move_response, end_response, tfl_response

class Brain():
    def __init__(self, initial_games = 100, test_games = 100, goal_steps = 100, lr = 1e-2):
        self.initial_games = initial_games
        self.test_games = test_games
        self.goal_steps = goal_steps
        self.lr = lr
        self.vectors_and_keys = [
            [[-1, 0], 0],
            [[0, 1], 1],
            [[1, 0], 2],
            [[0, -1], 3]
            ]

    def model(self):
        network = input_data(shape=[None, 4, 1], name='input')
        network = fully_connected(network, 1, activation='linear', name='l1')
        network = regression(network, optimizer='adam', learning_rate=self.lr, loss='mean_square', name='target')
        model = tflearn.DNN(network, tensorboard_dir='log')
        return model

@bottle.post('/smart')
def smart():
    data = bottle.request.json

    print(model.predict([0,1,1]))

    return tfl_response('ok')

@bottle.route('/')
def index():
    return '''
    Battlesnake documentation can be found at
       <a href="https://docs.battlesnake.io">https://docs.battlesnake.io</a>.
    '''

@bottle.route('/static/<path:path>')
def static(path):
    """
    Given a path, return the static file located relative
    to the static folder.

    This can be used to return the snake head URL in an API response.
    """
    return bottle.static_file(path, root='static/')

@bottle.post('/ping')
def ping():
    """
    A keep-alive endpoint used to prevent cloud application platforms,
    such as Heroku, from sleeping the application instance.
    """
    return ping_response()

@bottle.post('/start')
def start():
    global model
    global horizontalDirection, verticalDirection, lastMove
    
    horizontalDirection = 'right'
    verticalDirection = 'up'

    brain = Brain()
    data = bottle.request.json

    model = brain.model()
    model.load('model/model.tfl')

    print(json.dumps(data))

    color = "#00FF00"

    return start_response(color)


@bottle.post('/move')
def move():
    global horizontalDirection, verticalDirection, lastMove
    data = bottle.request.json

    head = data["you"]["body"][0]
    body = data["you"]["body"][1]


    print(move)

    lastMove = move
    return move_response(move)


@bottle.post('/end')
def end():
    data = bottle.request.json

    """
    TODO: If your snake AI was stateful,
        clean up any stateful objects here.
    """
    print(json.dumps(data))

    return end_response()

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug=os.getenv('DEBUG', True)
    )
