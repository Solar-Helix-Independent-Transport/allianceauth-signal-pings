from django.contrib import admin

from .models import WebHook, GroupSignal

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

