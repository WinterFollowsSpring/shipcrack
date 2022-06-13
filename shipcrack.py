
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
app.config['DEBUG'] = True

comments = []

@app.route('/', methods=['GET', 'POST'])
def index_page():
    if request.method == 'POST':
        comments.append(request.form['contents'])
        return redirect(url_for('index_page'))

    return render_template('ships.html', comments=comments)
