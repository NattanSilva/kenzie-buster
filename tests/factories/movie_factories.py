from movies.models import Movie
from django.contrib.auth.models import AbstractUser
from .user_factories import create_employee_with_token


def create_movie_with_employee(
    movie_data: dict = None, employee: AbstractUser = None
) -> Movie:
    if not employee:
        employee, _ = create_employee_with_token()

    if not movie_data:
        movie_data = {
            "title": "Revolver",
            "duration": "110min",
            "rating": "R",
            "synopsis": "Jake Green is a hotshot gambler, long on audacity and short on...",
        }

    movie = Movie.objects.create(**movie_data, user=employee)

    return movie


def create_multiple_movies_with_employee(
    employee: AbstractUser, movies_count: int
) -> list[Movie]:
    movies_data = [
        {
            "title": f"Movie {index}",
            "duration": "110min",
            "rating": "R",
            "synopsis": "Jake Green is a hotshot gambler, long on audacity and short on...",
            "user": employee,
        }
        for index in range(0, movies_count)
    ]
    movies_objects = [Movie(**movie_data) for movie_data in movies_data]
    movies = Movie.objects.bulk_create(movies_objects)

    return movies
