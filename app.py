#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import sys
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
from flask_migrate import Migrate
from sqlalchemy.orm import aliased
from sqlalchemy import func

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db, compare_type=True)
# TODO: done - connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

def get_venue_shows(venue_id, past):
    queries = [Show.venue_id==venue_id]
    if(past):
        queries.append(Show.start_time < datetime.utcnow().date())
    else:
        queries.append(Show.start_time > datetime.utcnow().date())
    return db.session.query(Show.id, Show.start_time, Artist.id, Artist.name, Artist.image_link).join(Artist, Artist.id==Show.artist_id).filter(*queries).all()

def get_artist_shows(artist_id, past):
    queries = [Show.artist_id==artist_id]
    if(past):
        queries.append(Show.start_time < datetime.utcnow().date())
    else:
        queries.append(Show.start_time > datetime.utcnow().date())
    return db.session.query(Show.id, Show.start_time, Venue.id, Venue.name, Venue.image_link).join(Venue, Venue.id==Show.venue_id).filter(*queries).all()

def flash_success(table, name, process):
    flash(table + ': ' + name + ' was successfully ' + process + '!')

def flash_error(table, name, process):
    flash('An error occurred. ' + table + ': '  + name + ' could not be ' + process + '.')

class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'))
    start_time = db.Column(db.DateTime)

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO:  done - implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String)
    shows = db.relationship('Show',backref='venue',lazy=True, cascade="save-update, merge, delete")

    def __repr__(self):
        return f'<Name: {self.name}, City: {self.city}, State: {self.state}>'

    @property
    def venue_details(self):
        upcoming_shows = get_venue_shows(self.id, False)
        past_shows = get_venue_shows(self.id, True)
        return {
          'id': self.id,
          'name': self.name,
          "genres": self.genres,
          'address': self.address,
          'city': self.city,
          'state': self.state,
          'phone': self.phone,
          'website_link': self.website_link,
          'facebook_link': self.facebook_link,
          'seeking_talent': self.seeking_talent,
          'seeking_description': self.seeking_description,
          'image_link': self.image_link,
          'past_shows': [{
            'artist_id': past_show.id,
            'artist_name': past_show.name,
            'artist_image_link': past_show.image_link,
            'start_time': str(past_show.start_time)
            } for past_show in past_shows],
            'upcoming_shows': [{
                'artist_id': upcoming_show.id,
                'artist_name': upcoming_show.name,
                'artist_image_link': upcoming_show.image_link,
                'start_time': str(upcoming_show.start_time)
            } for upcoming_show in upcoming_shows],
            'past_shows_count': len(past_shows),
            'upcoming_shows_count': len(upcoming_shows)
        }

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: done -  implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String)
    shows = db.relationship('Show', backref='artist',lazy=True, cascade="save-update, merge, delete")

    # TODO done - Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
    def __repr__(self):
            return f'<Id: {self.id}, Name: {self.name}>'

    @property
    def artist_details(self):
        upcoming_shows = get_artist_shows(self.id, False)
        past_shows = get_artist_shows(self.id, True)
        return {
          'id': self.id,
          'name': self.name,
          "genres": self.genres,
          'city': self.city,
          'state': self.state,
          'phone': self.phone,
          'website_link': self.website_link,
          'facebook_link': self.facebook_link,
          'seeking_venue': self.seeking_venue,
          'seeking_description': self.seeking_description,
          'image_link': self.image_link,
          'past_shows': [{
            'venue_id': past_show.id,
            'venue_name': past_show.name,
            'venue_image_link': past_show.image_link,
            'start_time': str(past_show.start_time)
            } for past_show in past_shows],
            'upcoming_shows': [{
                'venue_id': upcoming_show.id,
                'venue_name': upcoming_show.name,
                'venue_image_link': upcoming_show.image_link,
                'start_time': str(upcoming_show.start_time)
            } for upcoming_show in upcoming_shows],
            'past_shows_count': len(past_shows),
            'upcoming_shows_count': len(upcoming_shows)
        }

