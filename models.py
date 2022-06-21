from flask_sqlalchemy import SQLAlchemy
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
        sorted_list.sort(reverse=True, key=lambda name : len(name.votes))
        return sorted_list

    @property
    def slash_name(self):
        join_str = ' / ' if not self.platonic else ' & '
        if len(self.characters) > 0:
            name = join_str.join([character.name for character in self.characters])
            if len(self.platonic_pairs) > 0:
                name += ': ('
                pairs_strings = []
                for pair in self.platonic_pairs:
                    pairs_strings.append(' & '.join([character.name for character in pair.characters]))
                name += ', '.join(pairs_strings) + ')'
        return name

    @property
    def consensus_name(self):
        if len(self.names) > 0:
            return self.sorted_names[0].name
        return self.slash_name

    @property
    def string_names(self):
        return [name.name for name in self.names]

    likes = db.relationship('User', secondary=ship_likes, lazy='subquery', backref=db.backref('ship_likes', lazy=True))
    
    def __eq__(self, other):
        return self.id == other.id

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

    print('Creating Users...')
    user_a  = User(username='user_a',  password='password1', blurb='test1')
    user_b  = User(username='user_b',  password='password2', blurb='test2')
    user_c  = User(username='user_c',  password='password3', blurb='test3')
    curator = User(username='curator', password='password4', blurb='test4', permission_level=Permission.Curator)
    mod     = User(username='mod',     password='password5', blurb='test5', permission_level=Permission.Mod)
    admin   = User(username='admin',   password='password6', blurb='test6', permission_level=Permission.Admin)

    print('Adding Users...')
    db.session.add(user_a)
    db.session.add(user_b)
    db.session.add(user_c)
    db.session.add(curator)
    db.session.add(mod)
    db.session.add(admin)

    print('Committing Users...')
    db.session.commit()

    print('Testing Users...')
    usernames = ['user_a', 'user_b', 'user_c', 'curator', 'mod', 'admin']
    passwords = ['password1', 'password2', 'password3', 'password4', 'password5', 'password6']
    blurbs = ['test1', 'test2', 'test3', 'test4', 'test5', 'test6']
    permission_levels = [Permission.Standard, 
                            Permission.Standard, 
                            Permission.Standard, 
                            Permission.Curator, 
                            Permission.Mod, 
                            Permission.Admin]
    users = User.query.all()
    queried_usernames = [user.username for user in users]
    assert len(users) == 6, 'Incorrect number of users saved'
    assert all(username in queried_usernames for username in usernames), 'Failed to find all expected usernames. Expected: {usernames}, Got: {queried_usernames}'
    for user in users:
        i = usernames.index(user.username)
        assert user.password         == passwords[i], f'"{user.password}" should be "{passwords[i]}"'
        assert user.blurb            == blurbs[i],    f'"{user.blurb}" should be "{blurbs[i]}"'
        assert user.permission_level == permission_levels[i], f'"{user.permission_level}" should be "{permission_levels[i]}"'
    print('PASSED USER CHECKS\n')

    print('Creating Tags...')
    tag_names = ['Gay', 'Cute', 'Jedi', 'Spicy Noodles', 'Pink']
    tags = [Tag(name=tag_names[i]) for i in range(len(tag_names))]

    print('Adding Tags...')
    for tag in tags:
        db.session.add(tag)

    print('Committing Tags...')
    db.session.commit()

    print('Testing Tags...')
    tags = Tag.query.all()
    assert len(tags) == len(tag_names), 'Incorrect number of tags {len(tags)}, should be {len(tag_names)}'
    queried_tag_names = [tag.name for tag in tags]
    assert all(tag_name in queried_tag_names for tag_name in tag_names), 'Incorrect tag names, Expected: {tag_names}, Got: {queried_tag_names}'
    print('PASSED TAG CHECKS\n')

    print('Creating Fandoms...')
    fandom_names = [f'test fandom {i}' for i in range(10)]
    fandom_descs = [f'test fandom desc {i}' for i in range(10)]
    fandoms = [Fandom(name=fandom_names[i], desc=fandom_descs[i]) for i in range(10)]

    print('Adding Fandoms...')
    for fandom in fandoms:
        db.session.add(fandom)

    fandom_author_names = [f'test author {i}' for i in range(30)]
    fandom_author_company_bools = [*(True for i in range(10)), *(False for i in range(10)), *(None for i in range(10))]
    fandom_author_map = [(i, i + 10, i + 20) for i in range(10)]
    fandom_authors = [(Author(name=fandom_author_names[i], company=fandom_author_company_bools[i]) if fandom_author_company_bools[i] is not None else Author(name=fandom_author_names[i])) for i in range(30)]
    
    print('Adding Authors to Fandoms...')
    for i in range(10):
        fandoms[i].authors.extend([fandom_authors[fandom_author_map[i][j]] for j in range(3)])

    print('Creating Fandom Hierarchy...')
    fandom_hierarchy = [
            ((),   (1, 2)),    # 0
            ((0,), (3, 4, 7)), # 1
            ((0,), (7, 5, 6)), # 2
            ((1,), ()),        # 3
            ((1,), ()),        # 4
            ((2,), ()),        # 5
            ((2, 9), ()),      # 6
            ((1, 2), (8,)),    # 7
            ((7,), ()),        # 8
            ((), (6,))         # 9
    ]
    fandom_meta_hierarchy = [
            ((), (1, 2, 3, 4, 5, 6, 7, 8)), # 0
            ((0,), (3, 4, 7, 8)),           # 1
            ((0,), (8, 7, 5, 6)),           # 2
            ((1, 0), ()),                   # 3
            ((1, 0), ()),                   # 4
            ((2, 0), ()),                   # 5
            ((2, 0, 9), ()),                # 6
            ((1, 2, 0), (8,)),              # 7
            ((7, 1, 2, 0), ()),             # 8
            ((), (6,))                      # 9
    ]
    for i in range(3):
        fandoms[i].children.extend([fandoms[i * 2 + 1], fandoms[i * 2 + 2]])
    fandoms[7].parents.extend([fandoms[1], fandoms[2]])
    fandoms[8].parents.append(fandoms[7])
    fandoms[9].children.append(fandoms[6])

    print('Liking Fandoms...')
    like_user_ids = [[] for i in range(len(fandoms))]
    for i in range(3):
        for j in range(2 + i):
            fandoms[i].likes.append(users[j])
            like_user_ids[i].append(users[j].id)
    
    print('Adding Tags to Fandoms...')
    fandom_tag_ids = [[] for i in range(len(fandoms))]
    for i in range(2, 4):
        for j in range(i + 2):
            fandoms[i].tags.append(tags[j])
            fandom_tag_ids[i].append(tags[j].id)

    print('Committing Fandoms...')
    db.session.commit()

    print('Testing Fandoms...')
    fandoms = Fandom.query.all()
    assert len(fandoms) == len(fandom_names), f'Incorrect number of fandoms, expected {len(fandom_names)}, got {len(fandoms)}'
    queried_fandom_names = [fandom.name for fandom in fandoms]
    assert all(fandom.name in queried_fandom_names for fandom in fandoms), f'Incorrrect fandom names, expected: {fandom_names}, got: {queried_fandom_names}'

    for fandom in fandoms:
        i = fandom_names.index(fandom.name)
        
        # Descs
        assert fandom.desc == fandom_descs[i], f'Incorrect Fandom Desc, expected: {fandom_descs[i]}, got: {fandom.desc}'
        
        # Authors
        eans = [fandom_author_names[fandom_author_map[i][j]] for j in range(3)]
        qans = [author.name for author in fandom.authors]

        assert all(ean in qans for ean in eans) and all(qan in eans for qan in qans), f'Invalid authors for fandom "{fandom.name}", Expected: {eans}, Got: {qans}'

        # Parents and Children
        parent_ids, child_ids = fandom_hierarchy[i]

        assert len(parent_ids) == len(fandom.parents),  f'Incorrect number of parents for fandom "{fandom.name}", expected {len(parent_ids)}, got {len(fandom.parents)}'
        assert len(child_ids)  == len(fandom.children), f'Incorrect number of children for fandom "{fandom.name}", expected {len(child_ids)}, got {len(fandom.children)}'
        
        qpns = [parent.name for parent in fandom.parents ]
        qcns = [child.name  for child  in fandom.children]

        epns = [fandom_names[j] for j in parent_ids]
        ecns = [fandom_names[j] for j in child_ids ]

        assert all(qpn in epns for qpn in qpns) and all(epn in qpns for epn in epns), f'Invalid parents for fandom "{fandom.name}", Expected: {epns}, Got: {qpns}'
        assert all(qcn in ecns for qcn in qcns) and all(ecn in qcns for ecn in ecns), f'Invalid children for fandom "{fandom.name}", Expected: {ecns}, Got: {qcns}'

        # Ancestors and Descendents
        ancestor_ids, descendent_ids = fandom_meta_hierarchy[i]

        qans = [ancestor.name   for ancestor   in fandom.ancestors  ]
        qdns = [descendent.name for descendent in fandom.descendents]

        eans = [fandom_names[j] for j in ancestor_ids  ]
        edns = [fandom_names[j] for j in descendent_ids]

        assert all(qan in eans for qan in qans) and all(ean in qans for ean in eans), f'Invalid ancestors for fandom "{fandom.name}", Expected: {eans}, Got: {qans}'
        assert all(qdn in edns for qdn in qdns) and all(edn in qdns for edn in edns), f'Invalid descendents for fandom "{fandom.name}", Expected: {edns}, Got: {qdns}'

        # Likes

        elis = like_user_ids[i]
        qlis = [user.id for user in fandom.likes]

        assert all(eli in qlis for eli in elis) and all(qli in elis for qli in qlis), f'Invalid likes (user ids) for fandom "{fandom.name}", Expected: {elis}, Got: {qlis}'

        # Tags

        etis = fandom_tag_ids[i]
        qtis = [tag.id for tag in fandom.tags]

        assert all(eti in qtis for eti in etis) and all(qti in etis for qti in qtis), f'Invalid tags (tag ids) for fandom "{fandom.name}", Expected: {etis}, Got: {qtis}'

    print('PASSED FANDOM CHECKS\n')

    print('Creating Characters...')
    character_names = [f'character {i}' for i in range(30)]
    character_descs = [f'character desc {i}' for i in range(30)]
    characters = [Character(name=character_names[i], desc=character_descs[i]) for i in range(30)]
    
    print('Creating and Adding Aliases...')
    alias_names = [[] for i in range(30)]
    for i in range(len(characters)):
        character = characters[i]
        aliases = [f'character alias {i}:{j}' for j in range(i * 2)]
        alias_names[i].extend(aliases)
        character.aliases.extend([Character_Alias(name=aliases[j]) for j in range(len(aliases))])

    print('Liking Characters...')
    character_like_user_ids = [[] for i in range(len(characters))]
    for i in range(len(characters)):
        character = characters[i]
        num_likes = math.floor(random.random()*len(users))
        user_ids = list(set([math.floor(random.random()*len(users)) for k in range(num_likes)]))
        c_likes = [users[k] for k in user_ids]
        character_like_user_ids[i].extend([num + 1 for num in user_ids])
        character.likes.extend(c_likes)

    print('Adding Tags to Characters')
    character_tag_ids = [[] for i in range(30)]
    for i in range(len(characters)):
        character = characters[i]
        tag_ids = list(set([math.floor(random.random()*len(tags)) for k in range(math.floor(len(tags)/2))]))
        c_tags = [tags[k] for k in tag_ids]
        character_tag_ids[i].extend([tag.id for tag in c_tags])
        character.tags.extend(c_tags)

    print('Adding Characters to Fandoms...')
    character_fandom_ids = [[] for i in range(30)]
    for i in range(len(characters)):
        character = characters[i]
        fandom_ids = list(set([math.floor(random.random()*len(fandoms)) for k in range(math.floor(len(fandoms)/2))]))
        c_fandoms = [fandoms[k] for k in fandom_ids]
        character_fandom_ids[i].extend([fandom.id for fandom in c_fandoms])
        character.fandoms.extend(c_fandoms)

    print('Committing Characters...')
    db.session.commit()

    print('Testing Characters')
    characters = Character.query.all()
    
    qcns = [character.name for character in characters]
    ecns = character_names

    assert all(ecn in qcns for ecn in ecns) and all(qcn in ecns for qcn in qcns), f'Incorrect characters, Expected: {ecns}, got {qcns}'

    for character in characters:
        i = character_names.index(character.name)

        assert character_descs[i] == character.desc, f'Incorrect desc in character "{character.name}", Expected: "{character_descs[i]}", Got: {character.desc}'
        assert character.active == True, f'Character "{character.name}" isn\'t active'
        assert len(character.edit_suggestions) == 0, f'Incorrect number of edit suggestions for character "{character.name}"'
        
        # aliases
        eans = alias_names[i]
        qans = [alias.name for alias in character.aliases]
        
        assert all(ean in qans for ean in eans) and all(qan in eans for qan in qans), f'Incorrect Character Aliases for character "{character.name}"'

        # likes
        elis = character_like_user_ids[i]
        qlis = [user.id for user in character.likes]

        assert all(eli in qlis for eli in elis) and all(qli in elis for qli in qlis), f'Incorrect Likes (user ids) for character "{character.name}", Expected: {elis}, Got: {qlis}'

        # tags
        etis = character_tag_ids[i]
        qtis = [tag.id for tag in character.tags]

        assert all(eti in qtis for eti in etis) and all(qti in etis for qti in qtis), f'Incorrect Character Tags for character "{character.name}"'

        # fandoms
        efis = character_fandom_ids[i]
        qfis = [fandom.id for fandom in character.fandoms]

        assert all(efi in qfis for efi in efis) and all(qfi in efis for qfi in qfis), f'Incorrect Character Fandoms for character "{character.name}", Expected: {efis}, Got: {qfis}'

    print('PASSED CHARACTER CHECKS\n')

    print('Creating Ships...')
    ship_descs = [f'ship description {i}' for i in range(10)]
    ship_platonic_bools = [i % 2 == 1 for i in range(10)]
    ships = [Ship(desc=ship_descs[i], platonic=ship_platonic_bools) for i in range(10)]

    print('Adding Characters and Platonic Pairs to Ships')
    ship_characters = [{} for i in range(10)]
    for i in range(10):
        ship = ships[i]

        num_characters = math.floor(random.random()*len(characters))
        character_indicies = list(set([math.floor(random.random()*len(characters)) for j in range(num_characters)]))
        s_characters = [characters[j] for j in character_indicies]
        
        ship_characters[i].update({'character_indicies': character_indicies})
        ship.characters.extend(s_characters)

        p_pair_indicies = []
        if not ship.platonic and len(s_characters) > 2:
            ship_characters[i].update({'platonic_pair_indicies': []})
            num_platonic_pairs = math.floor(math.random() * (len(s_characters) - 2))
            for j in num_platonic_pairs:
                p_character_indicies = list(set([math.floor(random.random()*len(s_characters)) for k in range(2)]))
                if len(p_character_indicies) != 2:
                    continue

                ship_characters[i]['platonic_pair_indicies'].append(p_character_indicies)
                p_characters = [characters[k] for k in p_character_indicies]
                ship.platoniship.platonic_pairs.append(PlatonicPair(characters=p_characters))

        print(f'TEST SLASH NAME: {ship.slash_name}')

    print('Committing Ships...')
    db.session.commit()

    # Ship(characters=[], platonic=bool, desc='', platonicpairs=[], tags, names, likes...)

    print('INCOMPLETE') # TODO

