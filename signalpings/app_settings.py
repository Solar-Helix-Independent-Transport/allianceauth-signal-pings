from django.conf import settings
import re

def get_site_url():  # regex sso url
    regex = r"^(.+)\/s.+"
    matches = re.finditer(regex, settings.ESI_SSO_CALLBACK_URL, re.MULTILINE)
    url = "http://"

    for m in matches:
        url = m.groups()[0] # first match

    return url

def fleets_active():
    return 'allianceauth.optimer' in settings.INSTALLED_APPS

def timers_active():
    return 'allianceauth.timerboard' in settings.INSTALLED_APPS

def hr_active():
    return 'allianceauth.hrapplications' in settings.INSTALLED_APPS