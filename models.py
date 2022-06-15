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

    username = db.Column(db.Unicode(length=255), unique=True, nullable=False)
    password = db.Column(db.UnicodeText, nullable=False)
    
    blurb  = db.Column(db.UnicodeText, default='')

    permission_level = db.Column(db.Integer, default=Permission_Level.Standard)

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

    name = db.Column(db.Unicode(length=255), unique=True, nullable=False)
    desc = db.Column(db.UnicodeText, default='')

    # ships

    # links
    # likes
    # tags

    children = db.relationship('Fandom', secondary=fandom_child, primaryjoin=id == fandom_child.c.fandom_parent_id,
            secondaryjoin=id == fandom_child.c.fandom_child_id, backref=db.backref('parents'))

character_fandom = db.Table('character_fandom',
        db.Column('fandom_id',    db.Integer, db.ForeignKey('fandoms.id'),    primary_key=True),
        db.Column('character_id', db.Integer, db.ForeignKey('characters.id'), primary_key=True)
)

class Character(db.Model):
    __tablename__ = 'characters'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.UnicodeText, default='')
    desc = db.Column(db.UnicodeText, default='')

    fandoms = db.relationship('Fandom', secondary=character_fandom, lazy='subquery', 
            backref=db.backref('characters', lazy=True))
    # ships

    # links
    # likes
    # tags

ship_character = db.Table('ship_character',
        db.Column('character_id', db.Integer, db.ForeignKey('characters.id'), primary_key=True),
        db.Column('ship_id',      db.Integer, db.ForeignKey('ships.id'),      primary_key=True)
)

class Ship(db.Model):
    __tablename__ = 'ships'

    id = db.Column(db.Integer, primary_key=True)

    # name votes
    desc = db.Column(db.UnicodeText, default='')
    platonic = db.Column(db.Boolean, default=False)

    characters = db.relationship('Character', secondary=ship_character, lazy='subquery', 
            backref=db.backref('ships', lazy=True))

    @property
    def fandoms(self):
        fandoms = []
        for character in self.characters:
            fandoms.extend(character.fandoms)
        return list(set(fandoms))

    # tags
    # links
    # likes

