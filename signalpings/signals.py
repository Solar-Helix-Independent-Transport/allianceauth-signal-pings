from django.dispatch import receiver

from django.db.models.signals import post_save, pre_delete, pre_save
from django.urls import reverse
from allianceauth.groupmanagement.models import GroupRequest
from allianceauth.authentication.models import UserProfile, CharacterOwnership, EveCharacter
from allianceauth.eveonline.evelinks.eveimageserver import  type_icon_url, character_portrait_url
from .models import GroupSignal, TimerSignal, FleetSignal, HRAppSignal, CharacterSignal, StateSignal, SRPSignal
import requests
import json
import datetime
from django.utils import timezone

from .app_settings import get_site_url, hr_active, timers_active, fleets_active, srp_active
from .helpers import time_helpers

from allianceauth.services.hooks import get_extension_logger
logger = get_extension_logger(__name__)

RED = 16711710
BLUE = 42751
GREEN = 6684416

if hr_active():
    from allianceauth.hrapplications.models import Application

if fleets_active():
    from allianceauth.optimer.models import OpTimer

if timers_active():
    from allianceauth.timerboard.models import Timer

if srp_active():
    from allianceauth.srp.models import SrpUserRequest

@receiver(post_save, sender=GroupRequest)
def new_req(sender, instance, created, **kwargs):
    if created:
        try:
            logger.debug("New Group Request Signal for %s" % instance.user.profile.main_character)
            url = get_site_url() + reverse("groupmanagement:management")
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

@receiver(post_save, sender=CharacterOwnership)
def new_character(sender, instance, created, **kwargs):
    if created:
        try:
            logger.debug("New Character Ownership Signal (gained) for %s" % instance.character)
            url = get_site_url()
            character = instance.character
            main_char = instance.user.profile.main_character

            embed = {'title': "New Character Registered", 
                'color': GREEN,
                'description': ("**{}** Registered **{}**".format(main_char,character)),
                'image': {'url': main_char.portrait_url_128 },
                'url': url
                }

            hooks = CharacterSignal.objects.all().select_related('webhook')

            for hook in hooks:
                if hook.webhook.enabled:
                    if hook.add_notify:
                        hook.webhook.send_embed(embed)

        except Exception as e:
            logger.error(e)
            pass  # shits fucked... Don't worry about it...  Steve Irwin didn't stop and neither will I

@receiver(pre_delete, sender=CharacterOwnership)
def removed_character(sender, instance, **kwargs):
    try:
        logger.debug("New Character Ownership signal (lost) for %s" % instance.character)
        url = get_site_url()
        character = instance.character
        main_char = instance.user.profile.main_character

        embed = {'title': "Character Ownership Lost", 
            'color': RED,
            'description': ("**{}** lost ownership of **{}**".format(main_char,character)),
            'image': {'url': main_char.portrait_url_128 },
            'url': url
            }

        hooks = CharacterSignal.objects.all().select_related('webhook')

        for hook in hooks:
            if hook.webhook.enabled:
                if hook.remove_notify:
                    hook.webhook.send_embed(embed)

    except Exception as e:
        logger.error(e)
        pass  # shits fucked... Don't worry about it...  Steve Irwin didn't stop and neither will I

@receiver(post_save, sender=UserProfile)
def state_change(sender, instance, raw, using, update_fields, **kwargs):
    try:
        logger.debug("New State change signal for %s" % instance)
        url = get_site_url()
        username = instance
        state_new = instance.user.profile.state
        main_char = instance.user.profile.main_character

        embed = {'title': "State Change", 
            'color': BLUE,
            'description': ("User **{}** Changed State to **{}**".format(username,state_new)),
            'image': {'url': main_char.portrait_url_128 },
            'url': url
            }

        hooks = CharacterSignal.objects.all().select_related('webhook')

        if 'state' in update_fields:
            for hook in hooks:
                if hook.webhook.enabled:
                    hook.webhook.send_embed(embed)

    except Exception as e:
        logger.error(e)
        pass  # shits fucked... Don't worry about it...  Steve Irwin didn't stop and neither will I

