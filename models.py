from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from flask_login import UserMixin
import random, math

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

class Permission:
    Standard = 0
    Curator  = 1
    Mod      = 2
    Admin    = 3

class Item:
    Fandom    = 0
    Character = 1
    Ship      = 2

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.Unicode(length=255), unique=True, nullable=False)
    password = db.Column(db.UnicodeText, nullable=False)

    blurb  = db.Column(db.UnicodeText, default='')

    permission_level = db.Column(db.Integer, default=Permission.Standard)

    edit_suggestions = db.relationship('Edit_Suggestion', backref='user', lazy=True)
    suggestions      = db.relationship('Suggestion', backref='user', lazy=True)

    def __eq__(self, other):
        return self.id == other.id

fandom_likes = db.Table('fandom_likes',
        db.Column('fandom_id', db.Integer, db.ForeignKey('fandoms.id'), primary_key=True),
        db.Column('user_id',   db.Integer, db.ForeignKey('users.id'),   primary_key=True)
)

character_likes = db.Table('character_likes',
        db.Column('character_id', db.Integer, db.ForeignKey('characters.id'), primary_key=True),
        db.Column('user_id',      db.Integer, db.ForeignKey('users.id'),      primary_key=True)
)

ship_likes = db.Table('ship_likes',
        db.Column('ship_id', db.Integer, db.ForeignKey('ships.id'), primary_key=True),
        db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)

fandom_child = db.Table('children',
        db.Column('fandom_parent_id', db.Integer, db.ForeignKey('fandoms.id'), primary_key=True),
        db.Column('fandom_child_id',  db.Integer, db.ForeignKey('fandoms.id'), primary_key=True)
)

fandom_authors = db.Table('fandom_authors',
        db.Column('author_id', db.Integer, db.ForeignKey('authors.id'), primary_key=True),
        db.Column('fandom_id', db.Integer, db.ForeignKey('fandoms.id'), primary_key=True)
)

class Fandom(db.Model):
    __tablename__ = 'fandoms'

    id = db.Column(db.Integer, primary_key=True)

    active = db.Column(db.Boolean, default=True)
    suggestion = db.relationship('Suggestion', uselist=False, backref='fandom', lazy=True)

    name = db.Column(db.Unicode(length=255), unique=True, nullable=False)
    desc = db.Column(db.UnicodeText, nullable=False, default='')

    authors = db.relationship('Author', secondary=fandom_authors, lazy='subquery',
            backref=db.backref('fandoms', lazy=True))

    likes = db.relationship('User', secondary=fandom_likes, lazy='subquery', backref=db.backref('fandom_likes', lazy=True))

    children = db.relationship('Fandom', secondary=fandom_child, primaryjoin=id == fandom_child.c.fandom_parent_id,
            secondaryjoin=id == fandom_child.c.fandom_child_id, backref=db.backref('parents'))

    edit_suggestions = db.relationship('Edit_Suggestion', backref='fandom', lazy=True)

    @property
    def ancestors(self):
        ancestors = self.parents.copy()
        for parent in self.parents:
            ancestors.extend(parent.ancestors)

        unique_ancestors = []
        for ancestor in ancestors:
            if ancestor.id not in [unique_ancestor.id for unique_ancestor in unique_ancestors]:
                unique_ancestors.append(ancestor)
        return unique_ancestors

    @property
    def descendents(self):
        descendents = self.children.copy()
        for child in self.children:
            descendents.extend(child.descendents)

        unique_descendents = []
        for descendent in descendents:
            if descendent.id not in [unique_descendent.id for unique_descendent in unique_descendents]:
                unique_descendents.append(descendent)
        return unique_descendents

    def __eq__(self, other):
        return self.id == other.id

class Author(db.Model):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.Unicode(length=255), nullable=False, unique=True)
    company = db.Column(db.Boolean, default=False)

    def __eq__(self, other):
        return self.id == other.id

character_fandom = db.Table('character_fandom',
        db.Column('fandom_id',    db.Integer, db.ForeignKey('fandoms.id'),    primary_key=True),
        db.Column('character_id', db.Integer, db.ForeignKey('characters.id'), primary_key=True)
)

