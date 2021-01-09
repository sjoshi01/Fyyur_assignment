#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
  Flask, 
  render_template, 
  request,
  Response, 
  flash, 
  redirect, 
  url_for
)

from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import db,Venue,Artist,Show  
from flask_moment import Moment
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object('config')
moment = Moment(app)
migrate = Migrate(app,db)
db.init_app(app)
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
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data =[]
  distinct_city = db.session.query(Venue.city,Venue.state).distinct()
  venues = Venue.query.all()
  for each_city in distinct_city:
    data.append({
      'city': each_city.city,
      'state': each_city.state,
      'venues':[{
        'id': each_venue.id,
        'name': each_venue.name,
      } for each_venue in venues if each_venue.city == each_city.city  and
       each_venue.state == each_city.state
      ]
    })
    ## the for loop at the end of venues will gothrough each venue in venue and select only those who 
    ## has same city and state
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term','')
  venue_info = Venue.query.filter(Venue.name.ilike('%'+search_term+'%')).all()
  response={
    "count": len(venue_info),
    "data": venue_info
    }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')  
##****Genres not showing correctly******************************************
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  venue = Venue.query.filter_by(id=venue_id).first()

  ##**Need to join artist and show together because shows data clubs artist and show info together in array
  past_shows = (
    db.session.query(Artist,Show).join(Show)
    .join(Venue).filter(Show.venue_id == Venue.id,
    Show.artist_id == Artist.id,
    Show.start_time < datetime.now(),)
    .all()
  )
  
  upcoming_shows = (
    db.session.query(Artist, Show)
    .join(Show)
    .join(Venue).filter(Show.venue_id == venue_id,
    Show.artist_id == Artist.id,
    Show.start_time > datetime.now(),) .all()
  )
  
  venueResult = {
        'id': venue.id,
        'name': venue.name,
        'genres': venue.genres,
        'address': venue.address,
        'city': venue.city,
        'state': venue.state,
        'phone': venue.phone,
        'website': venue.website,
        'facebook_link': venue.facebook_link,
        'seeking_talent': venue.seeking_talent,
        'seeking_description': venue.seeking_description,
        'image_link': venue.image_link,
        'past_shows': [
            {
                'id': artist.id,
                'name': artist.name,
                'image_link': artist.image_link,
                'start_time': str(show.start_time),
            }
            for artist, show in past_shows
        ],
        'upcoming_shows': [
            {
                'id': artist.id,
                'name': artist.name,
                'image_link': artist.image_link,
                'start_time': str(show.start_time),
            }
            for artist, show in upcoming_shows
        ],
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows),
    }
  
  return render_template('pages/show_venue.html',venue = venueResult)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
   form = VenueForm(request.form)
   if form.validate_on_submit():
      venue = Venue()
      form.populate_obj(venue)
      db.session.add(venue)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
      return render_template('pages/home.html')
   else:
      flash('Venue ' + request.form['name'] +
        'failed due to validation error and could not be posted!')
      return render_template('forms/new_venue.html', form=form)
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
    
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

  try:
    Venue.query.filterby(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists_list = []
  artists = Artist.query.all()
  for artist_info in artists:
    artists_list.append({
      'id': artist_info.id,
      'name': artist_info.name
    })
 
  return render_template('pages/artists.html', artists=artists_list)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term','')
  artist_list = Artist.query.filter(Artist.name.ilike('%'+search_term+'%')).all()
  response={
    "count": len(artist_list),
    "data": []
    }
  for artist_info in artist_list:
    show_list = Show.query.filter(Show.artist_id == artist_info.id, Show.start_time > datetime.now())
    art = {
      'id': artist_info.id, 
      'name': artist_info.name,
      'num_upcoming_shows': show_list.count(),
    }
    response['data'].append(art)

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  ########Same as venue
  artist= Artist.query.filter_by(id=artist_id).first()
  past_shows = (
    db.session.query(Artist, Show).join(Show)
    .join(Venue).filter(
    Show.artist_id == artist_id,
    Show.venue_id == Venue.id,
    Show.start_time < datetime.now(),
    ).all()
  )

  upcoming_shows = (
    db.session.query(Artist, Show).join(Show)
    .join(Venue).filter(
    Show.artist_id == artist_id,
    Show.venue_id == Venue.id,
    Show.start_time > datetime.now(),
    ).all()
  )
  
  artistResult = {
        'id': artist.id,
        'name': artist.name,
        'genres': artist.genres,
        'city': artist.city,
        'state': artist.state,
        'phone': artist.phone,
        'facebook_link': artist.facebook_link,
        'seeking_venue': artist.seeking_venue,
        'seeking_description': artist.seeking_description,
        'image_link': artist.image_link,
        'past_shows': [
            {
                'id': artist.id,
                'name': artist.name,
                'image_link': artist.image_link,
                'start_time': str(show.start_time),
            }
            for artist, show in past_shows
        ],
        'upcoming_shows': [
            {
                'id': artist.id,
                'name': artist.name,
                'image_link': artist.image_link,
                'start_time': str(show.start_time),
            }
            for artist, show in upcoming_shows
        ],
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows),
    }
  return render_template('pages/show_artist.html', artist=artistResult)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
