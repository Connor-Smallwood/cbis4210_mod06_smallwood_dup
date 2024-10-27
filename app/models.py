from app import db

# Association Table for many-to-many relationship
movie_genres = db.Table(
    'movie_genres',
    db.Column('movie_id', db.Integer, db.ForeignKey('movies.id_movie'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id_genre'), primary_key=True)
)

class Movie(db.Model):
    __tablename__ = 'movies'

    id_movie = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(45), nullable=False)
    release_year = db.Column(db.Integer, nullable=False)

    genres = db.relationship('Genre', secondary=movie_genres, back_populates='movies')

class Genre(db.Model):
    __tablename__ = 'genres'

    id_genre = db.Column(db.Integer, primary_key=True)
    genre_name = db.Column(db.String(45), unique=True, nullable=False)

    movies = db.relationship('Movie', secondary=movie_genres, back_populates='genres')
