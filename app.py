# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import dateutil.parser
import babel
from flask import render_template, request, flash, redirect, url_for, abort
import logging
from logging import Formatter, FileHandler
from forms import *
from models import *

from datetime import datetime
import re
import sys

from models import app


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


# ----------------------------------------------------------------------------#
#  Venues
# ----------------------------------------------------------------------------#

@app.route('/venues')
def venues():

    # DONE this route passes the data dict to the view.
    # store this data into the db
    # write the route so that it pulls this very same data from the db

    # DONE: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming
    #       shows per venue.

    data = list()

    queried_areas = Venue.query.with_entities(Venue.city, Venue.state)\
        .group_by(Venue.city, Venue.state).all()

    for area in queried_areas:
        result = {
            "city": area[0],
            "state": area[1],
            "venues": [],
        }

        queried_venues = Venue.query.filter_by(city=area[0]).all()
        for venue in queried_venues:
            num_upcoming_shows = count_shows(venue.show)["upcoming"]

            inner_result = {
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": num_upcoming_shows
            }

            result["venues"].append(inner_result)
        data.append(result)

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():

    # DONE: implement search on artists with partial string search.
    #       Ensure it is case-insensitive.
    #       seach for Hop should return "The Musical Hop".
    #       search for "Music" should return "The Musical Hop" and "Park
    #       Square Live Music & Coffee"

    search_term = request.form.get("search_term").strip()
    venues = Venue.query.filter(Venue.name.ilike(f"%{search_term}%")).all()

    data = list()
    for venue in venues:
        venue_data = {
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": count_shows(venue.show)["upcoming"]
        }
        data.append(venue_data)
    response = {
        "count": len(venues),
        "data": data
    }

    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # DONE: replace with real venue data from the venues table, using venue_id

    venue = Venue.query.filter_by(id=venue_id).first_or_404()
    shows = check_shows(venue)
    # turn the list of Genre objects into a list of strings
    venue_genre = [genre.name for genre in list(venue.genre)]
    # convert the Venue object to its dict representation to assign items
    venue = venue.__dict__
    del venue["_sa_instance_state"]  # delete SQLAlchemy instance state
    venue["genres"] = venue_genre
    venue["upcoming_shows"] = shows["upcoming_shows"]
    venue["past_shows"] = shows["past_shows"]
    venue["past_shows_count"] = shows["past_shows_count"]
    venue["upcoming_shows_count"] = shows["upcoming_shows_count"]

    return render_template('pages/show_venue.html', venue=venue)


# ----------------------------------------------------------------
# Create Venue
# ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # DONE: insert form data as a new Venue record in the db, instead
    # DONE: modify data to be the data object returned from db insertion

    form = VenueForm(request.form, meta={"csrf": False})

    # Enforce form fields validation, rejecting malformed data
    if not form.validate():
        for k, v in form.errors.items():
            flash(f"Venue not saved: {v[0]}")
        return redirect(url_for('create_venue_submission'))
    else:
        error = False
        # the form returns a list of genres names (strings) whereas the
        # genres m2m relationship requires a list of Genre objects.
        # Turn the list of Genre names into a list of Genre objects
        if form.genres.data:
            genres = [Genre.query.filter_by(name=name).one_or_none() for name
                      in form.genres.data]

        venue = Venue(
            name=form.name.data.strip(),
            city=form.city.data.strip(),
            state=form.state.data,
            address=form.address.data.strip(),
            # strip non-digits
            phone=re.sub("\D", "", form.phone.data.strip()),
            genre=genres,
            seeking_talent=True if form.seeking_talent.data == "Yes" else False,
            seeking_description=form.seeking_description.data.strip(),
            image_link=form.image_link.data.strip(),
            website=form.website.data.strip(),
            facebook_link=form.facebook_link.data.strip(),
        )

        try:
            db.session.add(venue)
            db.session.commit()
            flash(f"Venue {venue.name} was successfully listed!")
        except Exception as e:
            print(sys.exc_info())
            print(e)
            error = True
            db.session.rollback()
        finally:
            db.session.close()

        if error:
            # DONE: on unsuccessful db insert, flash an error instead.
            flash(f"Venue {venue.name} could not be listed.")
            abort(500)

    return redirect(url_for('index'))


