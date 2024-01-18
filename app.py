#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import babel
import dateutil
from dateutil import parser
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
import sys
from forms import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class city_details(db.Model):
   __tablename__ = 'cities'

   city_id = db.Column(db.Integer, primary_key=True)
   city_name = db.Column(db.String)
   state = db.Column(db.String(120))

class Genre(db.Model):
   __tablename__= 'genre'

   genre_id = db.Column(db.Integer, primary_key=True)
   genre_name= db.Column(db.String, unique = True)

class Venue(db.Model):
    __tablename__ = 'venue'

    venue_id = db.Column(db.Integer, primary_key=True)
    venue_name = db.Column(db.String)
    city_id = db.Column(db.Integer, db.ForeignKey(city_details.city_id), nullable = False)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(500)) 
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))

class Artist(db.Model):
    __tablename__ = 'artist'

    artist_id = db.Column(db.Integer, primary_key=True)
    artist_name = db.Column(db.String)
    city_id = db.Column(db.Integer, db.ForeignKey(city_details.city_id), nullable = False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    searching = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    website = db.Column(db.String(500))

class Show(db.Model):
    __tablename__ = 'show'

    show_id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer)
    start_time = db.Column(db.DateTime)
    venue_id= db.Column(db.Integer)

class Art_genre(db.Model):
   __tablename__= 'artist_genre'

   art_genre_id = db.Column(db.Integer,primary_key=True)
   genre_id = db.Column(db.Integer, db.ForeignKey(Genre.genre_id),nullable = False)
   artist_id = db.Column(db.Integer, db.ForeignKey(Artist.artist_id),nullable = False)


class Venue_genre(db.Model):
    __tablename__='venue_genre'

    venue_genre_id = db.Column(db.Integer,primary_key=True)
    genre_id = db.Column(db.Integer, db.ForeignKey(Genre.genre_id),nullable = False)
    venue_id = db.Column(db.Integer, db.ForeignKey(Venue.venue_id),nullable = False)


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

def venue_genre_connector(venue_id):
   
  data = []
  genre_finder = Venue_genre.query.filter(Venue_genre.venue_id == venue_id).all()

  for genre in genre_finder:
    data.append(genre.genre_name)
        
  return data
   

def artist_genre_connector(artist_id):
   
  genre_data = []

  data = Art_genre.query.filter(Art_genre.artist_id == artist_id).all

  for genre in data:
     genre_data.append(Genre.query.filter(genre.genre_name).one)


  return genre_data

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  
  cities_data = city_details.query.all()

  data = []

  for location in cities_data:
    
    class city_venue:
      city = location.city_name       
      state = location.state
      venues = Venue.query.filter(Venue.city_id == location.city_id).all()

    data.append(city_venue)

  return render_template('pages/venues.html', areas= data)





@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  searchTerm=request.form.get('search_term','')
  
  search = Venue.query.filter(Venue.venue_name.like('%' + searchTerm + '%')).all()
  
  # response1={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }

  response={
    "count": len(search),
    "data": venue_search_data(search)
   }

  return render_template('pages/search_venues.html', results = response, search_term= searchTerm)




def venue_search_data(search_data):
   
  response_data = []
  print(search_data[0].venue_id)

  for venue in search_data:
    response_data.append({
       "id": venue.venue_id,
       "name": venue.venue_name,
       "num_upcoming_shows": len(find_future_venue_shows(venue.venue_id))
       }) 

  return response_data




@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  venue_data = Venue.query.filter(Venue.venue_id == venue_id).one()
  
  past_show_data = find_past_venue_shows(venue_id)
  past_show_info = []

  for show in past_show_data:
      
      artist = Artist.query.filter(Artist.artist_id == show.artist_id).first() 

      class show_info:
         artist_id = show.artist_id
         artist_name = artist.artist_name
         artist_image_link = artist.image_link
         start_time = str(show.start_time)

      past_show_info.append(show_info)


  past_parse = []

  for show in past_show_info:
     past_parse.append(
        {
        "artist_id": show.artist_id,
        "artist_name": show.artist_name,
        "artist_image_link": show.artist_image_link,
        "start_time": str(show.start_time)
        }
     )
    
  future_show_data = find_future_venue_shows(venue_id)
  future_show_info = []

  for show in future_show_data:
     
     artist = Artist.query.filter(Artist.artist_id == show.artist_id).first()

     class show_info:
      artist_id = show.artist_id
      artist_name = artist.artist_name
      artist_image_link = artist.image_link
      start_time = show.starting_time

     future_show_info.append(show_info)
    
  future_parse = []

  for show_data in future_show_data:
     future_parse.append(
        {
        "artist_id": show_data.artist_id,
        "artist_name": show_data.artist_name,
        "artist_image_link": show_data.artist_image_link,
        "start_time": str(show_data.start_time)
        }
     )

  city_info = city_details.query.filter(city_details.city_id == venue_data.city_id).first()
  
  data={
    "id": venue_id,
    "name": venue_data.venue_name,
    "genres": venue_genre_connector(venue_id),
    "address": venue_data.address,
    "city": city_info.city_name,
    "state": city_info.state,
    "phone": venue_data.phone,
    "website": venue_data.website_link,
    "facebook_link": venue_data.facebook_link,
    "seeking_talent": venue_data.seeking_talent,
    "seeking_description": venue_data.seeking_description,
    "image_link": venue_data.image_link,
    "past_shows": past_parse,
    "upcoming_shows": future_parse,
    "past_shows_count": len(past_parse),
    "upcoming_shows_count": len(future_parse)}
  
  
  return render_template('pages/show_venue.html', venue=data)

