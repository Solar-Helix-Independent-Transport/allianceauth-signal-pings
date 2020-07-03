import datetime
from django.utils import timezone

class time_helpers:

    @staticmethod
    def convert_timedelta(duration):
        days, seconds = duration.days, duration.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = (seconds % 60)
        return hours, minutes, seconds

    @staticmethod
    def format_timedelta(td):
        hours, minutes, seconds = time_helpers.convert_timedelta(td)
        return ("%d Days, %d Hours, %d Min" % (td.days, round(hours), round(minutes)))

    @staticmethod
    def get_time_until(dt):
        """ Return D / H / M Until DateTime """
        return time_helpers.format_timedelta(dt.replace(tzinfo=timezone.utc) - datetime.datetime.now(timezone.utc))