class Character(db.Model):
    __tablename__ = 'characters'

    id = db.Column(db.Integer, primary_key=True)

    active = db.Column(db.Boolean, default=True)
    suggestion = db.relationship('Suggestion', uselist=False, backref='character', lazy=True)

    name = db.Column(db.Unicode(length=255), default='', unique=True)
    desc = db.Column(db.UnicodeText, default='')

    aliases = db.relationship('Character_Alias', backref='character', lazy=True)

    fandoms = db.relationship('Fandom', secondary=character_fandom, lazy='subquery',
            backref=db.backref('characters', lazy=True))

    likes = db.relationship('User', secondary=character_likes, lazy='subquery',
            backref=db.backref('character_likes', lazy=True))

    edit_suggestions = db.relationship('Edit_Suggestion', backref='character', lazy=True)

    def __eq__(self, other):
        return self.id == other.id

class Character_Alias(db.Model):
    __tablename__ = 'aliases'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.UnicodeText, nullable=False)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)

    def __eq__(self, other):
        return self.id == other.id

ship_character = db.Table('ship_character',
        db.Column('character_id', db.Integer, db.ForeignKey('characters.id'), primary_key=True),
        db.Column('ship_id',      db.Integer, db.ForeignKey('ships.id'),      primary_key=True)
)

platonic_pair_characters = db.Table('platonic_pair_characters',
        db.Column('platonic_pair_id', db.Integer, db.ForeignKey('platonic_pairs.id'), primary_key=True),
        db.Column('character_id',     db.Integer, db.ForeignKey('characters.id'),     primary_key=True)
)

class PlatonicPair(db.Model):
    __tablename__ = 'platonic_pairs'

    id = db.Column(db.Integer, primary_key=True)
    ship_id = db.Column(db.Integer, db.ForeignKey('ships.id'), nullable=False)

    characters = db.relationship('Character', secondary=platonic_pair_characters, lazy='subquery',
            backref=db.backref('platonic_pairs', lazy=True))

    def __eq__(self, other):
        return self.id == other.id

    @property
    def name(self):
        character_names = [character.name for character in self.characters]
        character_names.sort(key=lambda name : name.lower())
        return ' & '.join(character_names)

#    character_ids = frozenset([character.id for character in characters])
#    platonic_pair_character_ids = frozenset([frozenset([character.id for character in pair.characters]) if isinstance(pair, PlatonicPair) else frozenset([character.id for character in pair]) for pair in platonic_pairs])
#    return str(set([character_ids, platonic_bool, platonic_pair_character_ids]))

class Ship(db.Model):
    __tablename__ = 'ships'

    id = db.Column(db.Integer, primary_key=True)

    active = db.Column(db.Boolean, default=True)
    suggestion = db.relationship('Suggestion', uselist=False, backref='ship', lazy=True)

    desc = db.Column(db.UnicodeText, default='')
    platonic = db.Column(db.Boolean, default=False)

    characters = db.relationship('Character', secondary=ship_character, lazy='subquery',
            backref=db.backref('ships', lazy=True))

    platonic_pairs = db.relationship('PlatonicPair', backref='ship', lazy=True)

    edit_suggestions = db.relationship('Edit_Suggestion', backref='ship', lazy=True)

    @property
    def fandoms(self):
        fandoms = []
        for character in self.characters:
            for fandom in character.fandoms:
                fandoms.append(fandom)
                fandoms.extend(fandom.ancestors)
        return list(set(fandoms))

    names = db.relationship('Ship_Name', backref='ship', lazy=True)

    @property
    def sorted_names(self):
        sorted_list = self.names.copy()
        sorted_list.sort(reverse=True, key=lambda name : [len(name.votes), name.name.lower()])
        return sorted_list

    @property
    def slash_name(self):
        join_str = ' / ' if not self.platonic else ' & '
        if len(self.characters) > 0:
            sorted_names = [character.name for character in self.characters]
            sorted_names.sort(key = lambda nm : nm.lower())
            name = join_str.join(sorted_names)
            if len(self.platonic_pairs) > 0:
                name += ': ('
                pair_names = [pair.name for pair in self.platonic_pairs]
                pair_names.sort(key = lambda name : name.lower())
                name += ', '.join(pair_names) + ')'
            return name
        return 'NO CHARACTERS'

    @property
    def name(self):
        if len(self.names) > 0:
            return self.sorted_names[0].name
        return self.slash_name

    @property
    def string_names(self):
        return [name.name for name in self.names]

    likes = db.relationship('User', secondary=ship_likes, lazy='subquery', backref=db.backref('ship_likes', lazy=True))

    def __eq__(self, other):
        return self.id == other.id

    @hybrid_property
    def identity(self):
        char_ids = [character.id for character in self.characters]
        pair_ids = [[character.id for character in pair.characters] for pair in self.platonic_pairs]

        char_ids.sort()
        for pair in pair_ids:
            pair.sort()
        pair_ids.sort()

        char_ids = ','.join([f'{id}' for id in char_ids])
        pair_ids = ';'.join([','.join([f'{id}' for id in pair]) for pair in pair_ids])

        return f'{char_ids}:{pair_ids}:{self.platonic}'

