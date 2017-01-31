from django.conf import settings
from django_cron import CronJobBase, Schedule

from frontpage_backend.plex import Plex
from frontpage_backend.notification import send_message

from .models import Request

from time import strftime

class ShowAvailability(CronJobBase):
    # Configure Cron parameters and set the unique code for this particular CronJob.
    RUN_EVERY_MINS = settings.CRON_INTERVAL
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'show.availability'

    # Create Plex object and retrieve every movie request that is marked as unavailable.
    def __init__(self):
        self.__plex = Plex(settings.PLEX_HOST, settings.PLEX_PORT)
        self.__shows = Request.objects.all().filter(available=False)

    def do(self):
        for show in self.__shows:
            if self.__plex.search_for_show(show.title, show.release_date.strftime('%Y-%m-%d')):
                show.available = True
                show.save()
                send_message(settings.NOTIFICATION_SENDER, show.user_email, 'Something you requested is now available.', show.title + ' is now available on Plex.', False)
