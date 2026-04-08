from app.repositories.review_repo import review_db

def get_average_rating(restaurant_id: int) -> float:
    """
    Return Value: Rating from 0 to 10, return -1 if there's no rating.
    """
    reviews = [review for review in review_db.get_all_reviews() if review.restaurant_id == restaurant_id]
    ratings = [review.rating for review in reviews]
    ratings_count = len(reviews)
    if (ratings_count == 0):
        return -1

    return sum(ratings) / ratings_count