@app.route('/venues/<int:venue_id>', methods=['POST'])
def delete_venue(venue_id):
    # DONE: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session
    # commit could fail.

    # make sure the venue exists
    # venue = Venue.query.get(venue_id)
    venue = Venue.query.filter_by(id=venue_id).first_or_404()
    if not venue:
        # the call was somehow faked
        flash("The requested venue doesn't exist.")
        return redirect(url_for("venues"))
    else:
        error = False
        venue_name = venue.name  # store for the final flash
        try:
            db.session.delete(venue)
            db.session.commit()
        except Exception as e:
            print(sys.exc_info())
            print(e)
            error = True
            db.session.rollback()
        finally:
            db.session.close()

        if error:
            flash(f"An error occurred while deleting {venue_name}.")
            print(f"An error occurred while deleting {venue_name}.")
            abort(500)
        else:
            flash(f"successfully deleted venue {venue_name}!")
            return redirect(url_for("venues"))

    # BONUS CHALLENGE: DONE Implement a button to delete a Venue on a Venue Page,
    # have it so that clicking that button delete it from the db then redirect
    # the user to the homepage
    # return None


#  ----------------------------------------------------------------
#  Artists
#  ----------------------------------------------------------------

@app.route('/artists')
def artists():
    # DONE: replace with real data returned from querying the database

    data = Artist.query.with_entities(Artist.id, Artist.name)\
        .group_by(Artist.id, Artist.name).all()
    data = [{"id": x[0], "name": x[1]} for x in data]

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # DONE: implement search on artists with partial string search.
    # Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and
    # "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    search_term = request.form.get("search_term").strip()
    artists = Artist.query.filter(Artist.name.ilike(f"%{search_term}%")).all()

    data = list()
    for artist in artists:
        artist_data = {
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": count_shows(artist.show)["upcoming"]
        }
        data.append(artist_data)
    response = {
        "count": len(artists),
        "data": data
    }

    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # DONE: replace with real venue data from the venues table, using venue_id

    artist = Artist.query.filter_by(id=artist_id).first_or_404()
    shows = check_shows(artist)
    # turn the list of Genre objects into a list of strings
    artist_genre = [genre.name for genre in list(artist.genre)]
    # convert the Venue object to its dict representation to assign items
    artist = artist.__dict__
    del artist["_sa_instance_state"]  # delete SQLAlchemy instance state
    artist["genres"] = artist_genre
    artist["upcoming_shows"] = shows["upcoming_shows"]
    artist["past_shows"] = shows["past_shows"]
    artist["past_shows_count"] = shows["past_shows_count"]
    artist["upcoming_shows_count"] = shows["upcoming_shows_count"]

    return render_template('pages/show_artist.html', artist=artist)


