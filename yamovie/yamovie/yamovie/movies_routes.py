import requests
from flask import Blueprint, render_template, request, redirect, url_for, abort, g

movies_bp = Blueprint('movies', __name__)

API_KEY = 'ff742994'
BASE_URL_KEY = f'http://www.omdbapi.com/?apikey={API_KEY}'
IMDB_BASE_URL = 'https://www.imdb.com/title/'


@movies_bp.route('/movies', methods=['GET'])
def get_movies():
    movies = g.movies_data_manager.get_movies()
    return render_template('movies.html', movies=movies)


def fetch_movie_api_response(title: str) -> dict:
    response = requests.get(f'{BASE_URL_KEY}&t={title}', timeout=5)
    response.raise_for_status()

    return response.json()


def get_error_messages(movie_info: dict) -> list:
    movie_name = movie_info.get('movie_name', '')
    director = movie_info.get('director', '')
    year = movie_info.get('year', '')
    rating = movie_info.get('rating', '')

    error_messages = []
    if len(movie_name) == 0:
        error_messages.append('Название фильма не может быть пустым')

    if len(movie_name) != 0 and not movie_name[0].isalpha():
        error_messages.append('Название фильма должно начинаться с буквы')

    if len(director) != 0 and not director[0].isalpha():
        error_messages.append('Имя режиссера должно начинаться с буквы')

    if len(year) != 0:
        if not year.isdigit():
            error_messages.append('Год должен быть числом')

        if year.isdigit() and len(year) != 4:
            error_messages.append('Год должен быть четырехзначным')

    if len(rating) != 0:
        if not isfloat(rating):
            error_messages.append('Рейтинг должен быть числом')
        elif not 1.0 <= float(rating) <= 10.0:
            error_messages.append('Рейтинг должен быть между 1 и 10')

    return error_messages


def format_movie_info(response: dict, movie_name: str) -> dict:
    return {'movie_name': response.get('Название', movie_name),
            'director': response.get('Режиссер', ''),
            'year': int(response.get('Год', '0000')[:4]),
            'rating': float(response.get('imdbРейтинг', 0.0)),
            'poster': response.get('Постер', ''),
            'website': IMDB_BASE_URL + response.get('imdbID', '')
            }


def get_empty_info(movie_name: str) -> dict:
    return {'movie_name': movie_name,
            'director': '',
            'year': 0,
            'rating': 0.0,
            'poster': '',
            'website': ''
            }


def get_new_movie_info() -> dict | list:
    movie_name = request.form.get('movie_name', '')

    error_messages = get_error_messages({'movie_name': movie_name})
    if error_messages:
        return error_messages

    try:
        response = fetch_movie_api_response(movie_name)
        return format_movie_info(response, movie_name)

    except (requests.exceptions.Timeout,
            requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError,
            requests.exceptions.RequestException):
        print("Ошибка запроса. "
              "Проверьте подключение к Интернету "
              "и убедитесь, что веб-сайт доступен.")
        return get_empty_info(movie_name)


@movies_bp.route('/movies/add_movie', methods=['GET', 'POST'])
def add_new_movie():
    if request.method == 'POST':
        new_movie_info = get_new_movie_info()
        if isinstance(new_movie_info, list):
            return render_template('add_new_movie.html',
                                   error_messages=new_movie_info)

        if g.movies_data_manager.add_new_movie(new_movie_info) is None:
            return render_template('add_new_movie.html',
                                   error_messages=['Нельзя добавить фильм '
                                                   'Фильм уже есть в базе данных.'])

        return redirect(url_for('movies.get_movies'))

    return render_template('add_new_movie.html')


def isfloat(number: str) -> bool:
    try:
        float(number)
        return True
    except ValueError:
        return False


def get_movie_info_from_user() -> dict:
    return {'movie_name': request.form.get('movie_name', ''),
            'director': request.form.get('director', ''),
            'year': request.form.get('year', 0),
            'rating': request.form.get('rating', 0.0)
            }


def get_updated_movie_info(movie_id) -> dict | list:
    updated_movie_info = get_movie_info_from_user()
    error_messages = get_error_messages(updated_movie_info)

    if len(error_messages) != 0:
        return error_messages

    year = updated_movie_info['year']
    if len(year) == 0:
        year = 0

    rating = updated_movie_info['rating']
    if len(rating) == 0:
        rating = 0.0

    return {'id': movie_id,
            'movie_name': updated_movie_info['movie_name'],
            'director': updated_movie_info['director'],
            'year': int(year),
            'rating': float(rating)
            }


@movies_bp.route('/movies/update_movie/<int:movie_id>', methods=['GET', 'POST'])
def update_movie(movie_id: int):
    movie = g.movies_data_manager.get_movie(movie_id)

    if movie is None:
        abort(404)

    if request.method == 'POST':
        updated_movie = get_updated_movie_info(movie_id)
        if isinstance(updated_movie, list):
            return render_template('update_movie.html',
                                   movie=movie,
                                   error_messages=updated_movie)

        if g.movies_data_manager.update_movie(updated_movie) is None:
            abort(400, ['Нет такого фильма'])
        return redirect(url_for('movies.get_movies'))

    return render_template('update_movie.html', movie=movie)


@movies_bp.route('/movies/delete_movie/<int:movie_id>')
def delete_movie(movie_id: int):
    if g.movies_data_manager.delete_movie(movie_id) is None:
        movies = g.movies_data_manager.get_movies()
        return render_template('movies.html',
                               movies=movies,
                               error_message='Невозможно удалить этот фильм, так как он добавлен в избранное.')

    return redirect(url_for('movies.get_movies'))


@movies_bp.route('/users/<int:user_id>/movie_reviews/<int:movie_id>', methods=['GET'])
def get_movie_reviews(user_id: int, movie_id: int):
    user = g.users_data_manager.get_user(user_id)
    if user is None:
        abort(404)

    movie = g.movies_data_manager.get_movie(movie_id)
    movie_reviews = g.movies_reviews_data_manager.get_movie_reviews()
    return render_template('movie_reviews.html',
                           user=user,
                           movie_reviews=movie_reviews,
                           movie=movie)


@movies_bp.route('/users/<int:user_id>/add_movie_review/<int:movie_id>', methods=['POST'])
def add_movie_review(user_id: int, movie_id: int):
    reviewed_info = {
        'user_id': user_id,
        'movie_id': movie_id,
        'rating': request.form.get('rating'),
        'review_text': request.form.get('review_text')
    }

    if g.movies_reviews_data_manager.add_movie_review(reviewed_info) is None:
        abort(404, ['Невозможно оставить отзыв об этом фильме.'])
    return redirect(url_for('movies.get_movie_reviews', movie_id=movie_id, user_id=user_id))
