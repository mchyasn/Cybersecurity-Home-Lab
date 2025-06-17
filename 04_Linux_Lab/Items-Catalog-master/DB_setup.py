#!/usr/bin/env python3

# Setting up our DataBase

from sqlalchemy import create_engine
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, String, Column, ForeignKey

# Base for Declaring Entities/RelationShips
BASE = declarative_base()


PATH = '/var/www/FlaskApp/FlaskApp/'


# Base Class/Entity/Schema for a User
class User(BASE):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    picture = Column(String(250))

    # Return User object data in easily serializable format
    @property
    def serialize(self):
        return {'id': self.id,
                'name': self.name,
                'email': self.email,
                'picture': self.picture
                }


# Base Class/Entity/Schema for a Category
class Category(BASE):
    __tablename__ = "category"

    # who created this category
    user = relationship(User)

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"))

    # Return Category object data in easily serializable format
    @property
    def serialize(self):
        return {'id': self.id, 'name': self.name, 'user_id': self.user_id}


# Base Class/Entity/Schema for an Item
class Item(BASE):

    __tablename__ = "item"

    # who created this item
    user = relationship(User)

    # what category does this belong to
    category = relationship(Category)

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(300))
    user_id = Column(Integer, ForeignKey('user.id'))
    category_id = Column(Integer, ForeignKey('category.id'))

    # Return Item object data in easily serializable format
    @property
    def serialize(self):
        return {'id': self.id,
                'name': self.name,
                'description': self.description,
                'user_id': self.user_id,
                'category_id': self.category_id
                }


# create the db engine
engine = create_engine('sqlite:///' + PATH + 'ItemCatalogDB.db')

# Create all Schemas/Entities as metadata
BASE.metadata.create_all(engine)
