from flask import Flask, render_template
from pathlib import Path
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')