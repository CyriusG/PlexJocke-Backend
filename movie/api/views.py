from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore
from django.utils.datastructures import MultiValueDictKeyError

from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    )
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from movie.models import Request

from .serializers import MovieCreateSerializer, MovieListSerializer

from .couchpotato import Couchpotato
from frontpage_backend.plex import Plex


class MovieCreateAPIView(APIView):
    queryset = Request.objects.all()
    serializer_class = MovieCreateSerializer

    def post(self, request, format=None):

        # Create a new Couchpotato object with the settings specified in settings.py
        couchpotato = Couchpotato(settings.COUCHPOTATO_HOST, settings.COUCHPOTATO_PORT, settings.COUCHPOTATO_API_KEY)
        plex = Plex(settings.PLEX_HOST, settings.PLEX_PORT)

        try:
            # Get the session of the current user.
            session = SessionStore(session_key=request.data['sessionid'])

            try:
                token = session['plexjocke_username']

                if token:
                    print(plex.search_for_movie(request.data['title'], request.data['release_date']))
                    if plex.search_for_movie(request.data['title'], request.data['release_date']):
                        return Response({'message': 'Movie is already on Plex.', 'success': False}, status=status.HTTP_409_CONFLICT)
                    else:
                        # If adding a request for a movie succeeds.
                        if couchpotato.addmovie(request.data['imdb_id']):

                            # Remove the sessionid from the post data.
                            data = request.data
                            del data['sessionid']

                            # Create a new MovieCreateSerializer using the data that was posted.
                            serializer = MovieCreateSerializer(data=data)

                            # If the serializer is valid, save the request to the database and return HTTP status 201.
                            if serializer.is_valid():
                                serializer.save(cp_id = couchpotato.reply['movie']['_id'], user = session['plexjocke_username'], user_email = session['plexjocke_email'])
                                return Response(serializer.data, status=status.HTTP_201_CREATED)
                            # If the serializer failed return an error.
                            else:
                                return Response({'message': 'Movie has already been requested.', 'success': False}, status=status.HTTP_409_CONFLICT)
                        else:
                            return Response(couchpotato.reply, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                else:
                    return Response(status=status.HTTP_401_UNAUTHORIZED)
            except KeyError:
                return Response(status=status.HTTP_401_UNAUTHORIZED)

        except MultiValueDictKeyError:
            return Response(status=status.HTTP_401_UNAUTHORIZED)



class MovieDeleteAPIView(APIView):

    def delete(self, request, pk, format=None):

        # Create a new Couchpotato object with the settings specified in settings.py
        couchpotato = Couchpotato(settings.COUCHPOTATO_HOST, settings.COUCHPOTATO_PORT, settings.COUCHPOTATO_API_KEY)

        try:
            # Get the session of the current user.
            session = SessionStore(session_key=request.data['sessionid'])

            try:
                token = session['plexjocke_token']

                if token:
                    try:
                        # Fetch the movie to delete using the primary key specified.
                        movie = Request.objects.get(pk=pk)

                        # If Couchpotato successfully removed the movie.
                        if couchpotato.deletemovie(movie.cp_id):
                            # Delete the movie from the request database.
                            movie.delete()

                            return Response(couchpotato.reply, status=status.HTTP_204_NO_CONTENT)
                        else:
                            return Response(couchpotato.reply, status=status.HTTP_400_BAD_REQUEST)
                    except Request.DoesNotExist:
                        return Response(status=status.HTTP_404_NOT_FOUND)
                else:
                    return Response(status=status.HTTP_401_UNAUTHORIZED)
            except KeyError:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
        except MultiValueDictKeyError:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class MovieDetailAPIView(RetrieveAPIView):
    queryset = Request.objects.all()
    serializer_class = MovieListSerializer


class MovieListAPIView(ListAPIView):
    queryset = Request.objects.all()
    serializer_class = MovieListSerializer
