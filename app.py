from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit
import json
import random
import time
import os

# Get the absolute path to the project directory
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__,
            static_folder=os.path.join(PROJECT_DIR, 'static'),
            template_folder=os.path.join(PROJECT_DIR, 'templates'))
socketio = SocketIO(app)

# Simulated grid data
grid_data = {
    'north': {'loadPercentage': 0, 'averageLoad': 0, 'peakLoad': 0},
    'south': {'loadPercentage': 0, 'averageLoad': 0, 'peakLoad': 0},
    'east': {'loadPercentage': 0, 'averageLoad': 0, 'peakLoad': 0},
    'west': {'loadPercentage': 0, 'averageLoad': 0, 'peakLoad': 0}
}

# Generate random data for testing
def generate_random_data():
    for region in grid_data:
        load = random.uniform(0, 100)
        grid_data[region]['loadPercentage'] = load
        grid_data[region]['averageLoad'] = random.uniform(0, 100)
        grid_data[region]['peakLoad'] = random.uniform(0, 100)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analysis')
def analysis():
    return render_template('analysis.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory(os.path.join(PROJECT_DIR, 'static'), path)

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    # Send initial data
    emit('data_update', get_grid_status())

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('region_selection')
def handle_region_selection(data):
    print(f'Region selected: {data["region"]}')
    emit('data_update', get_grid_status())

@socketio.on('time_range')
def handle_time_range(data):
    print(f'Time range changed: {data["range"]}')
    emit('data_update', get_grid_status())

@socketio.on('update_interval')
def handle_update_interval(data):
    print(f'Update interval changed: {data["interval"]}')
    emit('data_update', get_grid_status())

def get_grid_status():
    generate_random_data()
    return {
        'timestamp': time.time(),
        'regions': grid_data,
        'overallLoad': sum(region['loadPercentage'] for region in grid_data.values()) / len(grid_data),
        'stressLevel': sum(region['loadPercentage'] for region in grid_data.values()) / len(grid_data)
    }

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