def find_past_venue_shows(id):
  
 return Show.query.filter(Show.venue_id == id, Show.start_time < datetime.now()).all()

def find_future_venue_shows(id):
   
 return Show.query.filter(Show.venue_id == id, Show.start_time >= datetime.now()).all()

  

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm(request.form)

  city_name = len(city_details.query.filter(city_details.city_name == form.city.data).all())
  city_state = len(city_details.query.filter(city_details.state == form.state.data).all())

  if ((city_name < 1) or (city_state < 1)):
    
    new_city = city_details(city_name = form.city.data, state = form.state.data)
    db.session.add(new_city)
    db.session.commit()

    temp = (city_details.query.filter(city_details.city_name == form.city.data, city_details.state == form.state.data).one())
    city_id = temp.city_id
  else:
    temp = (city_details.query.filter(city_details.city_name == form.city.data, city_details.state == form.state.data).one())
    city_id = temp.city_id

    
  new_venue = Venue(
     venue_name = form.venue_name.data,
     city_id = city_id,
     address = form.address.data,
     phone = form.phone.data,
     image_link = form.image_link.data,
     website_link = form.website_link.data,
     facebook_link = form.facebook_link.data,
     seeking_talent = form.seeking_talent.data,
     seeking_description = form.seeking_description.data )
  
  db.session.add(new_venue)

  for genre in form.genres.data:
    
    if(len(Genre.query.filter(Genre.genre_name == genre).all())<0):
      new_genre = Genre(genre_name = genre)
      db.session.add(new_genre)
  
  db.session.commit()
  db.session.close()
  return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

   list = Venue.query.filter(Venue.venue_id == venue_id).first()
   show_list = Show.query.filter(Show.venue_id == venue_id).all()

  
   try:
        
        for show in show_list:
          db.session.delete(show)
        db.session.delete(list)
        db.session.commit()
        flash('Venue was successfully deleted!')
        db.session.close()
        return render_template('pages/home.html') 

   except():
        print("ERROR")
        db.session.rollback()


        


  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  art_data = Artist.query.all()
  data = []

  for artists in art_data:
    data.append({
       "id" :artists.artist_id,
       "name": artists.artist_name
    })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_term = request.form.get('search_term')

  search_result = Artist.query.filter(Artist.artist_name.like('%' + search_term + '%')).all()

  data = []
  for artist in search_result:
    data.append({
      "id" : artist.artist_id,
      "name" : artist.artist_name,
      "past_shows" : len(find_past_art_shows(artist.artist_id))})

  response={
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

def find_past_art_shows(id):
   
   return Show.query.filter(id == Show.artist_id, Show.start_time < datetime.now()).all()

def find_future_art_shows(id):
   
   return Show.query.filter(id == Show.artist_id, Show.start_time >= datetime.now()).all()




@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  
  art_data = Artist.query.filter(Artist.artist_id == artist_id).first()

  past_shows = find_past_art_shows(artist_id)
  past_show_data = []

  for show in past_shows:
    past_show_data.append({
      "venue_id": show.venue_id,
      "venue_name": Venue.query.filter(Venue.venue_id == show.venue_id).first().venue_name,
      "venue_image_link": Venue.query.filter(Venue.venue_id == show.venue_id).first().image_link,
      "start_time": str(show.start_time)

    })
    print (show.start_time)

  future_shows = find_future_art_shows(artist_id)
  future_show_data = []

  for show in future_shows:

    future_show_data.append({
      "venue_id": show.venue_id,
      "venue_name": Venue.query.filter(Venue.venue_id == show.venue_id).first().venue_name,
      "venue_image_link": Venue.query.filter(Venue.venue_id == show.venue_id).first().image_link,
      "start_time": str(show.start_time)
    
    })
    print (show.start_time)

  data={
    "id": artist_id,
    "name": art_data.artist_name,
    "genres": Art_genre.query.filter(Art_genre.artist_id == art_data.artist_id),
    "city": city_details.query.filter(city_details.city_id == art_data.city_id).first().city_name,
    "state": city_details.query.filter(city_details.city_id == art_data.city_id).first().state,
    "phone": art_data.artist_name,
    "website": art_data.website,
    "facebook_link": art_data.facebook_link,
    "seeking_venue": art_data.searching,
    "seeking_description": art_data.seeking_description,
    "image_link": art_data.image_link,
    "past_shows": past_show_data,
    "upcoming_shows": future_show_data,
    "past_shows_count": len(past_show_data),
    "upcoming_shows_count": len(future_show_data),
  }

  return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

  form = ArtistForm(request.form)

  data = Artist.query.filter(Artist.artist_id == artist_id)

  artist={
    "id": data.artist_id,
    "name": data.artist_name,
    "genres": artist_genre_connector(data.artist_id),
    "city": city_details.query.filter(city_details.city_id==data.city_id).first().city_name,
    "state": city_details.query.filter(city_details.city_id==data.city_id).first().state,
    "phone": data.phone,
    "website": data.website_link,
    "facebook_link": data.facebook_link,
    "seeking_venue": data.seeking_venue,
    "seeking_description": data.seeking_description,
    "image_link": data.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  form = ArtistForm(request.form)

  updated_artist = Artist()
  updated_artist.artist_name = form.name
  updated_artist.city_id = city_details.query.filter(form.city == city_details.city_name).first().city_id
  updated_artist.phone = form.phone
  updated_artist.image_link=form.image_link
  updated_artist.facebook_link = form.facebook_link
  updated_artist.searching = form.seeking_venue
  updated_artist.seeking_description = form.seeking_description
  updated_artist.website = form.website_link


  return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  data = Venue.query.filter(Venue.venue_id == venue_id).first()

  venue={
    "id": venue_id,
    "name": data.venue_name,
    "genres": venue_genre_connector(venue_id),
    "address": data.address,
    "city": city_details.query.filter(city_details.city_id==data.city_id).first().city_name,
    "state": city_details.query.filter(city_details.city_id==data.city_id).first().state,
    "phone": data.phone,
    "website": data.website_link,
    "facebook_link": data.facebook_link,
    "seeking_talent": data.seeking_talent,
    "seeking_description": data.seeking_description,
    "image_link": data.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  form = VenueForm(request.form)
  
  venue = Venue.query.filter(Venue.venue_name== venue_id).first

  venue.venue_name = form.venue_name
  venue.city_id = city_details.query.filter(city_details.city_name==form.city).first
  venue.address = form.address
  venue.phone = form.phone
  venue.image_link = form.image_link
  venue.facebook_link = form.facebook_link
  venue.website_link = form.website_link
  venue.seeking_talent = form.seeking_talent
  venue.seeking_description = form.seeking_description

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

  form = ArtistForm(request.form)

  error = False

  new_artist = Artist()

  if(len(city_details.query.filter(city_details.city_name == form.city.data).all()) < 1):
    new_city = city_details()
    new_city.city_name = form.city.data
    new_city.state = form.state.data
    db.session.add(new_city)
    db.session.commit()
    new_artist.city_id = city_details.query.filter(city_details.city_name == form.city.data).first().city_id

  else: new_artist.city_id = city_details.query.filter(city_details.city_name == form.city.data).first().city_id

  new_artist.artist_name = form.name.data
  new_artist.phone = form.phone.data
  new_artist.image_link = form.image_link.data
  new_artist.facebook_link = form.facebook_link.data
  new_artist.searching = form.seeking_venue.data
  new_artist.seeking_description = form.seeking_description.data
  new_artist.website = form.website_link.data

  try:
    db.session.add(new_artist)
    db.session.commit()

  except:
    error = True
    db.session.rollback()
    flash('Error: Artist was NOT successfully listed!')   
  finally:
    db.session.close()
    if(not error):
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
        
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
   
  show_data = Show.query.all()
  data = []

     
  for show in show_data:

     data.append({
      "venue_id": show.venue_id ,
      "venue_name": Venue.query.filter(Venue.venue_id == show.venue_id).first().venue_name,
      "artist_id": show.artist_id ,
      "artist_name": Artist.query.filter(Artist.artist_id == show.artist_id).first().artist_name,
      "artist_image_link": Artist.query.filter(Artist.artist_id == show.artist_id).first().image_link,
      "start_time": str(show.start_time)
      #  2024-01-17 10:01:06
      #  2019-05-21T21:30:00.000Z"
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
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  form = ShowForm(request.form)

  if(len(Artist.query.filter(Artist.artist_id == form.artist_id.data).all()) < 1):
     flash('Artist does not exist!')
     return render_template('pages/home.html')

  new_show = Show()
  new_show.artist_id = form.artist_id.data
  new_show.start_time = form.start_time.data
  new_show.venue_id = form.venue_id.data
  if(len(Venue.query.filter(Venue.venue_id == form.venue_id.data).all()) < 1):
     flash('Venue does not exist!')
     return render_template('pages/home.html')

  try:  
     db.session.add(new_show)
     db.session.commit()
  except:
     error = True    
     flash('Show failed to list!') 

  finally:
     db.session.close
     if(not error):
        flash('Show was successfully listed!')

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

