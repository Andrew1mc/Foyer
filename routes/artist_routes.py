from flask import render_template, request, flash, redirect, url_for, abort, jsonify
from forms import ArtistForm, datetime
from base import  app, db
from models import city_details, Venue, Artist, Show, Genre,Art_genre


def artist_genre_connector(artist_id):
   
  genre_data = []

  data = Art_genre.query.filter(Art_genre.artist_id == artist_id).all()

  for genre in data:
     genre_data.append(Genre.query.filter(genre.genre_name).one)


  return genre_data

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
      "artist_name" : artist.artist_name,
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
    
  data={
    "id": artist_id,
    "artist_name": art_data.artist_name,
    "genres": Art_genre.query.filter(Art_genre.artist_id == art_data.artist_id),
    "city": city_details.query.filter(city_details.city_id == art_data.city_id).first().city_name,
    "state": city_details.query.filter(city_details.city_id == art_data.city_id).first().state,
    "phone": art_data.phone,
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

  data = Artist.query.filter(Artist.artist_id == artist_id).first()

  artist={
    "id": data.artist_id,
    "artist_name": data.artist_name,
    "genres": artist_genre_connector(data.artist_id),
    "city": city_details.query.filter(city_details.city_id==data.city_id).first().city_name,
    "state": city_details.query.filter(city_details.city_id==data.city_id).first().state,
    "phone": data.phone,
    "website": data.website,
    "facebook_link": data.facebook_link,
    "seeking_venue": data.searching,
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


  updated_artist = Artist.query.filter(Artist.artist_id == artist_id).first()
  updated_artist.artist_name = form.name.data
  updated_artist.city_id = city_details.query.filter(form.city.data == city_details.city_name).first().city_id
  updated_artist.phone = form.phone.data
  updated_artist.image_link=form.image_link.data
  updated_artist.facebook_link = form.facebook_link.data
  updated_artist.searching = form.seeking_venue.data
  updated_artist.seeking_description = form.seeking_description.data
  updated_artist.website = form.website_link.data

  db.session.commit()
  


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