def gen_identity(characters, platonic_pairs, platonic):
    char_ids = [character.id for character in characters]
    pair_ids = [[character.id for character in pair] for pair in platonic_pairs]

    char_ids.sort()
    for pair in pair_ids:
        pair.sort()
    pair_ids.sort()

    char_ids = ','.join([f'{id}' for id in char_ids])
    pair_ids = ';'.join([','.join([f'{id}' for id in pair]) for pair in pair_ids])

    return f'{char_ids}:{pair_ids}:{platonic}'

ship_name_votes = db.Table('ship_name_votes',
        db.Column('user_id',      db.Integer, db.ForeignKey('users.id'),      primary_key=True),
        db.Column('ship_name_id', db.Integer, db.ForeignKey('ship_names.id'), primary_key=True)
)

class Ship_Name(db.Model):
    __tablename__ = 'ship_names'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.UnicodeText, nullable=False, default='')

    ship_id = db.Column(db.Integer, db.ForeignKey('ships.id'), nullable=False)

    votes = db.relationship('User', secondary=ship_name_votes, lazy='subquery',
            backref=db.backref('ship_name_votes', lazy=True))

    def __eq__(self, other):
        return self.id == other.id

fandom_tags = db.Table('fandom_tags',
        db.Column('fandom_id', db.Integer, db.ForeignKey('fandoms.id'), primary_key=True),
        db.Column('tag_id',    db.Integer, db.ForeignKey('tags.id'),    primary_key=True)
)

character_tags = db.Table('character_tags',
        db.Column('character_id', db.Integer, db.ForeignKey('characters.id'), primary_key=True),
        db.Column('tag_id',       db.Integer, db.ForeignKey('tags.id'),       primary_key=True)
)

ship_tags = db.Table('ship_tags',
        db.Column('ship_id', db.Integer, db.ForeignKey('ships.id'), primary_key=True),
        db.Column('tag_id',  db.Integer, db.ForeignKey('tags.id'),  primary_key=True)
)

class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)

    active = db.Column(db.Boolean, default=True)
    suggestion = db.relationship('Suggestion', uselist=False, backref='tag', lazy=True)

    name = db.Column(db.Unicode(length=255), nullable=False, unique=True)

    is_fandom_tag    = db.Column(db.Boolean, default=False)
    is_character_tag = db.Column(db.Boolean, default=False)
    is_ship_tag      = db.Column(db.Boolean, default=False)

    fandoms = db.relationship('Fandom', secondary=fandom_tags, lazy='subquery',
            backref=db.backref('tags', lazy=True))
    characters = db.relationship('Character', secondary=character_tags, lazy='subquery',
            backref=db.backref('tags', lazy=True))
    ships = db.relationship('Ship', secondary=ship_tags, lazy='subquery', backref=db.backref('tags', lazy=True))

    def __eq__(self, other):
        return self.id == other.id

class Suggestion_State:
    Pending  = 0
    Approved = 1
    Rejected = 2
    Failed   = 3

