from flask import render_template, request, flash
from forms import ShowForm
from base import app, db
from models import  Venue,  Artist, Show
import dateutil

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
   
  show_data = Show.query.all()
  data = []

  for show in show_data:

     data.append({
      "venue_id": show.venue_id ,
      "venue_name" : db.session.query(Venue).select_from(Show).join(Venue, Venue.venue_id == Show.venue_id).filter(Venue.venue_id == show.venue_id).first().venue_name,
      "artist_id": show.artist_id ,
      "artist_name": Artist.query.filter(Artist.artist_id == show.artist_id).first().artist_name,
      "artist_image_link": Artist.query.filter(Artist.artist_id == show.artist_id).first().image_link,
      "start_time": str(show.start_time)

     })  
     print(str(show.start_time))

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