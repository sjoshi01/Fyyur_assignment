from flask_sqlalchemy import SQLAlchemy
from flask import Flask

db = SQLAlchemy()

##Models
class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable=False)
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(120),nullable=False)
    address = db.Column(db.String(120),nullable=False)
    phone = db.Column(db.String(120),nullable=False)
    image_link = db.Column(db.String(500),nullable=False)
    facebook_link = db.Column(db.String(120),nullable=False)
    genres = db.Column(db.ARRAY(db.String(120)),nullable=False)
    website = db.Column(db.String(500),nullable=False)
    seeking_talent = db.Column(db.Boolean,nullable=False,default=True)
    seeking_description = db.Column(db.String(5000))
    shows = db.relationship('Show',backref='Venue',lazy=True)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable=False)
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(120),nullable=False)
    phone = db.Column(db.String(120),nullable=False)
    genres = db.Column(db.ARRAY(db.String(120)),nullable=False)
    image_link = db.Column(db.String(500),nullable=False)
    facebook_link = db.Column(db.String(120),nullable=False)
    seeking_venue = db.Column(db.Boolean,nullable=False,default=False)
    seeking_description=db.Column(db.String(120))
    shows = db.relationship('Show',backref='Artist',lazy=True)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
   __tablename__='show'

   id = db.Column(db.Integer, primary_key=True)
   artist_id = db.Column(db.Integer,db.ForeignKey('artist.id'),nullable=False)
   venue_id = db.Column(db.Integer,db.ForeignKey('venue.id'),nullable=False)
   start_time = db.Column(db.DateTime(),nullable=False)
