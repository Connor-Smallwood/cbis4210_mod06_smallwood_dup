from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.db_connect import get_db  # Replace with your actual database module
import pymysql

movies = Blueprint('movies', __name__)

@movies.route('/movies', methods=['GET'])
def show_movies():
    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    # Fetch all movies
    cursor.execute('SELECT movie_id, title, release_year FROM movies')
    movies_list = cursor.fetchall()

    # Fetch all genres for the forms
    cursor.execute('SELECT genre_id, genre_name FROM genres')
    genres = cursor.fetchall()

    # Attach genres to each movie
    for movie in movies_list:
        cursor.execute('''
            SELECT g.genre_id, g.genre_name
            FROM genres g
            INNER JOIN movie_genres mg ON g.genre_id = mg.genre_id
            WHERE mg.movie_id = %s
        ''', (movie['movie_id'],))
        movie['genres'] = cursor.fetchall()

    return render_template('movies.html', movies=movies_list, genres=genres)

@movies.route('/movies/add', methods=['POST'])
def add_movie():
    title = request.form['title']
    release_year = request.form['release_year']
    genre_ids = request.form.getlist('genre_ids')

    db = get_db()
    cursor = db.cursor()

    # Insert the new movie
    cursor.execute('INSERT INTO movies (title, release_year) VALUES (%s, %s)', (title, release_year))
    movie_id = cursor.lastrowid

    # Insert into movie_genres table
    for genre_id in genre_ids:
        cursor.execute('INSERT INTO movie_genres (movie_id, genre_id) VALUES (%s, %s)', (movie_id, genre_id))

    db.commit()
    flash('Movie added successfully!', 'success')
    return redirect(url_for('movies.show_movies'))

@movies.route('/movies/edit/<int:movie_id>', methods=['POST'])
def edit_movie(movie_id):
    title = request.form['title']
    release_year = request.form['release_year']
    genre_ids = request.form.getlist('genre_ids')

    db = get_db()
    cursor = db.cursor()

    # Update the movie details
    cursor.execute('UPDATE movies SET title=%s, release_year=%s WHERE movie_id=%s', (title, release_year, movie_id))

    # Update the movie_genres table
    cursor.execute('DELETE FROM movie_genres WHERE movie_id=%s', (movie_id,))
    for genre_id in genre_ids:
        cursor.execute('INSERT INTO movie_genres (movie_id, genre_id) VALUES (%s, %s)', (movie_id, genre_id))

    db.commit()
    flash('Movie updated successfully!', 'success')
    return redirect(url_for('movies.show_movies'))

@movies.route('/movies/delete/<int:movie_id>', methods=['POST'])
def delete_movie(movie_id):
    db = get_db()
    cursor = db.cursor()

    # Delete the movie and its associations
    cursor.execute('DELETE FROM movie_genres WHERE movie_id=%s', (movie_id,))
    cursor.execute('DELETE FROM movies WHERE movie_id=%s', (movie_id,))

    db.commit()
    flash('Movie deleted successfully!', 'success')
    return redirect(url_for('movies.show_movies'))
