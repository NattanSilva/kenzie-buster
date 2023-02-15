from django.db import models


class MovieChoices(models.TextChoices):
    DEFAULT = "G"
    PG = "PG"
    PG_13 = "PG-13"
    R = "R"
    NC_17 = "NC-17"


class Movie(models.Model):
    title = models.CharField(max_length=127, null=False)
    duration = models.CharField(max_length=10, null=True, default=None)
    rating = models.CharField(
        max_length=20,
        null=True,
        choices=MovieChoices.choices,
        default=MovieChoices.DEFAULT
    )
    synopsis = models.TextField(null=True, default=None)

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="movies",
        null=False
    )
