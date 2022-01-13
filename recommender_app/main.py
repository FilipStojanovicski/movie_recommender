from flask import Flask
from flask import session, render_template, url_for, request
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from sqlalchemy import UniqueConstraint
from sqlalchemy.sql import func
import json
import pandas as pd
import numpy as np

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

@app.route('/handle_data', methods=['POST'])
def handle_data():
    form_data = request.form

    # Get form data
    keys = list(form_data.keys())
    input_ratings = []
    for x in zip(*form_data.listvalues()):
        inputs = {}
        for i in range(len(keys)):
            inputs[keys[i]] = x[i]
        input_ratings.append(inputs)

    print(input_ratings)

    validated_ratings = [rating for rating in input_ratings if (rating['movies'] != '-1' and rating['ratings'] != '-1')]

    print(validated_ratings)

    response = {"successful": False}
    num_valid_ratings = len(validated_ratings)

    if num_valid_ratings < 5:
        return response

    validated_ratings = [{"movieId": int(x["movies"]), "rating": float(x["ratings"])} for x in validated_ratings]
    print(validated_ratings)

    ratings = pd.read_sql_table(
        "ratings",
        con=db.engine,
        schema="movie_recommender"
    )

    ratings_matrix = pd.pivot_table(data=ratings, index='userId', values='rating', columns='movieId')

    movie_ratings = get_nearest_neighbors_prediction(my_ratings = validated_ratings, ratings_matrix = ratings_matrix)

    movies = pd.read_sql_table(
        "movies",
        con=db.engine,
        schema="movie_recommender"
    )
    movie_ratings = pd.merge(movie_ratings, movies, left_index = True, right_index = True)[0:40]
    response['body'] = movie_ratings.to_dict(orient = 'records')
    print(movie_ratings)
    response = json.dumps(response)
    return response


def get_nearest_neighbors_prediction(my_ratings, ratings_matrix):
    min_support = 3
    max_neighbours = 40
    my_ratings = pd.DataFrame([{key: value for key, value in y.items() if key in [
        'movieId', 'rating']} for y in my_ratings]).set_index('movieId')

    my_ratings = my_ratings['rating']

    # Get a list of all movies rated by the user
    movies_rated = my_ratings.index

    # The total number of movies rated by the user
    num_movies_rated = len(my_ratings)

    # Only consider the users that are not yourself and the movies that the user has rated
    ratings_sub_matrix = ratings_matrix.loc[:, movies_rated]

    # Get the number of matching movies rated by other users
    num_matching_ratings = ratings_sub_matrix.notnull().sum(axis=1)

    # If there are more movies then the minimum support, we want to only consider
    # The users that have the minimum matching movies
    if num_movies_rated >= min_support:
        # Consider only the users greater then the min support
        matching_users = num_matching_ratings[num_matching_ratings >= min_support].index
        ratings_sub_matrix = ratings_sub_matrix.loc[matching_users]

    # Get the difference of movie ratings between the user and all other users
    ratings_diffs = (ratings_sub_matrix - my_ratings) ** 2
    # Get the Euclidian Distance
    user_dists = np.sqrt(ratings_diffs.sum(axis=1))
    # Get similarity score
    user_sims = 1 / (1 + user_dists);

    user_sims = pd.DataFrame(user_sims, columns=['similarity']).sort_values(
        by='similarity', ascending=False)
    most_similar_users = user_sims.iloc[0:max_neighbours]

    # Merge the most similar users and their similarity onto their movie ratings
    ratings_sub_matrix = pd.merge(ratings_matrix, most_similar_users,
                                  left_index=True, right_index=True)

    # Remove all movies that have not been rated
    ratings_sub_matrix = ratings_sub_matrix.dropna(axis=1, how='all')

    movies_to_rate = [x for x in ratings_sub_matrix.columns if x != 'similarity']

    for col in movies_to_rate:
        # Weight all of the ratings by the user similarity
        ratings_sub_matrix[col] = ratings_sub_matrix[col] * ratings_sub_matrix['similarity']
        total_weights = ratings_sub_matrix[ratings_sub_matrix[col].notnull()]['similarity'].sum()
        ratings_sub_matrix[col] = ratings_sub_matrix[col] / total_weights

    # Get the total number of ratings
    num_ratings = pd.DataFrame(ratings_sub_matrix[movies_to_rate].notnull().sum(), columns=['num_ratings'])
    # Get the weighted sum of the ratings
    movie_ratings = pd.DataFrame(ratings_sub_matrix[movies_to_rate].sum(), columns=['rating'])
    movie_ratings = pd.merge(movie_ratings, num_ratings, left_index=True, right_index=True)

    # Get the relative confidence score, the more total ratings, the more confident we can be in the score
    movie_ratings['relative_confidence'] = np.log(1 + movie_ratings['num_ratings'])
    # Weight the rating with the confidence
    movie_ratings['weighted_rating'] = movie_ratings['rating'] * movie_ratings['relative_confidence']

    movie_ratings = movie_ratings.sort_values(by='weighted_rating', ascending=False)

    return movie_ratings

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