class Edit_Action:
    Set_Desc   = 0  # set desc   (ship, character, fandom)
    Add_Name   = 1  # add name   (ship)
    Add_Tag    = 2  # add tag    (ship, character, fandom)
    Del_Tag    = 3  # del tag    (ship, character, fandom)
    Set_Name   = 4  # set name         (character, fandom)
    Add_Fandom = 5  # add fandom       (character)
    Del_Fandom = 6  # del fandom       (character)
    Add_Alias  = 7  # add alias        (character)
    Del_Alias  = 8  # del alias        (character)
    Add_Author = 9  # add author                  (fandom)
    Del_Author = 10 # del author                  (fandom)
    Add_Parent = 11 # add parent                  (fandom)
    Del_Parent = 12 # del parent                  (fandom)
    Add_Child  = 13 # add child                   (fandom)
    Del_Child  = 14 # del child                   (fandom)

class Suggestion_Type:
    Fandom    = 0
    Character = 1
    Ship      = 2

class Suggest_Action:
    Create_Tag       = 0
    Create_Fandom    = 1
    Create_Character = 2
    Create_Ship      = 3

class Suggestion(db.Model):
    __tablename__ = 'suggestions'

    id = db.Column(db.Integer, primary_key=True)

    def __eq__(self, other):
        return self.id == other.id

    reason = db.Column(db.UnicodeText, nullable=False)

    user_id      = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tag_id       = db.Column(db.Integer, db.ForeignKey('tags.id'))
    fandom_id    = db.Column(db.Integer, db.ForeignKey('fandoms.id'))
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'))
    ship_id      = db.Column(db.Integer, db.ForeignKey('ships.id'))

    state      = db.Column(db.Integer, default=Suggestion_State.Pending)
    comment    = db.Column(db.UnicodeText)
    discussion = db.Column(db.UnicodeText)

    @property
    def item(self):
        if tag:
            return tag
        if fandom:
            return fandom
        if character:
            return character
        return ship

    def reject(self, comment=None):
        if not self.item:
            self.state = Suggestion_State.Failed
            self.comment = 'Item no longer exists'
            return False

        self.comment = comment
        self.state = Suggestion_State.Rejected
        self.item.delete()

        return True

    def approve(self, comment=None):
        if not self.item:
            self.state = Suggestion_State.Failed
            self.comment = 'Item no longer exists'
            return False

        self.comment = comment
        self.state = Suggestion_State.Approved
        self.item.active = True

        return True

