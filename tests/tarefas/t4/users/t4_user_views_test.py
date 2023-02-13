from rest_framework.test import APITestCase
from rest_framework.views import status
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from tests.factories import (
    create_employee_with_token,
    create_movie_with_employee,
    create_non_employee_with_token,
    create_multiple_movies_with_employee,
)

User: AbstractUser = get_user_model()


class UserViewsT4Test(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.BASE_URL = "/api/users/%s/"
        cls.employee, cls.employee_token = create_employee_with_token()
        cls.non_employee, cls.non_employee_token = create_non_employee_with_token()

        # UnitTest Longer Logs
        cls.maxDiff = None

    def test_if_cannot_get_user_info_without_token(self):
        base_url = self.BASE_URL % self.employee.id
        response = self.client.get(base_url)

        # STATUS CODE
        expected_status_code = status.HTTP_401_UNAUTHORIZED
        resulted_status_code = response.status_code

        msg = (
            f"Verifique se o status code retornado do {response.request['REQUEST_METHOD']} sem token "
            + f"em `{base_url}` é {expected_status_code}"
        )
        self.assertEqual(expected_status_code, resulted_status_code, msg)

    def test_if_a_non_employee_user_can_get_own_profile_info(self):
        base_url = self.BASE_URL % self.non_employee.id
        non_employee_token = str(self.non_employee_token.access_token)
        # STATUS CODE
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + non_employee_token)
        response = self.client.get(base_url)
        # ipdb.set_trace()
        expected_status_code = status.HTTP_200_OK
        returned_status_code = response.status_code
        msg = (
            f"Verifique se o status code retornado do {response.request['REQUEST_METHOD']} "
            + f"em `{base_url}` é {expected_status_code}"
        )
        self.assertEqual(expected_status_code, returned_status_code, msg)

        # RETORNO JSON
        expected_keys = {
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "birthdate",
            "is_employee",
            "is_superuser",
        }
        returned_keys = set(response.json().keys())
        msg = (
            f"Verifique se as chaves corretas estão sendo retornadas do {response.request['REQUEST_METHOD']} em "
            + f"em `{base_url}`"
        )

        self.assertSetEqual(expected_keys, returned_keys, msg)

    def test_if_a_non_employee_user_cannot_get_another_user_profile_info(self):
        base_url = self.BASE_URL % self.employee.id
        non_employee_token = str(self.non_employee_token.access_token)
        # STATUS CODE
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + non_employee_token)
        response = self.client.get(base_url)

        expected_status_code = status.HTTP_403_FORBIDDEN
        returned_status_code = response.status_code
        msg = (
            f"Verifique se o status code retornado do {response.request['REQUEST_METHOD']} com token não employee e não dono da conta "
            + f"em `{base_url}` é {expected_status_code}"
        )
        self.assertEqual(expected_status_code, returned_status_code, msg)

    def test_if_a_employee_user_can_get_another_user_profile_info(self):
        base_url = self.BASE_URL % self.non_employee.id
        employee_token = str(self.employee_token.access_token)
        # STATUS CODE
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + employee_token)
        response = self.client.get(base_url)
        # ipdb.set_trace()
        expected_status_code = status.HTTP_200_OK
        returned_status_code = response.status_code
        msg = (
            f"Verifique se o status code retornado do {response.request['REQUEST_METHOD']} "
            + f"em `{base_url}` é {expected_status_code}"
        )
        self.assertEqual(expected_status_code, returned_status_code, msg)

        # RETORNO JSON
        expected_keys = {
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "birthdate",
            "is_employee",
            "is_superuser",
        }
        returned_keys = set(response.json().keys())
        msg = (
            f"Verifique se as chaves corretas estão sendo retornadas do {response.request['REQUEST_METHOD']} em "
            + f"em `{base_url}`"
        )

        self.assertSetEqual(expected_keys, returned_keys, msg)

    def test_if_cannot_update_user_info_without_token(self):
        base_url = self.BASE_URL % self.employee.id
        response = self.client.patch(base_url, data={}, format="json")
        # import ipdb

        # ipdb.set_trace()
        # STATUS CODE
        expected_status_code = status.HTTP_401_UNAUTHORIZED
        resulted_status_code = response.status_code

        msg = (
            f"Verifique se o status code retornado do {response.request['REQUEST_METHOD']} sem token "
            + f"em `{base_url}` é {expected_status_code}"
        )
        self.assertEqual(expected_status_code, resulted_status_code, msg)

    def test_if_a_non_employee_user_cannot_update_another_user_profile_info(self):
        base_url = self.BASE_URL % self.employee.id
        non_employee_token = str(self.non_employee_token.access_token)

        # STATUS CODE
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + non_employee_token)
        response = self.client.patch(base_url, data={}, format="json")

        expected_status_code = status.HTTP_403_FORBIDDEN
        returned_status_code = response.status_code
        msg = (
            f"Verifique se o status code retornado do {response.request['REQUEST_METHOD']} com token não employee e não dono da conta "
            + f"em `{base_url}` é {expected_status_code}"
        )
        self.assertEqual(expected_status_code, returned_status_code, msg)

    def test_if_a_non_employee_user_can_update_own_profile_info(self):
        base_url = self.BASE_URL % self.non_employee.id
        non_employee_token = str(self.non_employee_token.access_token)
        user_data = {"username": "non_employee_patch", "password": "new_password"}

        # STATUS CODE
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + non_employee_token)
        response = self.client.patch(base_url, data=user_data, format="json")

        expected_status_code = status.HTTP_200_OK
        returned_status_code = response.status_code
        msg = (
            f"Verifique se o status code retornado do {response.request['REQUEST_METHOD']} "
            + f"em `{base_url}` é {expected_status_code}"
        )
        self.assertEqual(expected_status_code, returned_status_code, msg)

        # RETORNO JSON
        expected_keys = {
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "birthdate",
            "is_employee",
            "is_superuser",
        }
        returned_keys = set(response.json().keys())
        msg = (
            f"Verifique se as chaves corretas estão sendo retornadas do {response.request['REQUEST_METHOD']} em "
            + f"em `{base_url}`"
        )

        self.assertSetEqual(expected_keys, returned_keys, msg)

        user = User.objects.last()
        msg = (
            f"Verifique se a senha está sendo atualizada no {response.request['REQUEST_METHOD']} em "
            + f"em `{base_url}`"
        )
        self.assertTrue(user.check_password(user_data["password"]), msg)

    def test_if_a_employee_user_can_update_another_user_profile_info(self):
        base_url = self.BASE_URL % self.non_employee.id
        employee_token = str(self.employee_token.access_token)
        user_data = {"username": "employee_patch", "password": "new_password"}

        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + employee_token)
        response = self.client.patch(base_url, data=user_data, format="json")

        # STATUS CODE
        expected_status_code = status.HTTP_200_OK
        returned_status_code = response.status_code
        msg = (
            f"Verifique se o status code retornado do {response.request['REQUEST_METHOD']} "
            + f"em `{base_url}` é {expected_status_code}"
        )
        self.assertEqual(expected_status_code, returned_status_code, msg)

        # RETORNO JSON
        expected_keys = {
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "birthdate",
            "is_employee",
            "is_superuser",
        }
        returned_keys = set(response.json().keys())
        msg = (
            f"Verifique se as chaves corretas estão sendo retornadas do {response.request['REQUEST_METHOD']} em "
            + f"em `{base_url}`"
        )

        self.assertSetEqual(expected_keys, returned_keys, msg)

        user = User.objects.last()
        msg = (
            f"Verifique se a senha está sendo atualizada no {response.request['REQUEST_METHOD']} em "
            + f"em `{base_url}`"
        )
        self.assertTrue(user.check_password(user_data["password"]), msg)
