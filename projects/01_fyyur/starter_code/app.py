#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

#Flask migration
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

#liniking migration with app
migrate = Migrate(app,db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
#Gener should be standalone table with id,name and this table will be linked through many to many relationship with artists and venues
class Gener(db.Model):
      __tablename__ = 'Gener'
      id = db.Column(db.Integer,primary_key=True)
      name = db.Column(db.String(),nullable=False)

#Table of Gener, Artist many to many relation as Artist can have many genres and one gener can be performed by many artists
gener_artist = db.Table('gener_artist',
  db.Column('gener_id',db.Integer,db.ForeignKey('Gener.id'),primary_key=True),
  db.Column('artist_id',db.Integer,db.ForeignKey('Artist.id'),primary_key=True)
)

#Table of Gener, Venue many to many relation as Venue can have many genres and one gener can be performed in many venues
gener_venue = db.Table('gener_venue',
  db.Column('gener_id',db.Integer,db.ForeignKey('Gener.id'),primary_key=True),
  db.Column('venue_id',db.Integer,db.ForeignKey('Venue.id'),primary_key=True)
)

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(),nullable=False)
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(120),nullable=False)
    address = db.Column(db.String(120),nullable=False)
    #Not mandatory in frontend so it is nullable
    phone = db.Column(db.String(120))
    #No entry field in front end so it is nullable
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120),nullable=False)

    #Adding fields that shows in MOC data, setting defaults as there is no field in front end to be inserted
    website = db.Column(db.String(),default='www.mysite.com')
    seeking_talent = db.Column(db.Boolean,default=False)
    seeking_description = db.Column(db.String(),default='Seeking Venue Description')

    #Adding relation and backreference with Gener
    genres = db.relationship('Gener',secondary=gener_venue, backref=db.backref('venues', lazy=True))
    #Adding relation and backreference with Show
    shows = db.relationship('Show',backref=db.backref('venue',lazy=True))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(),nullable=False)
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(120),nullable=False)
    phone = db.Column(db.String(120))
    #This column is replaced with M2M relation as it will violate the 1st normal form if it is saved with comma separation
    #genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    #Adding fields that shows in MOC data, setting defaults as there is no field in front end to be inserted
    website = db.Column(db.String(),default='www.mysite.com')
    seeking_venue = db.Column(db.Boolean,default=False)
    seeking_description = db.Column(db.String(),default='Seeking Venue Description')

    #Adding relation and backreference with Gener
    genres = db.relationship('Gener',secondary=gener_artist, backref=db.backref('artists', lazy=True))
    #Adding relation and backreference with Show
    shows = db.relationship('Show',backref=db.backref('artist',lazy=True))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
      __tablename__ = 'Show'

      id = db.Column(db.Integer, primary_key=True)
      start_time = db.Column(db.DateTime, nullable=False)
      artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'),nullable=False)
      venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'),nullable=False)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]

  #Getting all venues data , order by city and state to be able to group by these field in returned data 
  venues = Venue.query.order_by(Venue.city.asc(),Venue.state.asc()).all()
  #Data initialization
  data = []
  location = ''
  venue_obj = {}
  venue_list =[]
  #looping through data to group venues data based on city and state
  for venue in venues:
        #This condition means new group found, because we sorted data based on city and state
        #Now create venues list for this city and state
        #getting number of upcoming show for venue
        now = datetime.now()
        shows = Show.query.filter( Show.start_time > now , Show.venue_id == venue.id).all()
        if(venue.city+venue.state != location):
              location = venue.city+venue.state
              venue_list =[]
              #Adding venues of city and state
              venue_list.append({"id":venue.id,"name":venue.name,"num_upcoming_shows" : len(shows)})
              #creating objec of venue state and city
              venue_obj = {
                "city": venue.city,
                "state": venue.state,
                "venues" : venue_list
              }
              data.append(venue_obj)
        else:
              venue_list.append({"id":venue.id,"name":venue.name,"num_upcoming_shows" : len(shows)})

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  #Getting data submited from the form
  search_term = request.form.get('search_term')
  #Searching using like incase sensitive
  venueList = Venue.query.filter(Venue.name.ilike('%'+search_term+'%')).all()
  data = []
  for venue in venueList:
        #upcoming shows for each venue
        now = datetime.now()
        shows = Show.query.filter( Show.start_time > now , Show.venue_id == venue.id).all()
        data.append({"id":venue.id,"name":venue.name,"num_upcoming_shows":len(shows)})

  response = {"count":len(venueList),"data": data}

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  past_shows = []
  upcoming_shows = []
  past_shows_count = 0
  upcoming_shows_count = 0
  now = datetime.now()

  #Retriving venue data with id
  venue = Venue.query.get(venue_id)

  #looping through Venue shows
  for show in venue.shows:
        #these are upcoming shows,increment upcoming show count by 1 and fil upcoming shows array
        if show.start_time >= now:
              upcoming_shows_count += 1
              upcoming_shows.append(
                {
                  "artist_id": show.artist_id,
                  "artist_name": show.artist.name,
                  "artist_image_link": show.artist.image_link,
                  "start_time": str(show.start_time)
                }
              )
        else :
              #these are past shows
              past_shows_count += 1
              past_shows.append(
                {
                  "artist_id": show.artist_id,
                  "artist_name": show.artist.name,
                  "artist_image_link": show.artist.image_link,
                  "start_time": str(show.start_time)
                }
              )
          

  data = {
      "id" : venue.id,
      "name" : venue.name,
      "genres" :  [genre.name for genre in venue.genres],
      "address" :  venue.address,
      "city" :  venue.city,
      "state" :  venue.state,
      "phone" :  venue.phone,
      "website" :  venue.website,
      "facebook_link" :  venue.facebook_link,
      "seeking_talent" :  venue.seeking_talent,
      "seeking_description" :  venue.seeking_description,
      "image_link" :  venue.image_link,
      "past_shows" : past_shows,
      "upcoming_shows" : upcoming_shows,
      "past_shows_count" : past_shows_count,
      "upcoming_shows_count" : upcoming_shows_count
  }
  print(venue.genres)

  # data1={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #   "past_shows": [{
  #     "artist_id": 4,
  #     "artist_name": "Guns N Petals",
  #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 2,
  #   "name": "The Dueling Pianos Bar",
  #   "genres": ["Classical", "R&B", "Hip-Hop"],
  #   "address": "335 Delancey Street",
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "914-003-1132",
  #   "website": "https://www.theduelingpianos.com",
  #   "facebook_link": "https://www.facebook.com/theduelingpianos",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 3,
  #   "name": "Park Square Live Music & Coffee",
  #   "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
  #   "address": "34 Whiskey Moore Ave",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "415-000-1234",
  #   "website": "https://www.parksquarelivemusicandcoffee.com",
  #   "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #   "past_shows": [{
  #     "artist_id": 5,
  #     "artist_name": "Matt Quevedo",
  #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [{
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 1,
  # }
  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

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
  form = VenueForm()
  error = False

  #Creating venue object from form parameters
  venue = Venue(
    name = form.name.data,
    city = form.city.data,
    state = form.state.data,
    address = form.address.data,
    phone = form.phone.data,
    image_link = form.image_link.data,
    facebook_link = form.facebook_link.data,
    website = form.website.data ,
    seeking_talent = True if form.seeking_talent.data == 'Yes' else False,
    seeking_description = form.seeking_description.data
  )
  #Handling gnres of venues - should be added as object to object venue so we will check the existance of the type if exists return object from db for not duplicating
  #if not exist create it in db
  print(form.genres.data)
  for gener in form.genres.data:
        print(gener)
        gener_obj = Gener.query.filter_by(name=gener).one_or_none()

        if gener_obj:
              venue.genres.append(gener_obj)
        else:
              #if not found create gener and then add venue relation
              newGener = Gener(name=gener)
              db.session.add(newGener)
              venue.genres.append(newGener)

  #attaching venue object to db
  try:
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()

  if not error:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  else:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  venue = Venue.query.get(venue_id)
  error = False

  if venue:
        try:
          db.session.delete(venue)
          db.session.commit()
        except:
          error = True
          db.session.rollback()
        finally:
          db.session.close()
  
  if not error:
    flash('Venue  was successfully deleted!')
  else:
    flash('An error occurred. Venue  could not be deleted.')

  #For some reason this redirect is not working properly, but data is deleted
  return render_template('pages/home.html')


  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  # return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = []
  artistList = Artist.query.order_by(Artist.id).all()
  for artist in artistList:
        data.append(
          {
            "id": artist.id,
            "name": artist.name
          }
        )
        
  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  data = []
  now = datetime.now()
  search_term = request.form.get('search_term')
  artistList = Artist.query.filter(Artist.name.ilike('%'+search_term+'%')).all()
  for artist in artistList:
        #getting artist shows
        shows = Show.query.filter( Show.start_time > now , Show.artist_id == artist.id).all()
        data.append(
          {
            "id":artist.id,
            "name": artist.name,
            "num_upcoming_shows": len(shows)
          }
        )
  response={
    "count": len(artistList),
    "data": data
  }
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  past_shows = []
  upcoming_shows = []
  past_shows_count = 0
  upcoming_shows_count = 0
  now = datetime.now()

  #Retriving artist data with id
  artist = Artist.query.get(artist_id)

  #looping through Artist shows
  for show in artist.shows:
        #these are upcoming shows,increment upcoming show count by 1 and fil upcoming shows array
        if show.start_time >= now:
              upcoming_shows_count += 1
              upcoming_shows.append(
                {
                  "venue_id": show.venue_id,
                  "venue_name": show.venue.name,
                  "venue_image_link": show.venue.image_link,
                  "start_time": str(show.start_time)
                }
              )
        else :
              #these are past shows
              past_shows_count += 1
              past_shows.append(
                {
                  "venue_id": show.venue_id,
                  "venue_name": show.venue.name,
                  "venue_image_link": show.venue.image_link,
                  "start_time": str(show.start_time)
                }
              )
          

  data = {
      "id" : artist.id,
      "name" : artist.name,
      "genres" :  [genre.name for genre in artist.genres],
      "city" :  artist.city,
      "state" :  artist.state,
      "phone" :  artist.phone,
      "website" :  artist.website,
      "facebook_link" :  artist.facebook_link,
      "seeking_venue" :  artist.seeking_venue,
      "seeking_description" :  artist.seeking_description,
      "image_link" :  artist.image_link,
      "past_shows" : past_shows,
      "upcoming_shows" : upcoming_shows,
      "past_shows_count" : past_shows_count,
      "upcoming_shows_count" : upcoming_shows_count
  }
  
  # data1={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }

  # data1={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 5,
  #   "name": "Matt Quevedo",
  #   "genres": ["Jazz"],
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "300-400-5000",
  #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "past_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  #   "genres": ["Jazz", "Classical"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "432-325-5432",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 3,
  # }
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  artist = Artist.query.get(artist_id)

  if artist:
        form.name.data = artist.name
        form.genres.data = [ genre.name for genre in artist.genres]
        form.city.data = artist.city
        form.state.data = artist.state
        form.phone.data = artist.phone
        form.website.data = artist.website
        form.facebook_link.data = artist.facebook_link
        form.seeking_venue.data = artist.seeking_venue
        form.seeking_description.data = artist.seeking_description
        form.image_link.data = artist.image_link        
        

  # artist={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm()
  error = False

  artist = Artist.query.get(artist_id)

  #updaing fields
  artist.name = form.name.data
  artist.city = form.city.data
  artist.state = form.state.data
  artist.phone = form.phone.data
  artist.website = form.website.data
  artist.facebook_link = form.facebook_link.data
  artist.seeking_venue = True if form.seeking_venue.data == 'Yes' else False
  artist.seeking_description = form.seeking_description.data
  artist.image_link = form.image_link.data

  #reinserting geners
  artist.genres  = []
  for gener in form.genres.data:
    gener_obj = Gener.query.filter_by(name=gener).one_or_none()

    if gener_obj:
          artist.genres.append(gener_obj)
    else:
          #if not found create gener and then add venue relation
          newGener = Gener(name=gener)
          db.session.add(newGener)
          artist.genres.append(newGener)
  
  #attaching venue object to db
  try:
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()

  if not error:
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully edited!')
  else:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be edited.')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  venue = Venue.query.get(venue_id)

  if venue:
        form.name.data = venue.name
        form.genres.data = [ genre.name for genre in venue.genres]
        form.address.data = venue.address
        form.city.data = venue.city
        form.state.data = venue.state
        form.phone.data = venue.phone
        form.website.data = venue.website
        form.facebook_link.data = venue.facebook_link
        form.seeking_talent.data = venue.seeking_talent
        form.seeking_description.data = venue.seeking_description
        form.image_link.data = venue.image_link    
  
  # venue = {
  #     "id" : venueModel.id,
  #     "name" : venueModel.name,
  #     "genres" :  [genre.name for genre in venueModel.genres],
  #     "address": venueModel.address,
  #     "city" :  venueModel.city,
  #     "state" :  venueModel.state,
  #     "phone" :  venueModel.phone,
  #     "website" :  venueModel.website,
  #     "facebook_link" :  venueModel.facebook_link,
  #     "seeking_talent" : venueModel.seeking_talent,
  #     "seeking_description" :  venueModel.seeking_description,
  #     "image_link" :  venueModel.image_link
  # }

  # venue={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  # }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm()
  error = False

  venue = Venue.query.get(venue_id)

  #updaing fields
  venue.name = form.name.data
  venue.address = form.address.data
  venue.city = form.city.data
  venue.state = form.state.data
  venue.phone = form.phone.data
  venue.website = form.website.data
  venue.facebook_link = form.facebook_link.data
  venue.seeking_talent = True if form.seeking_talent.data == 'Yes' else False
  venue.seeking_description = form.seeking_description.data
  venue.image_link = form.image_link.data

  #reinserting geners
  venue.genres  = []
  for gener in form.genres.data:
    gener_obj = Gener.query.filter_by(name=gener).one_or_none()

    if gener_obj:
          venue.genres.append(gener_obj)
    else:
          #if not found create gener and then add venue relation
          newGener = Gener(name=gener)
          db.session.add(newGener)
          venue.genres.append(newGener)
  
  #attaching venue object to db
  try:
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()

  if not error:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully edited!')
  else:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be edited.')

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
  form = ArtistForm()
  error = False

  #Creating venue object from form parameters
  artist = Artist(
    name = form.name.data,
    city = form.city.data,
    state = form.state.data,
    phone = form.phone.data,
    image_link = form.image_link.data,
    facebook_link = form.facebook_link.data,
    website = form.website.data ,
    seeking_venue = True if form.seeking_venue.data == 'Yes' else False,
    seeking_description = form.seeking_description.data
  )
  #Handling gnres of venues - should be added as object to object venue so we will check the existance of the type if exists return object from db for not duplicating
  #if not exist create it in db
  for gener in form.genres.data:

        gener_obj = Gener.query.filter_by(name=gener).one_or_none()

        if gener_obj:
              artist.genres.append(gener_obj)
        else:
              #if not found create gener and then add venue relation
              newGener = Gener(name=gener)
              db.session.add(newGener)
              artist.genres.append(newGener)

  #attaching venue object to db
  try:
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()

  if not error:
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  else:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  showList = Show.query.all()
  for show in showList:
        data.append(
          {
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": str(show.start_time)
          }
        )
  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]
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
  form = ShowForm()
  error = False

  show = Show(
    venue_id = form.venue_id.data,
    artist_id = form.artist_id.data,
    start_time = form.start_time.data
  )

  try:
    db.session.add(show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    erroe = True
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()


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

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
