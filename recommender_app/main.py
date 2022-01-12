from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from sqlalchemy import UniqueConstraint
from sqlalchemy.sql import func
import json

FLASK_SECRET_KEY = '546cfaac2bd3703f257f7a95'
# Dev PostGres Credentials
pg_user_dev = 'postgres'
pg_pass_dev = 'admin'
pg_db_dev = 'postgres'
pg_host_dev = 'localhost'
pg_port_dev = 5432
DEV_DB = f"postgresql://{pg_user_dev}:{pg_pass_dev}@{pg_host_dev}:{pg_port_dev}/{pg_db_dev}"

app = Flask(__name__)

app.config['SECRET_KEY'] = FLASK_SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = DEV_DB

db = SQLAlchemy(app)

@app.route("/")
def hello_world():
    genres = ['genre_no_genres_listed', 'genre_action', 'genre_adventure', 'genre_animation', 'genre_children',
              'genre_comedy', 'genre_crime', 'genre_documentary', 'genre_drama', 'genre_fantasy', 'genre_film_noir',
              'genre_horror', 'genre_imax', 'genre_musical', 'genre_mystery', 'genre_romance', 'genre_sci_fi',
              'genre_thriller', 'genre_war', 'genre_western']
    # Get Top 20 Most Popular Movies
    movie_counts_subquery = db.session.query(Ratings.movieId, func.count(Ratings.movieId).label(
        "movies_count")).group_by(Ratings.movieId).subquery()
    cols = [Movies.id, Movies.title, movie_counts_subquery.c.movies_count] + \
           [getattr(Movies, genre) for genre in genres]
    movie_counts = db.session.query(*cols).join(
        movie_counts_subquery, (Movies.id == movie_counts_subquery.c.movieId)).order_by(
        sqlalchemy.desc("movies_count")).all()
    movie_counts = [dict(x) for x in movie_counts]
    return render_template('index.html', movies = movie_counts)

class MovieUsers(db.Model):
    id = db.Column("userId", db.Integer(), primary_key=True)
    ratings = db.relationship('Ratings', backref='movie_users', lazy=True)
    tags = db.relationship('Tags', backref='movie_users', lazy=True)
    __table_args__ = ({"schema":"movie_recommender"})

class Movies(db.Model):
    id = db.Column("movieId", db.Integer(), primary_key=True)
    title = db.Column(db.String(), nullable = False)
    # Genres
    genre_no_genres_listed = db.Column(db.Boolean(), nullable = False, default = False)
    genre_action = db.Column(db.Boolean(), nullable = False, default = False)
    genre_adventure = db.Column(db.Boolean(), nullable=False, default=False)
    genre_animation = db.Column(db.Boolean(), nullable=False, default=False)
    genre_children = db.Column(db.Boolean(), nullable=False, default=False)
    genre_comedy = db.Column(db.Boolean(), nullable=False, default=False)
    genre_crime = db.Column(db.Boolean(), nullable=False, default=False)
    genre_documentary = db.Column(db.Boolean(), nullable=False, default=False)
    genre_drama = db.Column(db.Boolean(), nullable=False, default=False)
    genre_fantasy = db.Column(db.Boolean(), nullable=False, default=False)
    genre_film_noir = db.Column(db.Boolean(), nullable=False, default=False)
    genre_horror = db.Column(db.Boolean(), nullable=False, default=False)
    genre_imax = db.Column(db.Boolean(), nullable=False, default=False)
    genre_musical = db.Column(db.Boolean(), nullable=False, default=False)
    genre_mystery = db.Column(db.Boolean(), nullable=False, default=False)
    genre_romance = db.Column(db.Boolean(), nullable=False, default=False)
    genre_sci_fi = db.Column(db.Boolean(), nullable=False, default=False)
    genre_thriller = db.Column(db.Boolean(), nullable=False, default=False)
    genre_war = db.Column(db.Boolean(), nullable=False, default=False)
    genre_western = db.Column(db.Boolean(), nullable=False, default=False)
    ratings = db.relationship('Ratings', backref='movies', lazy=True)
    tags = db.relationship('Tags', backref='movies', lazy=True)
    links = db.relationship('Links', backref='movies', uselist=False, lazy=True)
    __table_args__ = ({"schema":"movie_recommender"})

class Ratings(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    userId = db.Column(db.Integer(), db.ForeignKey('movie_recommender.movie_users.userId'))
    movieId = db.Column(db.Integer(), db.ForeignKey('movie_recommender.movies.movieId'))
    rating = db.Column(db.Float(), nullable = False)
    timestamp = db.Column(db.DateTime(), nullable = False)
    __table_args__ = (UniqueConstraint('userId', 'movieId', name='_ratings_user_movie_uc'),
                     {"schema":"movie_recommender"})

class Tags(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    userId = db.Column(db.Integer(), db.ForeignKey('movie_recommender.movie_users.userId'))
    movieId = db.Column(db.Integer(), db.ForeignKey('movie_recommender.movies.movieId'))
    tag = db.Column(db.String(), nullable = False)
    timestamp = db.Column(db.DateTime(), nullable = False)
    __table_args__ = ({"schema":"movie_recommender"})

class Links(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    movieId = db.Column(db.Integer(), db.ForeignKey('movie_recommender.movies.movieId'))
    imdbId = db.Column(db.Integer(), nullable = False)
    tmdbId = db.Column(db.Integer(), nullable = True)
    __table_args__ = ({"schema":"movie_recommender"})




