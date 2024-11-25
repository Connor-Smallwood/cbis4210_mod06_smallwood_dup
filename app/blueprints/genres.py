from flask import Blueprint, render_template, request, url_for, redirect, flash
import pymysql.cursors
from app.db_connect import get_db

genres = Blueprint('genres', __name__)

@genres.route('/genres', methods=['GET', 'POST'])
def show_genres():
    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    if request.method == 'POST':
        genre_name = request.form['genre_name']
        cursor.execute('INSERT INTO genres (genre_name) VALUES (%s)', (genre_name,))
        db.commit()
        flash('New genre added successfully!', 'success')
        return redirect(url_for('genres.show_genres'))

    # Fetch all genres to display in the template
    cursor.execute('SELECT genre_id, genre_name FROM genres')
    all_genres = cursor.fetchall()
    return render_template('genres.html', genres=all_genres)

@genres.route('/genres/edit/<int:genre_id>', methods=['GET', 'POST'])
def edit_genre(genre_id):
    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    if request.method == 'POST':
        genre_name = request.form['genre_name']
        cursor.execute('UPDATE genres SET genre_name = %s WHERE genre_id = %s', (genre_name, genre_id))
        db.commit()
        flash('Genre updated successfully!', 'success')
        return redirect(url_for('genres.show_genres'))
    else:
        # Fetch the genre to edit
        cursor.execute('SELECT genre_id, genre_name FROM genres WHERE genre_id = %s', (genre_id,))
        genre = cursor.fetchone()
        # Fetch all genres to display in the template
        cursor.execute('SELECT genre_id, genre_name FROM genres')
        all_genres = cursor.fetchall()
        return render_template('genres.html', genres=all_genres, edit_genre=genre)

@genres.route('/genres/delete/<int:genre_id>', methods=['POST'])
def delete_genre(genre_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM genres WHERE genre_id = %s', (genre_id,))
    db.commit()
    flash('Genre deleted successfully!', 'danger')
    return redirect(url_for('genres.show_genres'))
