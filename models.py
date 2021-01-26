from flask import Flask
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime


# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

# DONE: connect to a local postgresql database

app = Flask(__name__)
app.config.from_object("config")
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# ----------------------------------------------------------------------
# Models.
# ----------------------------------------------------------------------

venue_genre = db.Table("venue_genre",
                       db.Column("venue_id", db.Integer,
                                 db.ForeignKey("venue.id")),
                       db.Column("genre_id", db.Integer, db.ForeignKey("genre.id")))

artist_genre = db.Table("artist_genre",
                        db.Column("artist_id", db.Integer,
                                  db.ForeignKey("artist.id")),
                        db.Column("genre_id", db.Integer, db.ForeignKey("genre.id")))


class Venue(db.Model):
    __tablename__ = "venue"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))

    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    genre = db.relationship("Genre", secondary=venue_genre, backref="venue")
    show = db.relationship("Show", back_populates="venue")

    def __repr__(self):
        return f"<{self.name} {self.city} {self.state}>"


class Artist(db.Model):
    __tablename__ = "artist"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))

    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    genre = db.relationship("Genre", secondary=artist_genre, backref="artist")
    show = db.relationship("Show", back_populates="artist")

    def __repr__(self):
        return f"<{self.name}>"


class Genre(db.Model):
    __tablename__ = "genre"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)


class Show(db.Model):
    __tablename__ = "show"
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey("venue.id"))
    artist_id = db.Column(db.Integer, db.ForeignKey("artist.id"))
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    venue = db.relationship("Venue", back_populates="show")
    artist = db.relationship("Artist", back_populates="show")
    # artist = db.relationship(Artist, backref=db.backref('shows', cascade='all, delete'))
    # venue = db.relationship(Venue, backref=db.backref('shows', cascade='all, delete'))

    def __repr__(self):
        return f"<v_id: {self.venue_id}, a_id: {self.artist_id}, {self.start_time}>"


# DONE Implement Show and Artist models, and complete all model
# relationships and properties, as a database migration.
# Shows: Venues-Artists + datetime (Association Object)
# Genres-Venues (Association Table)
# Genres-Artists (Association Table)
