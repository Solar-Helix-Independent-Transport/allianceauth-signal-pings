import requests
import json

from django.db import models
from django.contrib.auth.models import Group
from allianceauth.eveonline.models import EveCorporationInfo


class WebHook(models.Model):
    """Discord Webhook for pings"""
    name = models.CharField(max_length=150)
    webhook_url = models.CharField(max_length=500)
    enabled = models.BooleanField()

    def send_embed(self, embed):
        custom_headers = {'Content-Type': 'application/json'}
        data = '{"embeds": [%s]}' % json.dumps(embed)
        r = requests.post(self.webhook_url, headers=custom_headers,
                          data=data)
        r.raise_for_status()

    class Meta:
        verbose_name = 'Webhook'
        verbose_name_plural = 'Webhooks'

    def __str__(self):
        return '{}'.format(self.name)


class GroupSignal(models.Model):
    """Group join/leave pings"""

    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    webhook = models.ForeignKey(WebHook, on_delete=models.CASCADE)

    def __str__(self):
        return '"{}" using "{}"'.format(self.group.name, self.webhook.name)

    class Meta:
        verbose_name = 'Group Signal'
        verbose_name_plural = 'Group Signals'


class FleetSignal(models.Model):
    """Fleet Timer Create/Delete pings"""

    webhook = models.ForeignKey(WebHook, on_delete=models.CASCADE)

    ignore_past_fleets = models.BooleanField(default=True)

    def __str__(self):
        return 'Send Fleets to "{}"'.format(self.webhook.name)

    class Meta:
        verbose_name = 'Fleet Signal'
        verbose_name_plural = 'Fleet Signals'


class TimerSignal(models.Model):
    """Timer Board Create/Delete pings"""

    webhook = models.ForeignKey(WebHook, on_delete=models.CASCADE)

    ignore_past_timers = models.BooleanField(default=True)
    corporation = models.ForeignKey(EveCorporationInfo, on_delete=models.CASCADE, blank=True, null=True, default=None)

    def __str__(self):
        return 'Send Timers to "{}"'.format(self.webhook.name)

    class Meta:
        verbose_name = 'Timer Board Signal'
        verbose_name_plural = 'Timer Board Signals'


class HRAppSignal(models.Model):
    """Timer Board Create/Delete pings"""

    webhook = models.ForeignKey(WebHook, on_delete=models.CASCADE)
    corporation = models.ForeignKey(EveCorporationInfo, on_delete=models.CASCADE, blank=True, null=True, default=None)

    notify_comments = models.BooleanField(default=True)

    def __str__(self):
        return 'Send HR to "{}"'.format(self.webhook.name)

    class Meta:
        verbose_name = 'HR Application Signal'
        verbose_name_plural = 'HR Application Signals'


class CharacterSignal(models.Model):
    """A character ownership is added/removed on Auth"""

    add_notify = models.BooleanField(default=True)
    remove_notify = models.BooleanField(default=True)
    webhook = models.ForeignKey(WebHook, on_delete=models.CASCADE)

    def __str__(self):
        return 'Send Characters to "{}"'.format(self.webhook.name)

    class Meta:
        verbose_name = 'Character Signal'
        verbose_name_plural = 'Character Signals'


class StateSignal(models.Model):
    """A characters State Changed on Auth"""

    webhook = models.ForeignKey(WebHook, on_delete=models.CASCADE)

    def __str__(self):
        return 'Send States to "{}"'.format(self.webhook.name)

    class Meta:
        verbose_name = 'State Change Signal'
        verbose_name_plural = 'State Signals'


class SRPSignal(models.Model):
    """An SRP Request is Created/Updated"""

    SRP_STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )

    webhook = models.ForeignKey(WebHook, on_delete=models.CASCADE)
    notify_type = models.CharField(max_length=8, default="Pending", choices=SRP_STATUS_CHOICES)
    mention_requestor = models.BooleanField(default=True)

    def __str__(self):
        return 'Send SRP to "{}"'.format(self.webhook.name)

    class Meta:
        verbose_name = 'SRP Signal'
        verbose_name_plural = 'SRP Signals'
