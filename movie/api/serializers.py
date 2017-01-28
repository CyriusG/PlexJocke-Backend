from rest_framework.serializers import ModelSerializer, HiddenField

from movie.models import Request


class MovieCreateSerializer(ModelSerializer):

    # THese fields are retrieved by the backend.
    cp_id = HiddenField(default='')
    user = HiddenField(default='')
    user_email = HiddenField(default='')

    class Meta:
        model = Request
        fields = [
            'title',
            'overview',
            'release_date',
            'imdb_id',
            'cp_id',
            'poster',
            'user',
            'user_email',
        ]


class MovieListSerializer(ModelSerializer):
    class Meta:
        model = Request
        fields = [
            'id',
            'title',
            'overview',
            'release_date',
            'imdb_id',
            'cp_id',
            'poster',
            'user',
            'user_email',
            'created',
            'updated',
            'available',
        ]
