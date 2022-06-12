
# A very simple Flask Hello World app for you to get started with...

from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello from ShipCrack!'

@app.route('/ships')
def ships():
    return '<head><title>ShipCrack - Ships</title></head><body>This is the Ships page! You\'ll search for ships here</body>'

