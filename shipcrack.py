from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True

SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}'.format(
        username='WinterFollowsSpr',
        password='Z3aGw~Jhjn$H`Mc!e3X6VW{h;(X,`j',
        hostname='WinterFollowsSpring.mysql.pythonanywhere-services.com',
        databasename='WinterFollowsSpr$shipcrack'
)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_POOL_RECYCLE'] = 299
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(4069))

comments = []

@app.route('/', methods=['GET', 'POST'])
def index_page():
    if request.method == 'POST':
        comments.append(request.form['contents'])
        return redirect(url_for('index_page'))

    return render_template('ships.html', comments=comments)
