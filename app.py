from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import numpy as np
import random
import string
from shapely.geometry import Polygon
import eventlet
eventlet.monkey_patch()

app = Flask(__name__)
socketio = SocketIO(app)

def random_name():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def create_polygon(center, radius, num_vertices):
    angles = np.linspace(0, 2 * np.pi, num_vertices, endpoint=False)
    angles += np.random.rand() * 2 * np.pi / num_vertices
    points = np.stack((np.cos(angles), np.sin(angles)), axis=1)
    points *= radius
    points += center
    return points

class Bot:
    def __init__(self, name):
        self.name = name
        self.color = tuple(np.random.randint(0, 256, 3).tolist())
        self.area = 0
        self.soldiers = 1000
        self.polygons = []

    def update_soldiers(self):
        self.soldiers += self.area * 2

    def move(self, all_polygons):
        if not self.polygons:
            return
        target_polygon = random.choice(all_polygons)
        if target_polygon not in self.polygons:
            self.polygons.append(target_polygon)
            self.area += Polygon(target_polygon).area

    def to_dict(self):
        return {
            'name': self.name,
            'color': self.color,
            'area': self.area,
            'soldiers': self.soldiers,
            'polygons': [polygon.tolist() for polygon in self.polygons]
        }

bots = [Bot(random_name()) for _ in range(100)]

polygons = []
for _ in range(100):
    center = np.random.rand(2) * 100
    radius = np.random.rand() * 10 + 10
    polygon = create_polygon(center, radius, 6)
    bot = random.choice(bots)
    bot.polygons.append(polygon)
    bot.area += Polygon(polygon).area
    polygons.append(polygon)

def update_leaderboard():
    bots.sort(key=lambda b: b.area, reverse=True)

def game_tick():
    for bot in bots:
        bot.update_soldiers()
        bot.move(polygons)
    update_leaderboard()
    socketio.emit('update', {'bots': [bot.to_dict() for bot in bots]})

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    emit('update', {'bots': [bot.to_dict() for bot in bots]})

if __name__ == '__main__':
    socketio.run(app, debug=True)
