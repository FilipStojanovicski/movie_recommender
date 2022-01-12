import os
import pandas as pd
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

pg_user_dev = 'postgres'
pg_pass_dev = 'admin'
pg_db_dev = 'postgres'
pg_host_dev = 'localhost'
pg_port_dev = 5432
DEV_DB = f"postgresql://{pg_user_dev}:{pg_pass_dev}@{pg_host_dev}:{pg_port_dev}/{pg_db_dev}"

# Start the session
engine = create_engine(DEV_DB, echo=False, client_encoding="UTF-8")
Session = sessionmaker(bind=engine)
Session.configure(bind=engine)
session = Session()
meta = MetaData(bind=engine)
Base = declarative_base()

# Read in tables from the database
class MovieUsers(Base):
    __table__ = Table('movie_users', meta, autoload=True, schema="movie_recommender")
    ratings = relationship('Ratings', backref='movie_users', lazy=True)
    tags = relationship('Tags', backref='movie_users', lazy=True)

# Read in tables from the database
class Movies(Base):
    __table__ = Table('movies', meta, autoload=True, schema="movie_recommender")
    ratings = relationship('Ratings', backref='movies', lazy=True)
    tags = relationship('Tags', backref='movies', lazy=True)
    links = relationship('Links', backref='movies', uselist=False, lazy=True)


class Ratings(Base):
    __table__ = Table('ratings', meta, autoload=True, schema="movie_recommender")

class Tags(Base):
    __table__ = Table('tags', meta, autoload=True, schema="movie_recommender")

class Links(Base):
    __table__ = Table('links', meta, autoload=True, schema="movie_recommender")

movies = pd.read_csv("data/movies.csv")

movies['genres'] = movies['genres'].apply(lambda x: x.split("|"))
movies_agg = movies.explode('genres')
movies_agg = pd.pivot_table(movies_agg, values = 'movieId', index = 'movieId',
               columns = 'genres', aggfunc = len).reset_index()
movies_agg.columns = ['genre_' + x.replace(" ", "_").replace("-","_").replace("(","").replace(")","") \
                      if x != 'movieId' else x for x in movies_agg.columns]

# ratings = pd.read_csv('data/ratings.csv')
# ratings['timestamp'] = ratings['timestamp'].apply(datetime.fromtimestamp)
#
# ratings = ratings.to_dict(orient="records")
# # Insert all of the stock data into the database
# for rating in ratings:
#     rating = Ratings(**rating)
#     try:
#         session.add(rating)
#         session.commit()
#
#     except Exception as e:
#         session.rollback()
#         print(f"Exception inserting {str(rating)} into database: {e}")
#
# tags = pd.read_csv('data/tags.csv')
#
# tags = tags.to_dict(orient="records")
# # Insert all of the stock data into the database
# for tag in tags:
#     tag = Tags(**tag)
#     try:
#         session.add(tag)
#         session.commit()
#
#     except Exception as e:
#         session.rollback()
#         print(f"Exception inserting {str(tag)} into database: {e}")