#  ----------------------------------------------------------------
#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    # DONE: populate form with fields from artist with ID <artist_id>
    artist = Artist.query.get(artist_id)
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # DONE: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    artist = Artist.query.get(artist_id)

    form = ArtistForm(request.form, meta={"csrf": False})

    # Enforce form fields validation, rejecting malformed data
    if not form.validate():
        for k, v in form.errors.items():
            flash(f"Artist not saved: {v[0]}")
        return redirect(url_for('edit_artist_submission', artist_id=artist_id))
    else:
        error = False
        # the form returns a list of genres names (strings) whereas the
        # genres m2m relationship requires a list of Genre objects.
        # Turn the list of Genre names into a list of Genre objects
        if form.genres.data:
            genres = [Genre.query.filter_by(name=name).one_or_none() for name
                      in form.genres.data]

        artist.name = form.name.data.strip()
        artist.city = form.city.data.strip()
        artist.state = form.state.data
        artist.phone = re.sub(
            "\D", "", form.phone.data.strip())  # strip non-digits
        artist.genre = genres
        artist.seeking_venue = True if form.seeking_venue.data == "Yes" else False
        artist.seeking_description = form.seeking_description.data.strip()
        artist.image_link = form.image_link.data.strip()
        artist.website = form.website.data.strip()
        artist.facebook_link = form.facebook_link.data.strip()

        try:
            db.session.add(artist)
            db.session.commit()
            flash(f"Artist {artist.name} was successfully listed!")
        except Exception as e:
            print(sys.exc_info())
            print(e)
            error = True
            db.session.rollback()
        finally:
            db.session.close()

        if error:
            # DONE: on unsuccessful db insert, flash an error instead.
            flash(f"Artist {artist.name} could not be listed.")
            abort(500)

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    # DONE: populate form with values from venue with ID <venue_id>
    venue = Venue.query.get(venue_id)
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # DONE: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes

    venue = Venue.query.get(venue_id)
    form = VenueForm(request.form, meta={"csrf": False})

    # Enforce form fields validation, rejecting malformed data
    if not form.validate():
        for k, v in form.errors.items():
            flash(f"Venue not saved: {v[0]}")
        return redirect(url_for('edit_venue_submission', venue_id=venue_id))
    else:
        error = False
        # the form returns a list of genres names (strings) whereas the
        # genres m2m relationship requires a list of Genre objects.
        # Turn the list of Genre names into a list of Genre objects
        if form.genres.data:
            genres = [Genre.query.filter_by(name=name).one_or_none() for name
                      in form.genres.data]

        venue.name = form.name.data.strip()
        venue.city = form.city.data.strip()
        venue.state = form.state.data
        venue.phone = re.sub("\D", "", form.phone.data.strip())  # strip non-digits
        venue.genre = genres
        venue.address = form.address.data.strip()
        venue.seeking_talent = True if form.seeking_talent.data == "Yes" else False
        venue.seeking_description = form.seeking_description.data.strip()
        venue.image_link = form.image_link.data.strip()
        venue.website = form.website.data.strip()
        venue.facebook_link = form.facebook_link.data.strip()

        try:
            db.session.add(venue)
            db.session.commit()
            flash(f"Venue {venue.name} was successfully listed!")
        except Exception as e:
            print(sys.exc_info())
            print(e)
            error = True
            db.session.rollback()
        finally:
            db.session.close()

        if error:
            # DONE: on unsuccessful db insert, flash an error instead.
            flash(f"Venue {venue.name} could not be listed.")
            abort(500)

    return redirect(url_for('show_venue', venue_id=venue_id))


