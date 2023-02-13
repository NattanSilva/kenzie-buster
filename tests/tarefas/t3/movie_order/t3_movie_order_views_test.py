from rest_framework.test import APITestCase
from rest_framework.views import status
from movies.models import Movie
from rest_framework_simplejwt.tokens import RefreshToken
from tests.factories import (
    create_employee_with_token,
    create_movie_with_employee,
    create_non_employee_with_token,
)
from unittest.mock import patch, MagicMock


class MovieOrderViewsT3Test(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        template_url = "/api/movies/%s/orders/"

        cls.movie = create_movie_with_employee()
        cls.BASE_URL = template_url % cls.movie.pk
        # UnitTest Longer Logs
        cls.maxDiff = None

    def test_movie_order_creation_without_required_fields(self):
        _, token = create_non_employee_with_token()
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + str(token.access_token))

        response = self.client.post(self.BASE_URL, data={}, format="json")

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
        expected_fields = {"price"}
        returned_fields = set(resulted_data.keys())
        msg = "Verifique se todas as chaves obrigatórias são retornadas ao tentar criar um movie order sem os campos obrigatórios"
        self.assertSetEqual(expected_fields, returned_fields, msg)

    def test_movie_order_without_token(self):
        order_data = {"price": 100.00}

        response = self.client.post(self.BASE_URL, data=order_data, format="json")

        # STATUS CODE
        expected_status_code = status.HTTP_401_UNAUTHORIZED
        resulted_status_code = response.status_code

        msg = (
            "Verifique se o status code retornado do POST sem token "
            + f"em `{self.BASE_URL}` é {expected_status_code}"
        )
        self.assertEqual(expected_status_code, resulted_status_code, msg)

    @patch("django.utils.timezone.now", return_value="2022-11-27T17:55:22.819371Z")
    def test_movie_order_creation_with_non_employee_token(self, mock_now: MagicMock):
        non_employee, token = create_non_employee_with_token()
        non_employee_token = str(token.access_token)

        order_data = {"price": 100.00}
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + non_employee_token)
        response = self.client.post(self.BASE_URL, data=order_data, format="json")

        # STATUS CODE
        expected_status_code = status.HTTP_201_CREATED
        resulted_status_code = response.status_code

        msg = (
            "Verifique se o status code retornado do POST sem token de employee"
            + f"em `{self.BASE_URL}` é {expected_status_code}"
        )
        self.assertEqual(expected_status_code, resulted_status_code, msg)

        # RESPONSE JSON
        expected_data = {
            **order_data,
            **{
                "id": 1,
                "title": self.movie.title,
                "buyed_by": f"{non_employee.email}",
                "price": "100.00",
                "buyed_at": mock_now.return_value,
            },
        }
        resulted_data = response.json()
        msg = (
            "Verifique as informações da order retornadas no POST "
            + f"em `{self.BASE_URL}` estão corretas."
        )
        self.assertEqual(expected_data, resulted_data, msg)

    @patch("django.utils.timezone.now", return_value="2022-11-27T17:55:22.819371Z")
    def test_movie_order_creation_with_employee_token(self, mock_now: MagicMock):
        employee_data = {
            "username": "lucira_buster2",
            "email": "lucira_buster2@kenziebuster.com",
            "birthdate": "1999-09-09",
            "first_name": "Lucira",
            "last_name": "Buster",
            "password": "1234",
            "is_employee": True,
        }
        employee, token = create_employee_with_token(employee_data=employee_data)
        employee_token = str(token.access_token)

        order_data = {"price": 100.00}
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + employee_token)
        response = self.client.post(self.BASE_URL, data=order_data, format="json")

        # STATUS CODE
        expected_status_code = status.HTTP_201_CREATED
        resulted_status_code = response.status_code

        msg = (
            "Verifique se o status code retornado do POST sem token de employee"
            + f"em `{self.BASE_URL}` é {expected_status_code}"
        )
        self.assertEqual(expected_status_code, resulted_status_code, msg)

        # RESPONSE JSON
        expected_data = {
            **order_data,
            **{
                "id": 1,
                "title": self.movie.title,
                "buyed_by": f"{employee.email}",
                "price": "100.00",
                "buyed_at": mock_now.return_value,
            },
        }
        resulted_data = response.json()
        msg = (
            "Verifique as informações da order retornadas no POST "
            + f"em `{self.BASE_URL}` estão corretas."
        )
        self.assertEqual(expected_data, resulted_data, msg)
