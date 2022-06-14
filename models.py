from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

DB_USERNAME = 'WinterFollowsSpr'
DB_PASSWORD = 'Z3aGw~Jhjn$H`Mc!e3X6VW{h;(X,`j'
DB_HOSTNAME = 'WinterFollowsSpring.mysql.pythonanywhere-services.com'
DB_NAME     = 'WinterFollowsSpr$shipcrack'
DB_URI = f'mysql+mysqlconnector://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOSTNAME}/{DB_NAME}'

from shipcrack import app

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_POOL_RECYCLE'] = 299
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Permission_Level:
    Standard = 0
    Curator  = 1
    Mod      = 2
    Admin    = 3

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.Unicode(length=255), unique=True)
    password = db.Column(db.UnicodeText)
    
    handle = db.Column(db.UnicodeText)
    blurb  = db.Column(db.UnicodeText)

    permission_level = db.Column(db.Integer)

    # Likes
    # Ship Name Votes
    # Suggestions (Pending, Accepted, Rejected)

fandom_child = db.Table('children',
        db.Column('fandom_parent_id', db.Integer, db.ForeignKey('fandoms.id'), primary_key=True),
        db.Column('fandom_child_id',  db.Integer, db.ForeignKey('fandoms.id'), primary_key=True)
)

class Fandom(db.Model):
    __tablename__ = 'fandoms'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.Unicode(length=255), unique=True)
    desc = db.Column(db.UnicodeText)

    children = db.relationship('Fandom', secondary=fandom_child, primaryjoin=id == fandom_child.c.fandom_parent_id,
            secondaryjoin=id == fandom_child.c.fandom_child_id, backref=db.backref('parents'))

'''
Suggestion:
 - User
 - Pending_Level (0 = Pending, 1 = Accepted, 2 = Rejected)
 - _item_type (0 = Fandom, 1 = Character, 2 = Ship)
 - _fandom
 - _character
 - _ship
 - _property
 - _value
 - property (@property getter/setter)
 - value (@property getter/setter)

Fandom: (fandoms)
 - Name
 - Desc
 - Links (OtM)
 - Parent Fandoms (MtM)
 - Child Fandoms (MtM)
 - Characters (MtM)
 - Ships (MtM)
 - Tags (MtM)
 - Likes

Character: (characters)
 - Name
 - Desc
 - Ships (MtM)
 - Fandoms (MtM)
 - Tags (OtM)
 - Links
 - Likes

Ship: (ships)
 - Names (priority queue where priority = number of likes/votes, let users submit suggestions for names)
 - Characters
 - Platonic
 - Desc
 - Tags
 - Links
 - Likes

Ship_Name: (ship_names)
 - Name
 - Votes
 - Ship

Ship_Name_Votes: (ship_name_votes)
 - User
 - Ship_Name

Like: (likes)
 - User
 - _item_type (0 Fandom, 1 Character, 2 Ship)
 - _fandom,    FK, nullable
 - _character, FK, nullable
 - _ship,      FK, nullable
 - item (@property getter/setter)

Tag: (tags)
 - Name
 - _item_type (0 Fandom, 1 Character, 2 Ship)
 - _fandom,    FK, nullable
 - _character, FK, nullable
 - _ship,      FK, nullable
 - item (@property getter/setter)

Link: (links)
 - Name
 - URL
 - _item_type (0 Fandom, 1 Character, 2 Ship)
 - _fandom,    FK, nullable
 - _character, FK, nullable
 - _ship,      FK, nullable
 - item (@property getter/setter)
'''
