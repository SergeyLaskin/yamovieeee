from flask import Blueprint, render_template, request, redirect, url_for, abort, g

users_bp = Blueprint('users', __name__)


@users_bp.route('/users', methods=['GET'])
def list_users():
    users = g.users_data_manager.get_all_users()
    if users is None:
        abort(404)
    return render_template('users.html', users=users)


@users_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user_movies(user_id: int):
    user = g.users_data_manager.get_user(user_id)

    movies = g.movies_data_manager.get_movies()
    un_favourite_movies = []

    for movie in movies:
        if movie['id'] not in \
                [user_movie['id'] for user_movie in user['movies']]:
            un_favourite_movies.append(movie)

    if user is None:
        abort(404)
    return render_template('user_movies.html',
                           user=user,
                           movies=un_favourite_movies)


def validate_user_input(user_info: dict) -> list:
    user_name = user_info['user_name']
    error_messages = []
    if len(user_name) == 0:
        error_messages.append('Имя пользователя не может быть пустым')
    else:
        if not user_name[0].isalpha():
            error_messages.append('Имя пользователя должно начинаться с буквы')
    return error_messages


@users_bp.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        user_name = request.form.get('user_name', '')

        error_messages = validate_user_input({'user_name': user_name})
        if len(error_messages) != 0:
            return render_template('add_user.html', error_messages=error_messages)

        new_user = {"user_name": user_name,
                    "movies": []}

        if g.users_data_manager.add_user(new_user) is None:
            abort(400, ['Неверные данные пользователя'])
        return redirect(url_for('users.list_users'))

    return render_template('add_user.html')


def get_user_info(user_id: int) -> dict:
    return {'id': user_id,
            'user_name': request.form.get('name', '')}


def get_updated_user_info(user_id: int) -> dict | list:
    updated_user = get_user_info(user_id)
    error_messages = validate_user_input(updated_user)

    if len(error_messages) != 0:
        return error_messages

    return updated_user


@users_bp.route('/users/<int:user_id>/update_user', methods=['GET', 'POST'])
def update_user(user_id: int):
    user = g.users_data_manager.get_user(user_id)

    if user is None:
        abort(404)

    if request.method == 'POST':
        updated_user = get_updated_user_info(user_id)
        if isinstance(updated_user, list):
            return render_template('update_user.html',
                                   user=user,
                                   error_messages=updated_user)

        if g.users_data_manager.update_user(updated_user) is None:
            abort(400, ['Пользователь не найден'])
        return redirect(url_for('users.list_users'))

    return render_template('update_user.html', user=user)


@users_bp.route('/users/<int:user_id>/delete_user')
def delete_user(user_id: int):
    if g.users_data_manager.delete_user(user_id) is None:
        abort(404)

    return redirect(url_for('users.list_users'))


@users_bp.route('/users/<int:user_id>/add_user_movie/<int:movie_id>')
def add_user_movie(user_id: int, movie_id: int):
    user_movie_info = {
        'user_id': user_id,
        'movie_id': movie_id
    }
    if g.users_movies_data_manager.add_user_movie(user_movie_info) is None:
        abort(404)

    return redirect(url_for('users.get_user_movies', user_id=user_id))


@users_bp.route('/users/<int:user_id>/delete_user_movie/<int:user_movie_id>')
def delete_user_movie(user_id: int, user_movie_id: int):
    if g.users_movies_data_manager.delete_user_movie(user_movie_id) is None:
        abort(404)

    return redirect(url_for('users.get_user_movies', user_id=user_id))
