import os
import sys

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

from app import app, socketio

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
