from django.db import models


# Model for show request.
class Request(models.Model):
    title = models.CharField(max_length=500)
    seasons = models.CharField(max_length=500)
    release_date = models.DateField(auto_now_add=False, auto_now=False)
    tvdb_id = models.IntegerField()
    sonarr_id = models.IntegerField()
    poster = models.CharField(max_length=500)
    user = models.CharField(max_length=500)
    user_email = models.EmailField()
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    available = models.BooleanField(default=False)

    def __str__(self):
        return self.title + ' requested by: ' + self.user

    class Meta:
        unique_together = ('title', 'tvdb_id')
