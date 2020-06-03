from django.dispatch import receiver

from django.db.models.signals import post_save
from allianceauth.groupmanagement.models import GroupRequest

from .models import GroupSignal
import requests
import json

from .app_settings import get_site_url

import logging
logger = logging.getLogger(__name__)

@receiver(post_save, sender=GroupRequest)
def new_req(sender, instance, created, **kwargs):
    if created:
        logger.debug("New signal for %s" % instance.user.profile.main_character, flush=True)
        try:
            url = get_site_url() + "/group/management/"
            main_char = instance.user.profile.main_character
            group = instance.group.name

            if not instance.leave_request:
                embed = {'title': "New Group Request", 
                    'description': ("From **{}** to join **{}**".format(main_char.character_name,group)),
                    'image': {'url': main_char.portrait_url_128 },
                    'url': url
                    }
            else:
                embed = {'title': "New Group Leave Request", 
                    'description': ("From **{}** to leave **{}**".format(main_char.character_name,group)),
                    'image': {'url': main_char.portrait_url_128 },
                    'url': url
                    }

            hooks = GroupSignal.objects.filter(group=instance.group).select_related('webhook')

            for hook in hooks:
                if hook.webhook.enabled:
                    hook.webhook.send_embed(embed)

        except Exception as e:
            logger.exception(e)
            pass  # shits fucked... Don't worry about it...