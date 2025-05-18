import json
import os

from yamovie.data_manager.json_data_manager import JSONDataManager
from yamovie.data_manager.users import Users

TEST_FILE_PATH = 'data/test_movies.json'

users_data_manager = Users(JSONDataManager(TEST_FILE_PATH, 'user_id'))


def create_test_file():
    test_data = [{"user_id": 1,
                  "name": "Test_user",
                  "movies": [{"movie_id": 1,
                              "name": "Titanic",
                              "director": "James Cameron",
                              "year": 1997,
                              "rating": 7.9,
                              "poster": "https://m.media-amazon.com/images/M/MV5BMDdmZGU3NDQtY2E5My00ZTliLWIzOTUtMTY4ZGI1YjdiNjk3XkEyXkFqcGdeQXVyNTA4NzY1MzY@._V1_SX300.jpg",
                              "website": "https://www.imdb.com/title/tt0120338"
                              }]
                  }]
    if os.path.exists(TEST_FILE_PATH):
        os.remove(TEST_FILE_PATH)

    with open(TEST_FILE_PATH, 'w', encoding='utf-8') as file:
        json.dump(test_data, file)


def test_get_all_users():
    create_test_file()
    assert users_data_manager.get_all_users()


def test_fail_to_get_all_users_when_file_not_exist():
    if os.path.exists(TEST_FILE_PATH):
        os.remove(TEST_FILE_PATH)
    assert users_data_manager.get_all_users() is None


def test_get_a_user():
    create_test_file()
    assert users_data_manager.get_user(1)


def test_get_an_invalid_user_id():
    create_test_file()
    assert users_data_manager.get_user(2) is None


def test_add_user():
    create_test_file()
    new_user = {"name": "Test_user",
                "movies": []}
    assert users_data_manager.add_user(new_user)


def test_add_user_with_invalid_key():
    create_test_file()
    new_user = {"n": "Test_user",
                "movies": []}
    assert users_data_manager.add_user(new_user) is None


def test_update_user():
    create_test_file()
    updated_user = {"user_id": 1,
                    "name": "Alice"}
    assert users_data_manager.update_user(updated_user)


def test_update_user_with_invalid_id():
    create_test_file()
    updated_user = {"user_id": 5,
                    "name": "Alice"}
    assert users_data_manager.update_user(updated_user) is None


def test_delete_user():
    create_test_file()
    assert users_data_manager.delete_user(1)


def test_delete_user_with_invalid_id():
    create_test_file()
    assert users_data_manager.delete_user(2) is None


def test_get_user_movies():
    create_test_file()
    assert users_data_manager.get_user_movies(1)


def test_get_user_movies_with_invalid_id():
    create_test_file()
    assert users_data_manager.get_user_movies(10) is None


def test_get_user_movie():
    create_test_file()
    assert users_data_manager.get_user_movie(1, 1)


def test_get_user_movie_with_invalid_id():
    create_test_file()
    assert users_data_manager.get_user_movie(10, 1) is None


def test_add_user_movie():
    create_test_file()
    new_movie = {"name": "Spiderman I"}
    assert users_data_manager.add_user_movie(1, new_movie)


def test_add_user_movie_with_invalid_user_id():
    create_test_file()
    new_movie = {"name": "Spiderman I"}
    assert users_data_manager.add_user_movie(6, new_movie) is None


def test_update_user_movie():
    create_test_file()
    updated_movie = {"name": "Spiderman 5"}
    assert users_data_manager.update_user_movie(1, 1, updated_movie)


def test_update_user_movie_with_invalid_user_id():
    create_test_file()
    updated_movie = {"name": "Spiderman 5"}
    assert users_data_manager.update_user_movie(10, 1, updated_movie) is None


def test_delete_user_movie():
    create_test_file()
    assert users_data_manager.delete_user_movie(1, 1)


def test_delete_user_movie_with_invalid_movie_id():
    create_test_file()
    assert users_data_manager.delete_user_movie(1, 19) is None


def test_delete_user_movie_with_invalid_user_id():
    create_test_file()
    assert users_data_manager.delete_user_movie(10, 1) is None
