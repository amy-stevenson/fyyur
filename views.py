from app import *

def flash_success(table, name, process):
    flash(table + ': ' + name + ' was successfully ' + process + '!')


def flash_error(table, name, process):
    flash('An error occurred. ' + table + ': ' +
          name + ' could not be ' + process + '.')

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
    venue_locations = db.session.query(
        Venue.city, Venue.state).group_by(
        Venue.city, Venue.state).all()
    data = []

    for location in venue_locations:
        venues = db.session.query(
            Venue.id,
            Venue.name).filter(
            Venue.city == location.city,
            Venue.state == location.state).all()
        venue_details = []
        for venue in venues:
            venue_details.append({
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len(db.session.query(Show).filter(Show.venue_id==venue.id).filter(Show.start_time>datetime.now()).all()
)
            })
        data.append({
            "city": location.city,
            "state": location.state,
            "venues": venue_details
        })
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: done - implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live
    # Music & Coffee"

    venues = Venue.query.filter(
        Venue.name.ilike(
            '%{}%'.format(
                request.form['search_term']))).all()
    response = {
        "count": len(venues),
        "data": []
    }
    for venue in venues:
        response["data"].append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": len(venue_upcoming_shows(venue.id))
        })
    return render_template(
        'pages/search_venues.html',
        results=response,
        search_term=request.form.get(
            'search_term',
            ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: done - replace with real venue data from the venues table, using
    # venue_id

    upcoming_shows = []
    past_shows = []
    venue_items = db.session.query(Venue, Show, Artist).outerjoin(Show, Venue.id==Show.venue_id).outerjoin(Artist, Show.artist_id==Artist.id).filter(Venue.id==venue_id).all()
    for item in venue_items:
        if item.Show is not None:
            if (item.Show.start_time >  datetime.now()):
                upcoming_shows.append({
                    'artist_id': item.Artist.id,
                    'artist_name': item.Artist.name,
                    'artist_image_link': item.Artist.image_link,
                    'start_time': str(item.Show.start_time)
                })
            else:
                past_shows.append({
                    'artist_id': item.Artist.id,
                    'artist_name': item.Artist.name,
                    'artist_image_link': item.Artist.image_link,
                    'start_time': str(item.Show.start_time)
                })


    venue_item = venue_items[0]
    venue_details={
        'id': venue_item.Venue.id,
        'name': venue_item.Venue.name,
        "genres": venue_item.Venue.genres,
        'address': venue_item.Venue.address,
        'city': venue_item.Venue.city,
        'state': venue_item.Venue.state,
        'phone': venue_item.Venue.phone,
        'website_link': venue_item.Venue.website_link,
        'facebook_link': venue_item.Venue.facebook_link,
        'seeking_talent': venue_item.Venue.seeking_talent,
        'seeking_description': venue_item.Venue.seeking_description,
        'image_link': venue_item.Venue.image_link,
        'past_shows': past_shows,
        'upcoming_shows': upcoming_shows,
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows)
    }

    return render_template(
        'pages/show_venue.html',
        venue=venue_details)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO:  done - insert form data as a new Venue record in the db, instead
    # TODO:  done - modify data to be the data object returned from db
    # insertion
    form = VenueForm(request.form)
    print(form.genres.data,'create_genre')
    venue = Venue(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        address=form.address.data,
        phone=form.phone.data,
        genres=form.genres.data,
        facebook_link=form.facebook_link.data,
        image_link=form.image_link.data,
        website_link=form.website_link.data,
        seeking_talent=form.seeking_talent.data,
        seeking_description=form.seeking_description.data
    )
    try:
        db.session.add(venue)
        db.session.commit()
        # on successful db insert, flash success
        flash_success('Venue', request.form.get('name'), 'listed')
    except BaseException:
        db.session.rollback()
        print(sys.exc_info())
        # TODO:  done - on unsuccessful db insert, flash an error instead.
        flash_error('Venue', request.form.get('name'), 'listed')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    finally:
        db.session.close()
    return redirect(url_for('index'))


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
    return render_template(
        'forms/edit_venue.html',
        form=form,
        venue=edit_venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: done - take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes

    try:
        form = VenueForm(request.form)
        print(form.seeking_talent.data,'seeking')
        print(form.genres.data,'genre')

        venue = Venue.query.get(venue_id)
        venue.name=form.name.data,
        venue.city=form.city.data,
        venue.state=form.state.data,
        venue.address=form.address.data,
        venue.phone=form.phone.data,
        venue.facebook_link=form.facebook_link.data,
        venue.image_link=form.image_link.data,
        venue.website_link=form.website_link.data,
        venue.seeking_talent='1' if form.seeking_talent.data else '0',
        venue.seeking_description=form.seeking_description.data,
        venue.genres=venue.genres.clear()
        venue.genres=form.genres.data

        db.session.commit()
        flash_success('Venue', request.form.get('name'), 'updated')
    except BaseException:
        db.session.rollback()
        print(sys.exc_info())
        flash_error('Venue', request.form.get('name'), 'updated')
    finally:
        db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))