# Create an Edit_Suggestion by doing: user_obj.edit_suggestions.append(Edit_Suggestion(reason='Argument for changing this fandom description', value='new description', item=fandom_obj, action=Edit_Action.Set_Desc))
class Edit_Suggestion(db.Model):
    __tablename__ = 'edit_suggestions'

    id = db.Column(db.Integer, primary_key=True)

    def __eq__(self, other):
        return self.id == other.id

    reason = db.Column(db.UnicodeText, nullable=False)
    value  = db.Column(db.UnicodeText, nullable=False)

    state      = db.Column(db.Integer, default=Suggestion_State.Pending)
    comment    = db.Column(db.UnicodeText)
    discussion = db.Column(db.UnicodeText)

    user_id      = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    fandom_id    = db.Column(db.Integer, db.ForeignKey('fandoms.id'))
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'))
    ship_id      = db.Column(db.Integer, db.ForeignKey('ships.id'))

    suggestion_type = db.Column(db.Integer, nullable=False)

    @property
    def item(self):
        if self.suggestion_type == Suggestion_Type.Ship:
            return self.ship
        if self.suggestion_type == Suggestion_Type.Character:
            return self.character
        return self.fandom

    @item.setter
    def item(self, value):
        if isinstance(value, Ship):
            self.suggestion_type = Suggestion_Type.Ship
            self.ship = value
        elif isinstance(value, Character):
            self.suggestion_type = Suggestion_Type.Character
            self.character = value
        elif isinstance(value, Fandom):
            self.suggestion_type = Suggestion_Type.Fandom
            self.fandom = value
        else:
            raise Exception(f'Unexpected value {value}, expected Ship, Character, or Fandom')

    action = db.Column(db.Integer, nullable=False)

    def reject(self, comment=None):
        self.state   = Suggestion_State.Rejected
        self.comment = comment

    def approve(self, comment=None):
        self.state = Suggestion_State.Approved
        self.comment = comment

        if not self.item:
            self.state = Suggestion_State.Failed
            self.comment = 'No longer exists'
            return False

        # easy actions (set property)
        if self.action == Edit_Action.Set_Name:
            self.item.name = self.value
        if self.action == Edit_Action.Set_Desc:
            self.item.desc = self.value

        # all (add/del tag)
        if self.action == Edit_Action.Add_Tag:
            if self.value in [tag.name for tag in self.item.tags]:
                self.state = Suggestion_State.Failed
                self.comment = f'Tag "{self.value}" already added'
                return False
            new_tag = Tag.query.filter(name=self.value).first()
            if not new_tag:
                new_tag = Tag(name=self.value)

            if self.suggestion_type == Suggestion_Type.Fandom:
                new_tag.is_fandom_tag = True
                new_tag.fandoms.append(self.fandom)
            if self.suggestion_type == Suggestion_Type.Character:
                new_tag.is_character_tag = True
                new_tag.characters.append(self.character)
            if self.suggestion_type == Suggestion_Type.Ship:
                new_tag.is_ship_tag = True
                new_tag.ships.append(self.ship)

        if self.action == Edit_Action.Del_Tag:
            if self.value not in [tag.name for tag in self.item.tags]:
                self.state = Suggestion_State.Failed
                self.comment = f'No Tag "{self.value}" to remove'
                return False
            for i in range(len(self.item.tags)):
                tag = self.item.tags[i]
                if tag.name == self.value:
                    self.item.tags.pop(i)
                    break

        # ship specific (add name)
        if self.action == Edit_Action.Add_Name:
            if self.value in self.ship.string_names:
                self.state = Suggestion_State.Failed
                self.comment = f'Name "{self.value}" already added to ship "{self.ship.consensus_name}"'
                return False
            new_ship_name = Ship_Name(name=self.value)
            new_ship_name.votes.append(self.user)
            self.ship.names.append(new_ship_name)

        # character specific (add/del alias, add/del fandom)
        if self.action == Edit_Action.Add_Alias:
            if self.value in [alias.name for alias in self.character.aliases]:
                self.state = Suggestion_State.Failed
                self.comment = f'Alias "{self.value}" already added to character "{self.character.name}"'
                return False

            self.character.aliases.append(Character_Alias(name=self.value))

        if self.action == Edit_Action.Del_Alias:
            if self.value not in [alias.name for alias in self.character.aliases]:
                self.state = Suggestion_State.Failed
                self.comment = f'"{self.value}" not an alias of "{self.character.name}"'

            for i in len(range(self.character.aliases)):
                alias = self.character[i]
                if alias.name == self.value:
                    self.character.aliases.pop(i)
                    break

        if self.action == Edit_Action.Add_Fandom:
            if self.value in [fandom.name for fandom in self.character.fandoms]:
                self.state = Suggestion_State.Failed
                self.comment = f'Fandom "{self.value}" already a fandom of "{self.character.name}"'
                return False

            fandom = Fandom.query.filter(name=self.value).first()
            if not fandom:
                self.state = Suggestion_State.Failed
                self.comment = f'No fandom exists by the name of "{self.value}"'
                return False

            self.character.fandoms.append(fandom)

        if self.action == Edit_Action.Del_Fandom:
            if self.value not in [fandom.name for fandom in self.character.fandoms]:
                self.state = Suggestion_State.Failed
                self.comment = f'"{self.value}" is not a fandom of "{self.character.name}"'
                return False

            for i in range(len(self.character.fandoms)):
                fandom = self.character.fandoms[i]
                if fandom.name == self.value:
                    self.character.fandoms.pop(i)
                    break

        # fandom specific (add/del author, add/del parent, add/del child)
        if self.action == Edit_Action.Add_Author:
            if self.value in [author.name for author in self.fandom.authors]:
                self.state = Suggestion_State.Failed
                self.comment = f'"{self.value}" already an author of fandom "{self.fandom.name}"'
                return False

            author = Author.query.filter(name=self.value).first()
            if not author:
                author = Author(name=self.value)

            self.fandom.authors.append(author)

        if self.action == Edit_Action.Del_Author:
            if self.value not in [author.name for author in self.fandom.authors]:
                self.state = Suggestion_State.Failed
                self.comment = f'"{self.value}" is not an author of fandom "{self.fandom.name}"'
                return False

            for i in range(len(self.fandom.authors)):
                author = self.fandom.authors[i]
                if author.name == self.value:
                    self.fandom.authors.pop(i)
                    break

        if self.action == Edit_Action.Add_Parent:
            if self.value in [parent.name for parent in self.fandom.parents]:
                self.state = Suggestion_State.Failed
                self.comment = f'"{self.value}" already a parent of fandom "{self.fandom.name}"'
                return False

            parent_fandom = Fandom.query.filter(name=self.value).first()
            if not parent_fandom:
                self.state = Suggestion_State.Failed
                self.comment = f'"{self.value}" is not a fandom'
                return False

            if parent_fandom.name in [descendent.name for descendent in self.fandom.descendents]:
                self.state = Suggestion_State.Failed
                self.comment = f'"{self.value}" is a descendent of fandom "{self.fandom.name}" thus it can\'t be its parent'
                return False

            self.fandom.parents.append(parent_fandom)

        if self.action == Edit_Action.Del_Parent:
            if self.value not in [parent.name for parent in self.fandom.parents]:
                self.state = Suggestion_State.Failed
                self.comment = f'"{self.value}" is not a parent of fandom "{self.fandom.name}"'
                return False

            for i in range(len(self.fandom.parents)):
                parent = self.fandom.parents[i]
                if parent.name == self.value:
                    self.fandom.parents.pop(i)
                    break

        if self.action == Edit_Action.Add_Child:
            if self.value in [child.name for child in self.fandom.children]:
                self.state = Suggestion_State.Failed
                self.comment = f'"{self.value}" is already a child of fandom "{self.fandom.name}"'
                return False

            child_fandom = Fandom.query.filter(name=self.value).first()
            if not child_fandom:
                self.state = Suggestion_State.Failed
                self.comment = f'"{self.value}" is not a fandom'
                return False

            if child_fandom.name in [child.name for child in self.fandom.ancestors]:
                self.state = Suggestion_State.Failed
                self.comment = f'"{self.value}" is an ancestor of "{self.fandom.name}" and thus can\'t be its child'
                return False

            self.fandom.children.append(child_fandom)

        if self.action == Edit_Action.Del_Child:
            if self.value not in [child.name for child in self.fandom.children]:
                self.state = Suggestion_State.Failed
                self.comment = f'"{self.value}" is not a child of "{self.fandom.name}"'
                return False

            for i in range(len(self.fandom.children)):
                child = self.fandom.children[i]
                if child.name == self.value:
                    self.fandom.children.pop(i)
                    break

        return True

def tests():
    print('Dropping All Tables...')
    db.drop_all()
    print('Creating All Tables...')
    db.create_all()

    print('Doing Customized Ship Identity Checks...')

    char_a = Character(name='char a', desc='Character A Desc')
    char_b = Character(name='char b', desc='Character B Desc')
    char_c = Character(name='char c', desc='Character C Desc')
    char_d = Character(name='char d', desc='Character D Desc')

    db.session.add(char_a)
    db.session.add(char_b)
    db.session.add(char_c)
    db.session.add(char_d)

    db.session.commit()

    ship_a = Ship(desc='ship_a desc', characters=[char_a, char_b, char_c, char_d], platonic_pairs=[PlatonicPair(characters=[char_a, char_d]), PlatonicPair(characters=[char_b, char_c])])

    db.session.add(ship_a)
    db.session.commit()

    idn = gen_identity([char_c, char_b, char_d, char_a], [[char_c, char_b], [char_d, char_a]], False)

    ship_o = Ship.query.filter_by(identity=idn).first()
    if not ship_o:
        print('FAILED')
    else:
        print(ship_o.slash_name)
