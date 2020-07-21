from django.dispatch import receiver

from django.db.models.signals import post_save, pre_delete
from allianceauth.groupmanagement.models import GroupRequest
from .models import GroupSignal, TimerSignal, FleetSignal, HRAppSignal
import requests
import json
import datetime
from django.utils import timezone

from .app_settings import get_site_url, hr_active, timers_active, fleets_active
from .helpers import time_helpers
import logging
logger = logging.getLogger(__name__)

RED = 16711710
BLUE = 42751
GREEN = 6684416

if hr_active():
    from allianceauth.hrapplications.models import Application

if fleets_active():
    from allianceauth.optimer.models import OpTimer

if timers_active():
    from allianceauth.timerboard.models import Timer

@receiver(post_save, sender=GroupRequest)
def new_req(sender, instance, created, **kwargs):
    if created:
        #logger.debug("New signal for %s" % instance.user.profile.main_character, flush=True)
        try:
            url = get_site_url() + "/group/management/"
            main_char = instance.user.profile.main_character
            group = instance.group.name

            if not instance.leave_request:
                embed = {'title': "New Group Request", 
                    'description': ("From **{}** to join **{}**".format(main_char.character_name,group)),
                    'color': BLUE,
                    'image': {'url': main_char.portrait_url_128 },
                    'url': url
                    }
            else:
                embed = {'title': "New Group Leave Request", 
                    'color': RED,
                    'description': ("From **{}** to leave **{}**".format(main_char.character_name,group)),
                    'image': {'url': main_char.portrait_url_128 },
                    'url': url
                    }

            hooks = GroupSignal.objects.filter(group=instance.group).select_related('webhook')

            for hook in hooks:
                if hook.webhook.enabled:
                    hook.webhook.send_embed(embed)

        except Exception as e:
            logger.error(e)
            pass  # shits fucked... Don't worry about it...

if timers_active():
    @receiver(post_save, sender=Timer)
    def timer_saved(sender, instance, created, **kwargs):
        #logger.debug("New signal for %s" % instance.user.profile.main_character, flush=True)
        try:
            corp_timer = instance.corp_timer
            if corp_timer:
                corp = instance.user.profile.main_character.corporation
            url = get_site_url() + "/timers/"
            main_char = instance.user.profile.main_character
            system = instance.system
            structure = instance.structure
            eve_time = instance.eve_time
            details = instance.details
            message = "New Timer Posted"
            col = GREEN
            if not created:
                message = "Timer Updated"
                col = BLUE
            restricted = ""
            if corp_timer:
                restricted = "Restricted to {}".format(corp)
            embed = {'title': message, 
                    'description': ("**{}** in **{}**\n\n{}\n{}".format(structure,system,details,restricted)),
                    'url': url,
                    'color': col,
                    "fields": [
                        {
                        "name": "Eve Time",
                        "value": eve_time.strftime("%Y-%m-%d %H:%M:%S")
                        },
                        {
                        "name": "Time Until",
                        "value": time_helpers.get_time_until(eve_time)
                        }

                    ],
                    "footer": {
                        "icon_url": main_char.portrait_url_64,
                        "text": "{}  [{}]".format(main_char.character_name, main_char.corporation_ticker)
                    }
                }

            hooks = TimerSignal.objects.all().select_related('webhook')
            old = datetime.datetime.now(timezone.utc) > eve_time
            for hook in hooks:
                if hook.webhook.enabled:
                    if old and hook.ignore_past_timers:
                        continue
                    if hook.corporation is not None:
                        if corp == hook.corporation:
                            hook.webhook.send_embed(embed)
                    elif not corp_timer:
                        hook.webhook.send_embed(embed)

        except Exception as e:
            logger.error(e)
            pass  # shits fucked... Don't worry about it... dont stop th UI

    @receiver(pre_delete, sender=Timer)
    def timer_deleted(sender, instance, **kwargs):
        #logger.debug("New signal for %s" % instance.user.profile.main_character, flush=True)
        try:
            corp_timer = instance.corp_timer

            corp_timer = instance.corp_timer
            if corp_timer:
                corp = instance.user.profile.main_character.corporation
            url = get_site_url() + "/timers/"
            main_char = instance.user.profile.main_character
            system = instance.system
            structure = instance.structure
            eve_time = instance.eve_time
            details = instance.details
            message = "Timer Deleted"
            restricted = ""
            if corp_timer:
                restricted = "Restricted to {}".format(corp)


            embed = {'title': message, 
                    'description': ("**{}** in **{}** has been removed\n\n{}\n{}".format(structure,system,details,restricted)),
                    'url': url,
                    'color': RED,
                    "fields": [
                        {
                        "name": "Eve Time",
                        "value": eve_time.strftime("%Y-%m-%d %H:%M:%S")
                        },
                    ],
                    "footer": {
                        "icon_url": main_char.portrait_url_64,
                        "text": "{}  [{}]".format(main_char.character_name, main_char.corporation_ticker)
                    }
                }

            hooks = TimerSignal.objects.all().select_related('webhook')
            old = datetime.datetime.now(timezone.utc) > eve_time
            for hook in hooks:
                if hook.webhook.enabled:
                    if old and hook.ignore_past_timers:
                        continue
                    if hook.corporation is not None:
                        if corp == hook.corporation:
                            hook.webhook.send_embed(embed)
                    elif not corp_timer:
                        hook.webhook.send_embed(embed)

        except Exception as e:
            logger.error(e)
            pass  # shits fucked... Don't worry about it... dont stop th UI

