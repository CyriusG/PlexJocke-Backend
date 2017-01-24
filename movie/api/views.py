from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore

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


class MovieCreateAPIView(APIView):
    queryset = Request.objects.all()
    serializer_class = MovieCreateSerializer

    def post(self, request, format=None):

        couchpotato = Couchpotato(settings.COUCHPOTATO_HOST, settings.COUCHPOTATO_PORT, settings.COUCHPOTATO_API_KEY)

        if couchpotato.addmovie(request.data['imdb_id']):
            session = SessionStore(session_key=request.data['sessionid'])

            data = request.data
            del data[-1]

            serializer = MovieCreateSerializer(data=data)

            if serializer.is_valid():
                serializer.save(cp_id = couchpotato.reply['movie']['_id'], user = session['plexjocke_username'], user_email = session['plexjocke_email'])
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({'message': 'Movie has already been requested.', 'success': False}, status=status.HTTP_409_CONFLICT)
        else:
            return Response(couchpotato.reply, status=status.HTTP_503_SERVICE_UNAVAILABLE)



class MovieDeleteAPIView(APIView):

    def delete(self, request, pk, format=None):

        couchpotato = Couchpotato(settings.COUCHPOTATO_HOST, settings.COUCHPOTATO_PORT, settings.COUCHPOTATO_API_KEY)

        try:
            movie = Request.objects.get(pk=pk)

            if couchpotato.deletemovie(movie.cp_id):
                movie.delete()

                return Response(couchpotato.reply, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(couchpotato.reply, status=status.HTTP_400_BAD_REQUEST)
        except Request.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class MovieDetailAPIView(RetrieveAPIView):
    queryset = Request.objects.all()
    serializer_class = MovieListSerializer


class MovieListAPIView(ListAPIView):
    queryset = Request.objects.all()
    serializer_class = MovieListSerializer
