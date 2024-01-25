from flask import render_template, request, flash, redirect, url_for
from forms import VenueForm, datetime
from base import app, db
from models import city_details, Venue, Venue_genre, Artist, Show, Genre




def venue_genre_connector(venue_id):
   
  data = []
  genre_finder = Venue_genre.query.filter(Venue_genre.venue_id == venue_id).all()

  for genre in genre_finder:
    data.append(Genre.query.filter(genre.genre_id==Genre.genre_id).first().genre_name)
        
  return data


def find_past_venue_shows(id):

  data = db.session.query(Show).select_from(Venue).join(Show, Show.venue_id == Venue.venue_id).filter(Venue.venue_id == id, Show.start_time<datetime.now()).all()
  return data

#  return Show.query.join(Venue).filter(Show.venue_id == id).filter(Show.start_time < datetime.now()).all()

def find_future_venue_shows(id):
 
 data = db.session.query(Show).select_from(Venue).join(Show, Show.venue_id == Venue.venue_id).filter(Venue.venue_id == id, Show.start_time>=datetime.now()).all()
 
 return data

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
  response={
    "count": len(search),
    "data": venue_search_data(search)
   }

  return render_template('pages/search_venues.html', results = response, search_term= searchTerm)




def venue_search_data(search_data):
   
  response_data = []

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

  venue_data = Venue.query.filter(Venue.venue_id == venue_id).first()
  
  past_show_data = find_past_venue_shows(venue_id)
  past_show_info = []

  for show in past_show_data:
      
      artist = Artist.query.filter(Artist.artist_id == show.artist_id).first() 

      past_show_info.append({
      'artist_id' : show.artist_id,
      'artist_name' : artist.artist_name,
      'artist_image_link' :artist.image_link,
      'start_time' : str(show.start_time)})

  future_show_data = find_future_venue_shows(venue_id)
  future_show_info = []

  for show in future_show_data:
     
     artist = Artist.query.filter(Artist.artist_id == show.artist_id).first()

     future_show_info.append(
        {
        "artist_id": show.artist_id,
        "artist_name": artist.artist_name,
        "artist_image_link": artist.image_link,
        "start_time": str(show.start_time)
        })
  

  city_info = city_details.query.filter(city_details.city_id == venue_data.city_id).first()
  
  data={
    "id": venue_id,
    "venue_name": venue_data.venue_name,
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
    "past_shows": past_show_info,
    "upcoming_shows": future_show_info,
    "past_shows_count": len(past_show_info),
    "upcoming_shows_count": len(future_show_info)}
  
  
  return render_template('pages/show_venue.html', venue=data)

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm(request.form)
  
  if(form.validate):

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
    
    try:

      db.session.add(new_venue)
      db.session.commit()

      for genre in form.genres.data:
        
        if(len(Genre.query.filter(Genre.genre_name == genre).all())<1):
          new_genre = Genre(genre_name = genre)
          db.session.add(new_genre)

        new_genre_connection = Venue_genre()
        new_genre_connection.genre_id = Genre.query.filter(genre == Genre.genre_name).first().genre_id
        new_genre_connection.venue_id = Venue.query.filter(Venue.venue_name == new_venue.venue_name, Venue.phone == new_venue.phone).first().venue_id
        
        db.session.add(new_genre_connection)
        db.session.commit()

    except:
      db.session.rollback()
      flash("Venue was not successfully loaded")

    finally:
      db.session.close()
      return render_template('pages/home.html')
    
  else: 
    flash("Form was improperly filled out")
    return render_template('pages/home.html')
  
    # flash("Please ensure that all fields are filled out appropriately!")
    # return('/venues/create')



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




@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  data = Venue.query.filter(Venue.venue_id == venue_id).first()

  venue={
    "id": venue_id,
    "venue_name": data.venue_name,
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
  
  
  venue = Venue.query.filter(Venue.venue_id== venue_id).first()

  venue.venue_name = form.venue_name.data
  venue.city_id = city_details.query.filter(city_details.city_name==form.city.data).first().city_id
  venue.address = form.address.data
  venue.phone = form.phone.data
  venue.image_link = form.image_link.data
  venue.facebook_link = form.facebook_link.data
  venue.website_link = form.website_link.data
  venue.seeking_talent = form.seeking_talent.data
  venue.seeking_description = form.seeking_description.data

  db.session.commit()

  for genre in form.genres.data:
    
    if(len(Genre.query.filter(Genre.genre_name == genre).all())<1):
      new_genre = Genre(genre_name = genre)
      db.session.add(new_genre)

    new_genre_connection = Venue_genre()
    new_genre_connection.genre_id = Genre.query.filter(genre == Genre.genre_name).first().genre_id
    new_genre_connection.venue_id = Venue.query.filter(Venue.venue_name == venue.venue_name, Venue.phone == venue.phone).first().venue_id
    
    db.session.add(new_genre_connection)
    db.session.commit()

  

  return redirect(url_for('show_venue', venue_id=venue_id))