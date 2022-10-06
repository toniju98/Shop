from django.contrib import admin

from .models import Item, OrderItem, Order, Address, UserProfile
from users.models import MyUser
from .signals import send_order_shipped_email, send_order_delivered_mail


def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


def make_being_delivered(modeladmin, request, queryset):
    for query in queryset:
        send_order_shipped_email(query)
    queryset.update(ordered=False, being_delivered=True)


def make_received(modeladmin, request, queryset):
    for query in queryset:
        send_order_delivered_mail(query)
    queryset.update(being_delivered=False, received=True)


make_refund_accepted.short_description = 'Update orders to refund granted'
make_being_delivered.short_description = 'Update orders to being delivered'
make_received.short_description = 'Update orders to received'


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'name',
                    'forename',
                    'ordered',
                    'being_delivered',
                    'received',
                    'refund_requested',
                    'refund_granted',
                    'shipping_address'
                    ]
    list_display_links = [
        'user',
        'shipping_address',
    ]
    list_filter = ['ordered',
                   'being_delivered',
                   'received',
                   'refund_requested',
                   'refund_granted']
    search_fields = [
        'user__username',
        'ref_code'
    ]
    actions = [make_refund_accepted, make_being_delivered, make_received]


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'street_address',
        'apartment_address',
        'country',
        'zip'
    ]
    list_filter = ['country']
    search_fields = ['user', 'street_address', 'apartment_address', 'zip']


admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(UserProfile)
admin.site.register(MyUser)
