import re

from django.apps import apps
from django.conf import settings


def get_site_url():  # regex sso url
    regex = r"^(.+)\/s.+"
    matches = re.finditer(regex, settings.ESI_SSO_CALLBACK_URL, re.MULTILINE)
    url = "http://"

    for m in matches:
        url = m.groups()[0] # first match

    return url

def fleets_active():
    return apps.is_installed('allianceauth.optimer')

def timers_active():
    return apps.is_installed('allianceauth.timerboard')

def hr_active():
    return apps.is_installed('allianceauth.hrapplications')

def srp_active():
    return apps.is_installed('allianceauth.srp')