if timers_active():
    @receiver(post_save, sender=Timer)
    def timer_saved(sender, instance, created, **kwargs):
        try:
            logger.debug("New Timerboard signal for %s" % instance )
            corp_timer = instance.corp_timer
            if corp_timer:
                corp = instance.user.profile.main_character.corporation
            url = get_site_url() + reverse("timerboard:view")
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
            pass  # shits fucked... Don't worry about it... don't stop th UI

    @receiver(pre_delete, sender=Timer)
    def timer_deleted(sender, instance, **kwargs):
        try:
            logger.debug("New timer removal for %s" % instance.structure)
            corp_timer = instance.corp_timer
            if corp_timer:
                corp = instance.user.profile.main_character.corporation
            url = get_site_url() + reverse("timerboard:view")
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
            pass  # shits fucked... Don't worry about it... don't stop th UI

if fleets_active():
    @receiver(post_save, sender=OpTimer)
    def fleet_saved(sender, instance, created, **kwargs):
        try:
            logger.debug("New signal fleet created for %s" % instance.operation_name)
            url = get_site_url() + reverse("optimer:view")
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
        try:
            logger.debug("New signal fleet deleted for %s" % instance.operation_name)
            url = get_site_url() + reverse("optimer:view")
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
        try:
            logger.debug("New signal for %s" % instance.user.profile.main_character)
            url = get_site_url() +  reverse("hrapplications:index")
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

if srp_active():
    @receiver(post_save, sender=SrpUserRequest)
    def application_saved(sender, instance, created, **kwargs):
        try:
            logger.debug("New SRP signal for %s" % instance.character) ##Cant pull userprofile, note in the model
            url = get_site_url() + reverse("srp:management")
            character = instance.character
            srp_status = instance.srp_status
            zkill_string = "[Link]({})".format(instance.killboard_link)
            srp_ship_name = instance.srp_ship_name
            value_string = "{} Isk".format(instance.srp_total_amount)
            additional_info = instance.additional_info
            hooks = SRPSignal.objects.all().select_related('webhook')
            character_icon = character.portrait_url_64

            ## Take our SRP character and resolve it to a proper model, then work our way to discord
            char = EveCharacter.objects.get(character_name=character)
            discord_id = char.character_ownership.user.discord.uid
            main = char.character_ownership.user.profile.main_character

            for hook in hooks:
                if hook.webhook.enabled:
                    if hook.notify_type == srp_status:

                        ## Format the Requestor field to be a Discord @Mention or if False, a users Main.
                        if hook.mention_requestor:
                            mention_string = "<@!%s>" % discord_id
                        else:
                            mention_string = "{}".format(main)

                        ## Setup Embed prettyness based on type
                        if srp_status == 'Pending':
                            message = "New SRP Request"
                            message_description = "**{}** Requested SRP for a **{}**".format(main,srp_ship_name)
                            message_color = BLUE
                        elif srp_status == 'Approved':
                            message = "SRP Request Approved"
                            message_description = "**{}**'s Request to SRP a **{}** was Approved".format(main,srp_ship_name)
                            message_color = GREEN
                        elif srp_status == 'Rejected':
                            message = "SRP Request Rejected"
                            message_description = "**{}**'s Request to SRP a **{}** was Rejected".format(main,srp_ship_name)
                            message_color = RED
                        else: ## Hey we better catch any weirdness here
                            message = 'SRP Signal Error'
                            message_description = "Error"
                            message_color = RED

                        ## Cook up a lil ol' payload from above settings
                        embed = {'title': message, 
                                'description': (message_description),
                                'url': url,
                                'color': message_color,
                                "fields": [
                                    {
                                    "name": "Requestor",
                                    "value": mention_string,
                                    "inline": True
                                    },
                                    {
                                    "name": "Status",
                                    "value": srp_status,
                                    "inline": True
                                    },
                                    {
                                    "name": "zKill",
                                    "value": zkill_string,
                                    "inline": True
                                    },
                                    {
                                    "name": "Value",
                                    "value": value_string,
                                    "inline": False
                                    },
                                    {
                                    "name": "Additional Info",
                                    "value": additional_info,
                                    "inline": False
                                    }
                                ],
                                "footer": {
                                    "icon_url": character_icon, ##evelinks needs a typeID for ship icon, Need to work this one out.
                                    "text": "{} - {}".format(character, srp_ship_name)
                                }
                            }

                        hook.webhook.send_embed(embed)

        except Exception as e:
            logger.error(e)
            pass  # shits fucked... Don't worry about it...