#  ----------------------------------------------------------------
#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # DONE: insert form data as a new Venue record in the db, instead
    # DONE: modify data to be the data object returned from db insertion
    form = ArtistForm(request.form, meta={"csrf": False})

    # Enforce form fields validation, rejecting malformed data
    if not form.validate():
        for k, v in form.errors.items():
            flash(f"Artist not saved: {v[0]}")
        return redirect(url_for('create_artist_submission'))
    else:
        error = False
        # the form returns a list of genres names (strings) whereas the
        # genres m2m relationship requires a list of Genre objects.
        # Turn the list of Genre names into a list of Genre objects
        if form.genres.data:
            genres = [Genre.query.filter_by(name=name).one_or_none() for name
                      in form.genres.data]

        artist = Artist(
            name=form.name.data.strip(),
            city=form.city.data.strip(),
            state=form.state.data,
            # strip non-digits
            phone=re.sub("\D", "", form.phone.data.strip()),
            genre=genres,
            seeking_venue=True if form.seeking_venue.data == "Yes" else False,
            seeking_description=form.seeking_description.data.strip(),
            image_link=form.image_link.data.strip(),
            website=form.website.data.strip(),
            facebook_link=form.facebook_link.data.strip(),
        )

        try:
            db.session.add(artist)
            db.session.commit()
            flash(f"Artist {artist.name} was successfully listed!")
        except Exception as e:
            print(sys.exc_info())
            print(e)
            error = True
            db.session.rollback()
        finally:
            db.session.close()

        if error:
            # DONE: on unsuccessful db insert, flash an error instead.
            flash(f"Artist {artist.name} could not be listed.")
            abort(500)

    return redirect(url_for('index'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # DONE: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.

    shows = Show.query.all()
    for show in shows:
        venue_name = show.venue.name
        artist_name = show.artist.name
        artist_image_link = show.artist.image_link
        start_time = str(show.start_time)
        show = show.__dict__
        del show["_sa_instance_state"]
        show["venue_name"] = venue_name
        show["artist_name"] = artist_name
        show["artist_image_link"] = artist_image_link
        show["start_time"] = start_time

    return render_template('pages/shows.html', shows=shows)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    form = ShowForm(request.form, meta={"csrf": False})

    # Enforce form fields validation, rejecting malformed data
    if not form.validate():
        for k, v in form.errors.items():
            flash(f"Show not saved: {v[0]}")
        return redirect(url_for('create_show_submission'))
    else:
        error = False

        show = Show(
            artist_id=form.artist_id.data.strip(),
            venue_id=form.venue_id.data.strip(),
            start_time=form.start_time.data
        )

        try:
            db.session.add(show)
            db.session.commit()
            flash(f"Show successfully listed!")
        except Exception as e:
            print(sys.exc_info())
            print(e)
            error = True
            db.session.rollback()
        finally:
            db.session.close()

        if error:
            # DONE: on unsuccessful db insert, flash an error instead.
            flash(f"Show could not be listed.")
            abort(500)

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
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')


# helper modules: I'd like to move these elsewhere but I forgot how to
# solve the circular imports issue and I have not time to re-learn that now
def count_shows(shows):
    """Given a list of Show objects, count both past and coming.
    Returns a dict:
    shows_count = {
        "upcoming": 0,
        "past": 0
        }
    """
    now = datetime.now()
    shows_count = {"upcoming": 0, "past": 0}
    for show in shows:
        if show.start_time > now:
            shows_count["upcoming"] += 1
        else:
            shows_count["past"] += 1
    return shows_count


def check_shows(object):
    """Given a Venue or Artist object, distinguish between past and upcoming
    shows, then count them. Returns a dict:
    shows = {
        "past_shows": [
            ...
            ],
        "upcoming_shows": [],
        "past_shows_count": 0,
        "upcoming_shows_count": 0
        }
    """
    now = datetime.now()
    shows = {"past_shows": [], "upcoming_shows": [], "past_shows_count": 0,
             "upcoming_shows_count": 0}
    for show in object.show:
        # extract artist information to bet stored in the show dict
        venue_id = show.venue.id
        venue_name = show.venue.name
        venue_image_link = show.venue.image_link
        artist_id = show.artist.id
        artist_name = show.artist.name
        artist_image_link = show.artist.image_link
        # store the Show start_time to allow for a comparison later
        start_time = show.start_time
        # app.show_venue() requires strings to be rendered in the HTML,
        # as well as artist name, artist image link therefore convert the Show
        # object to its dict representation to add extra keys + values.
        show = show.__dict__
        del show["_sa_instance_state"]
        show["venue_id"] = venue_id
        show["venue_name"] = venue_name
        show["venue_image_link"] = venue_image_link
        show["artist_id"] = artist_id
        show["artist_name"] = artist_name
        show["artist_image_link"] = artist_image_link
        # Remember that in order to parse start_time correctly in the HTML,
        # it must be converted to a string as well.
        show["start_time"] = str(start_time)
        if start_time > now:
            shows["upcoming_shows"].append(show)
        else:
            shows["past_shows"].append(show)
    shows["past_shows_count"] = len(shows["past_shows"])
    shows["upcoming_shows_count"] = len(shows["upcoming_shows"])
    return shows


# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#


# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port)
'''
