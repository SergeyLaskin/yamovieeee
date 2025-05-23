from .data_manager_interface import DataManagerInterface
from .data_models import MovieReview


class MoviesReviews:

    def __init__(self, data_manager: DataManagerInterface):
        self._data_manager = data_manager

    @staticmethod
    def __review_to_dict(review) -> dict:
        return {
            "id": review.id,
            "user_id": review.user_id,
            "movie_id": review.movie_id,
            "rating": review.rating,
            "review_text": review.review_text,
            "user_name": review.user.user_name,
        }

    def get_movie_reviews(self) -> list[dict] | None:
        movie_reviews_query = self._data_manager.get_all_data()

        if movie_reviews_query is None:
            return None

        reviews = []
        for review in movie_reviews_query:
            reviews.append(self.__review_to_dict(review))
        return reviews

    @staticmethod
    def __instantiate_new_movie(new_movie_review):
        return MovieReview(
            user_id=new_movie_review['user_id'],
            movie_id=new_movie_review['movie_id'],
            rating=new_movie_review['rating'],
            review_text=new_movie_review['review_text']
        )

    def add_movie_review(self, new_movie_review: dict) -> bool | None:
        return self._data_manager.add_item(self.__instantiate_new_movie(new_movie_review))
