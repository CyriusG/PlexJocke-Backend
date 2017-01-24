from rest_framework.serializers import ModelSerializer, HiddenField

from show.models import Request


class ShowCreateSerializer(ModelSerializer):

    sonarr_id = HiddenField(default='')
    user = HiddenField(default='')
    user_email = HiddenField(default='')

    class Meta:
        model = Request
        fields = [
            'title',
            'seasons',
            'release_date',
            'tvdb_id',
            'sonarr_id',
            'poster',
            'user',
            'user_email',
        ]

class ShowListSerializer(ModelSerializer):
    class Meta:
        model = Request
        fields = [
            'id',
            'title',
            'seasons',
            'release_date',
            'tvdb_id',
            'sonarr_id',
            'poster',
            'user',
            'user_email',
            'created',
            'updated',
            'available',
        ]
