from app import app, db
from app.models import Movie, Genre
from app.functions import filter_movies
from flask import render_template, request, redirect, url_for

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/movies', methods=['GET', 'POST'])
def movies():
    if request.method == 'POST':
        title = request.form['title']
        release_year = request.form['year']
        genre_ids = request.form.getlist('genre_ids')  # Get a list of selected genres

        new_movie = Movie(title=title, release_year=release_year)
        for genre_id in genre_ids:
            genre = Genre.query.get(genre_id)
            if genre:
                new_movie.genres.append(genre)

        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('movies'))

    genre_filter = request.args.get('genre')
    title_filter = request.args.get('title')
    year_filter = request.args.get('year')

    # Use the filter function to get movies based on filters
    movies = filter_movies(genre_filter, title_filter, year_filter)
    genres = Genre.query.all()

    return render_template('movies.html', movies=movies, genres=genres)

@app.route('/edit_movie/<int:movie_id>', methods=['GET', 'POST'])
def edit_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    if request.method == 'POST':
        movie.title = request.form['title']
        movie.release_year = request.form['year']
        genre_ids = request.form.getlist('genre_ids')

        movie.genres = []
        for genre_id in genre_ids:
            genre = Genre.query.get(genre_id)
            if genre:
                movie.genres.append(genre)

        db.session.commit()
        return redirect(url_for('movies'))

    genres = Genre.query.all()
    return render_template('edit_movie.html', movie=movie, genres=genres)

@app.route('/genres', methods=['GET', 'POST'])
def genres():
    if request.method == 'POST':
        genre_name = request.form['name']
        new_genre = Genre(genre_name=genre_name)
        db.session.add(new_genre)
        db.session.commit()
        return redirect(url_for('genres'))

    genres = Genre.query.all()
    return render_template('genres.html', genres=genres)

@app.route('/edit_genre/<int:genre_id>', methods=['GET', 'POST'])
def edit_genre(genre_id):
    genre = Genre.query.get_or_404(genre_id)
    if request.method == 'POST':
        genre.genre_name = request.form['name']
        db.session.commit()
        return redirect(url_for('genres'))

    return render_template('edit_genre.html', genre=genre)

@app.route('/delete_movie/<int:movie_id>')
def delete_movie(movie_id):
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('movies'))

@app.route('/delete_genre/<int:genre_id>')
def delete_genre(genre_id):
    genre = Genre.query.get(genre_id)
    db.session.delete(genre)
    db.session.commit()
    return redirect(url_for('genres'))