@app.route('/venues/<venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: done - Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit
    # could fail.
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
        flash('Venue was successfully deleted!')
    except BaseException:
        flash('An error occurred while deleting Venue!')
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    return redirect(url_for('index'))

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the
    # homepage


#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: done - replace with real data returned from querying the database

    data = []
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

    artists = Artist.query.filter(
        Artist.name.ilike(
            '%{}%'.format(
                request.form['search_term']))).all()
    response = {
        "count": len(artists),
        "data": []
    }
    for artist in artists:
        response["data"].append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": len(artist_upcoming_shows(artist.id))
        })
    return render_template(
        'pages/search_artists.html',
        results=response,
        search_term=request.form.get(
            'search_term',
            ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: done - replace with real artist data from the artist table, using
    # artist_id

    upcoming_shows = []
    past_shows = []
    artist_items = db.session.query(Artist, Show, Venue).outerjoin(Show, Artist.id==Show.artist_id).outerjoin(Venue, Show.venue_id==Venue.id).filter(Artist.id==artist_id).all()

    for item in artist_items:
        if item.Show is not None:
            if (item.Show.start_time >  datetime.now()):
                upcoming_shows.append({
                    'venue_id': item.Venue.id,
                    'venue_name': item.Venue.name,
                    'venue_image_link': item.Venue.image_link,
                    'start_time': str(item.Show.start_time)
                })
            else:
                past_shows.append({
                    'venue_id': item.Venue.id,
                    'venue_name': item.Venue.name,
                    'venue_image_link': item.Venue.image_link,
                    'start_time': str(item.Show.start_time)
                })


    artist_item = artist_items[0]
    artist_details={
        'id': artist_item.Artist.id,
        'name': artist_item.Artist.name,
        'genres': artist_item.Artist.genres,
        'city': artist_item.Artist.city,
        'state': artist_item.Artist.state,
        'phone': artist_item.Artist.phone,
        'website_link': artist_item.Artist.website_link,
        'facebook_link': artist_item.Artist.facebook_link,
        'seeking_venue': artist_item.Artist.seeking_venue,
        'seeking_description': artist_item.Artist.seeking_description,
        'image_link': artist_item.Artist.image_link,
        'past_shows': past_shows,
        'upcoming_shows': upcoming_shows,
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows)
    }

    return render_template(
        'pages/show_artist.html',
        artist=artist_details)

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
    return render_template(
        'forms/edit_artist.html',
        form=form,
        artist=edit_artists)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: done - take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    try:
        form = ArtistForm(request.form)
        artist = Artist.query.get(artist_id)
        artist.name=form.name.data,
        artist.city=form.city.data,
        artist.state=form.state.data,
        artist.phone=form.phone.data,
        artist.facebook_link=form.facebook_link.data,
        artist.image_link=form.image_link.data,
        artist.website_link=form.website_link.data,
        artist.seeking_venue='1' if form.seeking_venue.data else '0',
        artist.seeking_description=form.seeking_description.data,
        artist.genres=artist.genres.clear()
        artist.genres=form.genres.data

        db.session.commit()
        flash_success('Artist', request.form.get('name'), 'updated')
    except BaseException:
        db.session.rollback()
        print(sys.exc_info())
        flash_success('Artist', request.form.get('name'), 'updated')
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))



#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: done - insert form data as a new Venue record in the db, instead
    # TODO: done - modify data to be the data object returned from db insertion
    form = ArtistForm(request.form)
    artist = Artist(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        phone=form.phone.data,
        genres=form.genres.data,
        facebook_link=form.facebook_link.data,
        image_link=form.image_link.data,
        website_link=form.website_link.data,
        seeking_venue=form.seeking_venue.data == 'y',
        seeking_description=form.seeking_description.data
    )

    try:
        db.session.add(artist)
        db.session.commit()
        # on successful db insert, flash success
        flash_success('Artist', request.form.get('name'), 'listed')
    except BaseException:
        db.session.rollback()
        print(sys.exc_info())
        # TODO:  done - on unsuccessful db insert, flash an error instead.
        flash_error('Artist', request.form.get('name'), 'listed')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    finally:
        db.session.close()
    return redirect(url_for('index'))

#  Shows
#  ----------------------------------------------------------------


@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: done - replace with real venues data.

    data = []
    shows = db.session.query(
        Show,
        Venue,
        Artist).filter(
        Venue.id == Show.venue_id,
        Artist.id == Show.artist_id).all()
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
        flash_success('Show', "", 'listed')
    except BaseException:
        db.session.rollback()
        print(sys.exc_info())
        flash_error('Show', "", 'listed')
    finally:
        db.session.close()

    # on successful db insert, flash success
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