def test_shit():
    castlevania = Fandom(name='Castlevania (Netflix)', desc='A show where some guy fights a vampire god')
    print(f'Created: {castlevania.name} ({castlevania.desc})')
    clone_wars  = Fandom(name='Star Wars: The Clone Wars', desc='Star wars cg animated show')
    print(f'Created: {clone_wars.name} ({clone_wars.desc})')
    star_wars   = Fandom(name='Star Wars (All Media Types)', desc='A long time ago in a galaxy far far away...')
    print(f'Created: {star_wars.name} ({star_wars.desc})')
    star_trek   = Fandom(name='Star Trek (All Media Types)', desc='These are the voyages...')
    print(f'Created: {star_trek.name} ({star_trek.desc})')
    sci_fi      = Fandom(name='Science Fiction (All Media Types)', desc='Really Awesome')
    print(f'Created: {sci_fi.name} ({sci_fi.desc})')
    fantasy     = Fandom(name='Fantasy (All Media Types)', desc='Also really awesome')
    print(f'Created: {fantasy.name} ({fantasy.desc})')
    atla        = Fandom(name='Avatar: The Last Airbender (All Media Types)', desc='Everything was fine, until the Fire Nation attacked!')
    print(f'Created: {atla.name} ({atla.desc})')
    animated    = Fandom(name='Animated Series', desc='All animated series, cg or traditional animation.')
    print(f'Created: {animated.name} ({animated.desc})')

    db.session.add(castlevania)
    db.session.add(clone_wars)
    db.session.add(star_wars)
    db.session.add(star_trek)
    db.session.add(sci_fi)
    db.session.add(fantasy)
    db.session.add(atla)
    db.session.add(animated)

    print('Committing changes to db...')
    db.session.commit()
    input('Commited Changes to DB -- Check Fandoms table. (enter to continue)')

    castlevania.parents.append(animated)
    print(f'Added Parent to {castlevania.name}: {[fandom.name for fandom in castlevania.parents]}')

    fantasy.children.append(atla)
    print(f'Added Child to {fantasy.name}: {[fandom.name for fandom in fantasy.children]}')

    print('Committing changes to db...')
    db.session.commit()
    input('Committed changes to db -- check children table. (enter to continue)')

    print('Adding rest of relationships...')
    fantasy.children.append(castlevania)
    print(f'Added {castlevania.name} as child to {fantasy.name}')
    sci_fi.children.extend([star_wars, star_trek])
    print(f'Added {star_wars.name} and {star_trek.name} as children to {sci_fi.name}')
    animated.children.extend([atla, clone_wars])
    print(f'Added {atla.name} and {clone_wars.name} as children to {animated.name}')
    clone_wars.parents.append(star_wars)
    print(f'Added {star_wars.name} as parent to {clone_wars.name}')

    print('Committing changes to db..')
    db.session.commit()
    print('Committed')

    print('Getting Fandom data from query...')
    for fandom in Fandom.query.all():
        print(f'{fandom.name} ({fandom.desc}):')
        print(f' - Parents:  {[parent.name for parent in fandom.parents]}')
        print(f' - Children: {[child.name for child in fandom.children]}')

    input('Check to make sure everything is good (enter to continue)')

    print('Creating characters...')
    tano = Character(name='Ahsoka Tano', desc='Badass, Anakin\'s padawan')
    print(f'Created {tano.name} ({tano.desc})')
    anakin = Character(name='Anakin Skywalker', desc='The Chosen Boi, turns into Vader')
    print(f'Created {anakin.name} ({anakin.desc})')
    bariss = Character(name='Barriss Offee', desc='Hot green girl idk')
    print(f'Created {bariss.name} ({bariss.desc})')
    toph = Character(name='Toph Beifong', desc='First Metalbender ever, total badass')
    print(f'Created {toph.name} ({toph.desc})')
    alucard = Character(name='Alucard', desc='Daywalker, Dracula\'s son')
    print(f'Created {alucard.name} ({alucard.desc})')
    trevor = Character(name='Trevor Belmont', desc='Some random guy idk')
    print(f'Created {trevor.name} ({trevor.desc})')
    sypha = Character(name='Sypha Belnades', desc='Magic user hottie')
    print(f'Created {sypha.name} ({sypha.desc})')

    print('Adding characters to fandoms...')
    clone_wars.characters.extend([tano, anakin, bariss])
    print(f'Added {tano.name}, {anakin.name}, and {bariss.name} characters to {clone_wars.name} fandom')
    toph.fandoms.append(atla)
    print(f'Added {atla.name} fandom to {toph.name} character')
    castlevania.characters.extend([alucard, trevor, sypha])
    print(f'Added {alucard.name}, {trevor.name}, and {sypha.name} characters to {castlevania.name} fandom')

    print('Committing...')
    db.session.commit()

    for fandom in [fandom for fandom in Fandom.query.all() if len(fandom.characters) > 0]:
        print(f'{fandom.name}:')
        print(f' - Characters: {[character.name for character in fandom.characters]}')

    input('Check to see if above is correct. Then check in db. (enter to continue)')

    tariss = Ship(desc='Tariss')
    tariss.characters.extend([tano, bariss])
    print(f'Created {tariss.desc} with characters {[character.name for character in tariss.characters]}')
    anacard = Ship(desc='Angry boi and his half vamp lover')
    anacard.characters.extend([anakin, alucard])
    print(f'Created {anacard.desc} with characters {[character.name for character in anacard.characters]}')
    beinades = Ship(desc='Magic and metal')
    beinades.characters.extend([toph, sypha])
    print(f'Created {beinades.desc} with characters {[character.name for character in beinades.characters]}')
    tabapha = Ship(desc='TaBaPha')
    tabapha.characters.extend([tano, bariss, sypha])
    print(f'Created {tabapha.desc} with characters {[character.name for character in tabapha.characters]}')

    print('Committing...')
    db.session.commit()

    print('Showing all ships:')
    for ship in Ship.query.all():
        print(f'{ship.desc}:')
        print(f' - Characters: {[character.name for character in ship.characters]}')
        print(f' - Fandoms:    {[fandom.name for fandom in ship.fandoms]}')
    input('Check to see if data is correct, and check in DB (enter to continue)')

'''
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
'''
