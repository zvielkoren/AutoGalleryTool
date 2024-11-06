from flask import Flask, jsonify, request
from pathlib import Path
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.image_processor import ImageProcessor
from models.config import GalleryConfig
from utils.settings import Settings

app = Flask(__name__)
settings = Settings()
from flask import Flask, jsonify, request, render_template
from pathlib import Path
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/settings', methods=['GET', 'POST'])
def handle_settings():
    if request.method == 'GET':
        return jsonify(settings.load_settings().to_dict())
    else:
        settings.save_settings(GalleryConfig.from_dict(request.json))
        return jsonify({"status": "success"})

@app.route('/api/process', methods=['POST'])
def start_processing():
    config = settings.load_settings()
    processor = ImageProcessor(config)
    return jsonify({"status": "processing started"})

if __name__ == '__main__':
    app.run(debug=True)
