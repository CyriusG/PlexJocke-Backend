from django.conf import settings
from django_cron import CronJobBase, Schedule

from frontpage_backend.plex import Plex
from frontpage_backend.notification import send_message

from .models import Request

from time import strftime

class MovieAvailability(CronJobBase):
    # Configure Cron parameters and set the unique code for this particular CronJob.
    RUN_EVERY_MINS = settings.CRON_INTERVAL
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'movie.availability'

    # Create Plex object and retrieve every movie request that is marked as unavailable.
    def __init__(self):
        self.__plex = Plex(settings.PLEX_HOST, settings.PLEX_PORT)
        self.__movies = Request.objects.all().filter(available=False)

    def do(self):
        for movie in self.__movies:
            if self.__plex.search_for_movie(movie.title, movie.release_date.strftime('%Y-%m-%d')):
                movie.available = True
                movie.save()
                send_message(settings.NOTIFICATION_SENDER, movie.user_email, 'Something you requested is now available.', movie.title + ' is now available on Plex.', False)