if fleets_active():
    @receiver(post_save, sender=OpTimer)
    def fleet_saved(sender, instance, created, **kwargs):
        #logger.debug("New signal for %s" % instance.eve_character, flush=True)
        try:
            url = get_site_url() + "/optimer/"
            main_char = instance.eve_character
            system = instance.system
            operation_name = instance.operation_name
            doctrine = instance.doctrine
            eve_time = instance.start
            fc = instance.fc
            col = GREEN
            message = "New Fleet Timer Posted"
            if not created:
                message = "Fleet Timer Updated"
                col = BLUE


            embed = {'title': message, 
                    'description': ("**{}** from **{}**".format(operation_name,system)),
                    'url': url,
                    'color': col,
                    "fields": [
                        {
                        "name": "FC",
                        "value": fc,
                        "inline": True
                        },
                        {
                        "name": "Doctrine",
                        "value": doctrine,
                        "inline": True
                        },
                        {
                        "name": "Eve Time",
                        "value": eve_time.strftime("%Y-%m-%d %H:%M:%S")
                        },
                        {
                        "name": "Time Until",
                        "value": time_helpers.get_time_until(eve_time)
                        }

                    ],
                    "footer": {
                        "icon_url": main_char.portrait_url_64,
                        "text": "{}  [{}]".format(main_char.character_name, main_char.corporation_ticker)
                    }
                }

            hooks = FleetSignal.objects.all().select_related('webhook')
            old = datetime.datetime.now(timezone.utc) > eve_time
            for hook in hooks:
                if hook.webhook.enabled:
                    if old and hook.ignore_past_fleets:
                        continue
                    hook.webhook.send_embed(embed)

        except Exception as e:
            logger.error(e)
            pass  # shits fucked... Don't worry about it...

    @receiver(pre_delete, sender=OpTimer)
    def fleet_deleted(sender, instance, **kwargs):
        #logger.debug("New signal for %s" % instance.eve_character, flush=True)
        try:
            url = get_site_url() + "/optimer/"
            main_char = instance.eve_character
            system = instance.system
            operation_name = instance.operation_name
            doctrine = instance.doctrine

            eve_time = instance.start

            fc = instance.fc
            message = "Fleet Removed"

            embed = {'title': message, 
                    'description': ("**{}** from **{}** has been cancelled".format(operation_name,system)),
                    'url': url,
                    'color': RED,
                    "fields": [
                        {
                        "name": "FC",
                        "value": fc,
                        "inline": True
                        },
                        {
                        "name": "Eve Time",
                        "value": eve_time.strftime("%Y-%m-%d %H:%M:%S")
                        }

                    ],
                    "footer": {
                        "icon_url": main_char.portrait_url_64,
                        "text": "{}  [{}]".format(main_char.character_name, main_char.corporation_ticker)
                    }
                }

            hooks = FleetSignal.objects.all().select_related('webhook')
            old = datetime.datetime.now(timezone.utc) > eve_time

            for hook in hooks:
                if hook.webhook.enabled:
                    if old and hook.ignore_past_fleets:
                        continue
                    hook.webhook.send_embed(embed)

        except Exception as e:
            logger.error(e)
            pass  # shits fucked... Don't worry about it...

if hr_active():
    @receiver(post_save, sender=Application)
    def application_saved(sender, instance, created, **kwargs):
        #logger.debug("New signal for %s" % instance.user.profile.main_character, flush=True)
        try:
            url = get_site_url() + "/hr/"
            main_char = instance.user.profile.main_character
            corp = instance.form.corp
            message = "New Corp Application"

            embed = {'title': message, 
                    'description': ("**{}** Applied to **{}**".format(main_char,corp)),
                    'url': url,
                    'color': GREEN,
                    "footer": {
                        "icon_url": main_char.portrait_url_64,
                        "text": "{}  [{}]".format(main_char.character_name, main_char.corporation_ticker)
                    }
                }

            hooks = HRAppSignal.objects.all().select_related('webhook')

            for hook in hooks:
                if hook.webhook.enabled:
                    if hook.corporation is None:
                        hook.webhook.send_embed(embed)
                    elif hook.corporation == corp:
                        hook.webhook.send_embed(embed)

        except Exception as e:
            logger.error(e)
            pass  # shits fucked... Don't worry about it...