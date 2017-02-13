import pycurl
from io import BytesIO

from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore
from django.utils.datastructures import MultiValueDictKeyError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from show.models import Request

from .serializers import ShowCreateSerializer, ShowListSerializer

from .sonarr import Sonarr
from frontpage_backend.plex import Plex


class ShowCreateAPIView(APIView):
    queryset = Request.objects.all()
    serializer_class = ShowCreateSerializer

    def post(self, request, format=None):

        sonarr = Sonarr(settings.SONARR_HOST, settings.SONARR_PORT, settings.SONARR_API_KEY)
        plex = Plex(settings.PLEX_HOST, settings.PLEX_PORT)

        try:
            # Get the session of the current user.
            session = SessionStore(session_key=request.COOKIES['sessionid'])

            try:
                token = session['plexjocke_token']

                if token:
                    if not plex.search_for_show(request.data['title'], request.data['release_date']):
                        if sonarr.addshow(request.data['title'], request.data['poster'], request.data['tvdb_id'], settings.SONARR_PATH, settings.SONARR_QUALITY):
                            session = SessionStore(session_key=request.data['sessionid'])

                            data = request.data

                            serializer = ShowCreateSerializer(data=request.data)

                            if serializer.is_valid():
                                serializer.save(sonarr_id = sonarr.reply['id'], user = session['plexjocke_username'], user_email = session['plexjocke_email'])

                                sonarr.search_for_seasons(sonarr.reply['id'], request.data['seasons'])

                                return Response(serializer.data, status=status.HTTP_201_CREATED)
                            else:
                                return Response({'message': 'Show has already been requested.', 'success': False}, status=status.HTTP_409_CONFLICT)
                        else:
                            return Response({'message': 'Show has already been requested.', 'success': False}, status=status.HTTP_409_CONFLICT)
                    else:
                        return Response({'message': 'Show is already on Plex.', 'success': False}, status=status.HTTP_409_CONFLICT)
                else:
                    return Response(status=status.HTTP_401_UNAUTHORIZED)
            except KeyError:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
        except MultiValueDictKeyError:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class ShowDeleteAPIView(APIView):

    def delete(self, request, pk, format=None):

        sonarr = Sonarr(settings.SONARR_HOST, settings.SONARR_PORT, settings.SONARR_API_KEY)

        try:
            # Get the session of the current user.
            session = SessionStore(session_key=request.COOKIES['sessionid'])

            try:
                token = session['plexjocke_token']

                if token:
                    try:
                        show = Request.objects.get(pk=pk)

                        if sonarr.delete_show(show.sonarr_id):
                            show.delete()

                            return Response(sonarr.reply, status=status.HTTP_204_NO_CONTENT)
                        else:
                            return Response(sonarr.reply, status=status.HTTP_400_BAD_REQUEST)
                    except Request.DoesNotExist:
                        return Response(status=status.HTTP_404_NOT_FOUND)
                else:
                    return Response(status=status.HTTP_401_UNAUTHORIZED)
            except KeyError:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
        except MultiValueDictKeyError:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class ShowDetailAPIView(APIView):
    def get(self, request, pk, format=None):
        serializer = ShowListSerializer(Request.objects.get(pk=pk))

        return Response(serializer.data)


class ShowListAPIView(APIView):
    def get(self, request, format=None):
        try:
            # Get the session of the current user.
            session = SessionStore(session_key=request.COOKIES['sessionid'])

            # Try and get the session token, return 401 unauthorized if unable to.
            try:
                token = session['plexjocke_token']

                if token:
                    # See if the user only wants to see their requests
                    try:
                        useronly = request.GET['useronly']

                        if useronly == 'y':
                             requests = Request.objects.all().filter(user=session['plexjocke_username'])
                        else:
                            requests = Request.objects.all()
                    except KeyError:
                        requests = Request.objects.all()

                    serializer = ShowListSerializer(requests, many=True)

                    return Response(serializer.data)
                else:
                    return Response(status=status.HTTP_401_UNAUTHORIZED)
            except KeyError:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
        except KeyError:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