# initial create, commented to use migration
# db.create_all()

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: done - replace with real venues data.
    venue_locations = db.session.query(Venue.city,Venue.state).group_by(Venue.city,Venue.state).all()
    data = []

    for location in venue_locations:
        venues = db.session.query(Venue.id,Venue.name).filter(Venue.city==location.city,Venue.state==location.state).all()
        venue_details = []
        for venue in venues:
              venue_details.append({
                  "id": venue.id,
                  "name": venue.name,
                  "num_upcoming_shows": len(get_venue_shows(venue.id, False))
              })
        data.append({
            "city": location.city,
            "state": location.state,
            "venues": venue_details
        })
    return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: done - implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    venues = Venue.query.filter(Venue.name.ilike('%{}%'.format(request.form['search_term']))).all()
    response={
      "count": len(venues),
      "data": []
      }
    for venue in venues:
      response["data"].append({
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": len(get_venue_shows(venue.id, False))
        })
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: done - replace with real venue data from the venues table, using venue_id
    venue_item = Venue.query.get(venue_id)
    return render_template('pages/show_venue.html', venue=venue_item.venue_details)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
      # TODO:  done - insert form data as a new Venue record in the db, instead
      # TODO:  done - modify data to be the data object returned from db insertion
    create_venue = Venue()
    create_venue.name = request.form.get('name')
    create_venue.address = request.form.get('address')
    create_venue.city = request.form.get('city')
    create_venue.state = request.form.get('state')
    create_venue.phone = request.form.get('phone')
    create_venue.genres = request.form.getlist('genres')
    create_venue.facebook_link = request.form.get('facebook_link')
    create_venue.image_link = request.form.get('image_link')
    create_venue.website_link = request.form.get('website_link')
    create_venue.seeking_talent = request.form.get('seeking_talent')=='y'
    create_venue.seeking_description = request.form.get('seeking_description')

    try:
        db.session.add(create_venue)
        db.session.commit()
        # on successful db insert, flash success
        flash_success('Venue', request.form.get('name'), 'listed')
    except:
        db.session.rollback()
        print(sys.exc_info())
        # TODO:  done - on unsuccessful db insert, flash an error instead.
        flash_error('Venue', request.form.get('name'), 'listed')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    finally:
        db.session.close()
    return redirect(url_for('index'))

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: done - replace with real data returned from querying the database

  data=[]
  artists = Artist.query.all()
  for artist in artists:
    data.append({
        "id": artist.id,
        "name": artist.name
      })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: done - implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  artists = Artist.query.filter(Artist.name.ilike('%{}%'.format(request.form['search_term']))).all()
  response={
    "count": len(artists),
    "data": []
    }
  for artist in artists:
    response["data"].append({
        "id": artist.id,
        "name": artist.name,
        "num_upcoming_shows": len(get_artist_shows(artist.id, False))
      })
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: done - replace with real artist data from the artist table, using artist_id

  artist_item = Artist.query.get(artist_id)
  return render_template('pages/show_artist.html', artist=artist_item.artist_details)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

    edit_artists = Artist.query.get(artist_id)
    form = ArtistForm(
        name=edit_artists.name,
        city=edit_artists.city,
        state=edit_artists.state,
        phone=edit_artists.phone,
        genres=edit_artists.genres,
        facebook_link=edit_artists.facebook_link,
        website_link=edit_artists.website_link,
        image_link=edit_artists.image_link,
        seeking_venue=edit_artists.seeking_venue,
        seeking_description=edit_artists.seeking_description
    )

    # TODO: done - populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=edit_artists)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: done - take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  try:
    edit_artists = Artist.query.get(artist_id)
    edit_artists.name=request.form.get('name')
    edit_artists.city=request.form.get('city')
    edit_artists.state=request.form.get('state')
    edit_artists.phone=request.form.get('phone')
    edit_artists.genres=request.form.getlist('genres')
    edit_artists.facebook_link=request.form.get('facebook_link')
    edit_artists.website_link=request.form.get('website_link')
    edit_artists.image_link=request.form.get('image_link')
    edit_artists.seeking_venue=request.form.get('seeking_venue') == 'y'
    edit_artists.seeking_description=request.form.get('seeking_description')

    db.session.commit()
    flash_success('Artist', request.form.get('name'), 'updated')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash_success('Artist', request.form.get('name'), 'updated')
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

    edit_venue = Venue.query.get(venue_id)
    form = VenueForm(
        name=edit_venue.name,
        city=edit_venue.city,
        state=edit_venue.state,
        address=edit_venue.address,
        phone=edit_venue.phone,
        genres=edit_venue.genres,
        facebook_link=edit_venue.facebook_link,
        website_link=edit_venue.website_link,
        image_link=edit_venue.image_link,
        seeking_talent=edit_venue.seeking_talent,
        seeking_description=edit_venue.seeking_description
    )

    # TODO: - done populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=edit_venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: done - take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  try:
    edit_venue = Venue.query.get(venue_id)
    edit_venue.name=request.form.get('name')
    edit_venue.city=request.form.get('city')
    edit_venue.state=request.form.get('state')
    edit_venue.address=request.form.get('address')
    edit_venue.phone=request.form.get('phone')
    edit_venue.genres=request.form.getlist('genres')
    edit_venue.facebook_link=request.form.get('facebook_link')
    edit_venue.website_link=request.form.get('website_link')
    edit_venue.image_link=request.form.get('image_link')
    edit_venue.seeking_talent=request.form.get('seeking_talent') == 'y'
    edit_venue.seeking_description=request.form.get('seeking_description')

    db.session.commit()
    flash_success('Venue', request.form.get('name'), 'updated')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash_error('Venue', request.form.get('name'), 'updated')
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: done - replace with real venues data.

    data= []
    shows = db.session.query(Show, Venue, Artist).filter(Venue.id == Show.venue_id, Artist.id == Show.artist_id).all()
    for show in shows:
        data.append({
            "venue_id": show.Venue.id,
            "venue_name": show.Venue.name,
            "artist_id": show.Artist.id,
            "artist_name": show.Artist.name,
            "artist_image_link": show.Artist.image_link,
            "start_time": str(show.Show.start_time)
          })
    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: - done insert form data as a new Show record in the db, instead

  try:
    new_show = Show(
      start_time=request.form.get('start_time'),
      venue_id=request.form.get('venue_id'),
      artist_id=request.form.get('artist_id')
    )
    db.session.add(new_show)
    db.session.commit()
    flash_success('Show', request.form.get('name'), 'listed')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash_error('Show', request.form.get('name'), 'listed')
  finally:
    db.session.close()
    flash('An error occurred. Show could not be listed.')

  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: done - on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return redirect(url_for('index'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
