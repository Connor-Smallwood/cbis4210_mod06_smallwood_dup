from flask import Blueprint, render_template, request, url_for, redirect, flash
from app.db_connect import get_db

movies = Blueprint('movies', __name__)

@movies.route('/movies', methods=['GET', 'POST'])
def show_movies():
    db = get_db()
    cursor = db.cursor()

    # Handle POST request to add a new movie
    if request.method == 'POST':
        title = request.form['title']
        release_year = request.form['release_year']

        # Insert the new movie into the database
        cursor.execute('INSERT INTO movies (title, release_year) VALUES (%s, %s)', (title, release_year))
        db.commit()

        flash('New movie added successfully!', 'success')
        return redirect(url_for('movies.show_movies'))

    # Handle GET request to display all movies
    cursor.execute('SELECT * FROM movies')
    all_movies = cursor.fetchall()
    return render_template('movies.html', all_movies=all_movies)

@movies.route('/edit_movie/<int:movie_id>', methods=['GET', 'POST'])
def edit_movie(movie_id):
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        # Update the movie details
        title = request.form['title']
        release_year = request.form['release_year']

        cursor.execute('UPDATE movies SET title = %s, release_year = %s WHERE id_movie = %s', (title, release_year, movie_id))
        db.commit()

        flash('Movie updated successfully!', 'success')
        return redirect(url_for('movies.show_movies'))

    # GET method: fetch movie's current data for pre-populating the form
    cursor.execute('SELECT * FROM movies WHERE id_movie = %s', (movie_id,))
    current_movie = cursor.fetchone()
    return render_template('edit_movie.html', current_movie=current_movie)

@movies.route('/delete_movie/<int:movie_id>', methods=['POST'])
def delete_movie(movie_id):
    db = get_db()
    cursor = db.cursor()

    # Delete the movie
    cursor.execute('DELETE FROM movies WHERE id_movie = %s', (movie_id,))
    db.commit()

    flash('Movie deleted successfully!', 'danger')
    return redirect(url_for('movies.show_movies'))
