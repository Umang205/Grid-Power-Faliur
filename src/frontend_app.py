from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import os

# Get the absolute path to the project directory
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__,
            static_folder=os.path.join(PROJECT_DIR, 'static'),
            template_folder=os.path.join(PROJECT_DIR, 'templates'))
socketio = SocketIO(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analysis')
def analysis():
    return render_template('analysis.html')

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