# TODO: populate form with fields from artist with ID <artist_id>
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)  ## Populate the from from the exisiting info of the artist
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing artist record with ID <artist_id> using the new attributes
   form = ArtistForm(request.form)
   existing_artist = Artist.query.get(artist_id)
   if form.validate_on_submit():
      artist = Artist()
      form.populate_obj(artist)
      existing_artist.name = artist.name
      existing_artist.city = artist.city
      existing_artist.state = artist.state
      existing_artist.phone = artist.phone
      existing_artist.genres = artist.genres
      existing_artist.facebook_link = artist.facebook_link
      existing_artist.seeking_venue = artist.seeking_venue
      existing_artist.seeking_description = artist.seeking_description
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully edited!')
   else:
      db.session.rollback()
      flash('Artist ' + request.form['name'] +
        ' failed due to validation error and could not be edited!')
   return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
# TODO: populate form with values from venue with ID <venue_id>
def edit_venue(venue_id):
  venue=Venue.query.get(venue_id)
  form = VenueForm(obj=venue) 
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm(request.form)
  existing_venue = Venue.query.get(venue_id)
  if form.validate_on_submit():
     venue = Venue()
     form.populate_obj(venue)
     existing_venue.name = venue.name
     existing_venue.city = venue.city
     existing_venue.state = venue.state
     existing_venue.address = venue.address
     existing_venue.phone = venue.phone
     existing_venue.genres = venue.genres
     existing_venue.facebook_link = venue.facebook_link
     existing_venue.website = venue.website
     existing_venue.image_link = venue.image_link
     existing_venue.seeking_talent = venue.seeking_talent
     existing_venue.seeking_description = venue.seeking_description
     db.session.commit()
     flash('Venue ' + request.form['name'] + ' was successfully edited!')
  else:
     db.session.rollback()
     flash('Venue ' + request.form['name'] +
        ' failed due to validation error and could not be edited!')
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)
  if form.validate_on_submit():
     artist = Artist()
     form.populate_obj(artist)
     db.session.add(artist)
     db.session.commit()
     flash('Artist ' + request.form['name'] + ' was successfully listed!')
     return render_template('pages/home.html')
  else:
    flash('Artist ' + request.form['name'] +
        ' failed due to validation error and could not be posted!')
    return render_template('forms/new_artist.html', form=form)
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  ##************Show data of only upcoming shows****************************
  shows_data = []
  shows = db.session.query(Show.venue_id,Venue.name.label('venue_name'),Show.artist_id,Artist.name.label('artist_name'),Artist.image_link,Show.start_time).join(Venue).join(Artist).group_by(Show.venue_id,Venue.name,Show.artist_id,Artist.name,Artist.image_link,Show.start_time).filter(Show.start_time > datetime.now()).all()
  for each_show in shows:
    shows_data.append({
      'venue_id': each_show.venue_id,
      'venue_name': each_show.venue_name,
      'artist_id': each_show.artist_id,
      'artist_name': each_show.artist_name,
      'artist_image_link': each_show.image_link,
      'start_time': str(each_show.start_time)
    })
  return render_template('pages/shows.html', shows=shows_data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form)
  if form.validate_on_submit():
    show = Show(
      artist_id=form.artist_id.data,
      venue_id=form.venue_id.data,
      start_time=form.start_time.data
    )
    db.session.add(show)
    db.session.commit()
     # on successful db insert, flash success
    flash('Show ' + request.form['artist_id'] + ' was successfully listed!')
    return render_template('pages/home.html')
  else:
    flash('Show ' + request.form['artist_id'] + ' was failed to listed!')
    return render_template('pages/home.html')
  

 
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  

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
