from app import app, db_connect
from flask import render_template, request, redirect, url_for, flash
import pymysql.cursors  # Ensure you import cursors for DictCursor

@app.route('/')
def home():
    return render_template('home.html')

# -----------------------------------------------
# Movies Routes
# -----------------------------------------------

@app.route('/movies', methods=['GET', 'POST'])
def show_movies():
    db = db_connect()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    # Fetch all genres for the forms
    cursor.execute('SELECT genre_id, genre_name FROM genres')
    genres = cursor.fetchall()

    if request.method == 'POST':
        title = request.form['title']
        release_year = request.form['release_year']  # Adjusted to 'release_year' to match form field
        genre_ids = request.form.getlist('genre_ids')  # Get a list of selected genres

        # Insert the new movie into the movies table
        cursor.execute('INSERT INTO movies (title, release_year) VALUES (%s, %s)', (title, release_year))
        db.commit()
        new_movie_id = cursor.lastrowid

        # Insert the movie-genre relationships into the movie_genres table
        for genre_id in genre_ids:
            cursor.execute('INSERT INTO movie_genres (movie_id, genre_id) VALUES (%s, %s)', (new_movie_id, genre_id))
        db.commit()

        flash('New movie added successfully!', 'success')
        return redirect(url_for('show_movies'))

    # Fetch all movies with genres
    movies_with_genres = get_all_movies_with_genres()

    return render_template('movies.html', movies=movies_with_genres, genres=genres)

@app.route('/movies/edit/<int:movie_id>', methods=['GET', 'POST'])
def edit_movie(movie_id):
    db = db_connect()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    if request.method == 'POST':
        title = request.form['title']
        release_year = request.form['release_year']
        genre_ids = request.form.getlist('genre_ids')

        # Update movie details
        cursor.execute('UPDATE movies SET title = %s, release_year = %s WHERE movie_id = %s', (title, release_year, movie_id))
        db.commit()

        # Update movie-genre relationships
        cursor.execute('DELETE FROM movie_genres WHERE movie_id = %s', (movie_id,))
        for genre_id in genre_ids:
            cursor.execute('INSERT INTO movie_genres (movie_id, genre_id) VALUES (%s, %s)', (movie_id, genre_id))
        db.commit()

        flash('Movie updated successfully!', 'success')
        return redirect(url_for('show_movies'))

    # Fetch the movie to edit
    cursor.execute('SELECT movie_id, title, release_year FROM movies WHERE movie_id = %s', (movie_id,))
    movie = cursor.fetchone()

    # Fetch the associated genres
    cursor.execute('SELECT genre_id FROM movie_genres WHERE movie_id = %s', (movie_id,))
    associated_genres = [row['genre_id'] for row in cursor.fetchall()]

    # Fetch all genres for the form
    cursor.execute('SELECT genre_id, genre_name FROM genres')
    genres = cursor.fetchall()

    # Fetch all movies to display in the template
    movies_with_genres = get_all_movies_with_genres()

    return render_template('movies.html', movies=movies_with_genres, genres=genres, edit_movie=movie, associated_genres=associated_genres)

@app.route('/movies/delete/<int:movie_id>', methods=['POST'])
def delete_movie(movie_id):
    db = db_connect()
    cursor = db.cursor()

    # Delete associations first due to foreign key constraints
    cursor.execute('DELETE FROM movie_genres WHERE movie_id = %s', (movie_id,))
    cursor.execute('DELETE FROM movies WHERE movie_id = %s', (movie_id,))
    db.commit()

    flash('Movie deleted successfully!', 'danger')
    return redirect(url_for('show_movies'))

def get_all_movies_with_genres():
    db = db_connect()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute('''
        SELECT
            m.movie_id, m.title, m.release_year,
            GROUP_CONCAT(g.genre_name SEPARATOR ', ') AS genre_names
        FROM movies m
        LEFT JOIN movie_genres mg ON m.movie_id = mg.movie_id
        LEFT JOIN genres g ON mg.genre_id = g.genre_id
        GROUP BY m.movie_id
    ''')
    movies = cursor.fetchall()
    # Process the movies to include genres as a list of dictionaries
    movies_with_genres = []
    for movie in movies:
        genres = []
        if movie['genre_names']:
            genre_names = movie['genre_names'].split(', ')
            genres = [{'genre_name': name} for name in genre_names]
        movies_with_genres.append({
            'movie_id': movie['movie_id'],
            'title': movie['title'],
            'release_year': movie['release_year'],
            'genres': genres
        })
    return movies_with_genres

# -----------------------------------------------
# Genres Routes
# -----------------------------------------------

@app.route('/genres', methods=['GET', 'POST'])
def show_genres():
    db = db_connect()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    if request.method == 'POST':
        genre_name = request.form['genre_name']
        try:
            cursor.execute('INSERT INTO genres (genre_name) VALUES (%s)', (genre_name,))
            db.commit()
            flash('New genre added successfully!', 'success')
        except pymysql.MySQLError as e:
            print(f"Error: {e}")
            flash('Failed to add genre.', 'danger')

        return redirect(url_for('show_genres'))

    cursor.execute('SELECT genre_id, genre_name FROM genres')
    genres = cursor.fetchall()

    return render_template('genres.html', genres=genres)

@app.route('/genres/edit/<int:genre_id>', methods=['GET', 'POST'])
def edit_genre(genre_id):
    db = db_connect()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    if request.method == 'POST':
        genre_name = request.form['genre_name']
        cursor.execute('UPDATE genres SET genre_name = %s WHERE genre_id = %s', (genre_name, genre_id))
        db.commit()

        flash('Genre updated successfully!', 'success')
        return redirect(url_for('show_genres'))

    # Fetch the genre to edit
    cursor.execute('SELECT genre_id, genre_name FROM genres WHERE genre_id = %s', (genre_id,))
    genre = cursor.fetchone()

    # Fetch all genres
    cursor.execute('SELECT genre_id, genre_name FROM genres')
    genres = cursor.fetchall()

    return render_template('genres.html', genres=genres, edit_genre=genre)

@app.route('/genres/delete/<int:genre_id>', methods=['POST'])
def delete_genre(genre_id):
    db = db_connect()
    cursor = db.cursor()

    cursor.execute('DELETE FROM genres WHERE genre_id = %s', (genre_id,))
    db.commit()

    flash('Genre deleted successfully!', 'danger')
    return redirect(url_for('show_genres'))
