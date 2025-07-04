from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin

from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    # Table Columns
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)

    # Relationships
    recipes = db.relationship('Recipe', backref='user', cascade='all, delete-orphan')

    # Serialization Rules
    serialize_rules = ('-recipes.user',)

    # Password Hashing Logic
    @hybrid_property
    def password_hash(self):
        raise AttributeError("Password hashes may not be viewed.")

    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = bcrypt.generate_password_hash(password.encode('utf-8')).decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))

    # Validations
    @validates('username')
    def validate_username(self, key, value):
        if not value:
            raise ValueError("Username must be provided.")
        return value


class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'

    # Table Columns
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)

    # Foreign Key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Serialization Rules
    serialize_rules = ('-user.recipes',)

    # Validations
    @validates('title')
    def validate_title(self, key, value):
        if not value or value.strip() == '':
            raise ValueError("Title must be provided.")
        return value

    @validates('instructions')
    def validate_instructions(self, key, value):
        if not value or len(value.strip()) < 50:
            raise ValueError("Instructions must be at least 50 characters long.")
        return value
