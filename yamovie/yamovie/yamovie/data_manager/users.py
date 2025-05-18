from typing import List

from .data_manager_interface import DataManagerInterface
from .data_models import User


class Users:

    def __init__(self, data_manager: DataManagerInterface):
        self._data_manager = data_manager

    @staticmethod
    def __user_to_dict(user) -> dict:
        movies = []
        if user.movies:
            for user_movie in user.movies:
                movies.append(
                    {
                        "user_movie_id": user_movie.id,
                        "id": user_movie.movie.id,
                        "movie_name": user_movie.movie.movie_name,
                        "director": user_movie.movie.director,
                        "year": user_movie.movie.year,
                        "rating": user_movie.movie.rating,
                        "poster": user_movie.movie.poster,
                        "website": user_movie.movie.website
                    }
                )
        return {"id": user.id,
                "user_name": user.user_name,
                "movies": movies}

    def get_all_users(self) -> List[dict] | None:
        users_query = self._data_manager.get_all_data()
        if users_query is None:
            return None

        users = []
        for user in users_query:
            users.append(self.__user_to_dict(user))
        return users

    def get_user(self, user_id: int) -> dict | None:
        user = self._data_manager.get_item_by_id(user_id)
        if user is None:
            return None
        return self.__user_to_dict(user)

    @staticmethod
    def __validate_user_data(new_user: dict) -> bool:
        return 'user_name' in new_user and 'movies' in new_user

    @staticmethod
    def __instantiate_new_user(name):
        return User(
            user_name=name
        )

    def add_user(self, new_user: dict) -> bool | None:
        if self.__validate_user_data(new_user):
            return self._data_manager.\
                    add_item(self.__instantiate_new_user(new_user['user_name']))
        return None

    def update_user(self, updated_user: dict):
        return self._data_manager.update_item(updated_user)

    def delete_user(self, user_id: int) -> bool | None:
        return self._data_manager.delete_item(user_id)
