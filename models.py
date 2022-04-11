import sys
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from app import db

class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'))
    start_time = db.Column(db.DateTime)

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO:  done - implement any missing fields, as a database migration
    # using Flask-Migrate
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Integer, nullable=False, default=False)
    seeking_description = db.Column(db.String)
    shows = db.relationship(
        'Show',
        backref='venue',
        lazy=True,
        cascade="save-update, merge, delete")

    def __repr__(self):
        return f'<Name: {self.name}, City: {self.city}, State: {self.state}>'

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: done -  implement any missing fields, as a database migration
    # using Flask-Migrate
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Integer, nullable=False, default=False)
    seeking_description = db.Column(db.String)
    shows = db.relationship(
        'Show',
        backref='artist',
        lazy=True,
        cascade="save-update, merge, delete")

    # TODO done - Implement Show and Artist models, and complete all model
    # relationships and properties, as a database migration.
    def __repr__(self):
        return f'<Id: {self.id}, Name: {self.name}>'

