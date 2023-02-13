from rest_framework.test import APITestCase
from rest_framework.views import status
from movies.models import Movie
from rest_framework_simplejwt.tokens import RefreshToken
from tests.factories import (
    create_employee_with_token,
    create_movie_with_employee,
    create_non_employee_with_token,
    create_multiple_movies_with_employee,
)


class MovieViewsT2Test(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.BASE_URL = "/api/movies/"
        cls.BASE_DETAIL_URL = cls.BASE_URL + "1/"
        # UnitTest Longer Logs
        cls.maxDiff = None

    def test_movies_listing(self):
        employee, _ = create_employee_with_token()
        movies_count = 4
        create_multiple_movies_with_employee(employee, movies_count)

        response = self.client.get(self.BASE_URL)

        expected_count = movies_count
        resulted_count = len(response.json())

        msg = "Verifique se todos os filmes estão sendo retornados corretamente"
        self.assertEqual(expected_count, resulted_count, msg)

    def test_movie_creation_without_token(self):
        movie_data = {
            "title": "Frozen",
            "duration": "102min",
        }
        response = self.client.post(self.BASE_URL, data=movie_data, format="json")

        # STATUS CODE
        expected_status_code = status.HTTP_401_UNAUTHORIZED
        resulted_status_code = response.status_code

        msg = (
            "Verifique se o status code retornado do POST sem token "
            + f"em `{self.BASE_URL}` é {expected_status_code}"
        )
        self.assertEqual(expected_status_code, resulted_status_code, msg)

    def test_movie_creation_with_non_employee_token(self):
        non_employee, token = create_non_employee_with_token()
        non_employee_token = str(token.access_token)

        movie_data = {
            "title": "Frozen",
            "duration": "102min",
        }
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + non_employee_token)
        response = self.client.post(self.BASE_URL, data=movie_data, format="json")

        # STATUS CODE
        expected_status_code = status.HTTP_403_FORBIDDEN
        resulted_status_code = response.status_code

        msg = (
            "Verifique se o status code retornado do POST sem token de employee"
            + f"em `{self.BASE_URL}` é {expected_status_code}"
        )
        self.assertEqual(expected_status_code, resulted_status_code, msg)

    def test_movie_creation_with_employee_token(self):
        employee, token = create_employee_with_token()
        employee_token = str(token.access_token)

        movie_data = {
            "title": "Frozen",
            "duration": "102min",
        }
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + employee_token)
        response = self.client.post(self.BASE_URL, data=movie_data, format="json")

        # STATUS CODE
        expected_status_code = status.HTTP_201_CREATED
        resulted_status_code = response.status_code

        msg = (
            "Verifique se o status code retornado do POST com token de employee "
            + f"em `{self.BASE_URL}` é {expected_status_code}"
        )
        self.assertEqual(expected_status_code, resulted_status_code, msg)

        # RESPONSE JSON
        expected_data = {
            **movie_data,
            **{
                "id": 1,
                "added_by": f"{employee.email}",
                "rating": "G",
                "synopsis": None,
            },
        }
        resulted_data = response.json()
        msg = (
            "Verifique as informações do filme retornadas no POST "
            + f"em `{self.BASE_URL}` estão corretas."
        )
        self.assertEqual(expected_data, resulted_data, msg)

    def test_movie_creation_without_required_fields(self):
        _, token = create_employee_with_token()
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + str(token.access_token))

        movie_data = {"rating": "AAAAA"}

        response = self.client.post(self.BASE_URL, data=movie_data, format="json")

        # STATUS CODE
        expected_status_code = status.HTTP_400_BAD_REQUEST
        resulted_status_code = response.status_code
        msg = (
            "Verifique se o status code retornado do POST sem todos os campos obrigatórios "
            + f"em `{self.BASE_URL}` é {expected_status_code}"
        )
        self.assertEqual(expected_status_code, resulted_status_code, msg)

        # RETORNO JSON
        resulted_data: dict = response.json()
        expected_fields = {"title", "rating"}
        returned_fields = set(resulted_data.keys())
        msg = "Verifique se todas as chaves obrigatórias são retornadas ao tentar criar um filme sem os campos obrigatórios"
        self.assertSetEqual(expected_fields, returned_fields, msg)

    def test_movie_deletion_by_employee(self):
        employee, token = create_employee_with_token()

        # Criando movie 1
        movie_data = {"title": "Frozen", "duration": "102min"}
        create_movie_with_employee(movie_data, employee)

        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + str(token.access_token))
        response = self.client.delete(self.BASE_DETAIL_URL)

        expected_status_code = status.HTTP_204_NO_CONTENT
        result_status_code = response.status_code
        msg = (
            "Verifique se o status code retornado do DELETE "
            + f"em `{self.BASE_DETAIL_URL}` é {expected_status_code}"
        )
        self.assertEqual(expected_status_code, result_status_code, msg)

        msg = "Verifique se a deleção não está retornando nenhum body"
        self.assertRaises(TypeError, response.json)

        msg = "Verifique se o registro está sendo deletado do banco corretamente"
        self.assertFalse(Movie.objects.exists(), msg)

    def test_movie_deletion_by_non_employee(self):
        _, token = create_non_employee_with_token()
        movie_data = {"title": "Frozen", "duration": "102min"}

        # Criando movie 1
        employee, _ = create_employee_with_token()
        create_movie_with_employee(movie_data, employee)

        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + str(token.access_token))
        response = self.client.delete(self.BASE_DETAIL_URL)

        expected_status_code = status.HTTP_403_FORBIDDEN
        result_status_code = response.status_code
        msg = (
            "Verifique se o status code retornado do DELETE "
            + f"em `{self.BASE_URL}` é {expected_status_code}"
        )
        self.assertEqual(expected_status_code, result_status_code, msg)

        msg = "Verifique se o registro continua no banco quando uma tentativa de deleção sem token adequado falhar"
        self.assertTrue(Movie.objects.exists(), msg)

    def test_movie_deletion_without_token(self):
        movie_data = {
            "title": "Frozen",
            "duration": "102min",
        }
        response = self.client.delete(self.BASE_URL, data=movie_data, format="json")

        # STATUS CODE
        expected_status_code = status.HTTP_401_UNAUTHORIZED
        resulted_status_code = response.status_code

        msg = (
            "Verifique se o status code retornado do DELETE sem token "
            + f"em `{self.BASE_URL}` é {expected_status_code}"
        )
        self.assertEqual(expected_status_code, resulted_status_code, msg)
