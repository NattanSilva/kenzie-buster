from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView, Request, Response, status
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Movie
from .permissions import IsEmployeeOrReadOnly
from .serializers import MovieOrderSerializer, MovieSerializer


class MovieView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsEmployeeOrReadOnly]

    def get(self, req: Request) -> Response:
        movies_list = Movie.objects.all()
        serializer = MovieSerializer(movies_list, many=True)

        return Response(serializer.data, status.HTTP_200_OK)
    
    def post(self, req: Request) -> Response:
        serializer = MovieSerializer(data=req.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=req.user)

        return Response(serializer.data, status.HTTP_201_CREATED)


class MovieDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsEmployeeOrReadOnly]
    
    def get(self, req: Request, movie_id: int) -> Response:
        movie = get_object_or_404(id=movie_id)
        serializer = MovieSerializer(movie)

        return Response(serializer.data, status.HTTP_200_OK)
    
    def delete(self, req: Request, movie_id: int) -> Response:
        movie = get_object_or_404(Movie, id=movie_id)

        movie.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
    

class MovieOrderView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, req: Request, movie_id: int) -> Response:
        movie = get_object_or_404(Movie, id=movie_id)
        seriaizer = MovieOrderSerializer(data=req.data)
        seriaizer.is_valid(raise_exception=True)

        seriaizer.save(user=req.user, movie=movie)

        return Response(seriaizer.data, status.HTTP_201_CREATED)

