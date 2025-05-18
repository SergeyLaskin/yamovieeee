import requests
from flask import Blueprint, jsonify, g, request

api = Blueprint('api', __name__)

API_KEY = 'ff742994'
BASE_URL_KEY = f'http://www.omdbapi.com/?apikey={API_KEY}'
IMDB_BASE_URL = 'https://www.imdb.com/title/'


def jsonify_error_message(message, code: int):
    return jsonify({"error_message": message}), code


@api.route('/users', methods=['GET'])
def get_users():
    users = g.users_data_manager.get_all_users()
    if users is None:
        return jsonify_error_message("Пользователь не найден", 404)
    return jsonify(users), 200  # ok


def validate_user_input(user_info: dict) -> list:
    user_name = user_info['user_name']
    error_messages = []
    if len(user_name) == 0:
        error_messages.append('Имя пользователя не может быть пустым')
    else:
        if not user_name[0].isalpha():
            error_messages.append('Имя пользователя должно начинаться с буквы')
    return error_messages


@api.route('/users', methods=['POST'])
def add_user():
    user_name = request.json.get('user_name', '')
    error_messages = validate_user_input({'user_name': user_name})
    if len(error_messages) != 0:
        return jsonify_error_message("Неверное имя пользователя.", 400)

    new_user = {"user_name": user_name,
                "movies": []}

    if g.users_data_manager.add_user(new_user) is None:
        return jsonify_error_message("Не могу добавить пользователя.", 500)

    return jsonify_error_message("Пользователь успешно добавлен.", 201)


@api.route('/users/<int:user_id>/movies', methods=['GET'])
def get_user_movies(user_id: int):
    user = g.users_data_manager.get_user(user_id)
    if user is None:
        return jsonify_error_message("Пользователь не найден", 404)
    return jsonify(user['movies']), 200


@api.route('/users/<int:user_id>/movies/<int:movie_id>', methods=['POST'])
def add_user_movie(user_id: int, movie_id: int):
    user_movie_info = {
        'user_id': user_id,
        'movie_id': movie_id
    }
    user = g.users_data_manager.get_user(user_id)
    if user is None:
        return jsonify_error_message("Пользователь не найден", 404)
    if movie_id in [user_movie['id'] for user_movie in user['movies']]:
        return jsonify_error_message("Невозможно добавить фильм, так как он уже добавлен.", 400)
    if g.users_movies_data_manager.add_user_movie(user_movie_info) is None:
        return jsonify_error_message("Невозможно добавить фильм.", 500)
    return jsonify({"message": "Фильм успешно добавлен пользователю."}), 201


@api.route('/users/movies/<int:user_movie_id>', methods=['DELETE'])
def delete_user_movie(user_movie_id: int):
    user_movie = g.users_movies_data_manager.get_user_movie(user_movie_id)
    if not user_movie:
        return jsonify_error_message("Фильм пользователя не найден.", 404)

    if g.users_movies_data_manager.delete_user_movie(user_movie_id) is None:
        return jsonify_error_message("Невозможно удалить фильм.", 500)

    return jsonify({"message": "Фильм успешно удален у пользователя."}), 204  # no content


@api.route('/movies', methods=['GET'])
def get_movies():
    movies = g.movies_data_manager.get_movies()
    if movies is None:
        return jsonify_error_message("Фильмы не найдены.", 404)
    return jsonify(movies), 200


def fetch_movie_api_response(title: str) -> dict:
    response = requests.get(f'{BASE_URL_KEY}&t={title}', timeout=5)
    response.raise_for_status()
    return response.json()


def isfloat(number: str) -> bool:
    try:
        float(number)
        return True
    except ValueError:
        return False


def get_error_messages(movie_info: dict) -> list:
    movie_name = movie_info.get('Название', '')
    director = movie_info.get('Режиссер', '')
    year = movie_info.get('Год', '')
    rating = movie_info.get('Рейтинг', '')

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
            error_messages.append('Год должен иметь 4 цифры')

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
    movie_name = request.json.get('movie_name', '')

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
              "Проверьте подключение к Интернету"
              "и убедитесь, что веб-сайт доступен.")
        return get_empty_info(movie_name)


