from django.contrib import admin

from .models import WebHook, GroupSignal, TimerSignal, FleetSignal, HRAppSignal
from .app_settings import fleets_active, timers_active, hr_active

class WebHookAdmin(admin.ModelAdmin):
    list_display=('name', 'enabled')

admin.site.register(WebHook, WebHookAdmin)

class GroupSignalAdmin(admin.ModelAdmin):
    list_display=('get_name', 'get_webhook')

    def get_name(self, obj):
        return obj.group.name
    get_name.short_description = 'Group Name'
    get_name.admin_order_field = 'group__name'

    def get_webhook(self, obj):
        return obj.webhook.name
    get_webhook.short_description = 'Webhook Name'
    get_webhook.admin_order_field = 'webhook__name'

admin.site.register(GroupSignal, GroupSignalAdmin)

if timers_active():
    class TimerSignalAdmin(admin.ModelAdmin):
        list_display=('get_webhook','ignore_past_timers')

        def get_webhook(self, obj):
            return obj.webhook.name
        get_webhook.short_description = 'Webhook Name'
        get_webhook.admin_order_field = 'webhook__name'

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

        def get_webhook(self, obj):
            return obj.webhook.name
        get_webhook.short_description = 'Webhook Name'
        get_webhook.admin_order_field = 'webhook__name'

    admin.site.register(HRAppSignal, HRSignalAdmin)

