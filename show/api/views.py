import pycurl
from io import BytesIO

from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore

from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    )
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from show.models import Request

from .serializers import ShowCreateSerializer, ShowListSerializer

from .sonarr import Sonarr


class ShowCreateAPIView(APIView):
    queryset = Request.objects.all()
    serializer_class = ShowCreateSerializer

    def post(self, request, format=None):

        sonarr = Sonarr(settings.SONARR_HOST, settings.SONARR_PORT, settings.SONARR_API_KEY)

        if sonarr.addshow(request.data['title'], request.data['poster'], request.data['tvdb_id'], settings.SONARR_PATH, settings.SONARR_QUALITY):
            session = SessionStore(session_key=request.data['sessionid'])

            data = request.data
            del data[-1]

            serializer = ShowCreateSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save(sonarr_id = sonarr.reply['id'], user = session['plexjocke_username'], user_email = session['plexjocke_email'])

                sonarr.search_for_seasons(sonarr.reply['id'], request.data['seasons'])

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({'message': 'Show has already been requested.', 'success': False}, status=status.HTTP_409_CONFLICT)
        else:
            return Response({'message': 'Show has already been requested.', 'success': False}, status=status.HTTP_409_CONFLICT)


class ShowDeleteAPIView(APIView):

    def delete(self, request, pk, format=None):

        sonarr = Sonarr(settings.SONARR_HOST, settings.SONARR_PORT, settings.SONARR_API_KEY)

        try:
            show = Request.objects.get(pk=pk)

            if sonarr.delete_show(show.sonarr_id):
                show.delete()

                return Response(sonarr.reply, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(sonarr.reply, status=status.HTTP_400_BAD_REQUEST)
        except Request.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class ShowDetailAPIView(RetrieveAPIView):
    queryset = Request.objects.all()
    serializer_class = ShowListSerializer


class ShowListAPIView(ListAPIView):
    queryset = Request.objects.all()
    serializer_class = ShowListSerializer