@api.route('/movies/add_movie', methods=['POST'])
def add_new_movie():
    new_movie_info = get_new_movie_info()
    if isinstance(new_movie_info, list):
        return jsonify_error_message(new_movie_info, 400)

    if g.movies_data_manager.add_new_movie(new_movie_info) is None:
        return jsonify_error_message('Невозможно добавить фильм. '
                                     'Фильм уже есть в базе данных.', 500)

    return jsonify({'message': 'Фильм успешно добавлен.'}), 201


def get_movie_info() -> dict:
    return {'movie_name': request.json.get('movie_name', ''),
            'director': request.json.get('director', ''),
            'year': request.json.get('year', 0),
            'rating': request.json.get('rating', 0.0)
            }


def get_updated_movie_info(movie_id) -> dict | list:
    updated_movie_info = get_movie_info()
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


@api.route('/movies/update_movie/<int:movie_id>', methods=['PATCH'])
def update_movie(movie_id: int):
    movie = g.movies_data_manager.get_movie(movie_id)
    if not movie:
        return jsonify_error_message('Фильм не найден', 404)

    updated_movie = get_updated_movie_info(movie_id)
    if isinstance(updated_movie, list):
        return jsonify_error_message(updated_movie, 400)

    if g.movies_data_manager.update_movie(updated_movie) is None:
        return jsonify_error_message('Невозможно обновить фильм', 500)

    return jsonify({'message': 'Фильм успешно обновлен'}), 201


@api.route('/movies/delete_movie/<int:movie_id>', methods=['DELETE'])
def delete_movie(movie_id: int):
    movie = g.movies_data_manager.get_movie(movie_id)
    if not movie:
        return jsonify_error_message('Фильм не найден', 404)

    if g.movies_data_manager.delete_movie(movie_id) is None:
        return jsonify_error_message('Невозможно удалить фильм. Он мог быть добавлен в избранное.', 500)

    return jsonify({"message": "Фильм успешно удален"}), 204  # no content


@api.route('/movies/<int:movie_id>/reviews', methods=['GET'])
def get_movie_reviews(movie_id: int):
    movie = g.movies_data_manager.get_movie(movie_id)
    if movie is None:
        return jsonify_error_message("Фильм не найден", 404)
    return jsonify(movie["movie_reviews"]), 200  # ok


def get_error_message(user_id: int, movie_id: int):
    user = g.users_data_manager.get_user(user_id)
    if user is None:
        return jsonify_error_message("Пользователь не найден", 404)

    movie = g.movies_data_manager.get_movie(movie_id)
    if not movie:
        return jsonify_error_message("Фильм не найден.", 404)

    user_movies = user.get('movies')
    if movie_id not in [user_movie['id'] for user_movie in user_movies]:
        return jsonify_error_message("Пользователь, не добавивший этот фильм в избранное, не может оставить отзыв.", 404)

    movie_reviews = movie["movie_reviews"]
    movie_reviews_user_ids = [movie_review["user_id"] for movie_review in movie_reviews]
    if user_id in movie_reviews_user_ids:
        return jsonify_error_message("Невозможно добавить отзыв, так как он уже добавлен.", 400)

    return False


def get_reviewed_info(user_id: int, movie_id: int) -> dict:
    return {'user_id': user_id,
            'movie_id': movie_id,
            'rating': request.json.get('rating', 0.0),
            'review_text': request.json.get('review_text', '')
            }


@api.route('/users/<int:user_id>/add_movie_review/<int:movie_id>', methods=['POST'])
def add_movie_review(user_id: int, movie_id: int):
    if get_error_message(user_id, movie_id):
        return get_error_message(user_id, movie_id)

    if g.movies_reviews_data_manager. \
            add_movie_review(get_reviewed_info(user_id, movie_id)) is None:
        return jsonify_error_message("Невозможно добавить отзыв.", 500)

    return jsonify({"message": "Обзор фильма успешно добавлен для этого пользователя."}), 201
