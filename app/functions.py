from app.models import Movie, Genre

def filter_movies(genre_filter=None, title_filter=None, year_filter=None):
    """
    Filter movies based on genre, title, and year.
    Args:
        genre_filter (int, optional): Genre ID to filter movies.
        title_filter (str, optional): Substring to filter movie titles.
        year_filter (int, optional): Year to filter movies.
    Returns:
        list: Filtered list of Movie objects.
    """
    movies_query = Movie.query

    if genre_filter:
        # Join with genres table to filter by genre
        movies_query = movies_query.join(Movie.genres).filter(Genre.id_genre == genre_filter)
    if title_filter:
        # Use case-insensitive search to filter by title
        movies_query = movies_query.filter(Movie.title.ilike(f"%{title_filter}%"))
    if year_filter:
        try:
            year_filter = int(year_filter)
            movies_query = movies_query.filter_by(release_year=year_filter)
        except ValueError:
            pass  # Ignore the filter if year_filter is not a valid integer

    return movies_query.all()