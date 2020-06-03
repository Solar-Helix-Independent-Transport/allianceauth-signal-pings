import requests
import json

from django.db import models
from django.contrib.auth.models import Group

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

