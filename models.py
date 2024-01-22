from base import app,db

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
    venue_id= db.Column((db.Integer), db.ForeignKey(Venue.venue_id))

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