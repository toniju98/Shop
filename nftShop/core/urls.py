from django.conf.urls import url
from django.urls import path, include
from .views import (
    ItemDetailView,
    CheckoutView,
    HomeView,
    OrderSummaryView,
    add_to_cart,
    remove_from_cart,
    remove_single_item_from_cart,
    login_user, OrderView, get_category, logout_user, login_message, get_nonce, verify_user
)

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('category/<category>/', get_category, name='category'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('add-to-cart/<slug>/<size>/', add_to_cart, name='add-to-cart'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('my-orders/', OrderView.as_view(), name='my-orders'),
    path('remove-from-cart/<slug>/<size>/', remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug>/<size>/', remove_single_item_from_cart,
         name='remove-single-item-from-cart'),
    path('login-user/', login_user, name='login-user'),
    path('logout-user/', logout_user, name='logout-user'),
    path('login-message/', login_message, name='login-message'),
    path('get-nonce/', get_nonce, name='get-nonce'),
    path('verify-user/', verify_user, name="verify-user")
]
