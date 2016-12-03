from django.db import models


# Model for movie request.
class Request(models.Model):
    title = models.CharField(max_length=500)
    overview = models.TextField()
    release_date = models.DateField(auto_now_add=False, auto_now=False)
    imdb_id = models.CharField(max_length=12)
    cp_id = models.CharField(max_length=48)
    poster = models.CharField(max_length=500)
    user = models.CharField(max_length=500)
    user_email = models.EmailField()
    created = models.DateField(auto_now_add=True, auto_now=False)
    updated = models.DateField(auto_now_add=False, auto_now=True)
    available = models.BooleanField(default=False)

    def __str__(self):
        return self.title + ' requested by: ' + self.user

    class Meta:
        unique_together = ('title', 'imdb_id')