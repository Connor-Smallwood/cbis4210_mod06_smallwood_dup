from app import app, db_connect
from flask import render_template, request, redirect, url_for, flash
import pymysql

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/movies', methods=['GET', 'POST'])
def show_movies():
    db = db_connect()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    if request.method == 'POST':
        title = request.form['title']
        release_year = request.form['year']
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

    # Apply filters if provided
    genre_filter = request.args.get('genre')
    title_filter = request.args.get('title')
    year_filter = request.args.get('year')

    query = 'SELECT * FROM movies'
    filters = []
    if genre_filter:
        query += ' JOIN movie_genres ON movies.id_movie = movie_genres.movie_id WHERE movie_genres.genre_id = %s'
        filters.append(genre_filter)
    if title_filter:
        query += ' AND' if filters else ' WHERE'
        query += ' title LIKE %s'
        filters.append(f"%{title_filter}%")
    if year_filter:
        query += ' AND' if filters else ' WHERE'
        query += ' release_year = %s'
        filters.append(year_filter)

    cursor.execute(query, filters)
    movies = cursor.fetchall()

    # Get all genres
    cursor.execute('SELECT * FROM genres')
    genres = cursor.fetchall()

    return render_template('movies.html', movies=movies, genres=genres)

@app.route('/edit_movie/<int:movie_id>', methods=['GET', 'POST'])
def edit_movie(movie_id):
    db = db_connect()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    if request.method == 'POST':
        title = request.form['title']
        release_year = request.form['year']
        genre_ids = request.form.getlist('genre_ids')

        # Update movie details
        cursor.execute('UPDATE movies SET title = %s, release_year = %s WHERE id_movie = %s', (title, release_year, movie_id))
        db.commit()

        # Update movie-genre relationships
        cursor.execute('DELETE FROM movie_genres WHERE movie_id = %s', (movie_id,))
        for genre_id in genre_ids:
            cursor.execute('INSERT INTO movie_genres (movie_id, genre_id) VALUES (%s, %s)', (movie_id, genre_id))
        db.commit()

        flash('Movie updated successfully!', 'success')
        return redirect(url_for('show_movies'))

    # Fetch movie details
    cursor.execute('SELECT * FROM movies WHERE id_movie = %s', (movie_id,))
    movie = cursor.fetchone()

    # Fetch movie genres
    cursor.execute('SELECT genre_id FROM movie_genres WHERE movie_id = %s', (movie_id,))
    movie_genres = [row['genre_id'] for row in cursor.fetchall()]

    # Get all genres
    cursor.execute('SELECT * FROM genres')
    genres = cursor.fetchall()

    return render_template('edit_movie.html', movie=movie, genres=genres, movie_genres=movie_genres)


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

    cursor.execute('SELECT * FROM genres')
    genres = cursor.fetchall()

    return render_template('genres.html', genres=genres)

@app.route('/edit_genre/<int:genre_id>', methods=['GET', 'POST'])
def edit_genre(genre_id):
    db = db_connect()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    if request.method == 'POST':
        genre_name = request.form['name']
        cursor.execute('UPDATE genres SET genre_name = %s WHERE id_genre = %s', (genre_name, genre_id))
        db.commit()

        flash('Genre updated successfully!', 'success')
        return redirect(url_for('show_genres'))

    cursor.execute('SELECT * FROM genres WHERE id_genre = %s', (genre_id,))
    genre = cursor.fetchone()

    return render_template('edit_genre.html', genre=genre)

@app.route('/delete_movie/<int:movie_id>', methods=['POST'])
def delete_movie(movie_id):
    db = db_connect()
    cursor = db.cursor()

    cursor.execute('DELETE FROM movies WHERE id_movie = %s', (movie_id,))
    cursor.execute('DELETE FROM movie_genres WHERE movie_id = %s', (movie_id,))
    db.commit()

    flash('Movie deleted successfully!', 'danger')
    return redirect(url_for('show_movies'))

@app.route('/delete_genre/<int:genre_id>', methods=['POST'])
def delete_genre(genre_id):
    db = db_connect()
    cursor = db.cursor()

    cursor.execute('DELETE FROM genres WHERE id_genre = %s', (genre_id,))
    db.commit()

    flash('Genre deleted successfully!', 'danger')
    return redirect(url_for('show_genres'))
