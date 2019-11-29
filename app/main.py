import json
import os
import random
import bottle
import copy

from api import ping_response, start_response, move_response, end_response

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
    global horizontalDirection, verticalDirection, lastMove, occupiedZones
    horizontalDirection = 'right'
    verticalDirection = 'up'

    data = bottle.request.json

    print(json.dumps(data))

    color = "#00FF00"

    return start_response(color)


@bottle.post('/move')
def move():
    global horizontalDirection, verticalDirection, lastMove, occupiedZones
    data = bottle.request.json

    head = copy.deepcopy(data["you"]["body"][0])
    body = copy.deepcopy(data["you"]["body"][1])
    occupiedZones = copy.deepcopy(data["you"]["body"])

    print(head)

    if head["y"] == 1:
        verticalDirection = 'down'

    if head["y"] == 13:
        verticalDirection = 'up'

    if head["x"] == 1:
        horizontalDirection = 'right'

    if head["x"] == 13:
        horizontalDirection = 'left'


    if head["y"] == 1:
        if lastMove == 'right' or lastMove == 'left':
            move = verticalDirection
        else:
            move = horizontalDirection
    elif head["y"] == 13:
        if lastMove == 'right' or lastMove == 'left':
            move = verticalDirection
        else:
            move = horizontalDirection
    else:
        move = verticalDirection

    if not is_safe(projected_location(copy.deepcopy(head), move)):
        move = find_safe(copy.deepcopy(head))

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


def is_safe(location):
    global occupiedZones
    return not location in occupiedZones


def find_safe(head):
    if is_safe(projected_location(copy.deepcopy(head), "left")):
        direction = "left"
    elif is_safe(projected_location(copy.deepcopy(head), "right")):
        direction = "right"
    elif is_safe(projected_location(copy.deepcopy(head), "up")):
        direction = "up"
    else:
        direction = "down"

    return direction


def projected_location(head, direction):
    if direction == "up":
        head["y"] = head["y"] - 1
    elif direction == "down":
        head["y"] = head["y"] + 1
    elif direction == "right":
        head["x"] = head["x"] - 1
    elif direction == "left":
        head["x"] = head["x"] + 1

    return head


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug=os.getenv('DEBUG', True)
    )
