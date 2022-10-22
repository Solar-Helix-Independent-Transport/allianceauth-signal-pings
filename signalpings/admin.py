from django.contrib import admin

from .app_settings import fleets_active, hr_active, srp_active, timers_active
from .models import (
    CharacterSignal, FleetSignal, GroupSignal, HRAppSignal, SRPSignal,
    StateSignal, TimerSignal, WebHook,
)


class WebHookAdmin(admin.ModelAdmin):
    list_display=('name', 'enabled')

admin.site.register(WebHook, WebHookAdmin)

class GroupSignalAdmin(admin.ModelAdmin):
    list_display=('get_name', 'get_webhook')
    # autocomplete_fields = ['group'] proxy model says no...
    def get_name(self, obj):
        return obj.group.name
    get_name.short_description = 'Group Name'
    get_name.admin_order_field = 'group__name'

    def get_webhook(self, obj):
        return obj.webhook.name
    get_webhook.short_description = 'Webhook Name'
    get_webhook.admin_order_field = 'webhook__name'

admin.site.register(GroupSignal, GroupSignalAdmin)

class CharacterSignalAdmin(admin.ModelAdmin):
    list_display=('get_webhook','add_notify','remove_notify')
    def get_webhook(self, obj):
        return obj.webhook.name
    get_webhook.short_description = 'Webhook Name'
    get_webhook.admin_order_field = 'webhook__name'

admin.site.register(CharacterSignal, CharacterSignalAdmin)

class StateSignalAdmin(admin.ModelAdmin):
    list_display=('get_webhook',)
    def get_webhook(self, obj):
        return obj.webhook.name
    get_webhook.short_description = 'Webhook Name'
    get_webhook.admin_order_field = 'webhook__name'

admin.site.register(StateSignal, StateSignalAdmin)

if timers_active():
    class TimerSignalAdmin(admin.ModelAdmin):
        list_display=('get_webhook','get_corp','ignore_past_timers')
        raw_id_fields = ['corporation']

        def get_webhook(self, obj):
            return obj.webhook.name
        get_webhook.short_description = 'Webhook Name'
        get_webhook.admin_order_field = 'webhook__name'

        def get_corp(self, obj):
            if obj.corporation is None:
                return "All"
            return obj.corporation.corporation_name
        get_corp.short_description = 'Corporation Name'
        get_corp.admin_order_field = 'corporation__corporation_name'

    admin.site.register(TimerSignal, TimerSignalAdmin)

if fleets_active():
    class FleetSignalAdmin(admin.ModelAdmin):
        list_display=('get_webhook','ignore_past_fleets')

        def get_webhook(self, obj):
            return obj.webhook.name
        get_webhook.short_description = 'Webhook Name'
        get_webhook.admin_order_field = 'webhook__name'

    admin.site.register(FleetSignal, FleetSignalAdmin)

if hr_active():
    class HRSignalAdmin(admin.ModelAdmin):
        list_display=('get_webhook','corporation')
        raw_id_fields = ['corporation']

        def get_webhook(self, obj):
            return obj.webhook.name
        get_webhook.short_description = 'Webhook Name'
        get_webhook.admin_order_field = 'webhook__name'

    admin.site.register(HRAppSignal, HRSignalAdmin)

if srp_active():
    class SRPSignalAdmin(admin.ModelAdmin):
        list_display=('get_webhook','notify_type', 'mention_requestor')

        def get_webhook(self, obj):
            return obj.webhook.name
        get_webhook.short_description = 'Webhook Name'
        get_webhook.admin_order_field = 'webhook__name'

    admin.site.register(SRPSignal, SRPSignalAdmin)
