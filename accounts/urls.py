from django.urls import path
from accounts.views import login_page, register_page ,activate_email , cart , add_to_cart ,remove_cart_item ,logout_page , remove_coupon


urlpatterns = [
    path('login/' , login_page , name="login"),
    path('register/' , register_page , name = "register"),
    path('logout/' , logout_page , name = "logout"),
    path('activate/<email_token>/' , activate_email , name = "activate_email"),
    path('add-to-cart/<uuid:uid>/' , add_to_cart , name = "add_to_cart"),
    path('cart/' , cart , name = "cart"),
    path('remove-cart/<cart_item_uid>/' , remove_cart_item , name = "remove_cart"),
    path('remove-coupon/', remove_coupon, name='remove_coupon'),
    
]