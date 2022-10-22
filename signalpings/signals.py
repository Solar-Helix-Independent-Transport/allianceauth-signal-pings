import datetime

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone

from allianceauth.authentication.models import (
    CharacterOwnership, EveCharacter, UserProfile,
)
from allianceauth.eveonline.evelinks.dotlan import solar_system_url
from allianceauth.eveonline.evelinks.evewho import (
    character_url, corporation_url,
)
from allianceauth.groupmanagement.models import GroupRequest
from allianceauth.services.hooks import get_extension_logger

from .app_settings import (
    fleets_active, get_site_url, hr_active, srp_active, timers_active,
)
from .helpers import time_helpers
from .models import (
    CharacterSignal, FleetSignal, GroupSignal, HRAppSignal, SRPSignal,
    TimerSignal,
)

logger = get_extension_logger(__name__)

RED = 16711710
BLUE = 42751
GREEN = 6684416

if hr_active():
    from allianceauth.hrapplications.models import (
        Application, ApplicationComment,
    )

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
            logger.debug(
                f"New Group Request Signal for {instance.user.profile.main_character}")
            url = get_site_url() + reverse("groupmanagement:management")
            main_char = instance.user.profile.main_character

            if main_char.alliance_ticker is not None:
                footer_string = f"{main_char.character_name}  [{main_char.corporation_ticker}] - [{main_char.alliance_ticker}]"
            else:
                footer_string = f"{main_char.character_name}  [{main_char.corporation_ticker}]"

            if not instance.leave_request:
                embed = {
                    'title': "New Group Request",
                    'description': f"From **{main_char.character_name}** to join **{instance.group.name}**",
                    'color': BLUE,
                    'image': {'url': main_char.portrait_url_128},
                    'url': url,
                    "footer": {
                        "icon_url": main_char.portrait_url_64,
                        "text": footer_string
                    }
                }
            else:
                embed = {
                    'title': "New Group Leave Request",
                    'color': RED,
                    'description': f"From **{main_char.character_name}** to leave **{instance.group.name}**",
                    'image': {'url': main_char.portrait_url_128},
                    'url': url,
                    "footer": {
                        "icon_url": main_char.portrait_url_64,
                        "text": footer_string
                    }
                }

            hooks = GroupSignal.objects.filter(
                group=instance.group).select_related('webhook')

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
            logger.debug(
                "New Character Ownership Signal (gained) for %s" % instance.character)
            url = get_site_url()
            character = instance.character
            main_char = instance.user.profile.main_character
            embed = {
                'title': "New Character Registered",
                'color': GREEN,
                'description': "[{}]({}) [ [{}]({}) ]\nRegistered\n[{}]({}) [ [{}]({}) ]".format(
                    main_char,
                    character_url(main_char.character_id),
                    main_char.corporation_name,
                    corporation_url(main_char.corporation_id),
                    character,
                    character_url(character.character_id),
                    character.corporation_name,
                    corporation_url(character.corporation_id)
                ),
                'image': {'url': character.portrait_url_128},
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
        logger.debug(f"New Character Ownership signal (lost) for {instance.character}")
        url = get_site_url()
        character = instance.character
        main_char = instance.user.profile.main_character

        embed = {
            'title': "Character Ownership Lost",
            'color': RED,
            'description': "[{}]({}) [ [{}]({}) ]\nLost Ownership of\n[{}]({}) [ [{}]({}) ]".format(
                main_char,
                character_url(main_char.character_id),
                main_char.corporation_name,
                corporation_url(main_char.corporation_id),
                character,
                character_url(character.character_id),
                character.corporation_name,
                corporation_url(character.corporation_id)
            ),
            'image': {'url': character.portrait_url_128},
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

        embed = {
            'title': "State Change",
            'color': BLUE,
            'description': ("**{}** ([{}]({})) \nChanged State to **{}**".format(
                username,
                main_char,
                character_url(main_char.character_id),
                state_new)),
            'image': {'url': main_char.portrait_url_128},
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
            logger.debug("New Timerboard signal for %s" % instance)
            corp_timer = instance.corp_timer
            if corp_timer:
                corp = instance.user.profile.main_character.corporation
            url = get_site_url() + reverse("timerboard:view")
            main_char = instance.user.profile.main_character
            system = "[" + instance.system + \
                "](" + solar_system_url(instance.system) + ")"
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
                restricted = f"Restricted to {corp}"
            embed = {
                'title': message,
                'description': (f"**{structure}** in **{system}**\n\n{details}\n{restricted}"),
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
                    "text": f"{main_char.character_name}  [{main_char.corporation_ticker}]"
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
                restricted = f"Restricted to {corp}"

            embed = {
                'title': message,
                'description': (f"**{structure}** in **{system}** has been removed\n\n{details}\n{restricted}"),
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
                    "text": f"{main_char.character_name}  [{main_char.corporation_ticker}]"
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
            logger.debug(f"New signal fleet created for {instance.operation_name}")
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

            embed = {
                'title': message,
                'description': (f"**{operation_name}** from **{system}**"),
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
                    "text": f"{main_char.character_name}  [{main_char.corporation_ticker}]"
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
            logger.debug(f"New signal fleet deleted for {instance.operation_name}")
            url = get_site_url() + reverse("optimer:view")
            main_char = instance.eve_character
            system = instance.system
            operation_name = instance.operation_name
            doctrine = instance.doctrine

            eve_time = instance.start

            fc = instance.fc
            message = "Fleet Removed"

            embed = {
                'title': message,
                'description': (f"**{operation_name}** from **{system}** has been cancelled"),
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
                    "text": f"{main_char.character_name}  [{main_char.corporation_ticker}]"
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
            logger.debug(
                f"New HRApp Signal for {instance.user.profile.main_character.character_name}")
            url = get_site_url() + "/hr/"
            main_char = "[" + instance.user.profile.main_character.character_name + \
                "](" + character_url(instance.user.profile.main_character.character_id) + ")"
            corp = "[" + instance.form.corp.corporation_name + \
                "](" + corporation_url(instance.form.corp.corporation_id) + ")"
            sending = False
            if created:
                message = "New Corp Application"
                message_colour = GREEN
                message_description = (
                    f"**{main_char}** Has applied to **{corp}**")
                sending = True
            elif instance.approved is not None:
                message = "Approved"
                message_colour = BLUE
                if instance.approved == False:
                    message = "Denied"
                    message_colour = RED
                message_title = f"Corp Application {message}"
                application_approver = "[" + instance.reviewer.profile.main_character.character_name + \
                    "](" + character_url(instance.reviewer.profile.main_character.character_id) + ")"
                message_description = (
                    f"**{main_char}** Application to **{corp}** {message} by **{application_approver}**")
                sending = True

            if sending == True:
                hooks = HRAppSignal.objects.all().select_related('webhook')
                embed = {
                    'title': message_title,
                    'description': message_description,
                    'url': url,
                    'color': message_colour,
                    "footer": {
                        "icon_url": instance.user.profile.main_character.portrait_url_64,
                        "text": f"{instance.user.profile.main_character.character_name}  [{instance.user.profile.main_character.corporation_ticker}]"
                    }
                }

                for hook in hooks:
                    if hook.webhook.enabled:
                        if hook.corporation is None:
                            hook.webhook.send_embed(embed)
                        elif hook.corporation == instance.form.corp:
                            hook.webhook.send_embed(embed)

        except Exception as e:
            logger.error(e)
            pass  # shits fucked... Don't worry about it...

if hr_active():
    @receiver(post_save, sender=ApplicationComment)
    def comment_saved(sender, instance, created, update_fields, **kwargs):
        try:
            logger.debug(
                "New HRApp Application Comment signal for {instance.user.profile.main_character.character_name}")
            url = get_site_url() + "/hr/"
            comment_main_char = "[" + instance.user.profile.main_character.character_name + \
                "](" + character_url(instance.user.profile.main_character.character_id) + ")"
            application_main_char = "[" + instance.application.user.profile.main_character.character_name + \
                "](" + character_url(instance.application.user.profile.main_character.character_id) + ")"

            corp = "[" + instance.application.form.corp.corporation_name + \
                "](" + corporation_url(instance.application.form.corp.corporation_id) + ")"

            message = "New HRApp Comment"
            message_colour = BLUE
            message_description = (
                f"**{comment_main_char}** Commented on **{application_main_char}**'s Application to **{corp}**")

            embed = {
                'title': message,
                'description': message_description,
                'url': url,
                'color': message_colour,
                "fields": [
                    {
                        "name": instance.user.profile.main_character.character_name,
                        "value": instance.text,
                    },
                ],
                "footer": {
                    "icon_url": instance.application.user.profile.main_character.portrait_url_64,
                    "text": f"{instance.application.user.profile.main_character.character_name}  [{instance.application.user.profile.main_character.corporation_ticker}]"
                }
            }

            hooks = HRAppSignal.objects.all().select_related('webhook')

            for hook in hooks:
                if hook.notify_comments:
                    if hook.webhook.enabled:
                        if hook.corporation is None:
                            hook.webhook.send_embed(embed)
                        elif hook.corporation == instance.application.form.corp:
                            hook.webhook.send_embed(embed)

        except Exception as e:
            logger.error(e)
            pass  # shits fucked... Don't worry about it...


if srp_active():
    @receiver(post_save, sender=SrpUserRequest)
    def application_saved(sender, instance, created, **kwargs):
        try:
            # Cant pull userprofile, note in the model
            logger.debug("New SRP signal for %s" % instance.character)
            url = get_site_url() + reverse("srp:management")
            character = instance.character
            srp_status = instance.srp_status
            zkill_string = f"[Link]({instance.killboard_link})"
            srp_ship_name = instance.srp_ship_name
            value_string = f"{instance.srp_total_amount} Isk"
            additional_info = instance.additional_info
            hooks = SRPSignal.objects.all().select_related('webhook')
            character_icon = character.portrait_url_64

            # Take our SRP character and resolve it to a proper model, then work our way to discord
            char = EveCharacter.objects.get(character_name=character)
            discord_id = char.character_ownership.user.discord.uid
            main = char.character_ownership.user.profile.main_character

            for hook in hooks:
                if hook.webhook.enabled:
                    if hook.notify_type == srp_status:

                        # Format the Requestor field to be a Discord @Mention or if False, a users Main.
                        if hook.mention_requestor:
                            mention_string = "<@!%s>" % discord_id
                        else:
                            mention_string = f"{main}"

                        # Setup Embed prettyness based on type
                        if srp_status == 'Pending':
                            message = "New SRP Request"
                            message_description = "**{}** Requested SRP for a **{}**".format(
                                main, srp_ship_name)
                            message_color = BLUE
                        elif srp_status == 'Approved':
                            message = "SRP Request Approved"
                            message_description = "**{}**'s Request to SRP a **{}** was Approved".format(
                                main, srp_ship_name)
                            message_color = GREEN
                        elif srp_status == 'Rejected':
                            message = "SRP Request Rejected"
                            message_description = "**{}**'s Request to SRP a **{}** was Rejected".format(
                                main, srp_ship_name)
                            message_color = RED
                        else:  # Hey we better catch any weirdness here
                            message = 'SRP Signal Error'
                            message_description = "Error"
                            message_color = RED

                        # Cook up a lil ol' payload from above settings
                        embed = {
                            'title': message,
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
                                # evelinks needs a typeID for ship icon, Need to work this one out.
                                "icon_url": character_icon,
                                "text": f"{character} - {srp_ship_name}"
                            }
                        }

                        hook.webhook.send_embed(embed)

        except Exception as e:
            logger.error(e)
            pass  # shits fucked... Don't worry about it...
